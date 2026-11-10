"""Robust alignment of one prediction onto another (scale / affine / disparity-with-geometry).

Used in two different places, which must not be confused:

1. *Inference-time* alignment (no ground truth!): a re-projected view prediction is put on the
   scale of the baseline ERP prediction, using only "anchor" pixels where the baseline is
   assumed reliable (low latitude) and the view itself is low-distortion. This is needed for
   models whose output is only defined up to scale/shift (e.g. MiDaS) and is optional for
   metric models (e.g. DAP).

2. *Evaluation* alignment to ground truth (standard protocol for relative-depth models),
   implemented in evaluation/metrics.py, applied identically to every method.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np


def robust_lstsq(A: np.ndarray, y: np.ndarray, iters: int = 3, k: float = 2.5,
                 w: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Least squares with iterative MAD-based outlier rejection. Returns (coef, inlier_mask)."""
    inl = np.ones(len(y), bool)
    coef = np.zeros(A.shape[1])
    for _ in range(iters + 1):
        Ai, yi = A[inl], y[inl]
        if w is not None:
            sw = np.sqrt(w[inl])[:, None]
            Ai, yi = Ai * sw, yi * sw[:, 0]
        coef, *_ = np.linalg.lstsq(Ai, yi, rcond=None)
        r = y - A @ coef
        mad = np.median(np.abs(r[inl] - np.median(r[inl]))) + 1e-12
        new = np.abs(r - np.median(r[inl])) < k * 1.4826 * mad
        if new.sum() < max(10, A.shape[1] * 5) or np.array_equal(new, inl):
            break
        inl = new
    return coef, inl


def robust_median_scale(src: np.ndarray, dst: np.ndarray) -> float:
    """Scale s minimising |log(s*src) - log(dst)| (median of log ratios): robust for depth."""
    r = np.log(np.clip(dst, 1e-8, None)) - np.log(np.clip(src, 1e-8, None))
    return float(np.exp(np.median(r)))


def align_view_to_reference(view: np.ndarray, ref: np.ndarray, anchor: np.ndarray, space: str, mode: str,
                            geometry: str = "range", cos_axis: Optional[np.ndarray] = None,
                            min_anchor: int = 200, fallback: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Dict]:
    """Align `view` (ERP grid) to `ref` on `anchor` pixels.

    space='depth':      mode 'none' | 'scale' (median ratio) | 'affine' (robust LSQ in depth)
    space='disparity':  affine in disparity. For a pinhole view (geometry='planar') whose output is
                        affine in 1/z, the inverse *range* is cos(angle) * (a*d + b), so we fit
                        ref ~ A*(cos*d) + B*cos + C (3 parameters); otherwise ref ~ A*d + C.
    Returns (aligned view on the ERP grid, info dict).
    """
    info = {"mode": mode, "n_anchor": int(anchor.sum()), "anchor_fallback": False}
    if mode == "none":
        out = view.copy()
        if space == "depth" and geometry == "planar" and cos_axis is not None:
            out = out / np.clip(cos_axis, 1e-6, None)  # z -> range
        return out, info
    a = anchor & np.isfinite(view) & np.isfinite(ref)
    if a.sum() < min_anchor and fallback is not None:
        a = fallback & np.isfinite(view) & np.isfinite(ref)
        info["anchor_fallback"] = True
    info["n_anchor_used"] = int(a.sum())
    if a.sum() < 10:
        info["failed"] = True
        return np.full_like(view, np.nan), info

    if space == "depth":
        v = view
        if geometry == "planar" and cos_axis is not None:
            v = view / np.clip(cos_axis, 1e-6, None)
        if mode == "scale":
            s = robust_median_scale(v[a], ref[a])
            info["coef"] = [s]
            return v * s, info
        A = np.stack([v[a], np.ones(a.sum())], -1)
        coef, inl = robust_lstsq(A, ref[a])
        info["coef"] = coef.tolist()
        info["inlier_frac"] = float(inl.mean())
        return v * coef[0] + coef[1], info

    # disparity space. Affine-invariant models may use an affine fit, while
    # scale-invariant models (e.g. DA360) must not gain a free intercept.
    if mode == "scale":
        src = view if geometry != "planar" or cos_axis is None else cos_axis * view
        A = src[a, None]
        coef, inl = robust_lstsq(A, ref[a])
        out = coef[0] * src
    elif geometry == "planar" and cos_axis is not None:
        c = cos_axis
        A = np.stack([c[a] * view[a], c[a], np.ones(a.sum())], -1)
        coef, inl = robust_lstsq(A, ref[a])
        out = coef[0] * c * view + coef[1] * c + coef[2]
    else:
        A = np.stack([view[a], np.ones(a.sum())], -1)
        coef, inl = robust_lstsq(A, ref[a])
        out = coef[0] * view + coef[1]
    info["coef"] = coef.tolist()
    info["inlier_frac"] = float(inl.mean())
    return out, info
