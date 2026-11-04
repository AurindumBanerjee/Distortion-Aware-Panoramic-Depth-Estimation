#!/usr/bin/env python3
"""Compare 20-view icosahedral 360MonoDepth-style inference with two polar tangent views."""
from __future__ import annotations
import argparse, csv, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import numpy as np
import torch
from common import (environment_info, evaluate_one, load_config, load_dataset, load_model,
                    prepare_output, save_json, scene_group, cluster_bootstrap_gain)
from inference.pipeline import DistortionAwareInference, MethodConfig
from inference.tangent_inference import predict_tangent_raw
from mono360 import icosahedron_planes, mono360_fuse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config.yaml"))
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--output-dir")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    cfg = load_config(a.config, a.set)
    if not torch.cuda.is_available():
        raise SystemExit("CUDA required.")
    model, ds = load_model(cfg["model"]), load_dataset(cfg["dataset"], limit=a.limit)
    out = prepare_output(Path(a.output_dir or cfg["output_dir"]) /
                         ("run_" + time.strftime("%Y%m%d_%H%M%S")), a.overwrite)
    inf, mono, ev = cfg["inference"], cfg["mono360"], cfg["evaluation"]
    size = int(inf["tangent_size"])
    planes = icosahedron_planes(size=size, padding=float(inf["padding"]))
    if model.spec.space != "disparity":
        raise SystemExit("The current mono360 implementation is defined for disparity models.")
    dai = DistortionAwareInference(model, batch_size=int(inf["batch_size"]), use_cache=True)
    protocols = ev.get("protocols", ["align-all", "align-equatorial"])
    lo, hi = float(ev["min_depth"]), float(ev["max_depth"])
    rows, per_scene, groups = [], {}, {}
    print(f"20-view planes: {len(planes)}; scenes: {len(ds)}; model: {model.name}")
    for i, s in enumerate(ds):
        groups[s.id] = scene_group(s.id)
        base = dai.run(s.rgb, s.id, MethodConfig(method="baseline", name="baseline"))["pred"]
        simple_mc = MethodConfig(method="tangent", lat_threshold=float(inf["polar_threshold"]),
                                 views_per_pole=int(inf["simple_views_per_pole"]),
                                 tangent_size=size, fusion=inf["simple_fusion"],
                                 align=inf["simple_align"], name="two_pole_tangent")
        simple = dai.run(s.rgb, s.id, simple_mc)
        t0 = time.perf_counter()
        raw = predict_tangent_raw(model, s.rgb, planes, batch_size=int(inf["batch_size"]))
        fused, align_info = mono360_fuse(
            raw, planes, s.rgb.shape[0], s.rgb.shape[1],
            iters=int(mono["lbfgs_iters"]), max_samples=int(mono["max_overlap_samples"]),
            sample_frac=float(mono["sample_fraction"]), seed=int(cfg.get("seed", 0)) + i,
        )
        mono_runtime = time.perf_counter() - t0
        per_scene[s.id] = {}
        preds = {"baseline": base, "two_pole_tangent": simple["pred"], "mono360_20view": fused}
        for proto in protocols:
            per_scene[s.id][proto] = {}
            for name, pred in preds.items():
                metrics = evaluate_one(pred, s, model, protocol=proto, align=ev["alignment"],
                                       min_depth=lo, max_depth=hi)
                per_scene[s.id][proto][name] = metrics
                for band, q in metrics.items():
                    rows.append({"scene": s.id, "environment": groups[s.id], "protocol": proto,
                                 "method": name, "band": band, **q})
        per_scene[s.id]["runtime"] = {
            "baseline_calls": 1, "two_pole_total_calls": int(simple["model_calls"]),
            "mono360_calls": 20, "mono360_alignment_runtime_s": float(mono_runtime),
            "mono360_alignment_energy": align_info["alignment_energy"],
        }
        dai.clear_cache()
        if (i + 1) % 5 == 0 or i + 1 == len(ds):
            print(f"[{i+1}/{len(ds)}] {s.id}; mono360 solve {mono_runtime:.1f}s")

    bands = ["all", "60-75", "75-90"]
    summary, paired = {}, {}
    for proto in protocols:
        summary[proto], paired[proto] = {}, {}
        for method in ("baseline", "two_pole_tangent", "mono360_20view"):
            summary[proto][method] = {}
            for band in bands:
                vals = [per_scene[s][proto][method][band]["abs_rel"] for s in per_scene]
                summary[proto][method][band] = {"mean": float(np.nanmean(vals)), "median": float(np.nanmedian(vals))}
        paired[proto] = {}
        for method in ("two_pole_tangent", "mono360_20view"):
            paired[proto][method] = {}
            for band in bands:
                b = {s: per_scene[s][proto]["baseline"][band]["abs_rel"] for s in per_scene}
                x = {s: per_scene[s][proto][method][band]["abs_rel"] for s in per_scene}
                paired[proto][method][band] = cluster_bootstrap_gain(b, x, groups, seed=int(cfg.get("seed", 0)))
    with (out / "per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    save_json(out / "summary.json", {"experiment": "04_mono360_20view", "model": model.describe(),
              "environment": environment_info(), "n_scenes": len(ds), "summary": summary,
              "paired_cluster_bootstrap_vs_baseline": paired, "per_scene_runtime": {s: per_scene[s]["runtime"] for s in per_scene}})
    lines = ["# Experiment 4 — 20-view full-sphere inference", "",
             "The 20-view system uses icosahedral tangent views, per-view disparity standardisation,",
             "deformable scale/offset alignment over overlapping views, and frustum blending.",
             "It is compared against the baseline and the existing two-pole tangent correction.", ""]
    for proto in protocols:
        lines += [f"## {proto}", "", "| method | global median AbsRel | 60–75° median | 75–90° median | calls/image |",
                  "|---|---:|---:|---:|---:|"]
        for name in ("baseline", "two_pole_tangent", "mono360_20view"):
            calls = 1 if name == "baseline" else (int(np.median([per_scene[s]["runtime"]["two_pole_total_calls"] for s in per_scene]))
                                                  if name == "two_pole_tangent" else 20)
            q = summary[proto][name]
            lines.append(f"| {name} | {q['all']['median']:.4f} | {q['60-75']['median']:.4f} | {q['75-90']['median']:.4f} | {calls} |")
        lines.append("")
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved", out / "REPORT.md")


if __name__ == "__main__":
    main()
