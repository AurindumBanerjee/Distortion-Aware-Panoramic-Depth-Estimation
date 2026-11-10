#!/usr/bin/env python3
"""Appendix figures of the submission runs, drawn from the result JSON files (never from the markdown tables).

  fig_diag_nadir_jpeg.png      nadir / nadir+JPEG ladder (results/diag): region AbsRel change vs raw per variant, 95% bootstrap CI
  fig_da2_protocols.png        DA2 least-squares vs median scale fit: change per scenario (6 datasets) and clean AbsRel
  fig_strict_rules.png         offline threshold sweep: harmful cells against mean change for the rule grid (core LOO, external)
  fig_da2_sweeps_protocols.png rotation / dilation excess error dE(L) for DA2 under both protocols (5 datasets)

Writes into results/figures/ and, if the folder exists, Report/draft/figs/.
Usage: python scripts/make_submission_figures.py [--out DIR]"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402

from scripts.analysis.da2_protocol_report import clean_median, load_json, matched, sweep_path  # noqa: E402
from scripts.analysis.final_summary import CORE, EXT, SCEN, cell  # noqa: E402
from scripts.run.nadir_jpeg_diagnosis import summarize  # noqa: E402

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
                     "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False,
                     "axes.spines.right": False})
GOOD, BAD = "#2e7d32", "#c62828"
RES = ROOT / "results"
DRAFT_FIGS = ROOT / "Report" / "draft" / "figs"
LADDER = [("oracle", "true mask"), ("oracle+1.5", "true mask + 1.5$^\\circ$"), ("detected", "detected mask"),
          ("detected+1.5", "detected + 1.5$^\\circ$"), ("deblock_oracle", "deblock, then fill (true mask)"),
          ("pipe_photometric", "photometric, then fill (pipeline)"), ("pipe_cap_first", "fill, then photometric")]
SCEN_LABEL = {"clean": "clean", "tilt": "tilt", "nadir": "bottom", "vfov": "FOV", "yawblur": "shake", "jpeg": "JPEG", "nadir+jpeg": "bot.+JPEG"}


def ladder_values(rows, protocol, fill, metric="region"):
    """{kind: {ladder key: (change %, ci_lo %, ci_hi %)}} from diag rows; variants a kind lacks are absent."""
    out = {}
    for kind in ("nadir", "nadir+jpeg"):
        if not rows or kind not in rows[0] or protocol not in rows[0][kind]:
            continue
        _, items = summarize(rows, kind, protocol, metric)
        d = {n: (100 * m, 100 * lo, 100 * hi) for n, _, m, _, lo, hi in items}
        out[kind] = {k: d[f"{k}:{fill}"] for k, _ in LADDER if f"{k}:{fill}" in d}
    return out


def fig_diag(panels, out):
    """panels: [(title, rows, protocol, fill)]. Horizontal bars, one pair (nadir, nadir+JPEG) per ladder variant."""
    fig, axes = plt.subplots(1, len(panels), figsize=(7.0, 3.0), sharey=True, squeeze=False)
    for ax, (title, rows, protocol, fill) in zip(axes[0], panels):
        v = ladder_values(rows, protocol, fill)
        y0 = np.arange(len(LADDER))[::-1]
        for off, kind, alpha in ((0.19, "nadir", 0.45), (-0.19, "nadir+jpeg", 1.0)):
            for y, (key, _) in zip(y0, LADDER):
                if kind in v and key in v[kind]:
                    m, lo, hi = v[kind][key]
                    ax.barh(y + off, m, height=0.34, color=GOOD if m < 0 else BAD, alpha=alpha, edgecolor="none")
                    ax.errorbar(m, y + off, xerr=[[max(m - lo, 0)], [max(hi - m, 0)]], fmt="none", ecolor="k", elinewidth=0.7, capsize=1.5)
        ax.axvline(0, color="k", lw=0.6)
        ax.set_title(title)
        ax.set_xlabel("change vs no fix (%)")
        ax.set_yticks(y0)
        ax.set_yticklabels([lab for _, lab in LADDER])
    h = [plt.Rectangle((0, 0), 1, 1, color=GOOD, alpha=0.45), plt.Rectangle((0, 0), 1, 1, color=GOOD, alpha=1.0),
         plt.Rectangle((0, 0), 1, 1, color=BAD, alpha=1.0)]
    fig.text(0.5, 0.075, "median change of region AbsRel vs no fix, 95% bootstrap CI", ha="center", fontsize=7)
    fig.legend(h, ["bottom cap only (light)", "bottom cap + JPEG (dark)", "worse (red)"], loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(out, dpi=200)
    plt.close(fig)


def da2_protocol_data(res=RES):
    """{dataset: {'frames': n, 'lsq': {'clean': x, scenario: change %}, 'median': {...}}} on the frame ids both runs contain."""
    data = {}
    for d in (*CORE, *EXT):
        a, b = load_json("da2", d), load_json("da2m", d)
        if not a or not b:
            continue
        ra, rb = matched(a, b)
        rec = {"frames": len(ra)}
        for name, rows in (("lsq", ra), ("median", rb)):
            rec[name] = {"clean": clean_median(rows)}
            for s in SCEN[1:]:
                c = cell(rows, s, n_boot=200)
                rec[name][s] = c["chg"] if c else float("nan")
        data[d] = rec
    return data


def fig_da2_protocols(data, out):
    sets = list(data)
    scen = SCEN[1:]
    fig = plt.figure(figsize=(7.0, 4.3))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15])
    ax0 = fig.add_subplot(gs[0, :])
    x = np.arange(len(sets))
    ax0.bar(x - 0.19, [data[d]["lsq"]["clean"] for d in sets], 0.36, color="#9e9e9e", label="least squares")
    ax0.bar(x + 0.19, [data[d]["median"]["clean"] for d in sets], 0.36, color="#37474f", label="median")
    ax0.set_yscale("log")
    ax0.set_xticks(x)
    ax0.set_xticklabels([f"{d} (N={data[d]['frames']})" for d in sets])
    ax0.set_ylabel("clean AbsRel (log)")
    ax0.set_yticks([0.05, 0.1, 0.2, 0.5])
    ax0.set_yticklabels(["0.05", "0.1", "0.2", "0.5"])
    ax0.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax0.axvline(len(CORE) - 0.5, color="k", ls="--", lw=0.6)
    ax0.legend(frameon=False, ncol=2, loc="upper left")
    for k, d in enumerate([s for s in sets if s in ("holo_out", "stanford", "nyc")]):
        ax = fig.add_subplot(gs[1, k])
        y = np.arange(len(scen))[::-1]
        for off, name, col in ((0.19, "lsq", "#9e9e9e"), (-0.19, "median", "#37474f")):
            vals = [data[d][name][s] for s in scen]
            ax.barh(y + off, vals, 0.34, color=col, label={"lsq": "least squares", "median": "median"}[name])
        ax.axvline(0, color="k", lw=0.6)
        ax.set_title(d)
        ax.set_yticks(y)
        ax.set_yticklabels([SCEN_LABEL[s] for s in scen] if k == 0 else [])
        ax.set_xlabel("median change (%)")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def fig_strict_rules(thr, out, headline="0.02|0.6|0", strict="0.05|0.7|0"):
    """thr: {'gain|win|all': {'core': {...harmful, mean_change}, 'external': {...}}}."""
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))
    for ax, part, title in zip(axes, ("core", "external"), ("core, leave-one-dataset-out", "external (Stanford2D3D, NYC)")):
        for key, v in thr.items():
            h, m = v[part]["harmful"], 100 * v[part]["mean_change"]
            all_sets = key.endswith("|1")
            ax.scatter(h, m, s=14, marker="s" if all_sets else "o", facecolor="none" if all_sets else "#546e7a", edgecolor="#546e7a", lw=0.8)
        for key, lab, col in ((headline, "headline 2% / 60%", BAD), (strict, "5% / 70%", GOOD)):
            if key in thr:
                v = thr[key][part]
                ax.scatter(v["harmful"], 100 * v["mean_change"], s=60, facecolor="none", edgecolor=col, lw=1.6, label=lab)
        ax.scatter([], [], s=14, marker="o", facecolor="#546e7a", edgecolor="#546e7a", label="rule: gain + share of frames")
        ax.scatter([], [], s=14, marker="s", facecolor="none", edgecolor="#546e7a", label="rule: … + every training set improves")
        ax.set_title(title)
        ax.set_xlabel("harmful cells: fix applied and error up (count)")
        ax.set_ylabel("mean change of AbsRel over cells (%)\n(lower = better)")
        ax.legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.text(0.01, 0.015, "Each marker is one candidate selection rule from the grid min. median gain {0, 2, 5, 10}% ×\n"
             "min. share of improved frames {50–90}%; rings mark the headline and the stricter rule.", fontsize=6.5)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig(out, dpi=200)
    plt.close(fig)


def sweep_curves(res=RES):
    """{(mode, set): {'lsq'|'median': (centres, dE)}} from the DA2 sweep files that exist."""
    out = {}
    for mode in ("rotation", "dilation"):
        for ds in ("s3_eval", "panox_all", "holo_in_all", "holo_out_all", "nyc_all"):
            rec = {}
            for name, tag in (("lsq", "da2"), ("median", "da2m")):
                p = sweep_path(mode, tag, ds)
                if p.is_file():
                    s = json.loads(p.read_text())["summary"]
                    rec[name] = (np.array(s["centres"], float), np.array(s["de_global"]["mean"], float))
            if len(rec) == 2:
                out[(mode, ds)] = rec
    return out


def fig_da2_sweeps(curves, out):
    sets = ["s3_eval", "panox_all", "holo_in_all", "holo_out_all", "nyc_all"]
    fig, axes = plt.subplots(2, len(sets), figsize=(7.0, 3.2), sharex=True, squeeze=False)
    for r, mode in enumerate(("rotation", "dilation")):
        for c, ds in enumerate(sets):
            ax = axes[r][c]
            rec = curves.get((mode, ds))
            if rec:
                for name, col in (("lsq", "#9e9e9e"), ("median", "#37474f")):
                    ax.plot(*rec[name], color=col, lw=1.2, label={"lsq": "least squares", "median": "median"}[name])
            ax.axhline(0, color="k", lw=0.5)
            if r == 0:
                ax.set_title(ds.replace("_all", "").replace("_eval", ""))
            if c == 0:
                ax.set_ylabel(f"{mode}: $\\Delta E$ (AbsRel)")
            if r == 1:
                ax.set_xlabel("latitude (deg)")
    h, l = axes[0][4].get_legend_handles_labels()
    if h:
        axes[0][4].legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(RES / "figures"))
    ap.add_argument("--no_report", action="store_true", help="do not copy the figures into Report/draft/figs/")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    diag = lambda tag: json.loads((RES / "diag" / f"nadir_jpeg_{tag}.json").read_text())["rows"]
    try:
        fig_diag([("DAP, NYC, raw metres", diag("dap_nyc"), "none", "plane_fill"),
                  ("DAP, NYC, median scale fit", diag("dap_nyc"), "align-all", "plane_fill"),
                  ("DA$^2$ (median fit), NYC", diag("da2m_nyc"), "align-all", "inpaint_erp")], out / "fig_diag_nadir_jpeg.png")
        made.append("fig_diag_nadir_jpeg.png")
    except FileNotFoundError as e:
        print("skip diag figure:", e)
    data = da2_protocol_data()
    if data:
        fig_da2_protocols(data, out / "fig_da2_protocols.png")
        made.append("fig_da2_protocols.png")
    tj = RES / "threshold_sweep" / "thresholds.json"
    if tj.is_file():
        fig_strict_rules(json.loads(tj.read_text()), out / "fig_strict_rules.png")
        made.append("fig_strict_rules.png")
    cur = sweep_curves()
    if cur:
        fig_da2_sweeps(cur, out / "fig_da2_sweeps_protocols.png")
        made.append("fig_da2_sweeps_protocols.png")
    if DRAFT_FIGS.is_dir() and not a.no_report:
        for m in made:
            shutil.copy2(out / m, DRAFT_FIGS / m)
    print("wrote", ", ".join(made), "to", out)


if __name__ == "__main__":
    main()
