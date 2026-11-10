#!/usr/bin/env python3
"""Compare DA360 scale-only and affine-in-disparity GT evaluation protocols."""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np
import torch
from pano.paths import ROOT

from experiments.followups.shared.common import (
    band_metrics, cluster_bootstrap_gain, environment_info,
    load_config, load_dataset, load_model, prepare_output, save_json,
    scene_group, align_prediction,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "followups" / "scale_only_protocol.yaml"))
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config, args.set)
    seed = int(cfg.get("seed", 0))
    np.random.seed(seed)
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required. Enable the Kaggle T4 accelerator.")
    ds = load_dataset(cfg["dataset"], limit=args.limit)
    model = load_model(cfg["model"])
    if model.spec.space != "disparity":
        raise SystemExit(f"Expected a disparity model, got {model.spec}")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_base = args.output_dir or cfg["output_dir"]
    out = prepare_output(Path(out_base) / f"run_{stamp}", overwrite=args.overwrite)
    protocols = cfg["evaluation"].get("protocols", ["align-all", "align-equatorial"])
    min_d, max_d = float(cfg["evaluation"]["min_depth"]), float(cfg["evaluation"]["max_depth"])
    rows, per_scene = [], {}
    groups = {}

    print(f"Model: {model.describe()}")
    print(f"Dataset: {len(ds)} scenes; output: {out}")
    for i, sample in enumerate(ds):
        pred = model.predict(sample.rgb, kind="erp")
        sid = sample.id
        groups[sid] = scene_group(sid)
        per_scene[sid] = {}
        for protocol in protocols:
            per_scene[sid][protocol] = {}
            for align_mode in ("scale", "affine"):
                depth = align_prediction(pred, sample.depth, sample.valid, model,
                                         protocol=protocol, mode=align_mode,
                                         min_depth=min_d, max_depth=max_d)
                metrics = band_metrics(depth, sample.depth, sample.valid, min_d, max_d)
                per_scene[sid][protocol][align_mode] = metrics
                for band, metric in metrics.items():
                    rows.append({
                        "scene": sid, "environment": groups[sid], "protocol": protocol,
                        "alignment": "scale_only" if align_mode == "scale" else "affine",
                        "band": band, **metric,
                    })
        if (i + 1) % 10 == 0 or i + 1 == len(ds):
            print(f"[{i + 1}/{len(ds)}] {sid}")

    summaries = {}
    comparisons = {}
    bands = ["all", "45-60", "60-75", "75-90"]
    for protocol in protocols:
        summaries[protocol] = {}
        for mode in ("scale", "affine"):
            summaries[protocol][mode] = {}
            for band in bands:
                vals = [per_scene[s][protocol][mode][band]["abs_rel"] for s in per_scene]
                summaries[protocol][mode][band] = {
                    "mean_abs_rel": float(np.nanmean(vals)),
                    "median_abs_rel": float(np.nanmedian(vals)),
                    "n_scenes": int(np.isfinite(vals).sum()),
                }
        comparisons[protocol] = {}
        for band in bands:
            b = {s: per_scene[s][protocol]["affine"][band]["abs_rel"] for s in per_scene}
            x = {s: per_scene[s][protocol]["scale"][band]["abs_rel"] for s in per_scene}
            comparisons[protocol][band] = cluster_bootstrap_gain(
                b, x, groups, n_boot=int(cfg["stats"].get("bootstrap_samples", 2000)), seed=seed
            )
            comparisons[protocol][band]["direction"] = "positive = scale-only lower AbsRel than affine"

    with (out / "per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    save_json(out / "per_scene.json", per_scene)
    save_json(out / "summary.json", {
        "experiment": "01_scale_only_protocol",
        "model": model.describe(),
        "dataset": cfg["dataset"],
        "num_scenes": len(ds),
        "environment": environment_info(),
        "summary": summaries,
        "paired_cluster_bootstrap_scale_vs_affine": comparisons,
    })

    report = [
        "# Experiment 1: DA360 scale-only evaluation protocol", "",
        f"- Scenes: {len(ds)}",
        f"- Model: {model.name}",
        "- Primary comparison: scale-only disparity fit vs affine disparity fit",
        "- Protocols: " + ", ".join(protocols),
        "- Positive bootstrap gain means scale-only has lower AbsRel than affine.", "",
    ]
    for protocol in protocols:
        report += [f"## {protocol}", "", "| Band | Scale-only median | Affine median | Scale-only vs affine gain (95% CI) |",
                   "|---|---:|---:|---:|"]
        for band in bands:
            a = summaries[protocol]["scale"][band]["median_abs_rel"]
            b = summaries[protocol]["affine"][band]["median_abs_rel"]
            ci = comparisons[protocol][band]["ci95"]
            gain = comparisons[protocol][band]["median_gain"]
            report.append(f"| {band} | {a:.4f} | {b:.4f} | {gain:+.2%} [{ci[0]:+.2%}, {ci[1]:+.2%}] |")
        report.append("")
    report += [
        "## Interpretation guardrails", "",
        "DA360 describes its prediction as scale-invariant disparity. The scale-only fit is therefore the",
        "methodologically preferred headline protocol; affine fitting is retained as a sensitivity analysis.",
        "This script does not alter model predictions or fit alignment separately by latitude band.",
        "The same scenes and validity masks are used in paired comparisons.", "",
        "Raw per-scene metrics are in per_scene.csv; the complete record is summary.json.",
    ]
    (out / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Saved: {out / 'REPORT.md'}")


if __name__ == "__main__":
    main()
