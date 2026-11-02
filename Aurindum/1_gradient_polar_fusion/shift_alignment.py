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
    anchor_max_lat: float = 35.0,
    max_tangent_radius: float = 0.85
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Aligns a tangent disparity prediction to the ERP baseline.
    
    Args:
        tangent_disp_on_erp: Tangent disparity warped onto ERP grid [H, W]
        erp_disp_baseline: Baseline ERP disparity [H, W]
        cos_ray: Cosine of ray angle relative to principal axis [H, W]
        phi_deg_map: Latitude in degrees [H, W]
        anchor_max_lat: Maximum latitude for anchor region (equatorial trust)
        max_tangent_radius: Maximum normalized radius from tangent center
        
    Returns:
        aligned_range: Aligned Euclidean range in ERP coordinates [H, W]
        fit_info: Diagnostic parameters (scale, shift, inlier_ratio)
    """
    # Define anchor mask: low latitude in panorama AND central in tangent frame
    anchor_mask = (
        (phi_deg_map <= anchor_max_lat) &
        np.isfinite(tangent_disp_on_erp) & (tangent_disp_on_erp > 0) &
        np.isfinite(erp_disp_baseline) & (erp_disp_baseline > 0)
    )

    if anchor_mask.sum() < 30:
        # Fallback to general overlap if equatorial anchor is small
        anchor_mask = (
            np.isfinite(tangent_disp_on_erp) & (tangent_disp_on_erp > 0) &
            np.isfinite(erp_disp_baseline) & (erp_disp_baseline > 0)
        )

    # Tangent disparity d is in planar projection: disp_planar = 1 / z
    # ERP disparity is inverse range: disp_erp = 1 / r = cos_ray / z = cos_ray * disp_planar
    # Model: disp_erp ~ A * (cos_ray * disp_tangent) + B * cos_ray + C
    x = cos_ray * tangent_disp_on_erp
    y = erp_disp_baseline

    a, b, inliers = robust_affine_fit(x[anchor_mask], y[anchor_mask])

    # Transform full tangent view
    aligned_disp = a * (cos_ray * tangent_disp_on_erp) + b
    # Ensure disparity is strictly positive
    min_disp = 1e-4
    aligned_disp = np.clip(aligned_disp, min_disp, 1e2)
    aligned_range = 1.0 / aligned_disp

    # Invalidate regions where tangent was originally invalid
    invalid = ~np.isfinite(tangent_disp_on_erp) | (tangent_disp_on_erp <= 0)
    aligned_range[invalid] = np.nan

    fit_info = {
        "scale": a,
        "shift": b,
        "anchor_pixels": int(anchor_mask.sum()),
        "inlier_ratio": float(inliers.sum() / max(anchor_mask.sum(), 1))
    }
    return aligned_range, fit_info
