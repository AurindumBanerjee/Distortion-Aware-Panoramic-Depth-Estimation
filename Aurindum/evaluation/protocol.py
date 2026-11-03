"""Shared evaluation protocol for the three experiment series.

Why this exists
---------------
The first GPU run aligned affine-invariant disparity to GT on the equatorial band only
(|phi| < 30 deg) and then extrapolated that fit to the poles with an effectively
unbounded depth clip (1e3 m). Whenever  s * d + t  approached zero at a pole, the
"depth" exploded to hundreds of metres (Series 2 scene 12: polar AbsRel 385,
Series 3 baseline polar AbsRel 3.47 on 10 m rooms). One such scene dominates a mean.

The protocol below
  * supports two alignment protocols:
      - 'align-all'        fit on all valid pixels (standard MiDaS protocol; headline)
      - 'align-equatorial' fit on |phi| < eq_max_lat (stricter: tests whether the polar
                           prediction is *consistent* with the equator, no polar help)
  * clamps aligned depth to the dataset's valid GT range (standard practice, e.g.
    the KITTI / NYU / Stanford2D3D evaluation code caps predictions at max depth), so a
    near-zero disparity costs a bounded error instead of an unbounded one;
  * aggregates scenes with BOTH the mean and the median, so a single blow-up cannot
    flip a conclusion unnoticed.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from evaluation.metrics import to_metric_depth
from geometry.spherical import latitude_map

PROTOCOLS = ("align-all", "align-equatorial")


def model_space(model) -> tuple:
    spec = getattr(model, "spec", None)
    space = getattr(model, "space", getattr(spec, "space", "depth"))
    scale = getattr(model, "scale", getattr(spec, "scale", "metric"))
    return space, scale


def alignment_mask(valid: np.ndarray, protocol: str, eq_max_lat: float = 30.0) -> np.ndarray:
    if protocol == "align-all":
        return valid.copy()
    if protocol == "align-equatorial":
        H, W = valid.shape
        return valid & (np.abs(latitude_map(H, W)) < eq_max_lat)
    raise ValueError(f"unknown align protocol {protocol!r}; expected one of {PROTOCOLS}")


def align_to_gt(pred: np.ndarray, gt: np.ndarray, valid: np.ndarray, model, protocol: str = "align-all",
                min_depth: float = 0.1, max_depth: float = 10.0, eq_max_lat: float = 30.0) -> np.ndarray:
    """Model-space prediction -> metric depth, aligned with `protocol` and clamped to [min, max] depth."""
    space, scale = model_space(model)
    if space == "disparity":
        mode = "affine"
    else:
        mode = "none" if scale == "metric" else "lsq"
    m = alignment_mask(valid, protocol, eq_max_lat)
    aligned, _ = to_metric_depth(pred, gt, m, space=space, mode=mode, max_depth=max_depth, min_depth=min_depth)
    aligned = np.where(np.isfinite(aligned), aligned, max_depth)
    return np.clip(aligned, min_depth, max_depth)


def aggregate(list_m: List[Dict], how: str = "mean") -> Dict:
    """Aggregate per-scene per-band metric dicts into one dict (mean or median over scenes)."""
    fn = np.nanmedian if how == "median" else np.nanmean
    out: Dict = {}
    for band in list_m[0]:
        out[band] = {}
        for k in list_m[0][band]:
            vals = np.array([m[band][k] for m in list_m], dtype=float)
            out[band][k] = float(fn(vals)) if np.isfinite(vals).any() else float("nan")
    return out


def win_rate(base: List[Dict], method: List[Dict], band: str, key: str = "abs_rel") -> float:
    """Fraction of scenes where `method` beats `base` on band/key (lower is better)."""
    b = np.array([m[band][key] for m in base])
    x = np.array([m[band][key] for m in method])
    ok = np.isfinite(b) & np.isfinite(x)
    return float((x[ok] < b[ok]).mean()) if ok.any() else float("nan")


def depth_cap_from_cfg(cfg: Dict, default_min: float, default_max: float) -> tuple:
    ev = cfg.get("evaluation", {})
    return float(ev.get("min_depth", default_min)), float(ev.get("max_depth", default_max))


BANDS = ["all", "0-15", "15-30", "30-45", "45-60", "60-75", "75-90"]


def summarize_methods(per_scene: Dict[str, List[Dict]], protocols, baseline_key: str = "Baseline") -> Dict:
    """per_scene[method] = list over scenes of {protocol: per-band metrics}.

    Returns {protocol: {method: {"mean": ..., "median": ..., "win_rate_vs_baseline": {band: x}}}}.
    """
    out: Dict = {}
    for proto in protocols:
        out[proto] = {}
        base = [s[proto] for s in per_scene[baseline_key]]
        for name, scenes in per_scene.items():
            lst = [s[proto] for s in scenes]
            out[proto][name] = {
                "mean": aggregate(lst, "mean"),
                "median": aggregate(lst, "median"),
                "win_rate_vs_baseline": {b: win_rate(base, lst, b) for b in BANDS} if name != baseline_key else {},
            }
    return out


def format_table(summary_proto: Dict, stat: str = "median") -> List[str]:
    lines = [f"{'Method':<25} | {'Global AbsRel':>13} | {'60-75 AbsRel':>12} | {'75-90 AbsRel':>12} | "
             f"{'d1 (all)':>8} | {'win 75-90':>9}"]
    lines.append("-" * len(lines[0]))
    for name, rec in summary_proto.items():
        m = rec[stat]
        wr = rec["win_rate_vs_baseline"].get("75-90", float("nan"))
        wr_s = "    -    " if not rec["win_rate_vs_baseline"] else f"{100 * wr:8.0f}%"
        lines.append(f"{name:<25} | {m['all']['abs_rel']:13.4f} | {m['60-75']['abs_rel']:12.4f} | "
                     f"{m['75-90']['abs_rel']:12.4f} | {100 * m['all']['d1']:7.2f}% | {wr_s}")
    return lines
