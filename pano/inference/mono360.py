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

from pano.geometry.spherical import xyz_to_lonlat
from pano.geometry.tangent_plane import TangentPlane, generate_tangent_plane, ray_norm, tangent_geometry_on_erp, tangent_to_erp


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
    info: Dict = {"n_views": V, "n_samples": int(len(S)), "n_overlap_samples": int(len(S)), "energy": [], "alignment_energy": []}
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
        e_val = float(energy().detach())
        info["energy"].append(e_val)
        info["alignment_energy"].append(e_val)
        with torch.no_grad():
            grid_full = torch.from_numpy(np.stack([gx, gy], -1)).to(torch.float64)  # (V,H,W,2)
            sf = F.grid_sample(s.detach(), grid_full, mode="bilinear", align_corners=True, padding_mode="border")[:, 0]
            of = F.grid_sample(o.detach(), grid_full, mode="bilinear", align_corners=True, padding_mode="border")[:, 0]
            cur = np.where(valid, sf.numpy() * cur + of.numpy(), 0.0)
    den = wts.sum(0)
    out = np.where(den > 0, (wts * cur).sum(0) / np.maximum(den, 1e-12), np.nan)
    return out, info


def anchored_grid_align(Xs: List[np.ndarray], anchors: List[np.ndarray], planes: List[TangentPlane], base: np.ndarray,
                        grids: Tuple[Tuple[int, int], ...] = ((4, 3), (8, 7)), lam_smooth: float = 40.0,
                        lam_scale: float = 0.007, iters: int = 50, max_samples: int = 4000,
                        min_samples: int = 200) -> Tuple[List[np.ndarray], Dict]:
    """acgf|ico-grid: the deformable per-view (scale, offset) grids of mono360_fuse, fitted to the ERP BASELINE on
    each view's anchor pixels instead of to the other views (no mutual-consistency term):

        E = mean_v mean_{p in A_v} (s_v(p) X_v(p) + o_v(p) - b(p))^2 + lam_smooth E_smooth + lam_scale sum 1/s

    with E_smooth as in mono360_fuse and the no-collapse term averaged per cell (mono360 sums it: harmless when
    only mutual consistency matters, but against the baseline it biases every scale upwards), coarse to fine over
    `grids`. X_v (already on
    the ERP grid, in baseline units) and b are standardised by the baseline's median / mean absolute deviation so
    that the weights mean what they mean in mono360. Views with fewer than `min_samples` anchors are left as they are.
    """
    H, W = base.shape
    fb = np.isfinite(base)
    med = float(np.median(base[fb]))
    sc = float(np.mean(np.abs(base[fb] - med))) + 1e-12
    b = ((base - med) / sc).ravel()
    cur = [((X - med) / sc).ravel() for X in Xs]
    pix, gcoord, samp = [], [], []
    for X, A, pl in zip(cur, anchors, planes):
        j, i, _, _, _ = tangent_geometry_on_erp(pl, H, W)
        idx = np.flatnonzero(np.isfinite(X))
        g = np.stack([((j.numpy().ravel()[idx] + 0.5) / pl.size * 2 - 1),
                      ((i.numpy().ravel()[idx] + 0.5) / pl.size * 2 - 1)], -1)
        a = np.flatnonzero(A.ravel()[idx] & np.isfinite(b[idx]))
        if len(a) > max_samples:  # deterministic subsample
            a = a[np.linspace(0, len(a) - 1, max_samples).astype(int)]
        pix.append(idx); gcoord.append(g); samp.append(a)
    fit = [k for k in range(len(Xs)) if len(samp[k]) >= min_samples]
    info: Dict = {"n_refined": len(fit), "energy": []}
    if not fit:
        return [np.array(X, copy=True) for X in Xs], info
    S = max(len(samp[k]) for k in fit)
    V = len(fit)
    G = np.zeros((V, 1, S, 2)); M = np.zeros((V, S)); Y = np.zeros((V, S)); idx_s = []
    for r, k in enumerate(fit):
        a = samp[k]
        G[r, 0, :len(a)] = gcoord[k][a]
        M[r, :len(a)] = 1.0
        Y[r, :len(a)] = b[pix[k][a]]
        idx_s.append(a)
    G, M, Y = (torch.from_numpy(x) for x in (G, M, Y))
    for cols, rows in grids:
        Xt = np.zeros((V, S))
        for r, k in enumerate(fit):
            Xt[r, :len(idx_s[r])] = cur[k][pix[k][idx_s[r]]]
        Xt = torch.from_numpy(Xt)
        s = torch.ones(V, 1, rows, cols, dtype=torch.float64, requires_grad=True)
        o = torch.zeros(V, 1, rows, cols, dtype=torch.float64, requires_grad=True)
        opt = torch.optim.LBFGS([s, o], max_iter=iters, line_search_fn="strong_wolfe")

        def energy():
            ss = F.grid_sample(s, G, mode="bilinear", align_corners=True, padding_mode="border")[:, 0, 0]
            oo = F.grid_sample(o, G, mode="bilinear", align_corners=True, padding_mode="border")[:, 0, 0]
            res = (ss * Xt + oo - Y) * M
            e_data = ((res * res).sum(1) / M.sum(1).clamp_min(1)).mean()
            e_smooth = sum(((p[..., 1:, :] - p[..., :-1, :]) ** 2).sum() + ((p[..., :, 1:] - p[..., :, :-1]) ** 2).sum()
                           for p in (s, o)) / (V * rows * cols)
            # per-cell mean, not mono360's sum: against a fixed target the summed term inflates every scale (it is
            # as large as the data term); averaged, it only guards against s -> 0
            e_scale = (1.0 / s.clamp_min(1e-3)).sum() / (V * rows * cols)
            return e_data + lam_smooth * e_smooth + lam_scale * e_scale

        def closure():
            opt.zero_grad()
            e = energy()
            e.backward()
            return e
        opt.step(closure)
        info["energy"].append(float(energy().detach()))
        with torch.no_grad():
            for r, k in enumerate(fit):
                g = torch.from_numpy(gcoord[k])[None, None]  # (1, 1, N, 2)
                sf = F.grid_sample(s[r:r + 1].detach(), g, mode="bilinear", align_corners=True, padding_mode="border")
                of = F.grid_sample(o[r:r + 1].detach(), g, mode="bilinear", align_corners=True, padding_mode="border")
                cur[k][pix[k]] = sf[0, 0, 0].numpy() * cur[k][pix[k]] + of[0, 0, 0].numpy()
    return [(c * sc + med).reshape(H, W) for c in cur], info
