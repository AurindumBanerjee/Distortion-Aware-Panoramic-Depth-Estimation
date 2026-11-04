#!/usr/bin/env python3
"""FOV x tangent-resolution sweep for polar tangent correction (DAC-motivated)."""
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
from geometry.spherical import latitude_map


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
    model = load_model(cfg["model"])
    if model.spec.space != "disparity":
        raise SystemExit("FOV sweep currently expects an affine-disparity perspective model.")
    ds = load_dataset(cfg["dataset"], limit=a.limit)
    out = prepare_output(Path(a.output_dir or cfg["output_dir"]) /
                         ("run_" + time.strftime("%Y%m%d_%H%M%S")), a.overwrite)
    inf, ev = cfg["inference"], cfg["evaluation"]
    combos = [(int(f), int(n)) for f in inf["fov_degrees"] for n in inf["tangent_resolutions"]]
    dai = DistortionAwareInference(model, batch_size=int(inf["batch_size"]), use_cache=True)
    protocols = ev.get("protocols", ["align-all", "align-equatorial"])
    lo, hi = float(ev["min_depth"]), float(ev["max_depth"])
    rows, per_scene, groups = [], {}, {}
    labels = [f"fov{f}_size{n}" for f, n in combos]
    print(f"{len(combos)} configurations x {len(ds)} panoramas")
    for i, s in enumerate(ds):
        groups[s.id] = scene_group(s.id)
        base = dai.run(s.rgb, s.id, MethodConfig(method="baseline", name="baseline"))["pred"]
        per_scene[s.id] = {}
        for (fov, size), label in zip(combos, labels):
            mc = MethodConfig(
                method="tangent", lat_threshold=float(inf["polar_threshold"]),
                views_per_pole=int(inf["views_per_pole"]), tangent_fov=float(fov),
                tangent_size=int(size), fusion=inf["fusion"], band=float(inf["band"]),
                power=float(inf["power"]), align=inf["align"], name=label,
            )
            result = dai.run(s.rgb, s.id, mc)
            pred = result["pred"]
            polar = np.abs(latitude_map(*s.valid.shape)) >= 60
            cover = result.get("corrected_valid")
            coverage = float((cover & polar & s.valid).sum() / max(1, (polar & s.valid).sum())) if cover is not None else 0.0
            per_scene[s.id][label] = {"coverage_60_90": coverage, "runtime_s": result["runtime_s"],
                                       "model_calls": result["model_calls"], "metrics": {}}
            for proto in protocols:
                m = evaluate_one(pred, s, model, protocol=proto, align=inf["align"],
                                 min_depth=lo, max_depth=hi)
                per_scene[s.id][label]["metrics"][proto] = m
                for band, q in m.items():
                    rows.append({"scene": s.id, "environment": groups[s.id], "config": label,
                                 "fov_deg": fov, "tangent_size": size, "protocol": proto,
                                 "band": band, "coverage_60_90": coverage,
                                 "runtime_s": result["runtime_s"], "model_calls": result["model_calls"], **q})
        for proto in protocols:
            b = evaluate_one(base, s, model, protocol=proto, align=inf["align"], min_depth=lo, max_depth=hi)
            per_scene[s.id]["baseline"] = per_scene[s.id].get("baseline", {})
            per_scene[s.id]["baseline"][proto] = b
            for band, q in b.items():
                rows.append({"scene": s.id, "environment": groups[s.id], "config": "baseline",
                             "fov_deg": 0, "tangent_size": 0, "protocol": proto,
                             "band": band, "coverage_60_90": 0.0, "runtime_s": 0.0,
                             "model_calls": 1, **q})
        dai.clear_cache()
        if (i + 1) % 5 == 0 or i + 1 == len(ds):
            print(f"[{i+1}/{len(ds)}] {s.id}")

    bands = ["all", "60-75", "75-90"]
    summary, paired = {}, {}
    for proto in protocols:
        summary[proto], paired[proto] = {}, {}
        for label in ["baseline"] + labels:
            summary[proto][label] = {}
            for band in bands:
                if label == "baseline":
                    vals = [per_scene[s]["baseline"][proto][band]["abs_rel"] for s in per_scene]
                else:
                    vals = [per_scene[s][label]["metrics"][proto][band]["abs_rel"] for s in per_scene]
                summary[proto][label][band] = {"mean": float(np.nanmean(vals)), "median": float(np.nanmedian(vals))}
        paired[proto] = {}
        for label in labels:
            paired[proto][label] = {}
            for band in bands:
                b = {s: per_scene[s]["baseline"][proto][band]["abs_rel"] for s in per_scene}
                x = {s: per_scene[s][label]["metrics"][proto][band]["abs_rel"] for s in per_scene}
                paired[proto][label][band] = cluster_bootstrap_gain(b, x, groups, seed=int(cfg.get("seed", 0)))
    with (out / "per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    save_json(out / "summary.json", {"experiment": "05_fov_resolution_sweep", "model": model.describe(),
              "environment": environment_info(), "n_scenes": len(ds), "configs": combos,
              "summary": summary, "paired_cluster_bootstrap_vs_baseline": paired})
    lines = ["# Experiment 5 — FOV and tangent resolution sweep", "",
             "This probes how view geometry and sampling density affect inference-time polar correction.",
             "It is DAC-motivated, but uses the current MiDaS perspective wrapper; it is not a DAC model reproduction.", ""]
    for proto in protocols:
        lines += [f"## {proto}", "", "| config | FOV | size | median AbsRel (75–90°) | polar coverage | calls/image |",
                  "|---|---:|---:|---:|---:|---:|"]
        for label, (fov, size) in zip(labels, combos):
            vals = [per_scene[s][label]["coverage_60_90"] for s in per_scene]
            calls = [per_scene[s][label]["model_calls"] for s in per_scene]
            ar = summary[proto][label]["75-90"]["median"]
            lines.append(f"| {label} | {fov}° | {size}² | {ar:.4f} | {np.mean(vals):.1%} | {np.median(calls):.0f} |")
        lines.append("")
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved", out / "REPORT.md")


if __name__ == "__main__":
    main()
