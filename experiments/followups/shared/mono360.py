"""360MonoDepth-style 20-view icosahedral inference baseline.

Reimplementation of the pipeline described by Rey-Area et al. (CVPR 2022):
20 icosahedral tangent views, per-view standardisation, smooth spatial affine
alignment over overlap, and frustum blending. This is a comparison baseline,
not a claim of byte-for-byte reproduction.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from scipy.spatial import ConvexHull

from pano.geometry.spherical import xyz_to_lonlat
from pano.geometry.tangent_plane import (
    TangentPlane, generate_tangent_plane, ray_norm,
    tangent_geometry_on_erp, tangent_to_erp,
)


def icosahedron_planes(size: int = 384, padding: float = 0.3) -> List[TangentPlane]:
    g = (1 + math.sqrt(5)) / 2
    vertices = np.array([
        [-1, g, 0], [1, g, 0], [-1, -g, 0], [1, -g, 0],
        [0, -1, g], [0, 1, g], [0, -1, -g], [0, 1, -g],
        [g, 0, -1], [g, 0, 1], [-g, 0, -1], [-g, 0, 1],
    ], dtype=np.float64)
    vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)
    faces = ConvexHull(vertices).simplices
    planes = []
    for face in faces:
        centre = vertices[face].mean(0)
        centre /= np.linalg.norm(centre)
        half = max(math.acos(float(np.clip(vertices[k] @ centre, -1, 1))) for k in face)
        fov = 2 * math.degrees(math.atan((1 + padding) * math.tan(half)))
        lon, lat = xyz_to_lonlat(centre)
        planes.append(generate_tangent_plane(math.degrees(float(lon)), math.degrees(float(lat)), fov, size))
    if len(planes) != 20:
        raise RuntimeError(f"Expected 20 icosahedron faces, got {len(planes)}")
    return planes


def _standardise(disparity: np.ndarray) -> np.ndarray:
    med = np.nanmedian(disparity)
    mad = np.nanmean(np.abs(disparity - med))
    return (disparity - med) / (mad + 1e-12)


def mono360_fuse(raw: List[np.ndarray], planes: List[TangentPlane], height: int, width: int,
                 grids: Tuple[Tuple[int, int], ...] = ((4, 3), (8, 7)),
                 lam_smooth: float = 40.0, lam_scale: float = 0.007,
                 iters: int = 50, sample_frac: float = 0.02,
                 max_samples: int = 20000, seed: int = 0) -> tuple[np.ndarray, Dict]:
    if len(raw) != len(planes):
        raise ValueError("One disparity map is required per tangent plane")
    values, valid, gx, gy, weights = [], [], [], [], []
    for disparity, plane in zip(raw, planes):
        spherical_disp = disparity / ray_norm(plane)
        spherical_disp = _standardise(spherical_disp)
        reproj = tangent_to_erp(np.nan_to_num(spherical_disp).astype(np.float64), plane, height, width,
                                mode="bilinear", mask=np.isfinite(spherical_disp))
        j, i, _, _, _ = tangent_geometry_on_erp(plane, height, width)
        values.append(reproj.values)
        valid.append(reproj.valid)
        gx.append(((j + 0.5) / plane.size * 2 - 1).numpy())
        gy.append(((i + 0.5) / plane.size * 2 - 1).numpy())
        weights.append(np.where(reproj.valid, np.clip((1.0 - reproj.radial) / 0.3, 0.0, 1.0) + 1e-6, 0.0))

    values, valid = np.stack(values), np.stack(valid)
    gx, gy, weights = np.stack(gx), np.stack(gy), np.stack(weights)
    rng = np.random.default_rng(seed)
    overlap = np.flatnonzero(valid.sum(0).ravel() >= 2)
    if overlap.size < 100:
        raise RuntimeError("Insufficient overlap between the 20 tangent views")
    n_samples = min(max_samples, max(1000, int(sample_frac * overlap.size)))
    selected = rng.choice(overlap, size=min(n_samples, overlap.size), replace=False)
    view_mask = torch.from_numpy(valid.reshape(len(planes), -1)[:, selected].T.astype(np.float64))
    grid_sample = torch.from_numpy(np.stack([gx.reshape(len(planes), -1)[:, selected],
                                             gy.reshape(len(planes), -1)[:, selected]], -1))[:, None]
    current = values.copy()
    info: Dict = {"n_views": len(planes), "n_overlap_samples": int(len(selected)), "alignment_energy": []}
    for cols, rows in grids:
        d_sample = torch.from_numpy(current.reshape(len(planes), -1)[:, selected].T.copy())
        scale = torch.ones(len(planes), 1, rows, cols, dtype=torch.float64, requires_grad=True)
        offset = torch.zeros(len(planes), 1, rows, cols, dtype=torch.float64, requires_grad=True)
        n_pairs = (view_mask.sum(1) * (view_mask.sum(1) - 1) / 2).sum().clamp_min(1)
        optimizer = torch.optim.LBFGS([scale, offset], max_iter=iters, line_search_fn="strong_wolfe")

        def energy():
            s = F.grid_sample(scale, grid_sample, mode="bilinear", align_corners=True,
                              padding_mode="border")[:, 0, 0].T
            o = F.grid_sample(offset, grid_sample, mode="bilinear", align_corners=True,
                              padding_mode="border")[:, 0, 0].T
            aligned = (s * d_sample + o) * view_mask
            count = view_mask.sum(1)
            disagreement = ((count * (aligned * aligned).sum(1) - aligned.sum(1) ** 2).sum() / n_pairs)
            smooth = sum(
                ((p[..., 1:, :] - p[..., :-1, :]) ** 2).sum()
                + ((p[..., :, 1:] - p[..., :, :-1]) ** 2).sum()
                for p in (scale, offset)
            ) / (len(planes) * rows * cols)
            scale_penalty = (1.0 / scale.clamp_min(1e-3)).sum()
            return disagreement + lam_smooth * smooth + lam_scale * scale_penalty

        def closure():
            optimizer.zero_grad()
            loss = energy()
            loss.backward()
            return loss

        optimizer.step(closure)
        info["alignment_energy"].append(float(energy().detach()))
        with torch.no_grad():
            full_grid = torch.from_numpy(np.stack([gx, gy], -1)).to(torch.float64)
            sf = F.grid_sample(scale.detach(), full_grid, mode="bilinear",
                               align_corners=True, padding_mode="border")[:, 0]
            of = F.grid_sample(offset.detach(), full_grid, mode="bilinear",
                               align_corners=True, padding_mode="border")[:, 0]
            current = np.where(valid, sf.numpy() * current + of.numpy(), 0.0)

    denominator = weights.sum(0)
    fused = np.where(denominator > 0, (weights * current).sum(0) / np.maximum(denominator, 1e-12), np.nan)
    return fused, info