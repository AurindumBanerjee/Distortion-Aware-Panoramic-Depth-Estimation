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

PROTOCOLS = ("none", "align-all", "align-equatorial")


def model_space(model) -> tuple:
    spec = getattr(model, "spec", None)
    space = getattr(model, "space", getattr(spec, "space", "depth"))
    scale = getattr(model, "scale", getattr(spec, "scale", "metric"))
    return space, scale


def default_protocols(model) -> tuple:
    """Metric models (DAP): raw metres is the headline, a global median-scale fit second.
    Relative models (MiDaS): align-all headline, align-equatorial second."""
    space, scale = model_space(model)
    if space == "depth" and scale == "metric":
        return ("none", "align-all")
    return ("align-all", "align-equatorial")


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
    if protocol == "none":
        if not (space == "depth" and scale == "metric"):
            raise ValueError("protocol 'none' (raw metric output) needs a metric depth model")
        aligned = np.asarray(pred, dtype=np.float64)
        aligned = np.where(np.isfinite(aligned), aligned, max_depth)
        return np.clip(aligned, min_depth, max_depth)
    if space == "disparity":
        mode = "affine"
    else:
        # relative depth: least-squares scale; metric depth under align-*: median scale
        # (removes a global scale error only, as in the DAP / PanDA evaluation code)
        mode = "lsq" if scale != "metric" else "median"
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


def group_of(scene_id) -> str:
    """Cluster id of a scene: scenes of the same house / environment are correlated, so they must be
    resampled together. Structured3D 'scene_03202_room_x' -> 'scene_03202'; PanoX 'ClothingStore_0028' -> 'ClothingStore'; anything else: the id itself (no clustering)."""
    import re
    sid = str(scene_id)
    m = re.match(r"(scene_\d+)", sid)
    if m:
        return m.group(1)
    m = re.match(r"((?:Indoor|Outdoor)_\d+)_", sid)  # Holo360D 'Indoor_016_1753495960.845721' -> scene 'Indoor_016'
    if m:
        return m.group(1)
    # PanoX: '<environment>_<frame>' -> environment. Environment names may contain digits and underscores
    # ('Diner50_0002', 'FeudalJapan_Meshingun_0000', 'Mountain_Environment_Set_0028'); the first version only
    # accepted letters, so 3 of the 8 environments fell back to one cluster per frame (80 groups instead of 8).
    m = re.match(r"(.+?)_\d+$", sid)
    return m.group(1) if m else sid


def paired_test(base: List[Dict], method: List[Dict], band: str, key: str = "abs_rel",
                n_boot: int = 2000, seed: int = 0, groups: Optional[List[str]] = None) -> Dict[str, float]:
    """Paired comparison of method vs baseline over the SAME scenes (lower `key` is better).

    Returns
      p_wilcoxon: two-sided Wilcoxon signed-rank p-value on per-scene differences
      rel_gain_median: median over scenes of (base - method) / base   (> 0 = method better)
      ci_low / ci_high: 95% bootstrap CI (scenes resampled) of rel_gain_median
      n: number of paired scenes
    If `groups` (one label per scene) is given, scene differences are first averaged within each group and
    the bootstrap / Wilcoxon run over groups (cluster-robust); `n_groups` is then reported.
    """
    b = np.array([m[band][key] for m in base], dtype=float)
    x = np.array([m[band][key] for m in method], dtype=float)
    ok = np.isfinite(b) & np.isfinite(x) & (b > 0)
    b, x = b[ok], x[ok]
    n_scenes = int(ok.sum())
    n_groups = None
    if groups is not None:
        g = np.array([str(v) for v in groups])[ok]
        uniq = sorted(set(g))
        b = np.array([b[g == u].mean() for u in uniq])
        x = np.array([x[g == u].mean() for u in uniq])
        n_groups = len(uniq)
    res = {"n": n_scenes, "n_groups": n_groups, "p_wilcoxon": float("nan"), "rel_gain_median": float("nan"),
           "ci_low": float("nan"), "ci_high": float("nan")}
    if len(b) < 2:
        return res
    rel = (b - x) / b
    res["rel_gain_median"] = float(np.median(rel))
    rng = np.random.default_rng(seed)
    boots = np.median(rel[rng.integers(0, len(rel), (n_boot, len(rel)))], axis=1)
    res["ci_low"], res["ci_high"] = (float(v) for v in np.percentile(boots, [2.5, 97.5]))
    d = b - x
    if np.any(d != 0):
        try:
            from scipy.stats import wilcoxon
            res["p_wilcoxon"] = float(wilcoxon(b, x, zero_method="wilcox", alternative="two-sided").pvalue)
        except Exception:
            pass
    return res


def summarize_methods(per_scene: Dict[str, List[Dict]], protocols, baseline_key: str = "Baseline",
                      groups: Optional[List[str]] = None) -> Dict:
    """per_scene[method] = list over scenes of {protocol: per-band metrics}.

    Returns {protocol: {method: {"mean", "median", "win_rate_vs_baseline": {band},
                                 "paired_vs_baseline": {band: paired_test(...)}}}}.
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
                "paired_vs_baseline": {b: paired_test(base, lst, b, groups=groups) for b in BANDS} if name != baseline_key else {},
            }
    return out


def _fmt_p(p: float) -> str:
    if not np.isfinite(p):
        return "   n/a"
    return f"{p:6.3f}" if p >= 0.001 else "<0.001"


def format_table(summary_proto: Dict, stat: str = "median", band: str = "75-90") -> List[str]:
    """One row per method: global/polar AbsRel, d1, and the paired test vs baseline on `band`."""
    hdr = (f"{'Method':<25} | {'Global AbsRel':>13} | {'60-75 AbsRel':>12} | {'75-90 AbsRel':>12} | "
           f"{'d1 (all)':>8} | {'win ' + band:>9} | {'gain ' + band + ' [95% CI]':>24} | {'p (Wilcoxon)':>12}")
    lines = [hdr, "-" * len(hdr)]
    for name, rec in summary_proto.items():
        m = rec[stat]
        if rec["win_rate_vs_baseline"]:
            wr = f"{100 * rec['win_rate_vs_baseline'][band]:8.0f}%"
            pt = rec["paired_vs_baseline"][band]
            gain = f"{100 * pt['rel_gain_median']:+6.1f}% [{100 * pt['ci_low']:+5.1f},{100 * pt['ci_high']:+5.1f}]"
            pv = _fmt_p(pt["p_wilcoxon"])
        else:
            wr, gain, pv = "    -    ", "(reference)", "-"
        lines.append(f"{name:<25} | {m['all']['abs_rel']:13.4f} | {m['60-75']['abs_rel']:12.4f} | "
                     f"{m['75-90']['abs_rel']:12.4f} | {100 * m['all']['d1']:7.2f}% | {wr} | {gain:>24} | {pv:>12}")
    return lines


def format_band_table(summary_proto: Dict, method: str, stat: str = "median", baseline_key: str = "Baseline") -> List[str]:
    """Per-band baseline vs method with win rate, median relative gain + CI and Wilcoxon p."""
    hdr = (f"{'Band':<8} | {'Baseline':>9} | {method[:12]:>12} | {'win':>5} | {'gain [95% CI]':>24} | {'p':>7}")
    lines = [hdr, "-" * len(hdr)]
    for b in BANDS:
        bv = summary_proto[baseline_key][stat][b]["abs_rel"]
        mv = summary_proto[method][stat][b]["abs_rel"]
        wr = summary_proto[method]["win_rate_vs_baseline"][b]
        pt = summary_proto[method]["paired_vs_baseline"][b]
        gain = f"{100 * pt['rel_gain_median']:+6.1f}% [{100 * pt['ci_low']:+5.1f},{100 * pt['ci_high']:+5.1f}]"
        lines.append(f"{b:<8} | {bv:9.4f} | {mv:12.4f} | {100 * wr:4.0f}% | {gain:>24} | {_fmt_p(pt['p_wilcoxon']):>7}")
    return lines
