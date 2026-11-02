"""360MonoDepth-style baseline (Rey-Area, Yuan & Richardt, CVPR 2022), re-implemented for comparison.

Pipeline, as in the paper:
  1. 20 tangent images centred on the faces of an icosahedron, padded by p = 0.3
     (half-FOV tan grows by 1 + p over the face's circumradius);
  2. the frozen perspective model predicts disparity on each; disparity is converted from the view
     axis to the sphere (x cos(off-axis), since 1/range = cos / z) and standardised per view
     (median / mean absolute deviation);
  3. global *deformable* alignment: per view a grid of (scale, offset) pairs, bilinearly interpolated
     over the view, minimising  E_align + 40 E_smooth + 0.007 E_scale  (pairwise disagreement on
     sampled overlap pixels, grid smoothness, sum of 1/scale), first on a 4x3 grid then on 8x7, with
     L-BFGS (50 iterations per scale);
  4. blending with "frustum" weights (1 inside the inner 70% of the view, linear to 0 at the border).

Differences from the paper (documented, not tuned): square N x N views instead of 400 x 346;
frustum blending instead of Poisson blending (the paper's Table 3 shows frustum within 0.002 AbsRel of
Poisson); torch L-BFGS instead of Ceres. The output is a full-sphere disparity map in arbitrary
affine units; it is NOT anchored to the ERP baseline (that is the method).
Only defined for disparity models.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from geometry.spherical import xyz_to_lonlat
from geometry.tangent_plane import TangentPlane, generate_tangent_plane, ray_norm, tangent_geometry_on_erp, tangent_to_erp


def icosahedron_planes(size: int = 384, padding: float = 0.3) -> List[TangentPlane]:
    """20 tangent planes centred on the icosahedron faces."""
    from scipy.spatial import ConvexHull
    g = (1 + math.sqrt(5)) / 2
    V = np.array([[-1, g, 0], [1, g, 0], [-1, -g, 0], [1, -g, 0], [0, -1, g], [0, 1, g], [0, -1, -g], [0, 1, -g],
                  [g, 0, -1], [g, 0, 1], [-g, 0, -1], [-g, 0, 1]], dtype=np.float64)
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    faces = ConvexHull(V).simplices
    planes = []
    for f in faces:
        c = V[f].mean(0)
        c /= np.linalg.norm(c)
        half = max(math.acos(float(np.clip(V[k] @ c, -1, 1))) for k in f)  # face circumradius angle
        fov = 2 * math.degrees(math.atan((1 + padding) * math.tan(half)))
        lon, lat = xyz_to_lonlat(c)
        planes.append(generate_tangent_plane(math.degrees(float(lon)), math.degrees(float(lat)), fov, size))
    return planes


def _standardise(d: np.ndarray) -> np.ndarray:
    med = np.nanmedian(d)
    return (d - med) / (np.nanmean(np.abs(d - med)) + 1e-12)


def mono360_fuse(raw: List[np.ndarray], planes: List[TangentPlane], H: int, W: int, perspective_geometry: str = "planar",
                 grids: Tuple[Tuple[int, int], ...] = ((4, 3), (8, 7)), lam_smooth: float = 40.0,
                 lam_scale: float = 0.007, iters: int = 50, sample_frac: float = 0.02, max_samples: int = 20000,
                 seed: int = 0) -> Tuple[np.ndarray, Dict]:
    """Align and blend icosahedral tangent disparities into one ERP disparity map."""
    V = len(planes)
    vals, valid, gx, gy, wts = [], [], [], [], []
    for d, pl in zip(raw, planes):
        sph = d * (1.0 / ray_norm(pl) if perspective_geometry == "planar" else 1.0)
        sph = _standardise(sph)
        r = tangent_to_erp(np.nan_to_num(sph).astype(np.float64), pl, H, W, mode="bilinear", mask=np.isfinite(sph))
        j, i, _, _, _ = tangent_geometry_on_erp(pl, H, W)
        vals.append(r.values)
        valid.append(r.valid)
        gx.append(((j + 0.5) / pl.size * 2 - 1).numpy())  # view coords in [-1, 1] for the parameter grid
        gy.append(((i + 0.5) / pl.size * 2 - 1).numpy())
        wts.append(np.where(r.valid, np.clip((1.0 - r.radial) / 0.3, 0.0, 1.0) + 1e-6, 0.0))
    vals, valid = np.stack(vals), np.stack(valid)
    gx, gy, wts = np.stack(gx), np.stack(gy), np.stack(wts)

    rng = np.random.default_rng(seed)
    overlap = np.flatnonzero(valid.sum(0).ravel() >= 2)
    n_s = int(min(max_samples, max(1000, sample_frac * overlap.size)))
    S = rng.choice(overlap, size=min(n_s, overlap.size), replace=False)
    m_s = torch.from_numpy(valid.reshape(V, -1)[:, S].T.astype(np.float64))  # (S, V)
    grid_s = torch.from_numpy(np.stack([gx.reshape(V, -1)[:, S], gy.reshape(V, -1)[:, S]], -1))[:, None]  # (V,1,S,2)
    cur = vals.copy()
    info: Dict = {"n_views": V, "n_samples": int(len(S)), "energy": []}
    for cols, rows in grids:
        d_s = torch.from_numpy(cur.reshape(V, -1)[:, S].T.copy())  # (S, V)
        s = torch.ones(V, 1, rows, cols, dtype=torch.float64, requires_grad=True)
        o = torch.zeros(V, 1, rows, cols, dtype=torch.float64, requires_grad=True)
        n_pairs = (m_s.sum(1) * (m_s.sum(1) - 1) / 2).sum().clamp_min(1)
        opt = torch.optim.LBFGS([s, o], max_iter=iters, line_search_fn="strong_wolfe")

        def energy():
            ss = F.grid_sample(s, grid_s, mode="bilinear", align_corners=True, padding_mode="border")[:, 0, 0].T
            oo = F.grid_sample(o, grid_s, mode="bilinear", align_corners=True, padding_mode="border")[:, 0, 0].T
            y = (ss * d_s + oo) * m_s
            n = m_s.sum(1)
            e_align = ((n * (y * y).sum(1) - y.sum(1) ** 2)).sum() / n_pairs  # sum_{a<b} (y_a - y_b)^2
            e_smooth = sum(((p[..., 1:, :] - p[..., :-1, :]) ** 2).sum() + ((p[..., :, 1:] - p[..., :, :-1]) ** 2).sum()
                           for p in (s, o)) / (V * rows * cols)
            e_scale = (1.0 / s.clamp_min(1e-3)).sum()
            return e_align + lam_smooth * e_smooth + lam_scale * e_scale

        def closure():
            opt.zero_grad()
            e = energy()
            e.backward()
            return e
        opt.step(closure)
        info["energy"].append(float(energy().detach()))
        with torch.no_grad():
            grid_full = torch.from_numpy(np.stack([gx, gy], -1)).to(torch.float64)  # (V,H,W,2)
            sf = F.grid_sample(s.detach(), grid_full, mode="bilinear", align_corners=True, padding_mode="border")[:, 0]
            of = F.grid_sample(o.detach(), grid_full, mode="bilinear", align_corners=True, padding_mode="border")[:, 0]
            cur = np.where(valid, sf.numpy() * cur + of.numpy(), 0.0)
    den = wts.sum(0)
    out = np.where(den > 0, (wts * cur).sum(0) / np.maximum(den, 1e-12), np.nan)
    return out, info
