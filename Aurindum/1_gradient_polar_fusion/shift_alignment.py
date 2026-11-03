"""Shift-Decoupled Disparity Alignment for Heterogeneous Projections.

Inspired by DA360 (arXiv:2512.22819) and Depth Anywhere (arXiv:2406.12849).
Perspective foundation models (MiDaS, Depth Anything V2) output affine-invariant disparity:
    d = s * (1 / z) + t
where s is scale and t is an unknown per-view additive shift.

When projecting tangent views back to equirectangular range r = z / cos(ray_angle),
an uncalibrated shift t severely warps depths non-linearly:
    1 / r = cos(theta) * (d - t) / s.

This module provides:
1. Robust equatorial anchor fitting on trusted overlap pixels (|phi| < anchor_max_lat).
2. Outlier rejection via Median Absolute Deviation (MAD).
3. Shift-decoupled scale alignment to guarantee continuity at the polar boundary.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger("ShiftAlignment")


def robust_affine_fit(
    x: np.ndarray,
    y: np.ndarray,
    max_iters: int = 5,
    mad_threshold: float = 2.5
) -> Tuple[float, float, np.ndarray]:
    """Fits y ~ a * x + b using iteratively reweighted least squares with MAD outlier rejection."""
    valid = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if valid.sum() < 20:
        logger.warning("Too few anchor pixels for robust fit; defaulting to identity.")
        return 1.0, 0.0, valid

    inliers = valid.copy()
    a, b = 1.0, 0.0

    for _ in range(max_iters):
        xi = x[inliers]
        yi = y[inliers]
        if len(xi) < 10:
            break

        A = np.stack([xi, np.ones_like(xi)], axis=-1)
        res, *_ = np.linalg.lstsq(A, yi, rcond=None)
        a, b = float(res[0]), float(res[1])

        # Enforce positive scale
        if a <= 0:
            a = 1.0

        # Residuals
        residuals = np.abs(y[valid] - (a * x[valid] + b))
        med = np.median(residuals)
        mad = np.median(np.abs(residuals - med)) + 1e-6
        inliers_idx = np.where(valid)[0]
        inliers_mask = residuals < (mad_threshold * 1.4826 * mad)
        inliers = np.zeros_like(valid)
        inliers[inliers_idx[inliers_mask]] = True

    return a, b, inliers


def align_tangent_disparity_to_erp(
    tangent_disp_on_erp: np.ndarray,
    erp_disp_baseline: np.ndarray,
    cos_ray: np.ndarray,
    phi_deg_map: np.ndarray,
    anchor_max_lat: float = 60.0,
    max_tangent_radius: float = 0.85,
    return_range: bool = False,
    min_anchor_pixels: int = 200,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Aligns a tangent disparity prediction to the ERP baseline disparity.

    The result is returned in the SAME space as `erp_disp_baseline` (ERP inverse range),
    so it can be blended / gradient-fused with the ERP prediction directly. (The first
    version returned *range* here and fused it against ERP *disparity*: a unit mismatch.)

    Anchor pixels: tangent/ERP overlap with |phi| <= anchor_max_lat. A polar tangent view
    with a 90 deg FOV only reaches down to ~35-45 deg latitude, so the old default of 35 deg
    left (almost) no anchor pixels and silently fell back to fitting on the pole itself,
    i.e. on exactly the region the ERP prediction is not trusted. The default ring is now
    the 45-60 deg overlap band; if it is still too small we fall back to the lowest-latitude
    20% of the overlap (never to the full cap).

    Args:
        tangent_disp_on_erp: Tangent (planar) disparity warped onto the ERP grid [H, W]
        erp_disp_baseline: Baseline ERP disparity [H, W]
        cos_ray: Cosine of ray angle relative to the tangent principal axis [H, W]
        phi_deg_map: |latitude| in degrees [H, W]
        anchor_max_lat: Maximum |latitude| of anchor pixels
        return_range: if True, return 1 / aligned disparity (legacy behaviour)

    Returns:
        aligned: Aligned ERP disparity (or range if return_range) [H, W], NaN outside the view
        fit_info: Diagnostic parameters (scale, shift, anchor_pixels, inlier_ratio)
    """
    overlap = (
        np.isfinite(tangent_disp_on_erp) & (tangent_disp_on_erp > 0) &
        np.isfinite(erp_disp_baseline) & (erp_disp_baseline > 0) & np.isfinite(cos_ray)
    )
    anchor_mask = overlap & (phi_deg_map <= anchor_max_lat)
    fallback = False
    if anchor_mask.sum() < min_anchor_pixels and overlap.any():
        thr = np.percentile(phi_deg_map[overlap], 20.0)
        anchor_mask = overlap & (phi_deg_map <= thr)
        fallback = True
        logger.warning(f"Anchor ring |phi|<={anchor_max_lat} too small; using lowest-latitude 20% "
                       f"of the overlap (|phi|<={thr:.1f}).")

    # Tangent disparity is planar: d_t ~ 1 / z.  ERP disparity ~ 1 / r = cos_ray / z.
    # Model:  d_erp ~ a * (cos_ray * d_t) + b
    x = cos_ray * tangent_disp_on_erp
    y = erp_disp_baseline
    a, b, inliers = robust_affine_fit(x[anchor_mask], y[anchor_mask])

    aligned_disp = a * x + b
    floor = max(1e-6, 0.25 * float(np.nanpercentile(y[overlap], 1.0))) if overlap.any() else 1e-6
    aligned_disp = np.clip(aligned_disp, floor, None)
    aligned_disp = np.where(overlap | (np.isfinite(tangent_disp_on_erp) & (tangent_disp_on_erp > 0)),
                            aligned_disp, np.nan)
    out = 1.0 / aligned_disp if return_range else aligned_disp

    fit_info = {
        "scale": a,
        "shift": b,
        "anchor_pixels": int(anchor_mask.sum()),
        "inlier_ratio": float(inliers.sum() / max(anchor_mask.sum(), 1)),
        "anchor_fallback": fallback,
    }
    return out, fit_info
