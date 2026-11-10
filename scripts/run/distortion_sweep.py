#!/usr/bin/env python3
"""A2 (+A4): causal distortion sweep. Every panorama is rotated in pitch, predicted and rotated back, so each pixel is
predicted while being seen at several latitudes with its content unchanged (evaluation/distortion_analysis.py).

  python scripts/distortion_sweep.py --config 3_structured3d_benchmark/config.yaml --tag midas_s3_calib
  python scripts/distortion_sweep.py --config 3_structured3d_benchmark/config_dap.yaml --tag dap_s3_calib
  python scripts/distortion_sweep.py --config 3_structured3d_benchmark/config.yaml --set model.name=da360 --tag da360_s3_calib

Writes results/sweep_<tag>.json (per-frame curves + cluster-robust summary: onset latitude, error-ratio curve used by
Part B), results/SWEEP_<tag>.md and results/sweep_<tag>.png. Cost: len(pitches) forward passes per frame.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from scripts.analysis.analysis_common import add_common_args, depth_range, load_config, load_dataset, load_model
from pano.paths import BENCHMARK_RESULTS  # noqa: E402
from pano.evaluation.distortion_analysis import MODES, default_values, summarize_sweep, sweep_frame  # noqa: E402


def planar_mask_for(model, pred):
    """A4: cap pixels explained by an accepted floor / ceiling plane (planar prior fit on the model's own ring)."""
    from methods.polar_fusion.planar_prior import fit_polar_planes
    from methods.polar_fusion.polar_views import fusion_space
    plane, _ = fit_polar_planes(pred, "disparity" if fusion_space(model) == "disparity" else "depth")
    return np.isfinite(plane)


def report(summary: dict, tag: str, model_name: str) -> str:
    c = summary["centres"]
    f = lambda v: "n/a" if v is None or not np.isfinite(v) else f"{v:.4f}"
    lines = [f"# Distortion sweep: {tag}", "",
             f"model `{model_name}` · {summary['n_frames']} frames · {summary['n_clusters']} clusters · bins "
             f"{summary['bin_deg']:.0f} deg · onset rule: two consecutive bins with cluster-CI lower bound of dE above "
             f"{100 * summary['rel_min']:.0f}% of the equator-seen error", "",
             f"**Sweep mode: {summary.get('mode', 'rotation')}** "
             + {"rotation": "(pitch rotations: content moves in latitude, the scene is tipped)",
                "dilation": "(stereographic dilations: content moves in latitude, up stays up, content is magnified by exp(log_mag))",
                "flip": "(roll 180: same |latitude|, upside down; dE = orientation penalty, not distortion)"}[summary.get("mode", "rotation")],
             "",
             f"**Onset latitude (global estimator, used by Part B): {summary['onset_global']}**  ·  local estimator "
             f"(sensitivity only): {summary['onset_local']}  ·  non-planar content only: {summary.get('onset_nonplanar')}", "",
             "dE = error of a pixel seen at latitude L minus the error of the SAME pixel in the pass where it is seen "
             "closest to the equator (content fixed). ratio = E(L) / E_ref of the same samples. floor = GT rotated there "
             "and back (interpolation cost, not distortion).", "",
             "| seen lat | E (global) | dE [95% CI] | ratio | dE local | floor | ref lat | log mag | clusters |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for j, cc in enumerate(c):
        dg = summary["de_global"]
        lines.append(f"| {cc:.1f} | {f(summary['e_global']['mean'][j])} | {f(dg['mean'][j])} [{f(dg['ci_lo'][j])}, "
                     f"{f(dg['ci_hi'][j])}] | {summary['ratio_global'][j]:.2f} | {f(summary['de_local']['mean'][j])} | "
                     f"{f(summary['floor']['mean'][j])} | {summary['ref_lat']['mean'][j]:.1f} | "
                     f"{summary['log_mag']['mean'][j]:+.2f} | {dg['n_clusters'][j]} |")
    if "de_global_planar" in summary:
        lines += ["", "**A4 content split** (dE global): planar cap pixels (accepted floor / ceiling plane) vs the rest", "",
                  "| seen lat | dE planar | dE non-planar |", "|---|---:|---:|"]
        for j, cc in enumerate(c):
            lines.append(f"| {cc:.1f} | {f(summary['de_global_planar']['mean'][j])} | {f(summary['de_global_nonplanar']['mean'][j])} |")
    return "\n".join(lines) + "\n"


def figure(summary: dict, path: Path, title: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c = np.array(summary["centres"])
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for est, ls in (("global", "-"), ("local", "--")):
        d = summary[f"de_{est}"]
        ax[0].plot(c, d["mean"], ls, label={"global": "ΔE, one global alignment (headline)",
                                             "local": "ΔE, alignment per latitude band"}[est])
        if est == "global":
            ax[0].fill_between(c, d["ci_lo"], d["ci_hi"], alpha=0.25)
    ax[0].plot(c, summary["floor"]["mean"], ":", label="resampling floor (error from re-projection alone)")
    ax[0].axhline(0, color="k", lw=0.5)
    if summary["onset_global"] is not None:
        ax[0].axvline(summary["onset_global"], color="r", lw=1, label="onset latitude")
    ax[0].set_xlabel("latitude at which the content is seen, |φ| (°)")
    ax[0].set_ylabel("excess AbsRel ΔE(L) vs the equator-seen pass\n(0 = no extra error)")
    ax[0].set_title("excess error (band = 95% cluster bootstrap CI)", fontsize=9)
    ax[0].legend(fontsize=7)
    ax[1].plot(c, summary["ratio_global"], "-o", ms=3, label="E(L) / E(equator), global alignment")
    ax[1].axhline(1, color="k", lw=0.5)
    ax[1].set_xlabel("latitude at which the content is seen, |φ| (°)")
    ax[1].set_ylabel("error ratio (1 = no extra error)")
    ax[1].set_title("error ratio", fontsize=9)
    ax[1].legend(fontsize=7)
    for a_ in ax:
        a_.set_xlim(0, 90)
        a_.grid(True, ls=":", alpha=0.5)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(ap)
    ap.add_argument("--mode", default="rotation", choices=MODES,
                    help="rotation (pitch; tips the scene) | dilation (stereographic lambda; keeps up, magnifies) | "
                         "flip (roll 180; same |lat|, upside down: orientation penalty only)")
    ap.add_argument("--values", default=None, help="comma list of pitches (deg) / lambdas / rolls; default per mode")
    ap.add_argument("--pitches", default=None, help="deprecated alias of --values for --mode rotation")
    ap.add_argument("--bin", type=float, default=5.0)
    ap.add_argument("--rel_min", type=float, default=0.10)
    ap.add_argument("--no_planar", action="store_true", help="skip the A4 planar / non-planar split")
    a = ap.parse_args()
    cfg = load_config(a.config, a.overrides)
    model = load_model(cfg)
    ds = load_dataset(cfg, a.split, a.max_scenes)
    min_d, max_d = depth_range(cfg)
    raw = a.values or a.pitches
    from fractions import Fraction  # accepts 0.5, 1/16, -90
    values = [float(Fraction(v.strip())) for v in raw.split(",")] if raw else list(default_values(a.mode))
    frames, ids, skipped = [], [], 0
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        pred0 = np.asarray(model.predict(smp.rgb, kind="erp"), dtype=np.float64)
        pm = None if a.no_planar else planar_mask_for(model, pred0)
        fr = sweep_frame(model, smp.rgb, gt, valid, bin_deg=a.bin, min_depth=min_d, max_depth=max_d,
                         identity_pred=pred0, planar_mask=pm, mode=a.mode, values=values)
        if fr is None:
            skipped += 1
            continue
        frames.append(fr)
        ids.append(smp.id)
        print(f"[{i + 1}/{len(ds)}] {smp.id}", flush=True)
    if len(frames) < 2:
        raise SystemExit(f"only {len(frames)} usable frames ({skipped} skipped)")
    summ = summarize_sweep(frames, ids, a.bin, rel_min=a.rel_min)
    out = BENCHMARK_RESULTS
    out.mkdir(exist_ok=True)
    rec = {"tag": a.tag, "config": cfg, "split": a.split, "mode": a.mode, "values": values, "scene_ids": ids, "skipped": skipped,
           "model": getattr(model, "name", "?"), "frames": frames, "summary": summ}
    (out / f"sweep_{a.tag}.json").write_text(json.dumps(rec), encoding="utf-8")
    (out / f"SWEEP_{a.tag}.md").write_text(report(summ, a.tag, rec["model"]), encoding="utf-8")
    figure(summ, out / f"sweep_{a.tag}.png",
           f"{a.tag} ({a.mode}): {rec['model']}, {summ['n_frames']} frames / {summ['n_clusters']} clusters")
    print(f"onset (global) = {summ['onset_global']}  ->  results/SWEEP_{a.tag}.md")


if __name__ == "__main__":
    main()
