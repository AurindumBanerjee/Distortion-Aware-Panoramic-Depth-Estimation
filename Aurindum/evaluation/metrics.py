"""Depth metrics with explicit handling of invalid ground truth and of prediction alignment.

All metrics are computed on pixels where GT is valid (finite, > min_depth, <= max_depth)
AND the prediction is finite and positive. Every metric can be pixel-weighted (standard)
or solid-angle-weighted (each ERP pixel weighted by cos(latitude), i.e. by the area of the
sphere it covers) -- the latter avoids over-counting the stretched polar rows.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np

METRIC_NAMES = ["abs_rel", "sq_rel", "rmse", "rmse_log", "mae", "medae", "d1", "d2", "d3", "err_var",
                "pct_bad"]


def valid_gt_mask(gt: np.ndarray, min_depth: float = 1e-3, max_depth: float = 1e3) -> np.ndarray:
    return np.isfinite(gt) & (gt > min_depth) & (gt <= max_depth)


# ----------------------------------------------------------------------------
# Alignment of predictions to GT for evaluation (identical protocol for every method)
# ----------------------------------------------------------------------------

def to_metric_depth(pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, space: str, mode: str,
                    max_depth: float = 1e3, min_depth: float = 1e-3) -> Tuple[np.ndarray, Dict]:
    """Convert a model-space prediction to metric depth for evaluation.

    space='depth':     mode 'none' (metric model) | 'median' (scale = median(gt)/median(pred))
                       | 'lsq' (least-squares scale)
    space='disparity': mode 'affine' -- least squares  1/gt ~ s*pred + t  over valid pixels
                       (MiDaS protocol), then depth = 1/clip(s*pred + t).
    The parameters are fitted on ALL valid pixels of the panorama (never per latitude band),
    so a method cannot hide polar errors by re-fitting per band.
    """
    m = mask & np.isfinite(pred)
    info: Dict = {"eval_align": mode}
    if space == "depth":
        if mode == "none":
            return pred.copy(), info
        if mode == "median":
            s = np.median(gt[m]) / np.median(pred[m])
        elif mode == "lsq":
            s = (pred[m] * gt[m]).sum() / (pred[m] ** 2).sum()
        else:
            raise ValueError(mode)
        info["scale"] = float(s)
        return pred * s, info
    # disparity
    if mode != "affine":
        raise ValueError(f"disparity predictions need affine alignment, got {mode}")
    A = np.stack([pred[m], np.ones(m.sum())], -1)
    coef, *_ = np.linalg.lstsq(A, 1.0 / gt[m], rcond=None)
    disp = coef[0] * pred + coef[1]
    disp = np.clip(disp, 1.0 / max_depth, 1.0 / min_depth)
    info["scale"], info["shift"] = float(coef[0]), float(coef[1])
    return 1.0 / disp, info


# ----------------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------------

def _wmean(x, w):
    return float((x * w).sum() / w.sum())


def compute_metrics(pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, weights: Optional[np.ndarray] = None,
                    bad_threshold: float = 0.10) -> Dict[str, float]:
    """Standard depth metrics on `mask`. pct_bad = % pixels with abs_rel > bad_threshold."""
    m = mask & np.isfinite(pred) & (pred > 0) & np.isfinite(gt) & (gt > 0)
    n = int(m.sum())
    out = {"n": n}
    if n == 0:
        out.update({k: float("nan") for k in METRIC_NAMES})
        return out
    p, g = pred[m].astype(np.float64), gt[m].astype(np.float64)
    w = np.ones_like(p) if weights is None else weights[m].astype(np.float64)
    err = p - g
    ae = np.abs(err)
    rel = ae / g
    ratio = np.maximum(p / g, g / p)
    out["abs_rel"] = _wmean(rel, w)
    out["sq_rel"] = _wmean(err ** 2 / g, w)
    out["rmse"] = float(np.sqrt(_wmean(err ** 2, w)))
    out["rmse_log"] = float(np.sqrt(_wmean((np.log(p) - np.log(g)) ** 2, w)))
    out["mae"] = _wmean(ae, w)
    out["medae"] = float(_weighted_median(ae, w))
    out["d1"] = _wmean((ratio < 1.25).astype(float), w)
    out["d2"] = _wmean((ratio < 1.25 ** 2).astype(float), w)
    out["d3"] = _wmean((ratio < 1.25 ** 3).astype(float), w)
    mu = _wmean(ae, w)
    out["err_var"] = _wmean((ae - mu) ** 2, w)
    out["pct_bad"] = 100.0 * _wmean((rel > bad_threshold).astype(float), w)
    return out


def _weighted_median(x, w):
    if np.all(w == w[0]):
        return np.median(x)
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return x[o][np.searchsorted(cw, 0.5 * cw[-1])]


def error_maps(pred: np.ndarray, gt: np.ndarray, mask: np.ndarray) -> Dict[str, np.ndarray]:
    """Per-pixel abs error, abs-rel error and signed log ratio (NaN outside mask)."""
    m = mask & np.isfinite(pred) & (pred > 0)
    ae = np.where(m, np.abs(pred - gt), np.nan)
    rel = np.where(m, ae / np.where(m, gt, 1.0), np.nan)
    lr = np.where(m, np.log(np.where(m, pred, 1.0)) - np.log(np.where(m, gt, 1.0)), np.nan)
    return {"abs": ae, "abs_rel": rel, "log_ratio": lr}
