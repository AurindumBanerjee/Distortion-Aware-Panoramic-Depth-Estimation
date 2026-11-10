"""Panorama example figures in the layout shared with the other two authors' result pages.

Two columns of ERP panels, bold titles, a colour bar with units next to every map, latitude on the left column,
longitude on the bottom row and dashed lines at +-60 deg latitude (the polar band used for 'polar AbsRel').

The stored example images (results/*_img) are already colour-mapped (scripts/distortion_study.py, save_examples):
  depth  turbo(1 - x), x = log depth between the 2nd and 98th percentile of the frame's valid ground truth
         -> drawn here with cmap 'turbo_r' and a log norm over [lo, hi] metres from results/figures/example_gt.json
  error  magma(min(AbsRel, 0.5) / 0.5), grey = no valid ground truth
So the colour bars describe the stored pixels exactly; nothing is re-estimated from the images.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
POLAR = 60.0


def gt_info(ds: str, fid: str, height: int, res: Path = RES):
    p = res / "figures" / "example_gt.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text()).get(ds, {}).get(fid, {}).get(str(height))


def _depth_ticks(lo: float, hi: float):
    cand = [0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 500]
    t = [c for c in cand if lo <= c <= hi]
    return t if len(t) >= 2 else [lo, hi]


def figure(rows, title: str, info=None, note: str | None = None, dpi: int = 110):
    """rows: list of rows, each a list of (panel title, image path or None, kind in rgb | depth | err).
    info: {'lo', 'hi'} metres from example_gt.json, or None (depth bar then reads near / far).
    Returns the PNG bytes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import LogNorm, Normalize

    nr = len(rows)
    fig, axs = plt.subplots(nr, 2, figsize=(12, 2.95 * nr + 0.55), squeeze=False)
    plt.rcParams.update({"font.size": 9})
    for i, row in enumerate(rows):
        for j in range(2):
            ax = axs[i][j]
            if j >= len(row) or row[j][1] is None or not Path(row[j][1]).is_file():
                ax.axis("off")
                continue
            t, path, kind = row[j]
            im = mpimg.imread(str(path))
            ax.imshow(im, extent=[-180, 180, -90, 90], aspect="auto", interpolation="antialiased")
            for y in (POLAR, -POLAR):
                ax.axhline(y, color="white" if kind != "rgb" else "white", ls="--", lw=0.8, alpha=0.9)
            ax.set_title(t, loc="left", fontsize=10, fontweight="bold")
            ax.set_xticks([-180, -90, 0, 90, 180])
            ax.set_yticks([-90, -60, 0, 60, 90])
            ax.tick_params(labelsize=7, length=2)
            ax.set_xticklabels(["−180°", "−90°", "0°", "90°", "180°"] if i == nr - 1 else [])
            ax.set_yticklabels(["−90°", "−60°", "0°", "60°", "90°"] if j == 0 else [])
            if j == 0:
                ax.set_ylabel("latitude", fontsize=8)
            if i == nr - 1:
                ax.set_xlabel("longitude", fontsize=8)
            if kind == "depth":
                if info:
                    sm = cm.ScalarMappable(LogNorm(info["lo"], info["hi"]), "turbo_r")
                    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015)
                    tk = _depth_ticks(info["lo"], info["hi"])
                    cb.set_ticks(tk)
                    cb.set_ticklabels([f"{v:g}" for v in tk])
                    cb.minorticks_off()
                    cb.set_label("depth (m), log scale", fontsize=8)
                else:
                    sm = cm.ScalarMappable(Normalize(0, 1), "turbo_r")
                    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015, ticks=[0, 1])
                    cb.set_ticklabels(["near", "far"])
                    cb.set_label("depth (relative)", fontsize=8)
            elif kind == "err":
                sm = cm.ScalarMappable(Normalize(0, 0.5), "magma")
                cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015, ticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5])
                cb.set_ticklabels(["0.0", "0.1", "0.2", "0.3", "0.4", "≥0.5"])
                cb.set_label("AbsRel  |pred − true| / true", fontsize=8)
            else:  # keep the image width equal to the mapped panels
                cb = fig.colorbar(cm.ScalarMappable(Normalize(0, 1), "gray"), ax=ax, fraction=0.035, pad=0.015)
                cb.ax.set_visible(False)
            cb.ax.tick_params(labelsize=7) if cb.ax.get_visible() else None
    fig.suptitle(title, x=0.01, ha="left", fontsize=11, fontweight="bold")
    foot = ("Dashed lines: ±60° latitude (polar band).  Grey in error / ground-truth maps: no valid ground truth "
            "(sky, holes, outside the valid depth range).")
    if info:
        foot += f"  Depth colour scale: {info['lo']:.2g}–{info['hi']:.2g} m (2nd–98th percentile of this frame's ground truth)."
    if note:
        foot += "  " + note
    fig.text(0.01, 0.005, foot, fontsize=7, color="#444", ha="left", va="bottom", wrap=True)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    return buf.getvalue()
