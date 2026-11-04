#!/usr/bin/env python3
"""A1 + A3: latitude error profile of the plain ERP prediction, per alignment protocol, with a cluster-robust onset
(first |lat| bin whose excess over the < 15 deg reference is significant and >= rel_min of it) and the protocol gap.

  python scripts/latitude_profile.py --config 3_structured3d_benchmark/config.yaml --tag midas_s3_calib
Writes results/profile_<tag>.json, results/PROFILE_<tag>.md, results/profile_<tag>.png. One forward pass per frame.
Within a 2.5 deg bin pixel- and solid-angle weighting coincide (cos(lat) is ~constant), so only the pixel mean is kept.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import ROOT, add_common_args, depth_range, load_config, load_dataset, load_model  # noqa: E402
from evaluation.distortion_analysis import REF_MAX_LAT, bin_edges, cluster_curve, frame_profile, onset_from_curve  # noqa: E402
from evaluation.protocol import default_protocols, group_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(ap)
    ap.add_argument("--bin", type=float, default=2.5)
    ap.add_argument("--rel_min", type=float, default=0.10)
    ap.add_argument("--protocols", default=None, help="comma list; default: the model's two protocols + align-equatorial")
    a = ap.parse_args()
    cfg = load_config(a.config, a.overrides)
    model = load_model(cfg)
    ds = load_dataset(cfg, a.split, a.max_scenes)
    min_d, max_d = depth_range(cfg)
    protos = a.protocols.split(",") if a.protocols else list(dict.fromkeys(list(default_protocols(model)) + ["align-equatorial"]))
    per, ids = {p: [] for p in protos}, []
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        pr = frame_profile(np.asarray(model.predict(smp.rgb, kind="erp"), dtype=np.float64), gt, valid, model, protos,
                           bin_deg=a.bin, min_depth=min_d, max_depth=max_d)
        for p in protos:
            per[p].append(pr[p]["mean"])
        ids.append(smp.id)
        print(f"[{i + 1}/{len(ds)}] {smp.id}", flush=True)
    groups = [group_of(s) for s in ids]
    edges = bin_edges(a.bin)
    centres = (0.5 * (edges[:-1] + edges[1:])).tolist()
    ref_cols = np.array(centres) < REF_MAX_LAT
    summ = {"centres": centres, "bin_deg": a.bin, "n_frames": len(ids), "n_clusters": len(set(groups)), "protocols": {}}
    for p in protos:
        V = np.array(per[p], float)
        with np.errstate(invalid="ignore"):
            ref = np.nanmean(V[:, ref_cols], axis=1, keepdims=True)
        prof = cluster_curve(V, groups)
        exc = cluster_curve(V - ref, groups)  # paired per frame: bin minus the frame's own equatorial reference
        refc = cluster_curve(np.repeat(ref, V.shape[1], 1), groups)
        onset = onset_from_curve(centres, exc["ci_lo"], ref=refc["mean"], rel_min=a.rel_min, min_clusters=exc["n_clusters"])
        summ["protocols"][p] = {"profile": prof, "excess": exc, "onset": onset}
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    rec = {"tag": a.tag, "config": cfg, "split": a.split, "scene_ids": ids, "model": getattr(model, "name", "?"),
           "per_frame": per, "summary": summ}
    (out / f"profile_{a.tag}.json").write_text(json.dumps(rec), encoding="utf-8")
    f = lambda v: "n/a" if not np.isfinite(v) else f"{v:.4f}"
    lines = [f"# Latitude profile: {a.tag}", "", f"model `{rec['model']}` · {len(ids)} frames · {len(set(groups))} clusters", "",
             "| protocol | onset (deg) | AbsRel 0-15 | AbsRel 60-75 | AbsRel 75-90 |", "|---|---:|---:|---:|---:|"]
    c = np.array(centres)
    for p in protos:
        m = np.array(summ["protocols"][p]["profile"]["mean"])
        band = lambda lo, hi: float(np.nanmean(m[(c >= lo) & (c < hi)]))
        lines.append(f"| {p} | {summ['protocols'][p]['onset']} | {f(band(0, 15))} | {f(band(60, 75))} | {f(band(75, 90))} |")
    if "align-all" in protos and "align-equatorial" in protos:
        g = np.array(summ["protocols"]["align-equatorial"]["profile"]["mean"]) - np.array(summ["protocols"]["align-all"]["profile"]["mean"])
        lines += ["", f"**A3 protocol gap** (align-equatorial minus align-all), 75-90 deg: {f(float(np.nanmean(g[c >= 75])))}; "
                  f"0-15 deg: {f(float(np.nanmean(g[c < 15])))}. A large polar gap means part of the 'polar deficit' is the "
                  "alignment extrapolating from the equator, not the model."]
    (out / f"PROFILE_{a.tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for p in protos:
        pr = summ["protocols"][p]["profile"]
        ax.plot(c, pr["mean"], label=p)
        ax.fill_between(c, pr["ci_lo"], pr["ci_hi"], alpha=0.2)
    ax.set_xlabel("|latitude| (deg)")
    ax.set_ylabel("AbsRel")
    ax.set_title(f"{a.tag}: {rec['model']}", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / f"profile_{a.tag}.png", dpi=130)
    print(f"wrote results/PROFILE_{a.tag}.md")


if __name__ == "__main__":
    main()
