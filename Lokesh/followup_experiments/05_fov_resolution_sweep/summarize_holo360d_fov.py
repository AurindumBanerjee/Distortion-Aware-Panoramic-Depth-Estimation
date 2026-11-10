#!/usr/bin/env python3
"""Paired scene-cluster analysis for the Holo360D indoor FOV transfer run."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

LABELS = [f"fov{f}_size256" for f in (70, 90, 110, 130)]
BANDS = ("all", "60-75", "75-90")
PROTOCOLS = ("align-all", "align-equatorial")


def read_rows(path: Path):
    by_metric = defaultdict(dict)
    groups = {}
    metadata = defaultdict(dict)
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid, config = row["scene"], row["config"]
            protocol, band = row["protocol"], row["band"]
            groups[sid] = row["environment"]
            value = float(row["abs_rel"])
            if np.isfinite(value):
                by_metric[(protocol, band, config)][sid] = value
            metadata[(protocol, config)][sid] = {
                "coverage_60_90": float(row.get("coverage_60_90") or 0.0),
                "runtime_s": float(row.get("runtime_s") or 0.0),
                "model_calls": int(float(row.get("model_calls") or 0)),
            }
    return by_metric, groups, metadata


def paired_cluster_gain(reference, candidate, groups, seed=53, n_boot=2000):
    ids = sorted(set(reference) & set(candidate))
    by_group = defaultdict(list)
    wins, worsens = [], []
    for sid in ids:
        b, x = reference[sid], candidate[sid]
        if np.isfinite(b) and np.isfinite(x) and b > 0:
            by_group[groups[sid]].append((b - x) / b)
            wins.append(x < b)
            worsens.append(x > b * 1.01)
    cluster_values = np.asarray([np.mean(v) for _, v in sorted(by_group.items())], dtype=float)
    if cluster_values.size == 0:
        return {"n_scenes": 0, "n_clusters": 0, "median_gain": None, "ci95": [None, None],
                "win_rate": None, "worse_gt_1pct_rate": None}
    rng = np.random.default_rng(seed)
    boot = np.median(
        cluster_values[rng.integers(0, cluster_values.size, size=(n_boot, cluster_values.size))],
        axis=1,
    )
    return {
        "n_scenes": len(wins),
        "n_clusters": int(cluster_values.size),
        "median_gain": float(np.median(cluster_values)),
        "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "win_rate": float(np.mean(wins)),
        "worse_gt_1pct_rate": float(np.mean(worsens)),
    }


def metric_summary(values):
    vals = np.asarray(list(values.values()), dtype=float)
    vals = vals[np.isfinite(vals)]
    return {
        "n_scenes": int(vals.size),
        "median_abs_rel": float(np.median(vals)) if vals.size else None,
        "mean_abs_rel": float(np.mean(vals)) if vals.size else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True, help="Timestamped outputs directory from Experiment 05")
    ap.add_argument("--seed", type=int, default=53)
    ap.add_argument("--bootstrap", type=int, default=2000)
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    csv_path = run_dir / "per_scene.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(f"Missing per_scene.csv: {csv_path}")

    metrics, groups, metadata = read_rows(csv_path)
    result = {
        "experiment": "05_holo360d_indoor_fov_transfer",
        "run_dir": str(run_dir),
        "n_scenes": len(groups),
        "n_scene_clusters": len(set(groups.values())),
        "seed": args.seed,
        "bootstrap_samples": args.bootstrap,
        "protocols": {},
    }

    for protocol in PROTOCOLS:
        result["protocols"][protocol] = {}
        for band in BANDS:
            baseline = metrics.get((protocol, band, "baseline"), {})
            block = {"metrics": {}, "vs_baseline": {}, "vs_fov70": {}}
            for label in LABELS:
                values = metrics.get((protocol, band, label), {})
                block["metrics"][label] = metric_summary(values)
                block["vs_baseline"][label] = paired_cluster_gain(
                    baseline, values, groups, args.seed, args.bootstrap
                )
                if label == LABELS[0]:
                    block["vs_fov70"][label] = {
                        "n_scenes": len(values),
                        "n_clusters": len(set(groups[s] for s in values)),
                        "median_gain": 0.0,
                        "ci95": [0.0, 0.0],
                        "win_rate": None,
                        "worse_gt_1pct_rate": None,
                    }
                else:
                    ref70 = metrics.get((protocol, band, LABELS[0]), {})
                    block["vs_fov70"][label] = paired_cluster_gain(
                        ref70, values, groups, args.seed, args.bootstrap
                    )
            block["baseline"] = metric_summary(baseline)
            result["protocols"][protocol][band] = block

    # Runtime and coverage are per scene/config; de-duplicate across protocol/band CSV rows.
    result["runtime_coverage"] = {}
    for label in LABELS:
        per_scene = {}
        for protocol in PROTOCOLS:
            per_scene.update(metadata.get((protocol, label), {}))
        vals = list(per_scene.values())
        result["runtime_coverage"][label] = {
            "median_runtime_s": float(np.median([v["runtime_s"] for v in vals])) if vals else None,
            "median_model_calls": float(np.median([v["model_calls"] for v in vals])) if vals else None,
            "mean_coverage_60_90": float(np.mean([v["coverage_60_90"] for v in vals])) if vals else None,
        }

    report = [
        "# Experiment 05 cross-dataset validation — Holo360D indoor",
        "",
        f"- Scenes: {result['n_scenes']}",
        f"- Independent scene clusters: {result['n_scene_clusters']}",
        "- Model: MiDaS DPT-Hybrid 384 (frozen)",
        "- FOVs: 70°, 90°, 110°, 130°; fixed tangent resolution 256²",
        "- Other inference settings held fixed from Experiment 05",
        "- Statistics: paired cluster bootstrap over Holo360D scene IDs",
        "",
        "## Primary result: polar band (75–90°)",
        "",
        "| Protocol | FOV | Median AbsRel | Gain vs baseline [95% cluster CI] | Gain vs 70° [95% cluster CI] | Scene win rate vs baseline |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for protocol in PROTOCOLS:
        block = result["protocols"][protocol]["75-90"]
        for label, fov in zip(LABELS, (70, 90, 110, 130)):
            m = block["metrics"][label]
            b = block["vs_baseline"][label]
            g = block["vs_fov70"][label]
            gain_b = "n/a" if b["median_gain"] is None else f"{100*b['median_gain']:+.1f}% [{100*b['ci95'][0]:+.1f}, {100*b['ci95'][1]:+.1f}]"
            gain_70 = "n/a" if g["median_gain"] is None else f"{100*g['median_gain']:+.1f}% [{100*g['ci95'][0]:+.1f}, {100*g['ci95'][1]:+.1f}]"
            win = "n/a" if b["win_rate"] is None else f"{100*b['win_rate']:.0f}%"
            med = "n/a" if m["median_abs_rel"] is None else f"{m['median_abs_rel']:.4f}"
            report.append(f"| {protocol} | {fov}° | {med} | {gain_b} | {gain_70} | {win} |")
    report += ["", "## Global and 60–75° checks", ""]
    for band in ("all", "60-75"):
        report += [f"### {band}", "", "| Protocol | FOV | Median AbsRel | Gain vs baseline [95% cluster CI] |", "|---|---:|---:|---:|"]
        for protocol in PROTOCOLS:
            block = result["protocols"][protocol][band]
            for label, fov in zip(LABELS, (70, 90, 110, 130)):
                m, b = block["metrics"][label], block["vs_baseline"][label]
                gain = "n/a" if b["median_gain"] is None else f"{100*b['median_gain']:+.1f}% [{100*b['ci95'][0]:+.1f}, {100*b['ci95'][1]:+.1f}]"
                med = "n/a" if m["median_abs_rel"] is None else f"{m['median_abs_rel']:.4f}"
                report.append(f"| {protocol} | {fov}° | {med} | {gain} |")
        report.append("")

    report += ["## Runtime and coverage", "", "| FOV | Median runtime (s) | Median model calls | Mean 60–90° coverage |", "|---:|---:|---:|---:|"]
    for label, fov in zip(LABELS, (70, 90, 110, 130)):
        m = result["runtime_coverage"][label]
        cov = "n/a" if m["mean_coverage_60_90"] is None else f"{100*m['mean_coverage_60_90']:.1f}%"
        runtime = "n/a" if m["median_runtime_s"] is None else f"{m['median_runtime_s']:.3f}"
        calls = "n/a" if m["median_model_calls"] is None else f"{m['median_model_calls']:.0f}"
        report.append(f"| {fov}° | {runtime} | {calls} | {cov} |")
    report += [
        "",
        "## Interpretation rule",
        "",
        "Treat the FOV result as externally supported only when the polar gain over 70° is positive "
        "with a cluster-bootstrap CI excluding zero under both alignment protocols, while the global "
        "band does not materially regress. Report the number of independent scene clusters. Do not "
        "tune FOV thresholds on this validation set.",
        "",
    ]

    (run_dir / "HOLO360D_VALIDATION.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (run_dir / "HOLO360D_VALIDATION.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
