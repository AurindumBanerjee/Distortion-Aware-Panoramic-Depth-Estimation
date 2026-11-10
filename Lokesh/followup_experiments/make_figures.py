from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

RUNS = {
    "01": ROOT / "01_scale_only_protocol/outputs/run_20261105_192854/summary.json",
    "04": ROOT / "04_mono360_20view/outputs/run_20261105_195950/summary.json",
    "05": ROOT / "05_fov_resolution_sweep/outputs/run_20261105_202824/summary.json",
}


def load(key: str) -> dict:
    path = RUNS[key]
    if not path.is_file():
        raise FileNotFoundError(f"Required finalized run summary is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def plot_exp01() -> None:
    data = load("01")["summary"]
    bands = ["all", "45-60", "60-75", "75-90"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, protocol in zip(axes, ["align-all", "align-equatorial"]):
        scale = [data[protocol]["scale"][b]["median_abs_rel"] for b in bands]
        affine = [data[protocol]["affine"][b]["median_abs_rel"] for b in bands]
        x = np.arange(len(bands))
        width = 0.36
        ax.bar(x - width / 2, scale, width, label="Scale-only")
        ax.bar(x + width / 2, affine, width, label="Affine")
        ax.set_title(protocol)
        ax.set_xticks(x, bands)
        ax.set_xlabel("Latitude band (degrees)")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Median AbsRel (lower is better)")
    axes[1].legend(frameon=False)
    fig.suptitle("Experiment 01 — DA360 alignment sensitivity")
    fig.tight_layout()
    fig.savefig(FIGURES / "exp01_scale_vs_affine.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_exp04() -> None:
    data = load("04")["summary"]
    bands = ["all", "60-75", "75-90"]
    methods = ["baseline", "two_pole_tangent", "mono360_20view"]
    labels = ["Baseline", "Two-pole tangent", "20-view"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=False)
    for ax, protocol in zip(axes, ["align-all", "align-equatorial"]):
        x = np.arange(len(bands))
        width = 0.24
        for j, (method, label) in enumerate(zip(methods, labels)):
            vals = [data[protocol][method][b]["median"] for b in bands]
            ax.bar(x + (j - 1) * width, vals, width, label=label)
        ax.set_title(protocol)
        ax.set_xticks(x, bands)
        ax.set_xlabel("Latitude band (degrees)")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Median AbsRel (lower is better)")
    axes[1].legend(frameon=False)
    fig.suptitle("Experiment 04 — 20-view method vs baseline and two-pole tangent")
    fig.tight_layout()
    fig.savefig(FIGURES / "exp04_20view_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_exp05() -> None:
    data = load("05")["summary"]
    fovs = [70, 90, 110, 130]
    resolutions = [256, 384, 512]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=False)
    for ax, protocol in zip(axes, ["align-all", "align-equatorial"]):
        for resolution in resolutions:
            vals = [data[protocol][f"fov{fov}_size{resolution}"]["75-90"]["median"] for fov in fovs]
            ax.plot(fovs, vals, marker="o", linewidth=2, label=f"{resolution}²")
        ax.set_title(protocol)
        ax.set_xlabel("Tangent FOV (degrees)")
        ax.set_xticks(fovs)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Median AbsRel at 75–90° (lower is better)")
    axes[1].legend(title="Tangent resolution", frameon=False)
    fig.suptitle("Experiment 05 — FOV × tangent resolution sensitivity")
    fig.tight_layout()
    fig.savefig(FIGURES / "exp05_fov_resolution_sweep.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    plot_exp01()
    plot_exp04()
    plot_exp05()
    print("Wrote:")
    for path in sorted(FIGURES.glob("*.png")):
        print(f"  {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
