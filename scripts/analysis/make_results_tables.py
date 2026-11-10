"""Collect the key result tables (straight from the CSVs, no hand-copied numbers) into one markdown file.

    python scripts/make_results_tables.py results/midas_dpt_hybrid_synthetic [results/midas_swin2_tiny_synthetic ...]
"""
import os
import sys

import pandas as pd

COLS = ["abs_rel", "rmse", "d1", "abs_rel_0-15", "abs_rel_15-30", "abs_rel_30-45", "abs_rel_45-60", "abs_rel_60-75",
        "abs_rel_75-90", "abs_rel_polar_60_90", "model_calls", "runtime_ratio"]
IMP = ["band", "baseline_abs_rel", "corrected_abs_rel", "improvement_%", "baseline_median_abs_rel",
       "corrected_median_abs_rel", "median_per_image_impr_%", "ci95_lo_%", "ci95_hi_%", "wilcoxon_p", "images_improved"]


def short(m):
    return m.replace("|prior", "").replace("|", " ")


def md(df, fmt=".4f"):
    return df.to_markdown(floatfmt=fmt) + "\n\n"


def section(run):
    out = [f"# Results: `{run}`\n\n"]
    for region in ("equatorial", "all"):
        rep = os.path.join(run, f"report_align-{region}")
        if not os.path.isdir(rep):
            continue
        out.append(f"## GT alignment fitted on: **{region}**\n\n")
        lb = pd.read_csv(os.path.join(rep, f"latitude_bands_align-{region}.csv"), index_col=0)
        out.append("### Baseline by latitude band\n\n" + md(lb[["abs_rel", "rmse", "d1", "mae", "err_var", "pct_bad"]]))
        mc = pd.read_csv(os.path.join(rep, "main_comparison.csv"), index_col=0)
        mc.index = [short(i) for i in mc.index]
        out.append("### Main comparison (Exp. 1-4)\n\n" + md(mc[[c for c in COLS if c in mc]]))
        for name in ("tangent_plane", "rotation", "hybrid"):
            t = pd.read_csv(os.path.join(rep, f"{name}_improvement.csv"))
            out.append(f"### Improvement vs baseline: {name} (AbsRel, paired over images)\n\n" + md(t[IMP].set_index("band"), ".3f"))
        ab = pd.read_csv(os.path.join(rep, "ablation.csv"), index_col=0)
        for e, d in ab.groupby("experiment", sort=False):
            d = d.copy()
            d.index = [short(i) for i in d.index]
            out.append(f"### Ablation {e}\n\n" + md(d[["abs_rel", "abs_rel_0-15", "abs_rel_30-45", "abs_rel_45-60",
                                                        "abs_rel_60-75", "abs_rel_75-90", "abs_rel_polar_60_90",
                                                        "model_calls", "runtime_ratio"]]))
    for f, title in [("resolution.csv", "Resolution (Exp. 8, align-all)"),
                     ("resolution_align-equatorial.csv", "Resolution (Exp. 8, align-equatorial)"),
                     ("runtime_cold.csv", "Cold runtime (Exp. 9)")]:
        p = os.path.join(run, f)
        if os.path.exists(p):
            d = pd.read_csv(p, index_col=0)
            d.index = [short(i) for i in d.index]
            out.append(f"## {title}\n\n" + md(d, ".3f"))
    cdir = os.path.join(run, "latitude_control")
    if os.path.isdir(cdir):
        out.append("## Content-vs-latitude control\n\n")
        for sub in sorted(os.listdir(cdir)):
            sp = os.path.join(cdir, sub)
            if not os.path.isdir(sp):
                continue
            out.append(f"### {sub}\n\n")
            for f, t in [("control_error_by_view_latitude.csv", "AbsRel by |lat| in the model input (columns: pitch)"),
                         ("control_error_by_content_latitude.csv", "AbsRel by |lat| of the content (columns: pitch)"),
                         ("control_within_pitch_view_effect.csv", "Within-pitch, same image & content band: % change when the content sits delta deg further from the input equator")]:
                p = os.path.join(sp, f)
                if os.path.exists(p):
                    out.append(f"**{t}**\n\n" + md(pd.read_csv(p, index_col=0), ".3f"))
    return "".join(out)


if __name__ == "__main__":
    runs = sys.argv[1:] or ["results/midas_dpt_hybrid_synthetic"]
    text = "\n\n".join(section(r) for r in runs if os.path.isdir(r))
    with open("results/RESULT_TABLES.md", "w") as f:
        f.write(text)
    print("wrote results/RESULT_TABLES.md")
