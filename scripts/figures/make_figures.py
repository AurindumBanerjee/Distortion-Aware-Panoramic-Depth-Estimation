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
import textwrap
from pathlib import Path

import numpy as np

from pano.paths import ROOT
import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.family": "serif",
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
})

from methods.capture_faults.catalogue import CATALOGUE, MITIGATIONS  # noqa: E402

MODELS = ("midas", "dap", "da360", "da2")
CORE = ("s3", "panox", "holo_in", "holo_out")
EXTERNAL = ("stanford", "nyc")
SETS = CORE + EXTERNAL
SET_NAME = {"s3": "Structured3D", "panox": "PanoX", "holo_in": "Holo indoor", "holo_out": "Holo outdoor",
            "stanford": "Stanford2D3D (ext.)", "nyc": "NYC (ext.)"}
MODEL_NAME = {"midas": "MiDaS", "dap": "DAP", "da360": "DA360", "da2": "DA²"}
SHORT_SET = {"s3": "S3D", "panox": "PanoX", "holo_in": "Holo-in", "holo_out": "Holo-out", "stanford": "Stanford*", "nyc": "NYC*"}
SCEN_NAME = {"clean": "clean", "tilt": "tilt", "nadir": "blocked bottom", "vfov": "top/bottom missing",
             "yawblur": "shake (yaw blur)", "jpeg": "JPEG", "nadir+jpeg": "blocked bottom + JPEG"}


def col_label(m, d):
    return f"{MODEL_NAME[m]} · {SHORT_SET[d]}"


def wrap(t, n=34):
    return "\n".join(textwrap.wrap(t, n))


EXT_NOTE = "* external dataset (never used for any choice); thick vertical line separates core from external columns"
MODEL_COLOR = {"midas": "#0072B2", "dap": "#D55E00", "da360": "#009E73", "da2": "#CC79A7"}
SET_COLOR = {"s3": "#0072B2", "panox": "#E69F00", "holo_in": "#009E73", "holo_out": "#D55E00",
             "stanford": "#56B4E9", "nyc": "#CC79A7"}
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
    fig.savefig(out / name, dpi=200, bbox_inches="tight")
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
            ax.bar(np.arange(len(sets)) + k * w, vals, w, label=m, color=MODEL_COLOR[m])
        ax.set_xticks(np.arange(len(sets)) + 0.4 - w / 2)
        ax.set_xticklabels([SET_NAME[d] for d in sets], rotation=20, ha="right", fontsize=8)
        ax.set_xlabel("Dataset", fontsize=8)
        ax.set_ylabel("Median AbsRel (dimensionless, log scale)", fontsize=8)
        ax.set_title(f"Clean-image AbsRel, {ttl} (median over frames)", fontsize=9)
        ax.set_yscale("log")
        ax.grid(axis="y", ls=":", alpha=0.5)
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
        heat(ax, np.log2(np.clip(M, 1, 64)), [MODEL_NAME[m] for m in MODELS], [f.key for f in fz],
             SET_NAME[d] + ("  [external]" if d in EXTERNAL else ""), "magma_r", 0, 6, fmt="{:.1f}")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                if np.isfinite(M[i, j]):
                    ax.texts[i * M.shape[1] + j].set_text(f"{M[i, j]:.1f}x")
    fig.suptitle("Cost of each capture fault: median AbsRel with the fault ÷ AbsRel on the clean image\n"
                 "(affected region for nadir / vfov, whole panorama otherwise; 1.0× = no cost)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 0.92, 1))
    cax = fig.add_axes([0.935, 0.15, 0.012, 0.7])
    from matplotlib import cm
    from matplotlib.colors import Normalize
    cb = fig.colorbar(cm.ScalarMappable(Normalize(0, 6), "magma_r"), cax=cax, ticks=range(7))
    cb.set_ticklabels(["1×", "2×", "4×", "8×", "16×", "32×", "≥64×"])
    cb.set_label("error with the fault ÷ clean error (log scale)")
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
    labels = [col_label(m, ds) for m, ds in cols]
    im = heat(ax, M, [wrap(MITIGATIONS[k][0]) for k in d.mitigations], labels,
              f"{d.title}\nmedian change in {'affected-region' if f == 'region' else 'whole-panorama'} error vs no fix "
              "(green = better) and % of frames improved", "RdYlGn_r", -100, 100, annot=W, col_groups=groups)
    fig.colorbar(im, ax=ax, fraction=0.025, label="median change in AbsRel vs no fix (%)")
    fig.text(0.01, -0.02, "Cell: median change (%) and, below it, share of frames improved. " + EXT_NOTE, fontsize=7)
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
    grp = [sum(1 for c in cols if c[1] in CORE)] if any(c[1] in EXTERNAL for c in cols) else None
    im = heat(ax, M, [wrap(MITIGATIONS[k][0]) for k in BLIND], [col_label(m, d) for m, d in cols],
              "Blind fixes applied to CLEAN images: median change in whole-panorama AbsRel (red = harm, green = gain)",
              "RdYlGn_r", -50, 50, col_groups=grp)
    fig.colorbar(im, ax=ax, fraction=0.025, label="median change in AbsRel (%)")
    fig.text(0.01, -0.22, EXT_NOTE + ". Colour is clipped at ±50%; the number in each cell is the exact value.", fontsize=7)
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
    labels = [col_label(m, d) for m, d in cols]
    grp = [sum(1 for c in cols if c[1] in CORE)] if any(c[1] in EXTERNAL for c in cols) and any(c[1] in CORE for c in cols) else None
    rows = [SCEN_NAME.get(s, s) for s in scen]
    im = heat(axs[0], G, rows, labels, "End-to-end correction: median change in AbsRel vs uncorrected (green = better)",
              "RdYlGn_r", -60, 60, col_groups=grp)
    fig.colorbar(im, ax=axs[0], fraction=0.03, label="median change in AbsRel (%)")
    im = heat(axs[1], B, rows, labels, "Share of frames made worse by more than 1%", "Reds", 0, 100, fmt="{:.0f}", col_groups=grp)
    fig.colorbar(im, ax=axs[1], fraction=0.03, label="frames made worse (%)")
    fig.text(0.01, -0.03, "AbsRel on the affected region for blocked bottom / top-bottom missing, whole panorama otherwise. "
             + EXT_NOTE + ". Colour clipped at ±60%.", fontsize=7)
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
                    ax.plot(s["centres"], s["ratio_global"], marker="o", ms=3.5, lw=1.4,
                            color=SET_COLOR[d], ls="--" if d in EXTERNAL else "-", label=SET_NAME[d])
            ax.axhline(1.0, color="k", lw=0.8)
            ax.grid(True, ls=":", alpha=0.5)
            ax.set_title(MODEL_NAME[m], fontsize=9)
            ax.set_xlabel("latitude at which the content is seen, |φ| (°)", fontsize=8)
            ax.set_xlim(0, 90)
        axs[0][0].set_ylabel("error ratio E(L) / E(equator)\n(1 = no extra error; >1 = worse)", fontsize=8)
        axs[0][-1].legend(fontsize=7, title="dataset (dashed = external)", title_fontsize=7, loc="best")
        what = {"rotation": "content rotated from the equator to latitude L",
                "dilation": "content magnified as it would be at latitude L (stays upright)",
                "flip": "panorama turned upside down, content seen at latitude L"}[mode]
        fig.suptitle(f"{mode.capitalize()} sweep: {what}. Same pixels, same ground truth; error relative to the "
                     "equator-seen pass (global alignment).", fontsize=9)
        fig.tight_layout()
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


def _gt_info(ds, fid, h):
    p = FIG / "example_gt.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text()).get(ds, {}).get(fid, {}).get(str(h))


def visual_models(max_frames):
    """Same frame and fault, all models stacked; colour bars in metres (depth) and AbsRel (error), latitude axis."""
    from matplotlib import cm
    from matplotlib.colors import LogNorm, Normalize
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
                    folder = RES / f"study_{m}_{ds}_img"
                    if not names or not folder.is_dir():
                        continue
                    rows.append((m, folder, names, next((r.get(f"{d.key}|best_example") for r in study(m, ds)["rows"] if r["id"] == fid), None)))
                if len(rows) < 2:
                    continue
                fig, axs = plt.subplots(len(rows), 5, figsize=(17, 1.5 * len(rows) + 1.0), squeeze=False,
                                        gridspec_kw={"wspace": 0.5})
                for i, (m, folder, names, best) in enumerate(rows):
                    items = [("input with the fault", names.get(f"{d.key}_rgb"), "rgb"),
                             ("depth, no fix", names.get(f"{d.key}_none"), "depth"),
                             ("depth, best fix" + (f": {best}" if best else ""), names.get(f"{d.key}_best"), "depth"),
                             ("AbsRel, no fix", names.get(f"err_{d.key}_none"), "err"),
                             ("AbsRel, best fix", names.get(f"err_{d.key}_best"), "err")]
                    info = None
                    for j, (t, nm, kind) in enumerate(items):
                        ax = axs[i][j]
                        im = read(folder, nm) if nm else None
                        if im is None:
                            ax.axis("off")
                            continue
                        info = info or _gt_info(ds, fid, im.shape[0])
                        ax.imshow(im, extent=[-180, 180, -90, 90], aspect="equal")  # 360 x 180 degrees: 2:1 panel
                        for y in (60, -60):
                            ax.axhline(y, color="white", ls="--", lw=0.7)
                        ax.set_xticks([])
                        ax.set_yticks([-90, -60, 0, 60, 90] if j == 0 else [])
                        ax.tick_params(labelsize=6, length=2)
                        ax.set_title(t if i == 0 else "", fontsize=8, fontweight="bold", loc="left")
                        if j == 0:
                            ax.set_ylabel(f"{MODEL_NAME[m]}\nlatitude (°)", fontsize=8)
                        if kind == "depth" and j == 2:
                            if info:
                                cb = fig.colorbar(cm.ScalarMappable(LogNorm(info["lo"], info["hi"]), "turbo_r"), ax=axs[i][1:3].tolist(),
                                                  fraction=0.02, pad=0.01)
                                cb.set_label("depth (m)", fontsize=7)
                                tk = [v for v in (0.5, 1, 2, 3, 5, 10, 20, 50) if info["lo"] <= v <= info["hi"]]
                                cb.set_ticks(tk)
                                cb.set_ticklabels([f"{v:g}" for v in tk])
                                cb.minorticks_off()
                            else:
                                cb = fig.colorbar(cm.ScalarMappable(Normalize(0, 1), "turbo_r"), ax=axs[i][1:3].tolist(),
                                                  fraction=0.02, pad=0.01, ticks=[0, 1])
                                cb.set_ticklabels(["near", "far"])
                            cb.ax.tick_params(labelsize=6)
                        if kind == "err" and j == 4:
                            cb = fig.colorbar(cm.ScalarMappable(Normalize(0, 0.5), "magma"), ax=axs[i][3:5].tolist(),
                                              fraction=0.02, pad=0.01, ticks=[0, 0.25, 0.5])
                            cb.set_ticklabels(["0", "0.25", "≥0.5"])
                            cb.set_label("AbsRel", fontsize=7)
                            cb.ax.tick_params(labelsize=6)
                fig.suptitle(f"{SET_NAME[ds]} · {d.title} · frame {fid}", fontsize=10, fontweight="bold", x=0.01, ha="left")
                fig.text(0.01, 0.003, "Dashed lines: ±60° latitude. Depth colour scale: 2nd–98th percentile of the frame's ground "
                         "truth (log). MiDaS / DA360 / DA² after a scale (and shift) fit, DAP in raw metres. "
                         "Grey: no valid ground truth.", fontsize=7, color="#444")
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
