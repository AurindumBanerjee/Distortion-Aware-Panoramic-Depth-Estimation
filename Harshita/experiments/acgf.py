"""E10 (ACGF) and E11 (360MonoDepth-style baseline) reports."""
from __future__ import annotations

import os
from typing import List

import numpy as np
import pandas as pd

from evaluation.evaluation import improvement_table

from .common import BANDS, method_table, write_markdown_table


def harm_table(df: pd.DataFrame, methods: List[str], weighting: str = "pixel") -> pd.DataFrame:
    """Per method: how often, and how badly, it is worse than the baseline on single images.

    ratio = method / baseline per image, for global AbsRel, global SqRel and polar (|lat| >= 60) AbsRel.
    harmed  : ratio > 1.05;  severe : ratio > 1.5.
    """
    d = df[df.weighting == weighting]
    out = []
    for m in methods:
        if m == "baseline":
            continue
        row = {"method": m}
        for metric, bands, tag in (("abs_rel", ["all"], "absrel"), ("sq_rel", ["all"], "sqrel"),
                                   ("abs_rel", ["60-75", "75-90"], "polar_absrel")):
            x = d[d.band.isin(bands)]
            per = x.groupby(["method", "image"]).apply(lambda g: np.average(g[metric], weights=g.n),
                                                       include_groups=False)
            if m not in per.index.get_level_values(0):
                continue
            b, c = per.loc["baseline"], per.loc[m]
            idx = b.index.intersection(c.index)
            r = (c.loc[idx] / b.loc[idx]).replace([np.inf, -np.inf], np.nan).dropna()
            row[f"{tag}_harmed_%"] = 100 * float((r > 1.05).mean())
            row[f"{tag}_severe_%"] = 100 * float((r > 1.5).mean())
            row[f"{tag}_worst_ratio"] = float(r.max())
            row[f"{tag}_improved_%"] = 100 * float((r < 0.95).mean())
        out.append(row)
    return pd.DataFrame(out).set_index("method")


def visualize_acgf(model, tmodel, sample, cfg, out_dir: str):
    """Pole views as the model sees them (RGB + raw prediction), the gate gamma and the log change vs baseline."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from inference.conformal_fusion import pole_views, render_view
    from inference.pipeline import DistortionAwareInference

    dai = DistortionAwareInference(model, tmodel)
    res = dai.run(sample.rgb, sample.id, cfg, return_views=True)
    pv = pole_views(cfg.acgf_views, cfg.tangent_size)
    raws = [e["out"] for e in dai.views_raw_batch(sample.rgb, sample.id, [v for _, v in pv])]
    n = len(pv)
    fig, ax = plt.subplots(3, max(n, 2), figsize=(3.2 * max(n, 2), 9.5))
    for k, ((pole, v), raw) in enumerate(zip(pv, raws)):
        kind = v.to_dict().get("kind", "gnomonic")
        ax[0, k].imshow(render_view(sample.rgb, v))
        ax[0, k].set_title(f"{kind} {'N' if pole > 0 else 'S'} (fov {v.fov_deg:.0f})", fontsize=9)
        ax[1, k].imshow(raw, cmap="Spectral_r")
        ax[1, k].set_title("raw model output", fontsize=9)
    for a in ax[:2].ravel():
        a.axis("off")
    for a in ax[2]:
        a.axis("off")
    g = res.get("gamma")
    if g is not None:
        im = ax[2, 0].imshow(g, vmin=0, vmax=1, cmap="viridis")
        ax[2, 0].set_title("gate gamma (1 = trust views)", fontsize=9)
        fig.colorbar(im, ax=ax[2, 0], fraction=0.025)
    ch = np.log(np.clip(res["pred"], 1e-9, None)) - np.log(np.clip(res["baseline"], 1e-9, None))
    lim = np.nanpercentile(np.abs(ch), 99) + 1e-6
    im = ax[2, 1].imshow(ch, cmap="RdBu", vmin=-lim, vmax=lim)
    ax[2, 1].set_title("log(acgf / baseline), fusion space", fontsize=9)
    fig.colorbar(im, ax=ax[2, 1], fraction=0.025)
    fig.suptitle(f"{sample.id}: ACGF views and correction")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f"acgf_views_{sample.id}.png"), dpi=110)
    plt.close(fig)


def report(df: pd.DataFrame, rdir: str, names: List[str], main_names: dict):
    """main_names: tag -> method name for E2/E3/E4 (may be partial)."""
    os.makedirs(rdir, exist_ok=True)
    present = set(df.method.unique())
    comp = ["baseline"] + [main_names[t] for t in ("E2_tangent", "E3_rotation", "E4_hybrid") if t in main_names]
    comp += [n for n in ("mono360", "acgf") if n in present]
    comp = [c for c in comp if c in present]
    mt = method_table(df, comp)
    mt.to_csv(os.path.join(rdir, "acgf_comparison.csv"))
    write_markdown_table(mt, os.path.join(rdir, "acgf_comparison.md"))

    abl = ["baseline", "acgf"] + [n for n in names if n.startswith("acgf|") and n in present]
    at = method_table(df, abl)
    at.to_csv(os.path.join(rdir, "acgf_ablation.csv"))
    write_markdown_table(at, os.path.join(rdir, "acgf_ablation.md"))

    ht = harm_table(df, comp + [n for n in abl if n not in comp])
    ht.to_csv(os.path.join(rdir, "harm.csv"))
    write_markdown_table(ht, os.path.join(rdir, "harm.md"), floatfmt=".2f")

    with open(os.path.join(rdir, "acgf_paired.md"), "w") as f:
        for other in [c for c in comp if c != "acgf"]:
            t = improvement_table(df, other, "acgf", "abs_rel", "pixel")
            if len(t) == 0:
                continue
            order = {b: i for i, b in enumerate(["all"] + BANDS)}
            t = t.sort_values("band", key=lambda s: s.map(order).fillna(99))
            f.write(f"### acgf vs {other} (AbsRel, pixel-weighted; positive = acgf better)\n\n")
            f.write(t[["band", f"baseline_abs_rel", "corrected_abs_rel", "improvement_%", "median_per_image_impr_%",
                       "ci95_lo_%", "ci95_hi_%", "wilcoxon_p", "images_improved", "n_images"]]
                    .rename(columns={"baseline_abs_rel": other, "corrected_abs_rel": "acgf"})
                    .to_markdown(index=False, floatfmt=".4f"))
            f.write("\n\n")
    return mt, at, ht


ICO_ROWS = ["baseline", "mono360", "acgf", "acgf|ico-affine|polar", "acgf|ico-affine|sphere", "acgf|ico-grid|polar",
            "acgf|ico-grid|sphere"]


def ico_report(df: pd.DataFrame, rdir: str):
    """E12 (acgf|ico): one comparison table and paired tests against baseline, mono360 and ACGF v2."""
    present = set(df.method.unique())
    rows = [m for m in ICO_ROWS if m in present]
    if not any(m.startswith("acgf|ico-") for m in rows):
        return
    mt = method_table(df, rows)
    ht = harm_table(df, rows)
    keep = ["abs_rel", "abs_rel_0-15", "abs_rel_polar_60_90", "runtime_ratio", "runtime_s"]
    t = mt[[c for c in keep if c in mt.columns]].join(ht[["absrel_harmed_%", "absrel_severe_%", "polar_absrel_harmed_%"]],
                                                      how="left")
    t.to_csv(os.path.join(rdir, "ico_comparison.csv"))
    write_markdown_table(t, os.path.join(rdir, "ico_comparison.md"))
    order = {b: i for i, b in enumerate(["all"] + BANDS)}
    with open(os.path.join(rdir, "ico_paired.md"), "w") as f:
        for m in [r for r in rows if r.startswith("acgf|ico-")]:
            for other in [o for o in ("baseline", "mono360", "acgf") if o in present]:
                p = improvement_table(df, other, m, "abs_rel", "pixel")
                if len(p) == 0:
                    continue
                p = p[p.band.isin(["all", "0-15", "60-75", "75-90"])].sort_values("band", key=lambda s: s.map(order))
                f.write(f"### {m} vs {other} (AbsRel, pixel-weighted; positive = {m} better)\n\n")
                f.write(p[["band", "baseline_abs_rel", "corrected_abs_rel", "improvement_%", "median_per_image_impr_%",
                           "wilcoxon_p", "images_improved", "n_images"]]
                        .rename(columns={"baseline_abs_rel": other, "corrected_abs_rel": m})
                        .to_markdown(index=False, floatfmt=".4f"))
                f.write("\n\n")
