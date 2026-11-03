"""Training-free floor / ceiling plane prior for the polar caps (Method 1 variant 'PlanarPrior').

Indoors, the polar caps of a level panorama are mostly floor (nadir) and ceiling (zenith). A plane
n . X = h seen from the camera centre has range r = h / (n . w) for unit ray w, so its INVERSE range is
linear in the ray direction:  1/r = (n/h) . w. Consequently

  * affine-invariant disparity (MiDaS: d = s/r + t):   d = c . w + beta     (4 unknowns, t and s absorbed)
  * metric depth (DAP):                                1/r = c . w          (3 unknowns)

are linear least-squares problems. The plane is fitted (robustly) to the model's OWN prediction on a ring of
latitudes where the ERP prediction is still trusted (default 40-60 deg), checked, and extrapolated into the cap.
No ground truth is used. Checks that switch the prior off for one pole:
  * too few ring pixels agree with the plane (inlier share < min_inlier: furniture, clutter, outdoor terrain);
  * the plane is tilted more than max_tilt_deg from horizontal (panoramas are gravity-levelled);
  * the plane is behind the camera somewhere in the cap (c . w <= 0).
Inside an accepted cap, pixels where the model disagrees with the plane by more than agree_tol (relative, in
inverse range) keep the model (objects standing on the floor). The plane values are then handed to the
gradient-domain fusion, which uses only their GRADIENTS above the ring and pins the level at the ring.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from geometry.spherical import erp_to_sphere, latitude_map
from shift_alignment import robust_linear_fit


def fit_polar_planes(pred_erp: np.ndarray, space: str, ring: Tuple[float, float] = (40.0, 60.0),
                     cap_from: float = 40.0, min_inlier: float = 0.6, inlier_tol: float = 0.05,
                     max_tilt_deg: float = 20.0, agree_tol: float = 0.5) -> Tuple[np.ndarray, List[Dict]]:
    """Plane prediction for both caps in the model's output space (NaN where no accepted plane).

    pred_erp: model output on the ERP grid; space: 'disparity' (affine-invariant) or 'depth' (metric range).
    Returns (plane_pred, infos) with plane_pred in the same space as pred_erp.
    """
    H, W = pred_erp.shape
    lat = latitude_map(H, W)
    dirs = erp_to_sphere(H, W).numpy()  # (H, W, 3): x right, y down, z forward
    pred = np.asarray(pred_erp, dtype=np.float64)
    inv = pred if space == "disparity" else np.where(np.isfinite(pred) & (pred > 0), 1.0 / pred, np.nan)
    out = np.full((H, W), np.nan)
    infos = []
    up = np.array([0.0, -1.0, 0.0])
    for sign, name in ((-1.0, "floor"), (1.0, "ceiling")):
        info = {"pole": name, "accepted": False}
        ring_m = (lat * sign >= ring[0]) & (lat * sign <= ring[1]) & np.isfinite(inv)
        if ring_m.sum() < 200:
            info["reason"] = "ring too small"
            infos.append(info)
            continue
        X = dirs[ring_m]
        if space == "disparity":
            X = np.concatenate([X, np.ones((len(X), 1))], 1)
        y = inv[ring_m]
        coef, _ = robust_linear_fit(X, y)
        if not np.all(np.isfinite(coef)):
            info["reason"] = "fit failed"
            infos.append(info)
            continue
        c = coef[:3]
        beta = coef[3] if space == "disparity" else 0.0
        fit_ring = X @ coef
        share = float(np.mean(np.abs(fit_ring - y) <= inlier_tol * np.abs(y)))
        # plane normal from the camera towards the plane is +-c; it must point along gravity (down for the floor)
        tilt = float(np.degrees(np.arccos(np.clip(abs(c @ up) / max(np.linalg.norm(c), 1e-12), -1, 1))))
        cap = lat * sign >= cap_from
        cw = dirs[cap] @ c
        info.update(inlier_share=share, tilt_deg=tilt, c=c.tolist(), beta=float(beta))
        if share < min_inlier:
            info["reason"] = f"inlier share {share:.2f} < {min_inlier}"
        elif tilt > max_tilt_deg:
            info["reason"] = f"tilt {tilt:.1f} > {max_tilt_deg}"
        elif np.any(cw <= 0):
            info["reason"] = "plane behind camera in the cap"
        else:
            plane_inv = np.full((H, W), np.nan)
            plane_inv[cap] = cw + beta
            agree = np.abs(inv - plane_inv) <= agree_tol * np.abs(plane_inv)
            use = cap & (agree | ~np.isfinite(inv)) & (plane_inv > 0)
            vals = plane_inv if space == "disparity" else 1.0 / plane_inv
            out[use] = vals[use]
            info.update(accepted=True, cap_share_used=float(use.sum() / max(cap.sum(), 1)))
        infos.append(info)
    return out, infos
