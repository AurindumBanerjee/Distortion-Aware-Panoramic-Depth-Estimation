#!/usr/bin/env python3
"""All comparison figures, from whatever results exist (core and external datasets, every model). CPU only.

  python scripts/make_figures.py                 # everything found in results/
  python scripts/make_figures.py --only visual   # just the image montages  (plots | visual | sweeps)

Writes results/figures/ and results/figures/INDEX.md. Core datasets (s3, panox, holo_in, holo_out) and external ones
(stanford, nyc) are drawn side by side but labelled apart; external ones never feed any choice (see calibrate_correction.py).

  fig_clean_error.png            clean error per model and dataset (whole panorama and polar >= 60 deg)
  fig_fault_cost.png             how much each capture fault costs, per dataset x model (degraded / clean error)
  fig_fix_<fault>.png            every technique for one fault on every model x dataset (change vs no fix, win rate)
  fig_do_no_harm.png             blind fixes applied to CLEAN images
  fig_correction_gain.png        end-to-end pipeline: change in error and share of frames made worse
  fig_sweeps_<mode>.png          error ratio vs latitude (rotation / dilation / flip sweeps), per model, lines = datasets
  visual/<model>_<set>_<fault>.png        degraded input | depth from clean input | degraded depth | fixed depth | errors
  visual_models/<set>_<fault>.png         the same frame and fault, all models stacked (degraded vs fixed + errors)
  visual_correction/<model>_<set>_<scenario>.png   the end-to-end pipeline: input | clean | uncorrected | corrected | errors
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from distortions.catalogue import CATALOGUE, MITIGATIONS  # noqa: E402

MODELS = ("midas", "dap", "da360", "da2")
CORE = ("s3", "panox", "holo_in", "holo_out")
EXTERNAL = ("stanford", "nyc")
SETS = CORE + EXTERNAL
SET_NAME = {"s3": "Structured3D", "panox": "PanoX", "holo_in": "Holo indoor", "holo_out": "Holo outdoor",
            "stanford": "Stanford2D3D (ext.)", "nyc": "NYC (ext.)"}
BLIND = ("relevel_self", "gain_match", "flatfield", "denoise", "bilateral")
RES = ROOT / "results"
FIG = RES / "figures"


def set_results(path):
    global RES, FIG
    RES = Path(path)
    FIG = RES / "figures"
made = []


def load(path):
    return json.loads(Path(path).read_text()) if Path(path).is_file() else None


def study(m, d):
    return load(RES / f"study_{m}_{d}.json")


def correction(m, d):
    return load((RES if d in CORE else RES / "external") / f"correction_{m}_{d}.json")


def med(v):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    return float(np.median(v)) if len(v) else float("nan")


def metric(d):
    return "region" if d.region is not None else "all"


def save(fig, name, sub=""):
    out = FIG / sub if sub else FIG
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / name, dpi=130, bbox_inches="tight")
    plt.close(fig)
    made.append(f"{sub + '/' if sub else ''}{name}")


def heat(ax, M, rows, cols, title, cmap, vmin, vmax, fmt="{:+.0f}", annot=None, col_groups=None):
    im = ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    ax.set_title(title, fontsize=9)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            t = "" if not np.isfinite(v) else fmt.format(v)
            if annot is not None and np.isfinite(annot[i, j]):
                t += f"\n{annot[i, j]:.0f}%"
            rgba = im.cmap(im.norm(v)) if np.isfinite(v) else (1, 1, 1, 1)
            lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            ax.text(j, i, t, ha="center", va="center", fontsize=6, color="white" if lum < 0.45 else "black")
    if col_groups:
        for x in col_groups:
            ax.axvline(x - 0.5, color="k", lw=1.5)
    return im


def present():
    """(model, set) pairs that have study results."""
    return [(m, d) for d in SETS for m in MODELS if study(m, d)]


# ------------------------------------------------------------------------------------------------ plots
def plot_clean_error():
    pairs = present()
    if not pairs:
        return
    sets = [d for d in SETS if any(p[1] == d for p in pairs)]
    fig, axs = plt.subplots(1, 2, figsize=(13, 4), sharey=False)
    for ax, key, ttl in zip(axs, ("all", "polar"), ("whole panorama", "polar (|lat| >= 60 deg)")):
        w = 0.8 / len(MODELS)
        for k, m in enumerate(MODELS):
            vals = [med([r["clean"][key] for r in study(m, d)["rows"]]) if study(m, d) else np.nan for d in sets]
            ax.bar(np.arange(len(sets)) + k * w, vals, w, label=m)
        ax.set_xticks(np.arange(len(sets)) + 0.4 - w / 2)
        ax.set_xticklabels([SET_NAME[d] for d in sets], rotation=20, ha="right", fontsize=8)
        ax.set_title(f"Clean-image AbsRel, {ttl} (median over frames)", fontsize=9)
        ax.set_yscale("log")
        if "stanford" in sets or "nyc" in sets:
            ax.axvline(len([d for d in sets if d in CORE]) - 0.5 + 0.0, color="k", lw=1, ls="--")
    axs[0].legend(fontsize=8)
    fig.text(0.5, -0.02, "dashed line: core datasets on the left, external on the right. DAP is scored in raw metres, the others "
             "after a GT scale (and shift) fit, so absolute levels are not comparable across models.", ha="center", fontsize=7)
    save(fig, "fig_clean_error.png")


def plot_fault_cost():
    pairs = present()
    if not pairs:
        return
    sets = [d for d in SETS if any(p[1] == d for p in pairs)]
    fz = [d for d in CATALOGUE]
    n = len(sets)
    cols = 3 if n > 4 else 2
    rows_n = int(np.ceil(n / cols))
    fig, axs = plt.subplots(rows_n, cols, figsize=(5.2 * cols, 2.6 * rows_n + 0.6), squeeze=False)
    for ax in axs.ravel():
        ax.axis("off")
    for ax, d in zip(axs.ravel(), sets):
        ax.axis("on")
        M = np.full((len(MODELS), len(fz)), np.nan)
        for i, m in enumerate(MODELS):
            s = study(m, d)
            if not s:
                continue
            for j, f in enumerate(fz):
                c = med([r[f"{f.key}|clean"].get(metric(f)) for r in s["rows"] if f"{f.key}|clean" in r])
                x = med([r[f"{f.key}|none"].get(metric(f)) for r in s["rows"] if f"{f.key}|none" in r])
                if c > 0 and np.isfinite(x):
                    M[i, j] = x / c
        im = heat(ax, np.log2(np.clip(M, 0.25, 64)), list(MODELS), [f.key for f in fz],
                  SET_NAME[d] + ("  [external]" if d in EXTERNAL else ""), "magma_r", 0, 6, fmt="{:.1f}")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                if np.isfinite(M[i, j]):
                    ax.texts[i * M.shape[1] + j].set_text(f"{M[i, j]:.1f}x")
    fig.suptitle("Cost of each capture fault: median error with the fault / error on the clean image "
                 "(affected region for nadir / vfov, whole panorama otherwise; 1.0x = no cost)", fontsize=10)
    fig.tight_layout()
    save(fig, "fig_fault_cost.png")


def plot_fix(d):
    cols, labels, groups = [], [], []
    for ds in SETS:
        for m in MODELS:
            if study(m, ds):
                cols.append((m, ds))
                labels.append(f"{m}·{ds}")
        if cols and (not groups or groups[-1] != len(cols)) and ds == CORE[-1]:
            groups.append(len(cols))
    if not cols or not d.mitigations:
        return
    f = metric(d)
    M = np.full((len(d.mitigations), len(cols)), np.nan)
    W = np.full_like(M, np.nan)
    for j, (m, ds) in enumerate(cols):
        rows = study(m, ds)["rows"]
        for i, mk in enumerate(d.mitigations):
            rel, win = [], []
            for r in rows:
                n, x = r.get(f"{d.key}|none", {}).get(f), r.get(f"{d.key}|{mk}", {}).get(f)
                if n and x is not None and np.isfinite(n) and np.isfinite(x) and n > 0:
                    rel.append((x - n) / n)
                    win.append(x < n)
            if rel:
                M[i, j], W[i, j] = 100 * np.median(rel), 100 * np.mean(win)
    fig, ax = plt.subplots(figsize=(max(8, 0.55 * len(cols) + 3), 0.6 * len(d.mitigations) + 2.6))
    im = heat(ax, M, [MITIGATIONS[k][0][:44] for k in d.mitigations], labels,
              f"{d.title}\nmedian change in {'affected-region' if f == 'region' else 'whole-panorama'} error vs no fix "
              "(green = better) and % of frames improved", "RdYlGn_r", -100, 100, annot=W, col_groups=groups)
    fig.colorbar(im, ax=ax, fraction=0.025, label="% change in error")
    save(fig, f"fig_fix_{d.key}.png")


def plot_do_no_harm():
    cols = [(m, ds) for ds in SETS for m in MODELS if study(m, ds)]
    if not cols:
        return
    M = np.full((len(BLIND), len(cols)), np.nan)
    for j, (m, ds) in enumerate(cols):
        rows = study(m, ds)["rows"]
        for i, k in enumerate(BLIND):
            M[i, j] = 100 * med([(r[f"clean+{k}"]["all"] - r["clean"]["all"]) / r["clean"]["all"] for r in rows if f"clean+{k}" in r])
    fig, ax = plt.subplots(figsize=(max(8, 0.55 * len(cols) + 3), 3.4))
    im = heat(ax, M, [MITIGATIONS[k][0][:40] for k in BLIND], [f"{m}·{d}" for m, d in cols],
              "Blind fixes applied to CLEAN images: median change in error (red = harm)", "RdYlGn_r", -50, 50)
    fig.colorbar(im, ax=ax, fraction=0.025)
    save(fig, "fig_do_no_harm.png")


def plot_correction():
    cols = [(m, ds) for ds in SETS for m in MODELS if correction(m, ds)]
    if not cols:
        return
    scen = [k for k in correction(*cols[0])["rows"][0] if k != "id"]
    G, B = np.full((len(scen), len(cols)), np.nan), np.full((len(scen), len(cols)), np.nan)
    for j, (m, ds) in enumerate(cols):
        rows = correction(m, ds)["rows"]
        for i, sc in enumerate(scen):
            f = "region" if sc in ("nadir", "vfov", "nadir+jpeg") else "all"
            u = np.array([r[sc]["raw"][f] for r in rows], float)
            x = np.array([r[sc]["fixed"][f] for r in rows], float)
            ok = np.isfinite(u) & np.isfinite(x) & (u > 0)
            if ok.any():
                G[i, j] = 100 * np.median((x[ok] - u[ok]) / u[ok])
                B[i, j] = 100 * np.mean(x[ok] > u[ok] * 1.01)
    fig, axs = plt.subplots(1, 2, figsize=(2 * max(7, 0.5 * len(cols) + 3), 0.5 * len(scen) + 2.8))
    labels = [f"{m}·{d}" for m, d in cols]
    grp = [sum(1 for c in cols if c[1] in CORE)] if any(c[1] in EXTERNAL for c in cols) and any(c[1] in CORE for c in cols) else None
    im = heat(axs[0], G, scen, labels, "End-to-end correction: median change in error vs uncorrected (green = better)",
              "RdYlGn_r", -60, 60, col_groups=grp)
    fig.colorbar(im, ax=axs[0], fraction=0.03)
    im = heat(axs[1], B, scen, labels, "Share of frames made worse by more than 1% (%)", "Reds", 0, 100, fmt="{:.0f}", col_groups=grp)
    fig.colorbar(im, ax=axs[1], fraction=0.03)
    save(fig, "fig_correction_gain.png")


def plot_sweeps():
    for mode in ("rotation", "dilation", "flip"):
        data = {}
        for p in sorted(RES.glob(f"sweep_{mode}_*.json")):
            tag = p.stem[len(f"sweep_{mode}_"):]
            parts = tag.split("_")
            m = parts[0]
            split = parts[-1]
            d = "_".join(parts[1:-1])
            if m not in MODELS or d not in SETS or split == "calib":
                continue
            data[(m, d)] = load(p)["summary"]
        if not data:
            continue
        fig, axs = plt.subplots(1, len(MODELS), figsize=(4 * len(MODELS), 3.4), sharey=True, squeeze=False)
        for ax, m in zip(axs[0], MODELS):
            for d in SETS:
                s = data.get((m, d))
                if s:
                    ax.plot(s["centres"], s["ratio_global"], marker="o", ms=3, ls="--" if d in EXTERNAL else "-", label=SET_NAME[d])
            ax.axhline(1.0, color="k", lw=0.8)
            ax.set_title(m, fontsize=9)
            ax.set_xlabel("latitude the content is seen at (deg)", fontsize=8)
        axs[0][0].set_ylabel("E(L) / E at the equator (global fit)", fontsize=8)
        axs[0][0].legend(fontsize=6)
        fig.suptitle(f"{mode} sweep: error ratio vs latitude (dashed = external datasets; dilation for metric DAP also moves scale, "
                     "see the local estimator in SWEEP_*.md)", fontsize=8)
        save(fig, f"fig_sweeps_{mode}.png")


# ------------------------------------------------------------------------------------------------ visual
def read(folder, name):
    p = Path(folder) / name
    return mpimg.imread(p) if p.is_file() else None


def montage(panels, title, name, sub, width=3.3):
    panels = [(t, im) for t, im in panels if im is not None]
    if len(panels) < 2:
        return
    fig, axs = plt.subplots(1, len(panels), figsize=(width * len(panels), width * 0.5 + 0.7), squeeze=False)
    for ax, (t, im) in zip(axs[0], panels):
        ax.imshow(im)
        ax.set_title(t, fontsize=8)
        ax.axis("off")
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    save(fig, name, sub)


def frame_metric(rows, fid, key, f):
    for r in rows:
        if r["id"] == fid and key in r:
            v = r[key].get(f)
            return "n/a" if v is None or not np.isfinite(v) else f"{v:.3f}"
    return "n/a"


def visual_study(max_frames):
    for m, ds in present():
        s = study(m, ds)
        folder = RES / f"study_{m}_{ds}_img"
        for fid, names in list(s["examples"].items())[:max_frames]:
            for d in CATALOGUE:
                f = metric(d)
                best = next((r.get(f"{d.key}|best_example") for r in s["rows"] if r["id"] == fid), None)
                lab = lambda k: f"{k}: " + frame_metric(s["rows"], fid, f"{d.key}|{k}", f)
                panels = [("degraded input", read(folder, names.get(f"{d.key}_rgb", ""))),
                          ("depth, clean input", read(folder, names.get("clean", ""))),
                          (f"depth, degraded ({lab('none')})", read(folder, names.get(f"{d.key}_none", "")))]
                if best:
                    panels += [(f"depth, fixed: {MITIGATIONS[best][0][:30]} ({lab(best)})", read(folder, names.get(f"{d.key}_best", "")))]
                panels += [("error, degraded", read(folder, names.get(f"err_{d.key}_none", "")))]
                if best:
                    panels += [("error, fixed", read(folder, names.get(f"err_{d.key}_best", "")))]
                montage(panels, f"{m} · {SET_NAME[ds]} · {d.title}  ·  frame {fid}  ·  AbsRel on {'region' if f == 'region' else 'whole image'}",
                        f"{m}_{ds}_{d.key}_{fid[-24:]}.png", "visual")


def visual_models(max_frames):
    for ds in SETS:
        have = [m for m in MODELS if study(m, ds)]
        if len(have) < 2:
            continue
        ids = list(study(have[0], ds)["examples"])[:max_frames]
        for fid in ids:
            for d in CATALOGUE:
                rows = []
                for m in have:
                    names = study(m, ds)["examples"].get(fid)
                    if not names:
                        continue
                    folder = RES / f"study_{m}_{ds}_img"
                    if not folder.is_dir():
                        continue  # images live where the study ran; nothing to draw without them
                    rows.append((m, folder, names, next((r.get(f"{d.key}|best_example") for r in study(m, ds)["rows"] if r["id"] == fid), None)))
                if len(rows) < 2:
                    continue
                cols = 5
                fig, axs = plt.subplots(len(rows), cols, figsize=(3.0 * cols, 1.7 * len(rows) + 0.8), squeeze=False)
                for i, (m, folder, names, best) in enumerate(rows):
                    items = [("degraded input", names.get(f"{d.key}_rgb")), ("depth, degraded", names.get(f"{d.key}_none")),
                             ("depth, fixed" + (f" ({MITIGATIONS[best][0][:22]})" if best else ""), names.get(f"{d.key}_best")),
                             ("error, degraded", names.get(f"err_{d.key}_none")), ("error, fixed", names.get(f"err_{d.key}_best"))]
                    for j, (t, nm) in enumerate(items):
                        ax = axs[i][j]
                        im = read(folder, nm) if nm else None
                        if im is not None:
                            ax.imshow(im)
                        ax.axis("off")
                        if i == 0:
                            ax.set_title(t, fontsize=7)
                        if j == 0:
                            ax.text(-0.02, 0.5, m, transform=ax.transAxes, ha="right", va="center", fontsize=9)
                fig.suptitle(f"{SET_NAME[ds]} · {d.title} · frame {fid}", fontsize=9)
                fig.tight_layout()
                save(fig, f"{ds}_{d.key}_{fid[-24:]}.png", "visual_models")


def visual_correction(max_frames):
    for ds in SETS:
        for m in MODELS:
            c = correction(m, ds)
            if not c or not c.get("examples"):
                continue
            folder = (RES if ds in CORE else RES / "external") / f"correction_{m}_{ds}_img"
            for fid, names in list(c["examples"].items())[:max_frames]:
                for sc in [k for k in c["rows"][0] if k != "id"]:
                    f = "region" if sc in ("nadir", "vfov", "nadir+jpeg") else "all"
                    row = next(r for r in c["rows"] if r["id"] == fid)[sc]
                    v = lambda k: row[k].get(f)
                    t = lambda k, x: f"{x} ({v(k):.3f})" if v(k) is not None and np.isfinite(v(k)) else x
                    panels = [(f"input ({sc})", read(folder, names.get(f"{sc}_input", ""))),
                              (t("clean", "depth, clean input"), read(folder, names.get("clean", ""))),
                              (t("raw", "depth, uncorrected"), read(folder, names.get(f"{sc}_raw", ""))),
                              (t("fixed", "depth, corrected: " + re.sub(r"\(caps [^)]*\)", "", ", ".join(row["log"]))), read(folder, names.get(f"{sc}_fixed", ""))),
                              ("error, uncorrected", read(folder, names.get(f"err_{sc}_raw", ""))),
                              ("error, corrected", read(folder, names.get(f"err_{sc}_fixed", "")))]
                    montage(panels, f"{m} · {SET_NAME[ds]} · end-to-end correction, scenario '{sc}' · frame {fid}",
                            f"{m}_{ds}_{sc}_{fid[-24:]}.png", "visual_correction")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["plots", "visual", "sweeps"], default=None)
    ap.add_argument("--results", default=None, help="results folder (default: results/ of the repo)")
    ap.add_argument("--frames", type=int, default=1, help="example frames per model x dataset in the image montages")
    a = ap.parse_args()
    if a.results:
        set_results(a.results)
    if a.only in (None, "plots"):
        plot_clean_error()
        plot_fault_cost()
        for d in CATALOGUE:
            plot_fix(d)
        plot_do_no_harm()
        plot_correction()
    if a.only in (None, "sweeps"):
        plot_sweeps()
    if a.only in (None, "visual"):
        visual_study(a.frames)
        visual_models(a.frames)
        visual_correction(a.frames)
    if not made:
        sys.exit("nothing to draw: no results/study_<model>_<set>.json (or correction / sweep files) found")
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "INDEX.md").write_text("# Figures\n\nGenerated by scripts/make_figures.py. External datasets (stanford, nyc) are labelled "
                                  "'ext.' and never feed any choice.\n\n" + "\n".join(f"- {n}" for n in sorted(made)) + "\n")
    print(f"wrote {len(made)} figures to {FIG}")


if __name__ == "__main__":
    main()
