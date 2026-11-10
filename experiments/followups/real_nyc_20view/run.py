




#!/usr/bin/env python3
"""Run the locked 3-way MiDaS comparison on the held-out NYC manifest."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from pano.paths import ROOT
from experiments.followups.shared.common import (environment_info, evaluate_one, load_config, load_dataset, load_model,
                    prepare_output, save_json, seed_everything)
from experiments.followups.shared.mono360 import icosahedron_planes, mono360_fuse
from pano.inference.pipeline import DistortionAwareInference, MethodConfig
from pano.inference.tangent_inference import predict_tangent_raw


def cluster_for_nyc(scene_id: str) -> str:
    match = re.fullmatch(r"panorama_(\d+)", str(scene_id))
    if not match:
        raise ValueError(
            f"Unexpected NYC sample id {scene_id!r}; expected panorama_<integer>. "
            "Refusing to bootstrap with an ambiguous cluster assignment."
        )
    frame_id = int(match.group(1))
    return f"nyc_block_{frame_id // 20:03d}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def paired_cluster_bootstrap_gain(
    reference: dict[str, float],
    candidate: dict[str, float],
    groups: dict[str, str],
    *,
    n_boot: int = 10000,
    seed: int = 0,
) -> dict:
    """Equal-weight cluster bootstrap; positive gain means candidate has lower error."""
    ids = sorted(set(reference) & set(candidate))
    by_cluster: dict[str, list[float]] = {}
    for sid in ids:
        ref, cand = reference[sid], candidate[sid]
        if np.isfinite(ref) and np.isfinite(cand) and ref > 0:
            by_cluster.setdefault(groups[sid], []).append((ref - cand) / ref)
    if not by_cluster:
        raise RuntimeError("No valid paired scenes for cluster bootstrap.")
    cluster_effects = np.asarray(
        [np.mean(values) for _, values in sorted(by_cluster.items())], dtype=np.float64
    )
    if len(cluster_effects) < 8:
        raise RuntimeError(f"Only {len(cluster_effects)} clusters available; at least 8 are required.")
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(cluster_effects), size=(n_boot, len(cluster_effects)))
    boot = np.median(cluster_effects[draws], axis=1)
    point = float(np.median(cluster_effects))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {
        "n_scenes": len(ids),
        "n_clusters": len(cluster_effects),
        "median_cluster_gain": point,
        "ci95": [float(lo), float(hi)],
        "ci_excludes_zero": bool(lo > 0 or hi < 0),
        "interpretation": "positive = candidate reduces AbsRel vs reference",
        "bootstrap_replicates": int(n_boot),
    }


def summarize(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if not len(arr):
        return {"n": 0, "mean": None, "median": None}
    return {"n": int(len(arr)), "mean": float(np.mean(arr)), "median": float(np.median(arr))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "followups" / "real_nyc_20view.yaml"))
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument(
        "--limit", type=int, default=None,
        help="Pilot only: even number >=16, retaining complete two-frame clusters. "
             "Do not cite pilot confidence intervals as evaluation results.",
    )
    ap.add_argument("--output-dir", default=None, help="Optional base output directory.")
    args = ap.parse_args()

    cfg = load_config(args.config, args.set)
    seed_everything(int(cfg.get("seed", 0)))
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required. Run on a GPU runtime such as Kaggle T4.")
    if args.limit is not None and (args.limit < 16 or args.limit % 2):
        raise SystemExit("--limit must be an even number >=16 to retain at least eight complete clusters.")

    dataset_cfg = dict(cfg["dataset"])
    manifest = Path(dataset_cfg.pop("manifest"))
    if not manifest.is_absolute():
        manifest = ROOT / manifest
    manifest = manifest.resolve()
    if not manifest.is_file():
        raise SystemExit(f"Manifest not found: {manifest}. Run scripts/create_manifest.py first.")
    manifest_rows = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines()
                     if line.strip()]
    if len(manifest_rows) != 182:
        raise SystemExit(f"Expected 182 manifest rows; found {len(manifest_rows)}.")
    dataset_cfg["list"] = str(manifest)
    dataset = load_dataset(dataset_cfg, limit=args.limit)
    expected_scenes = args.limit if args.limit is not None else 182
    if len(dataset) != expected_scenes:
        raise RuntimeError(f"Loaded {len(dataset)} scenes; expected {expected_scenes}.")

    model = load_model(cfg["model"])
    if model.spec.space != "disparity":
        raise SystemExit("The current 20-view fusion is only defined here for disparity models.")
    inf, mono, ev = cfg["inference"], cfg["mono360"], cfg["evaluation"]
    tangent_size = int(inf["tangent_size"])
    planes = icosahedron_planes(size=tangent_size, padding=float(inf["padding"]))
    protocols = list(ev["protocols"])
    min_depth, max_depth = float(ev["min_depth"]), float(ev["max_depth"])
    n_boot = int(ev.get("bootstrap_replicates", 10000))

    groups = {sample.id: cluster_for_nyc(sample.id) for sample in dataset}
    cluster_sizes: dict[str, int] = {}
    for group in groups.values():
        cluster_sizes[group] = cluster_sizes.get(group, 0) + 1
    if any(size != 2 for size in cluster_sizes.values()):
        raise RuntimeError(f"Expected exactly two frames per 20-ID cluster; got {cluster_sizes}.")
    if args.limit is None and len(cluster_sizes) != 91:
        raise RuntimeError(f"Expected 91 assumed clusters; found {len(cluster_sizes)}.")

    output_base = Path(args.output_dir or cfg["output_dir"])
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    out = prepare_output(output_base / f"run_{stamp}")
    torch.cuda.reset_peak_memory_stats()
    dai = DistortionAwareInference(model, batch_size=int(inf["batch_size"]), use_cache=True)
    rows: list[dict] = []
    per_scene: dict[str, dict] = {}
    runtime_rows: dict[str, dict] = {}
    print(
        f"Experiment 07 | {len(dataset)} scenes | {len(cluster_sizes)} assumed 20-ID clusters | "
        f"20-view planes={len(planes)} | model={model.name}",
        flush=True,
    )

    for i, sample in enumerate(dataset):
        sid = sample.id
        per_scene[sid] = {}
        wall: dict[str, float] = {}

        torch.cuda.synchronize()
        t0 = time.perf_counter()
        baseline = dai.run(
            sample.rgb, sid, MethodConfig(method="baseline", name="baseline")
        )["pred"]
        torch.cuda.synchronize()
        wall["baseline_s"] = time.perf_counter() - t0

        simple_cfg = MethodConfig(
            method="tangent",
            lat_threshold=float(inf["polar_threshold"]),
            views_per_pole=int(inf["simple_views_per_pole"]),
            tangent_size=tangent_size,
            fusion=inf["simple_fusion"],
            align=inf["simple_align"],
            name="two_pole_tangent",
        )
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        simple_result = dai.run(sample.rgb, sid, simple_cfg)
        two_pole = simple_result["pred"]
        torch.cuda.synchronize()
        wall["two_pole_tangent_s"] = time.perf_counter() - t0

        torch.cuda.synchronize()
        t0 = time.perf_counter()
        raw = predict_tangent_raw(
            model, sample.rgb, planes, batch_size=int(inf["batch_size"])
        )
        full_sphere, align_info = mono360_fuse(
            raw,
            planes,
            sample.rgb.shape[0],
            sample.rgb.shape[1],
            iters=int(mono["lbfgs_iters"]),
            max_samples=int(mono["max_overlap_samples"]),
            sample_frac=float(mono["sample_fraction"]),
            seed=int(cfg.get("seed", 0)) + i,
        )
        torch.cuda.synchronize()
        wall["mono360_20view_s"] = time.perf_counter() - t0

        predictions = {
            "baseline": baseline,
            "two_pole_tangent": two_pole,
            "mono360_20view": full_sphere,
        }
        for protocol in protocols:
            per_scene[sid][protocol] = {}
            for method, prediction in predictions.items():
                metrics = evaluate_one(
                    prediction, sample, model, protocol=protocol,
                    align=ev["alignment"], min_depth=min_depth, max_depth=max_depth,
                )
                per_scene[sid][protocol][method] = metrics
                for band, metric_values in metrics.items():
                    rows.append({
                        "scene": sid,
                        "cluster": groups[sid],
                        "protocol": protocol,
                        "method": method,
                        "band": band,
                        **metric_values,
                    })

        runtime_rows[sid] = {
            **wall,
            "baseline_views": 1,
            "two_pole_views": int(simple_result["model_calls"]),
            "mono360_views": 20,
            "mono360_alignment_energy": align_info["alignment_energy"],
        }
        dai.clear_cache()
        torch.cuda.empty_cache()
        if (i + 1) % 5 == 0 or i + 1 == len(dataset):
            print(
                f"[{i + 1:>3}/{len(dataset)}] {sid} | "
                f"20-view={wall['mono360_20view_s']:.1f}s",
                flush=True,
            )

    methods = ("baseline", "two_pole_tangent", "mono360_20view")
    bands = ("all", "60-75", "75-90")
    summary: dict = {}
    paired: dict = {}
    for protocol in protocols:
        summary[protocol] = {}
        for method in methods:
            summary[protocol][method] = {
                band: summarize([
                    per_scene[sid][protocol][method][band]["abs_rel"]
                    for sid in per_scene
                ])
                for band in bands
            }
        paired[protocol] = {}
        for band in bands:
            maps = {
                method: {
                    sid: per_scene[sid][protocol][method][band]["abs_rel"]
                    for sid in per_scene
                }
                for method in methods
            }
            paired[protocol][band] = {
                "two_pole_vs_baseline": paired_cluster_bootstrap_gain(
                    maps["baseline"], maps["two_pole_tangent"], groups,
                    n_boot=n_boot, seed=int(cfg["seed"]) + 1,
                ),
                "20_view_vs_baseline": paired_cluster_bootstrap_gain(
                    maps["baseline"], maps["mono360_20view"], groups,
                    n_boot=n_boot, seed=int(cfg["seed"]) + 2,
                ),
                "20_view_vs_two_pole": paired_cluster_bootstrap_gain(
                    maps["two_pole_tangent"], maps["mono360_20view"], groups,
                    n_boot=n_boot, seed=int(cfg["seed"]) + 3,
                ),
            }

    with (out / "per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    runtime_values = {
        key: [runtime_rows[sid][key] for sid in runtime_rows]
        for key in ("baseline_s", "two_pole_tangent_s", "mono360_20view_s")
    }
    sample_ids = sorted(int(re.fullmatch(r"panorama_(\d+)", sid).group(1)) for sid in per_scene)
    try:
        manifest_location = manifest.relative_to(ROOT).as_posix()
    except ValueError:
        manifest_location = manifest.name
    config_record = dict(cfg)
    config_record.pop("_config_path", None)
    config_record["model"] = dict(cfg["model"], weights="<MIDAS_WEIGHTS>")
    config_record["dataset"] = dict(cfg["dataset"], root="<DAP_SELECTED_ROOT>",
                                    manifest=manifest_location)
    metadata = {
        "experiment": "07_real_nyc_20view",
        "model": model.describe(),
        "environment": environment_info(),
        "n_scenes": len(dataset),
        "n_clusters": len(cluster_sizes),
        "cluster_definition": "floor(numeric panorama ID / 20); two sampled frames per cluster",
        "pilot_only": args.limit is not None,
        "manifest": manifest_location,
        "manifest_sha256": sha256(manifest),
        "sampling_note": "IDs 0..74 excluded to avoid overlap with earlier 75-frame NYC run.",
        "evaluation": {
            "protocols": protocols,
            "alignment": ev["alignment"],
            "min_depth_m": min_depth,
            "max_depth_m": max_depth,
            "bootstrap_replicates": n_boot,
        },
        "config": config_record,
        "sample_ids": sample_ids,
        "summary": summary,
        "paired_cluster_bootstrap_gain": paired,
        "runtime_seconds": {key: summarize(value) for key, value in runtime_values.items()},
        "median_model_views_per_panorama": {
            "baseline": 1,
            "two_pole_tangent": float(np.median([
                runtime_rows[sid]["two_pole_views"] for sid in runtime_rows
            ])),
            "mono360_20view": 20,
        },
        "peak_cuda_memory_gb": float(torch.cuda.max_memory_allocated() / (1024 ** 3)),
        "per_scene_runtime": runtime_rows,
    }
    save_json(out / "summary.json", metadata)

    lines = [
        "# Experiment 07: Real NYC transfer: two-pole vs 20-view inference",
        "",
        f"- Scenes: **{len(dataset)}**; assumed 20-ID clusters: **{len(cluster_sizes)}**.",
        f"- Model: frozen **{model.name}**; evaluation grid: 512 x 1024.",
        f"- GT range: {min_depth:g}–{max_depth:g} m; both alignment protocols reported.",
        f"- Pilot only: **{args.limit is not None}**. Pilot intervals must not be treated as evaluation evidence.",
        "- IDs 0–74 are excluded because they were used in an earlier NYC run.",
        "- The 20-ID cluster is an assumed grouping, not a verified route/session identifier.",
        "",
        "Positive bootstrap gain means the candidate has lower AbsRel than its reference.",
        "The direct 20-view vs two-pole comparison is paired by scene and bootstrapped by 20-ID cluster.",
        "",
    ]
    for protocol in protocols:
        lines += [
            f"## {protocol}",
            "",
            "| Method | All median AbsRel | 60–75° median | 75–90° median | Views / image |",
            "|---|---:|---:|---:|---:|",
        ]
        for method in methods:
            q = summary[protocol][method]
            views = (
                1 if method == "baseline" else
                int(round(metadata["median_model_views_per_panorama"][method]))
            )
            lines.append(
                f"| {method} | {q['all']['median']:.4f} | "
                f"{q['60-75']['median']:.4f} | {q['75-90']['median']:.4f} | {views} |"
            )
        lines += [
            "",
            "### Paired cluster-bootstrap gains",
            "",
            "| Band | Comparison | Median gain | 95% CI |",
            "|---|---|---:|---:|",
        ]
        for band in bands:
            for name, result in paired[protocol][band].items():
                lo, hi = result["ci95"]
                lines.append(
                    f"| {band} | {name.replace('_', ' ')} | "
                    f"{100 * result['median_cluster_gain']:+.2f}% | "
                    f"[{100 * lo:+.2f}%, {100 * hi:+.2f}%] |"
                )
        lines.append("")
    lines += [
        "## Runtime",
        "",
        "| Method | Median seconds / panorama |",
        "|---|---:|",
    ]
    for key, label in (
        ("baseline_s", "Baseline"),
        ("two_pole_tangent_s", "Two-pole tangent"),
        ("mono360_20view_s", "20-view"),
    ):
        lines.append(f"| {label} | {metadata['runtime_seconds'][key]['median']:.2f} |")
    lines += [
        "",
        "## Interpretation guardrails",
        "",
        "- Do not tune FOV, padding, alignment or fusion on this evaluation subset.",
        "- A 20-view win is supported only when the direct paired 20-view-vs-two-pole interval excludes zero.",
        "- If the interval includes zero, prefer the lower-call method unless another prespecified metric supports the cost.",
        "- Do not interpret the 20-ID blocks as verified routes; they are an assumed grouping.",
        "- This is a held-out frame subset relative to an earlier 75-frame run, not a new dataset release.",
        "",
    ]
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved run: {out}", flush=True)
    print(f"Report: {out / 'REPORT.md'}", flush=True)


if __name__ == "__main__":
    main()