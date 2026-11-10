"""Choose the acgf|ico settings from the validation run, by the rule fixed in configs/acgf_ico.yaml (header).

    python scripts/select_acgf_ico.py results/acgf_ico_validation

Writes <dir>/selection.md and prints the values to put into inference.acgf_ico.
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import pandas as pd

TIE = 0.005


def per_image(df: pd.DataFrame, bands) -> pd.DataFrame:
    d = df[(df.weighting == "pixel") & df.band.isin(bands)]
    return d.groupby(["method", "image"]).apply(lambda g: np.average(g.abs_rel, weights=g.n),
                                                include_groups=False).unstack("method")


def score(df: pd.DataFrame, methods, bands) -> pd.DataFrame:
    err = per_image(df, bands)
    whole = per_image(df, ["all"])
    out = []
    for m in methods:
        ratio = whole[m] / whole["baseline"]
        out.append({"method": m, "criterion": float(err[m].mean()), "harm_%": 100 * float((ratio > 1.05).mean()),
                    "n_images": int(err[m].notna().sum())})
    return pd.DataFrame(out).set_index("method")


def pick(t: pd.DataFrame, simplicity) -> str:
    best = t.criterion.min()
    tied = t[t.criterion <= best + TIE].copy()
    tied["simplicity"] = [simplicity(m) for m in tied.index]
    return tied.sort_values(["harm_%", "simplicity", "criterion"]).index[0]


def main(rdir: str):
    df = pd.read_csv(os.path.join(rdir, "rows_align-equatorial.csv"))
    names = sorted(df.method.unique())
    grid = [m for m in names if m.startswith("acgf|ico-grid|polar|")]
    sph = [m for m in names if m.startswith("acgf|ico-affine|sphere|lam")]
    tg = score(df, grid, ["60-75", "75-90"])
    ts = score(df, sph, ["all"])

    def grid_simplicity(m):
        g, s = re.search(r"\|(g[\d-]+)\|s([\d.]+)$", m).groups()
        return (0 if g == "g43" else 1, float(s))

    bg, bs = pick(tg, grid_simplicity), pick(ts, lambda m: float(m.split("lam")[1]))
    g, s = re.search(r"\|(g[\d-]+)\|s([\d.]+)$", bg).groups()
    grids = {"g43": [[4, 3]], "g43-87": [[4, 3], [8, 7]]}[g]
    lam = float(bs.split("lam")[1])
    ref = score(df, [m for m in ("acgf", "mono360", "acgf|ico-affine|polar") if m in names], ["60-75", "75-90"])
    lines = [f"# acgf|ico validation selection ({rdir})", "",
             "Rule: configs/acgf_ico.yaml header (ties within %.3f -> lower harm -> simpler)." % TIE, "",
             "## ico-grid (criterion: mean per-image polar AbsRel, align-equatorial)", "", tg.round(4).to_markdown(), "",
             f"**chosen: {bg}** -> grids {grids}, lam_smooth {float(s):g}", "",
             "## sphere_lambda (criterion: mean per-image whole-image AbsRel)", "", ts.round(4).to_markdown(), "",
             f"**chosen: {bs}** -> sphere_lambda {lam:g}", "",
             "## reference (not selected on): polar AbsRel", "", ref.round(4).to_markdown(), ""]
    open(os.path.join(rdir, "selection.md"), "w").write("\n".join(lines))
    print("\n".join(lines))
    print("inference.acgf_ico ->", {"grids": grids, "lam_smooth": float(s), "sphere_lambda": lam})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/acgf_ico_validation")
