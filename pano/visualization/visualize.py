"""Static figures (matplotlib) for the paper-style report.

Colour roles (fixed, never cycled): categorical series use one fixed order
(blue, orange, aqua, yellow, magenta, green, violet, red); magnitudes use one-hue
sequential maps (errors: single-hue Reds); signed improvement uses a diverging
blue/orange map with a neutral grey midpoint. Depth maps use the perceptually uniform
'magma' map with a shared range per panorama.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
TEXT, TEXT2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
DIVERGING = LinearSegmentedColormap.from_list("blue_grey_orange", ["#eb6834", "#f3c3ad", "#e9e8e4", "#a9c7ee", "#2a78d6"])

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "font.size": 9, "axes.edgecolor": TEXT2, "axes.labelcolor": TEXT,
    "xtick.color": TEXT2, "ytick.color": TEXT2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2.0, "legend.frameon": False,
    "axes.titlesize": 10, "axes.titleweight": "bold",
})


def _save(fig, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def color_for(names: Sequence[str]) -> Dict[str, str]:
    """Stable method -> colour mapping (identity follows the entity, not its rank)."""
    return {n: SERIES[i % len(SERIES)] for i, n in enumerate(names)}


# ----------------------------------------------------------------------------
# Latitude curves
# ----------------------------------------------------------------------------

def plot_latitude_profiles(centres: np.ndarray, profiles: Dict[str, np.ndarray], path: str, ylabel: str = "AbsRel",
                           title: str = "Error vs |latitude|", ci: bool = True, colors: Optional[Dict] = None,
                           xlabel: str = "|latitude| (deg)"):
    """profiles: method -> (n_images, n_bins). Mean over images with a 95% bootstrap band."""
    colors = colors or color_for(list(profiles))
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    rng = np.random.default_rng(0)
    for name, P in profiles.items():
        P = np.asarray(P)
        m = np.nanmean(P, 0)
        ax.plot(centres, m, color=colors[name], label=name)
        if ci and P.shape[0] > 2:
            bs = np.stack([np.nanmean(P[rng.integers(0, len(P), len(P))], 0) for _ in range(500)])
            lo, hi = np.nanquantile(bs, [0.025, 0.975], axis=0)
            ax.fill_between(centres, lo, hi, color=colors[name], alpha=0.15, linewidth=0)
    for x in (15, 30, 45, 60, 75) if centres.min() >= 0 else ():
        ax.axvline(x, color=GRID, lw=0.8, zorder=0)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, path)


def plot_band_metrics(summary, methods: Sequence[str], bands: Sequence[str], metrics=("abs_rel", "rmse", "d1", "mae"),
                      path: str = "band_metrics.png", colors: Optional[Dict] = None):
    """Small multiples (one panel per metric, each with its own single y-axis)."""
    colors = colors or color_for(methods)
    fig, axes = plt.subplots(1, len(metrics), figsize=(3.2 * len(metrics), 3.0))
    for ax, met in zip(np.atleast_1d(axes), metrics):
        for mth in methods:
            s = summary[(summary.method == mth)].set_index("band").reindex(bands)[met]
            ax.plot(range(len(bands)), s.values, marker="o", ms=4, color=colors[mth], label=mth)
        ax.set_xticks(range(len(bands)))
        ax.set_xticklabels(bands, rotation=45, fontsize=7)
        ax.set_title(met, loc="left")
        ax.set_xlabel("|latitude| band (deg)")
    np.atleast_1d(axes)[0].legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    _save(fig, path)


def plot_error_heatmap(mean_err: np.ndarray, path: str, title: str = "Mean AbsRel over the dataset", vmax=None):
    H, W = mean_err.shape
    fig, ax = plt.subplots(figsize=(7, 3.8))
    vmax = vmax or np.nanpercentile(mean_err, 99)
    im = ax.imshow(mean_err, cmap="Reds", vmin=0, vmax=vmax, extent=[-180, 180, -90, 90], aspect="auto")
    ax.set_xlabel("longitude (deg)")
    ax.set_ylabel("latitude (deg)")
    ax.set_title(title, loc="left")
    ax.grid(False)
    for y in (-60, -45, -30, 30, 45, 60):
        ax.axhline(y, color="#52514e", lw=0.5, ls=":")
    fig.colorbar(im, ax=ax, fraction=0.025, label="AbsRel")
    _save(fig, path)


def plot_runtime_tradeoff(df, path: str, x="runtime_ratio", y="polar_abs_rel", label="method",
                          title="Accuracy vs compute"):
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    families = sorted(df["family"].unique()) if "family" in df else ["all"]
    cols = color_for(families)
    for fam in families:
        d = df[df["family"] == fam] if "family" in df else df
        ax.scatter(d[x], d[y], s=40, color=cols[fam], label=fam, edgecolor="white", linewidth=1, zorder=3)
    for _, r in df.iterrows():
        if r.get("annotate", False):
            ax.annotate(r[label], (r[x], r[y]), fontsize=7, color=TEXT2, xytext=(4, 3), textcoords="offset points")
    ax.set_xlabel("runtime relative to baseline (x)")
    ax.set_ylabel("AbsRel, |lat| >= 60 deg")
    ax.set_title(title, loc="left")
    ax.legend(fontsize=7)
    _save(fig, path)


def plot_distortion(path: str):
    """ERP horizontal stretch 1/cos(phi) and pixel solid angle vs latitude."""
    lat = np.linspace(0, 89, 400)
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    ax[0].plot(lat, 1 / np.cos(np.radians(lat)), color=SERIES[0])
    ax[0].set_yscale("log")
    ax[0].set_title("ERP horizontal stretch 1/cos(phi)", loc="left")
    ax[0].set_xlabel("|latitude| (deg)")
    ax[1].plot(lat, np.cos(np.radians(lat)), color=SERIES[0])
    ax[1].set_title("Relative solid angle per ERP pixel", loc="left")
    ax[1].set_xlabel("|latitude| (deg)")
    fig.tight_layout()
    _save(fig, path)


# ----------------------------------------------------------------------------
# Qualitative panels
# ----------------------------------------------------------------------------

def qualitative_panel(rgb, gt, base, corr, valid, path: str, title: str = "", err_max: float = 0.5,
                      lat_threshold: Optional[float] = None):
    """Original ERP | GT | baseline | corrected | baseline err | corrected err | improvement | latitude map."""
    from pano.geometry.spherical import latitude_map

    H, W = gt.shape
    lo, hi = np.nanpercentile(gt[valid], [1, 99])
    eb = np.where(valid, np.abs(base - gt) / gt, np.nan)
    ec = np.where(valid, np.abs(corr - gt) / gt, np.nan)
    imp = eb - ec
    lat = latitude_map(H, W)
    panels = [
        ("Original ERP", rgb, None, None, None), ("Ground-truth depth (m)", np.where(valid, gt, np.nan), "magma", lo, hi),
        ("Baseline prediction", base, "magma", lo, hi), ("Corrected prediction", corr, "magma", lo, hi),
        ("Baseline AbsRel", eb, "Reds", 0, err_max), ("Corrected AbsRel", ec, "Reds", 0, err_max),
        ("Improvement (base - corr AbsRel)", imp, DIVERGING, -err_max / 2, err_max / 2),
        ("Latitude (deg)", lat, "Blues", -90, 90),
    ]
    fig, axes = plt.subplots(4, 2, figsize=(11, 11.5))
    for ax, (t, img, cmap, vmin, vmax) in zip(axes.ravel(), panels):
        if cmap is None:
            ax.imshow(img)
        else:
            if cmap == "Blues":
                im = ax.imshow(np.abs(img), cmap=cmap, vmin=0, vmax=90)
            else:
                im = ax.imshow(img, cmap=cmap, vmin=vmin, vmax=vmax)
            plt.colorbar(im, ax=ax, fraction=0.023, pad=0.01)
        if lat_threshold is not None:
            for s in (1, -1):
                v = (90 - s * lat_threshold) / 180 * H - 0.5
                ax.axhline(v, color="white" if cmap in (None, "magma") else TEXT2, lw=0.7, ls="--")
        ax.set_title(t, loc="left", fontsize=9)
        ax.axis("off")
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    _save(fig, path)


def tangent_panel(rgb, plane, tan_rgb, tan_pred, reproj, reproj_valid, gt, path: str, title: str = ""):
    """Distorted polar region in ERP (with the tangent footprint) | tangent image | model output | reprojection."""
    from pano.geometry.tangent_plane import tangent_geometry_on_erp

    H, W = gt.shape
    inside = tangent_geometry_on_erp(plane, H, W)[2]
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), gridspec_kw={"width_ratios": [2, 1, 1, 2]})
    rows = slice(0, H // 3) if plane.lat_deg > 0 else slice(2 * H // 3, H)
    show = rgb[rows].copy()
    edge = inside[rows] ^ np.roll(inside[rows], 1, 0) | inside[rows] ^ np.roll(inside[rows], 1, 1)
    show[edge] = [42, 120, 214]
    axes[0].imshow(show)
    axes[0].set_title("ERP polar region (tangent footprint outlined)", loc="left", fontsize=9)
    axes[1].imshow(tan_rgb)
    axes[1].set_title(f"Tangent view ({plane.lon_deg:.0f}, {plane.lat_deg:.0f}), FOV {plane.fov_deg:.0f}", loc="left",
                      fontsize=9)
    axes[2].imshow(tan_pred, cmap="magma")
    axes[2].set_title("Model prediction (tangent)", loc="left", fontsize=9)
    rp = np.where(reproj_valid, reproj, np.nan)[rows]
    axes[3].imshow(rp, cmap="magma")
    axes[3].set_title("Re-projected to ERP", loc="left", fontsize=9)
    for a in axes:
        a.axis("off")
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    _save(fig, path)
