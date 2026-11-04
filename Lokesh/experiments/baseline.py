"""Experiment 1: baseline ERP inference + latitude analysis, and the content-vs-latitude control.

Latitude analysis answers "does error change with latitude?". On its own it cannot tell
*why*: in indoor panoramas the poles always show floor and ceiling, so latitude is
confounded with scene content. The control experiment re-runs the frozen model on
panoramas rotated on the sphere (pitch 0/30/60/90 deg; GT rotated identically). The same
content then appears at different latitudes of the image the model sees, so the error can
be attributed to (a) the latitude in the model's input ("distortion") vs (b) the latitude
of the content in the upright scene ("content").
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from evaluation.latitude_analysis import named_band_masks, onset_latitude
from evaluation.metrics import error_maps
from geometry.erp_projection import rotate_erp, rotated_latitude
from geometry.spherical import latitude_map, rotation_from_ypr
from visualization.visualize import SERIES, plot_error_heatmap, plot_latitude_profiles


def latitude_report(ev, out_dir: str, method: str = "baseline", tag: str = "align-all"):
    """Named-band table, error-vs-latitude curves (signed & absolute), onset latitude."""
    os.makedirs(out_dir, exist_ok=True)
    df = ev.frame()
    d = df[(df.method == method) & (df.weighting == "pixel")]
    tab = d.groupby("band")[["abs_rel", "rmse", "d1", "mae", "err_var", "pct_bad", "n"]].mean()
    order = [b for b in ["all", "0-15", "15-30", "30-45", "45-60", "60-75", "75-90"] if b in tab.index]
    tab = tab.loc[order]
    tab.to_csv(os.path.join(out_dir, f"latitude_bands_{tag}.csv"))
    P = np.stack(ev.profiles[method])
    c = ev.profile_centres
    on = onset_latitude(P, c)
    with open(os.path.join(out_dir, f"onset_{tag}.json"), "w") as f:
        json.dump(on, f, indent=2)
    plot_latitude_profiles(c, {method: P}, os.path.join(out_dir, f"abs_rel_vs_abs_latitude_{tag}.png"),
                           title=f"Baseline AbsRel vs |latitude| ({tag}, mean +- 95% CI over images)")
    return tab, on


def band_metric_plots(ev, out_dir, method="baseline", tag="align-all"):
    from visualization.visualize import plot_band_metrics
    sm = ev.summary()
    bands = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90"]
    plot_band_metrics(sm, [method], bands, metrics=("abs_rel", "rmse", "d1", "mae", "err_var", "pct_bad"),
                      path=os.path.join(out_dir, f"baseline_band_metrics_{tag}.png"))


def latitude_control(model, dataset, out_dir: str, pitches=(0, 30, 60, 90), eval_align="affine", space="disparity",
                     bin_deg: float = 15.0, log=print):
    """Content-vs-latitude disentanglement. Returns a long DataFrame of (pitch, view_band, content_band, error)."""
    from evaluation.metrics import to_metric_depth

    os.makedirs(out_dir, exist_ok=True)
    rows = []
    nb = int(90 / bin_deg)
    for s in dataset:
        H, W = s.depth.shape
        for p in pitches:
            R = rotation_from_ypr(0, p, 0)
            rgb_r = np.clip(rotate_erp(s.rgb.astype(np.float32), R) + 0.5, 0, 255).astype(np.uint8) if p else s.rgb
            gt_r, v_r = rotate_erp(np.nan_to_num(s.depth).astype(np.float64), R, mode="nearest", mask=s.valid)
            v_r = v_r & (gt_r > 0)
            pred = model.predict(rgb_r, "erp").astype(np.float64)
            view_lat = np.abs(latitude_map(H, W))
            # latitude of each rotated pixel's content in the upright scene: d_content = R d
            content_lat = np.abs(rotated_latitude(H, W, R.T))
            vb = np.minimum((view_lat // bin_deg).astype(int), nb - 1)
            cb = np.minimum((content_lat // bin_deg).astype(int), nb - 1)
            # GT alignment fitted on: all pixels / the input's equator / the content's equator (walls)
            fits = {"all": v_r, "view_equatorial": v_r & (view_lat < 30), "content_equatorial": v_r & (content_lat < 30)}
            for aname, fit in fits.items():
                depth, _ = to_metric_depth(pred, np.where(v_r, gt_r, 1.0), fit, space, eval_align)
                err = error_maps(depth, np.where(v_r, gt_r, 1.0), v_r)["abs_rel"]
                m = np.isfinite(err)
                for a in range(nb):
                    for b in range(nb):
                        mm = m & (vb == a) & (cb == b)
                        if mm.sum() > 50:
                            rows.append({"image": s.id, "pitch": p, "align": aname, "view_band": a * bin_deg,
                                         "content_band": b * bin_deg, "abs_rel": float(err[mm].mean()),
                                         "n": int(mm.sum())})
        log(f"[latitude-control] {s.id} done")
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "latitude_control_rows.csv"), index=False)
    return df


def latitude_control_report(df: pd.DataFrame, out_dir: str):
    """Per pitch: error vs view-latitude and vs content-latitude; and the content-controlled table."""
    import matplotlib.pyplot as plt

    def wavg(g):
        return np.average(g.abs_rel, weights=g.n)

    by_view = df.groupby(["pitch", "view_band"]).apply(wavg, include_groups=False).unstack(0)
    by_content = df.groupby(["pitch", "content_band"]).apply(wavg, include_groups=False).unstack(0)
    # content-controlled: per (image, content band, view band) cell, mean over images of
    # [error(view band) - error(view band 0)] within the same image and content band
    cells = df.groupby(["image", "content_band", "view_band"]).apply(wavg, include_groups=False).rename("e").reset_index()
    ref = cells[cells.view_band == cells.view_band.min()].set_index(["image", "content_band"]).e
    cells = cells.join(ref.rename("e_ref"), on=["image", "content_band"])
    cells["rel_change_%"] = (cells.e - cells.e_ref) / cells.e_ref * 100
    controlled = cells.dropna().groupby("view_band")["rel_change_%"].agg(["mean", "median", "count"])
    # Same analysis WITHIN each pitch: all cells then come from the same (equally rotated) input image,
    # so a global "rotated-input" penalty cannot masquerade as a latitude effect.
    wp = df.groupby(["pitch", "image", "content_band", "view_band"]).apply(wavg, include_groups=False).rename("e").reset_index()
    rows = []
    for p, g in wp.groupby("pitch"):
        for (img, cb), gg in g.groupby(["image", "content_band"]):
            if len(gg) < 2:
                continue
            r0 = gg.sort_values("view_band").iloc[0]
            for _, r in gg.iterrows():
                rows.append({"pitch": p, "content_band": cb, "ref_view_band": r0.view_band, "view_band": r.view_band,
                             "delta_view_deg": r.view_band - r0.view_band, "rel_change_%": (r.e - r0.e) / r0.e * 100})
    within = pd.DataFrame(rows)
    within_tab = within[within.delta_view_deg > 0].groupby(["pitch", "delta_view_deg"])["rel_change_%"].agg(
        ["mean", "median", "count"])
    within_tab.to_csv(os.path.join(out_dir, "control_within_pitch_view_effect.csv"))
    by_view.to_csv(os.path.join(out_dir, "control_error_by_view_latitude.csv"))
    by_content.to_csv(os.path.join(out_dir, "control_error_by_content_latitude.csv"))
    controlled.to_csv(os.path.join(out_dir, "control_content_controlled_view_effect.csv"))
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    for i, p in enumerate(by_view.columns):
        ax[0].plot(by_view.index + 7.5, by_view[p], marker="o", ms=4, color=SERIES[i], label=f"pitch {p}")
        ax[1].plot(by_content.index + 7.5, by_content[p], marker="o", ms=4, color=SERIES[i], label=f"pitch {p}")
    ax[0].set_title("AbsRel vs |latitude| in the model's input", loc="left")
    ax[1].set_title("AbsRel vs |latitude| of the content (upright scene)", loc="left")
    for a in ax:
        a.set_xlabel("|latitude| (deg)")
    ax[0].set_ylabel("AbsRel")
    ax[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "latitude_control.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return by_view, by_content, controlled
