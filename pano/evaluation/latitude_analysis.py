"""Latitude-resolved error analysis.

Bands are configurable, e.g. the 6 equal bands of |phi| used in the result tables
[0,15,30,45,60,75,90] or the named "distortion" bands of the spec
(equatorial <15, low 15-30, medium 30-45, high 45-60, severe 60-90).
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from pano.geometry.spherical import erp_area_weights, latitude_map

from .metrics import compute_metrics

DEFAULT_BANDS = [0, 15, 30, 45, 60, 75, 90]
NAMED_BANDS = {"equatorial": (0, 15), "low": (15, 30), "medium": (30, 45), "high": (45, 60), "severe": (60, 90.01)}


def band_masks(height: int, width: int, edges: Sequence[float] = DEFAULT_BANDS) -> Dict[str, np.ndarray]:
    a = np.abs(latitude_map(height, width))
    out = {}
    for lo, hi in zip(edges[:-1], edges[1:]):
        hi_incl = hi if hi < 90 else 90.01
        out[f"{int(lo)}-{int(hi)}"] = (a >= lo) & (a < hi_incl)
    return out


def named_band_masks(height: int, width: int, bands: Dict[str, Tuple[float, float]] = NAMED_BANDS):
    a = np.abs(latitude_map(height, width))
    return {k: (a >= lo) & (a < hi) for k, (lo, hi) in bands.items()}


def per_band_metrics(pred, gt, valid, edges=DEFAULT_BANDS, area_weighted: bool = False,
                     bad_threshold: float = 0.10, extra_masks: Optional[Dict[str, np.ndarray]] = None) -> Dict[str, Dict]:
    H, W = gt.shape
    w = erp_area_weights(H, W) if area_weighted else None
    res = {"all": compute_metrics(pred, gt, valid, w, bad_threshold)}
    masks = band_masks(H, W, edges)
    if extra_masks:
        masks.update(extra_masks)
    for k, m in masks.items():
        res[k] = compute_metrics(pred, gt, valid & m, w, bad_threshold)
    return res


def latitude_profile(err: np.ndarray, valid: np.ndarray, bin_deg: float = 2.5, signed: bool = True):
    """Mean of a per-pixel error map in latitude bins. Returns (bin centres, mean, count).

    signed=True bins latitude in [-90, 90] (north/south separately); False bins |latitude|.
    """
    H, W = err.shape
    lat = latitude_map(H, W)
    x = lat if signed else np.abs(lat)
    lo = -90 if signed else 0
    edges = np.arange(lo, 90 + 1e-9, bin_deg)
    centres = 0.5 * (edges[:-1] + edges[1:])
    idx = np.clip(np.digitize(x, edges) - 1, 0, len(centres) - 1)
    m = valid & np.isfinite(err)
    s = np.bincount(idx[m], weights=err[m], minlength=len(centres))
    c = np.bincount(idx[m], minlength=len(centres))
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = s / c
    return centres, mean, c


def bootstrap_ci(x: np.ndarray, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0, stat=np.mean):
    """Percentile bootstrap CI over images (x: per-image values)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    bs = np.array([stat(x[rng.integers(0, len(x), len(x))]) for _ in range(n_boot)])
    return float(np.quantile(bs, alpha / 2)), float(np.quantile(bs, 1 - alpha / 2))


def onset_latitude(per_image_profiles: np.ndarray, centres: np.ndarray, ref_max_lat: float = 15.0,
                   n_boot: int = 2000, seed: int = 0) -> Dict:
    """Smallest |latitude| bin whose error is significantly above the equatorial reference.

    per_image_profiles: (n_images, n_bins) mean error per |lat| bin per image.
    Test per bin: paired difference (bin - reference) across images, 95% bootstrap CI > 0.
    Returns the onset latitude and the per-bin CIs. Paired over images so that scene
    difficulty cancels out.
    """
    ref = np.nanmean(per_image_profiles[:, centres < ref_max_lat], axis=1)
    rows = []
    onset = None
    for j, c in enumerate(centres):
        d = per_image_profiles[:, j] - ref
        lo, hi = bootstrap_ci(d, n_boot=n_boot, seed=seed)
        mean_d = float(np.nanmean(d)) if np.isfinite(d).any() else float("nan")
        rel = float(np.nanmean(per_image_profiles[:, j]) / np.nanmean(ref)) if np.isfinite(d).any() else float("nan")
        sig = bool(np.isfinite(lo) and lo > 0)
        rows.append({"abs_lat": float(c), "mean_diff": mean_d, "ci_lo": lo, "ci_hi": hi, "ratio_to_ref": rel,
                     "significant": sig})
        if onset is None and c >= ref_max_lat and sig:
            # require the next bin to also be significant (avoid isolated blips)
            nxt = per_image_profiles[:, j + 1] - ref if j + 1 < len(centres) else d
            lo2, _ = bootstrap_ci(nxt, n_boot=n_boot, seed=seed + 1)
            if np.isfinite(lo2) and lo2 > 0:
                onset = float(c)
    return {"onset_abs_lat": onset, "bins": rows}
