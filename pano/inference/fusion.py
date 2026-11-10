"""Fusion of the baseline ERP prediction with corrected (tangent / rotated) predictions.

Two stages:
  1. `merge_views`: combine all correction views into one corrected map D_corr (+ validity),
     weighting each view per pixel by how undistorted that pixel was *in the image the
     model actually saw* (view_lat: latitude inside a rotated ERP, off-axis angle inside a
     pinhole view).
  2. `fuse_with_baseline`: combine D_corr with D_ERP using
       A. hard replacement            D = D_corr  if |phi| > phi_t else D_ERP
       B. soft latitude blending      D = (1 - w(phi)) D_ERP + w(phi) D_corr
          w in {linear, sigmoid, cosine, polynomial}
       C. confidence fusion (heuristic; no model provides uncertainty here):
          c_i(p) = prior_i(p) * agree_i(p) * smooth_i(p)
            prior_i  : cos(view_lat)^k * seam_i  (latitude / off-axis distortion prior; seam_i
                       down-weights pixels within `seam_width` deg of an ERP input's left/right border)
            agree_i  : exp(-(log x_i - log median_j x_j)^2 / (2 sigma^2))   (multi-view agreement)
            smooth_i : exp(-local_std(log x_i/x_base) / sigma_l)           (local consistency)
          D = sum_i c_i x_i / sum_i c_i   over the baseline and all correction views.
     All values are in the fusion space of the model (range for depth models, disparity for
     affine-invariant disparity models).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from pano.geometry.erp_projection import seam_factor
from pano.geometry.spherical import latitude_map

from .baseline import ViewPrediction


# ----------------------------------------------------------------------------
# Latitude weight functions w(phi) in [0, 1], increasing towards the poles
# ----------------------------------------------------------------------------

def latitude_weight(abs_lat_deg: np.ndarray, kind: str, threshold: float, band: float = 20.0,
                    power: float = 2.0) -> np.ndarray:
    """w(|phi|): 0 well below the threshold, 1 well above it.

    hard:       step at the threshold
    linear:     ramp over [threshold - band/2, threshold + band/2]
    cosine:     raised-cosine ramp over the same interval
    polynomial: ramp^power over the same interval
    sigmoid:    logistic centred at threshold with scale band/8 (~ 0.02..0.98 over the band)
    """
    a = np.asarray(abs_lat_deg, dtype=np.float64)
    if kind == "hard":
        return (a > threshold).astype(np.float64)
    t0, t1 = threshold - band / 2.0, threshold + band / 2.0
    r = np.clip((a - t0) / max(t1 - t0, 1e-6), 0.0, 1.0)
    if kind == "linear":
        return r
    if kind == "cosine":
        return 0.5 * (1.0 - np.cos(math.pi * r))
    if kind == "polynomial":
        return r ** power
    if kind == "sigmoid":
        return 1.0 / (1.0 + np.exp(-(a - threshold) / (band / 8.0)))
    raise ValueError(kind)


def distortion_prior(view_lat_deg: np.ndarray, power: float = 2.0) -> np.ndarray:
    """cos(view_lat)^power: 1 on the view's equator / optical axis, 0 at its pole / 90 deg off-axis."""
    return np.clip(np.cos(np.radians(view_lat_deg)), 0.0, 1.0) ** power


# ----------------------------------------------------------------------------
# Stage 1: merge correction views
# ----------------------------------------------------------------------------

def view_prior(v: ViewPrediction, prior_power: float = 2.0, seam_width: float = 20.0) -> np.ndarray:
    """Distortion prior of a view: cos(view_lat)^p, times a seam factor for ERP-type inputs."""
    w = distortion_prior(v.view_lat, prior_power)
    if v.view_lon is not None:
        w = w * seam_factor(v.view_lon, seam_width)
    return w


def merge_views(views: List[ViewPrediction], mode: str = "prior", prior_power: float = 2.0,
                source_weights: Optional[Dict[str, float]] = None,
                seam_width: float = 20.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Combine correction views into one map. Returns (values, valid, summed weight).

    mode 'prior': weighted mean with weight cos(view_lat)^p (distortion-aware)
    mode 'mean' : plain mean of all valid views
    mode 'median': per-pixel median of valid views
    """
    H, W = views[0].values.shape
    if mode == "median":
        stack = np.stack([np.where(v.valid, v.values, np.nan) for v in views])
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                med = np.nanmedian(stack, 0)
        valid = np.isfinite(med)
        return med, valid, valid.astype(float)
    num = np.zeros((H, W))
    den = np.zeros((H, W))
    for v in views:
        w = view_prior(v, prior_power, seam_width) if mode == "prior" else (
            seam_factor(v.view_lon, seam_width) if v.view_lon is not None else np.ones((H, W)))
        if source_weights:
            w = w * source_weights.get(v.source, 1.0)
        w = np.where(v.valid, w, 0.0)
        num += w * np.nan_to_num(v.values)
        den += w
    valid = den > 1e-8
    return np.where(valid, num / np.maximum(den, 1e-12), np.nan), valid, den


# ----------------------------------------------------------------------------
# Stage 2: fuse with the baseline
# ----------------------------------------------------------------------------

def fuse_with_baseline(baseline: ViewPrediction, corr: np.ndarray, corr_valid: np.ndarray, method: str,
                       threshold: float, band: float = 20.0, power: float = 2.0) -> np.ndarray:
    """Hard replacement or soft latitude blending (method = hard|linear|sigmoid|cosine|polynomial)."""
    H, W = baseline.values.shape
    w = latitude_weight(np.abs(latitude_map(H, W)), method, threshold, band, power)
    w = np.where(corr_valid & np.isfinite(corr), w, 0.0)
    return (1.0 - w) * baseline.values + w * np.nan_to_num(corr)


def _local_std(x: np.ndarray, k: int = 7) -> np.ndarray:
    x = np.nan_to_num(x).astype(np.float32)
    m = cv2.blur(x, (k, k), borderType=cv2.BORDER_REFLECT)
    m2 = cv2.blur(x * x, (k, k), borderType=cv2.BORDER_REFLECT)
    return np.sqrt(np.clip(m2 - m * m, 0, None)).astype(np.float64)


def confidence_fusion(baseline: ViewPrediction, views: List[ViewPrediction], prior_power: float = 2.0,
                      sigma_agree: float = 0.10, sigma_local: float = 0.05,
                      use_agreement: bool = True, use_local: bool = True,
                      seam_width: float = 20.0) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Heuristic per-pixel confidence fusion over {baseline} U views (see module docstring)."""
    cands = [baseline] + list(views)
    H, W = baseline.values.shape
    eps = 1e-6
    logs = np.stack([np.where(c.valid, np.log(np.clip(c.values, eps, None)), np.nan) for c in cands])
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        med = np.nanmedian(logs, 0)
    num = np.zeros((H, W))
    den = np.zeros((H, W))
    base_log = logs[0]
    for i, c in enumerate(cands):
        conf = view_prior(c, prior_power, seam_width)
        if use_agreement:
            conf = conf * np.exp(-((logs[i] - med) ** 2) / (2 * sigma_agree ** 2))
        if use_local and i > 0:
            conf = conf * np.exp(-_local_std(logs[i] - base_log) / sigma_local)
        conf = np.where(c.valid & np.isfinite(conf), conf, 0.0)
        num += conf * np.nan_to_num(c.values)
        den += conf
    out = np.where(den > 1e-12, num / np.maximum(den, 1e-12), baseline.values)
    return out, {"confidence_sum": den, "consensus_log": med}
