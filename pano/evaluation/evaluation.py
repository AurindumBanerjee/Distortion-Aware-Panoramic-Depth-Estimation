"""Evaluation bookkeeping: per-image/per-band metric rows, summaries, paired comparisons."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from .latitude_analysis import DEFAULT_BANDS, bootstrap_ci, latitude_profile, per_band_metrics
from .metrics import error_maps, to_metric_depth


class Evaluator:
    def __init__(self, space: str, eval_align: str, edges: Sequence[float] = DEFAULT_BANDS,
                 bad_threshold: float = 0.10, profile_bin: float = 2.5, max_depth: float = 100.0,
                 align_region: str = "all", align_region_max_lat: float = 30.0):
        """align_region: pixels used to fit the GT alignment of relative models.
        'all'        standard protocol: fit on every valid pixel.
        'equatorial' fit only on |lat| < align_region_max_lat. All correction methods leave
                     these pixels (almost) unchanged, so the fitted scale/shift is (almost) the
                     same for every method and polar differences are not blurred by the global fit.
        """
        self.align_region, self.align_region_max_lat = align_region, align_region_max_lat
        self.space, self.eval_align = space, eval_align
        self.edges, self.bad_threshold, self.profile_bin = list(edges), bad_threshold, profile_bin
        self.max_depth = max_depth
        self.rows: List[Dict] = []
        self.profiles: Dict[str, List[np.ndarray]] = defaultdict(list)  # method -> per-image |lat| profiles
        self.profile_centres: Optional[np.ndarray] = None

    def to_metric(self, pred, gt, valid):
        fit = valid
        if self.align_region == "equatorial":
            from pano.geometry.spherical import latitude_map
            fit = valid & (np.abs(latitude_map(*gt.shape)) < self.align_region_max_lat)
        return to_metric_depth(pred, np.nan_to_num(gt, nan=1.0), fit, self.space, self.eval_align,
                               max_depth=self.max_depth)

    def add(self, image_id: str, method: str, pred: np.ndarray, gt: np.ndarray, valid: np.ndarray,
            run_info: Optional[Dict] = None, extra_masks: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        """Evaluate one prediction (fusion space). Returns the metric-depth prediction used."""
        gt0 = np.nan_to_num(gt, nan=1.0)
        depth, ainfo = self.to_metric(pred, gt, valid)
        for weighting in ("pixel", "area"):
            res = per_band_metrics(depth, gt0, valid, self.edges, area_weighted=(weighting == "area"),
                                   bad_threshold=self.bad_threshold, extra_masks=extra_masks)
            for band, m in res.items():
                row = {"image": image_id, "method": method, "band": band, "weighting": weighting, **m}
                if run_info:
                    row.update({k: v for k, v in run_info.items() if isinstance(v, (int, float, str))})
                self.rows.append(row)
        rel = error_maps(depth, gt0, valid)["abs_rel"]
        c, mean, _ = latitude_profile(rel, valid, self.profile_bin, signed=False)
        self.profile_centres = c
        self.profiles[method].append(mean)
        return depth

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)

    def summary(self, weighting: str = "pixel", metrics=("abs_rel", "sq_rel", "rmse", "rmse_log", "mae", "medae",
                                                        "d1", "d2", "d3", "err_var", "pct_bad")) -> pd.DataFrame:
        df = self.frame()
        df = df[df.weighting == weighting]
        return df.groupby(["method", "band"], sort=False)[list(metrics)].mean().reset_index()


def improvement_table(df: pd.DataFrame, baseline: str, method: str, metric: str = "abs_rel",
                      weighting: str = "pixel", higher_is_better: bool = False, n_boot: int = 2000) -> pd.DataFrame:
    """Per band: baseline vs method, % improvement = (E_b - E_c)/E_b*100 (sign flipped for delta metrics),
    paired bootstrap 95% CI over images of the per-image improvement, and Wilcoxon p-value."""
    from scipy.stats import wilcoxon

    d = df[df.weighting == weighting]
    out = []
    for band in d.band.unique():
        b = d[(d.method == baseline) & (d.band == band)].set_index("image")[metric]
        c = d[(d.method == method) & (d.band == band)].set_index("image")[metric]
        idx = b.index.intersection(c.index)
        b, c = b.loc[idx].values, c.loc[idx].values
        ok = np.isfinite(b) & np.isfinite(c)
        b, c = b[ok], c[ok]
        if len(b) == 0:
            continue
        eb, ec = b.mean(), c.mean()
        imp = (ec - eb) / eb * 100 if higher_is_better else (eb - ec) / eb * 100
        per_img = (c - b) / b * 100 if higher_is_better else (b - c) / b * 100
        lo, hi = bootstrap_ci(per_img, n_boot=n_boot)
        try:
            p = float(wilcoxon(b, c).pvalue) if len(b) >= 6 and np.any(b != c) else float("nan")
        except ValueError:
            p = float("nan")
        out.append({"band": band, f"baseline_{metric}": eb, f"corrected_{metric}": ec, "improvement_%": imp,
                    "per_image_impr_mean_%": float(per_img.mean()), "ci95_lo_%": lo, "ci95_hi_%": hi,
                    "wilcoxon_p": p, "n_images": int(len(b)),
                    f"baseline_median_{metric}": float(np.median(b)), f"corrected_median_{metric}": float(np.median(c)),
                    "median_per_image_impr_%": float(np.median(per_img)),
                    "images_improved": int((per_img > 0).sum())})
    return pd.DataFrame(out)
