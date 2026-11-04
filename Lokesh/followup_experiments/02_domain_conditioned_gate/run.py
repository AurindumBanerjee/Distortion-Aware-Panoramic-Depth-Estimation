#!/usr/bin/env python3
"""Leave-one-environment-out calibration of distortion-aware rotation gates on PanoX."""
from __future__ import annotations
import argparse, csv, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import numpy as np
import torch
from common import (environment_info, load_config, load_dataset, load_model, prepare_output,
                    save_json, scene_group, evaluate_one)
from inference.pipeline import DistortionAwareInference, MethodConfig


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
        raise SystemExit("CUDA required; enable Kaggle T4 accelerator.")
    model = load_model(cfg["model"])
    ds = load_dataset(cfg["dataset"], limit=a.limit)
    out = prepare_output(Path(a.output_dir or cfg["output_dir"]) /
                         ("run_" + time.strftime("%Y%m%d_%H%M%S")), a.overwrite)
    inf, ev = cfg["inference"], cfg["evaluation"]
    thresholds = [int(x) for x in inf["candidate_thresholds"]]
    protocol, align = ev.get("protocol", "align-all"), ev.get("alignment", "scale")
    lo, hi = float(ev["min_depth"]), float(ev["max_depth"])
    band = cfg.get("gate", {}).get("score_band", "75-90")
    dai = DistortionAwareInference(model, batch_size=int(inf.get("batch_size", 4)), use_cache=True)
    records, groups = {}, {}
    print("Model:", model.describe(), "| scenes:", len(ds), "| candidate gates:", thresholds)
    for i, sample in enumerate(ds):
        sid, group = sample.id, scene_group(sample.id)
        groups[sid] = group
        base = dai.run(sample.rgb, sid, MethodConfig(method="baseline", name="baseline"))["pred"]
        bm = evaluate_one(base, sample, model, protocol=protocol, align=align,
                          min_depth=lo, max_depth=hi)
        rec = {"environment": group, "baseline": bm[band]["abs_rel"], "thresholds": {}}
        for thr in thresholds:
            mc = MethodConfig(
                method="rotation", lat_threshold=thr,
                rotations=[list(map(float, x)) for x in inf["rotations"]],
                fusion=inf.get("fusion", "cosine"), band=float(inf.get("band", 20)),
                power=float(inf.get("power", 2)), align=inf.get("align_views", "scale"),
                name=f"rotation_t{thr}",
            )
            pred = dai.run(sample.rgb, sid, mc)["pred"]
            m = evaluate_one(pred, sample, model, protocol=protocol, align=align,
                             min_depth=lo, max_depth=hi)
            rec["thresholds"][str(thr)] = m[band]["abs_rel"]
        records[sid] = rec
        dai.clear_cache()
        if (i + 1) % 10 == 0 or i + 1 == len(ds):
            print(f"[{i+1}/{len(ds)}] {sid} ({group})")

    envs = sorted(set(groups.values()))
    if len(envs) < 3:
        raise RuntimeError(f"Need at least 3 independent environment groups for LOEO, found: {envs}")
    min_gain = float(cfg.get("gate", {}).get("minimum_calibration_gain", 0.005))
    folds, scene_rows = [], []
    for heldout in envs:
        train_envs = [e for e in envs if e != heldout]
        train = [r for sid, r in records.items() if r["environment"] in train_envs]
        held = [(sid, r) for sid, r in records.items() if r["environment"] == heldout]
        train_gain = {}
        for thr in thresholds:
            gains = [(r["baseline"] - r["thresholds"][str(thr)]) / max(r["baseline"], 1e-8) for r in train]
            train_gain[str(thr)] = float(np.nanmedian(gains))
        selected = max(thresholds, key=lambda t: train_gain[str(t)])
        use_baseline = train_gain[str(selected)] < min_gain
        selected_label = "baseline" if use_baseline else str(selected)
        fixed_thr = min(thresholds, key=lambda t: abs(t - 45))
        for sid, r in held:
            sel = r["baseline"] if use_baseline else r["thresholds"][str(selected)]
            fixed = r["thresholds"][str(fixed_thr)]
            oracle_thr = min(thresholds, key=lambda t: r["thresholds"][str(t)])
            oracle = r["thresholds"][str(oracle_thr)]
            scene_rows.append({
                "scene": sid, "heldout_environment": heldout, "selected_gate": selected_label,
                "baseline_absrel": r["baseline"], "loeo_absrel": sel,
                "fixed_45_absrel": fixed, "oracle_absrel": oracle,
                "oracle_threshold": oracle_thr,
            })
        folds.append({"heldout_environment": heldout, "train_environments": train_envs,
                      "training_median_gain_by_threshold": train_gain,
                      "selected_threshold": selected_label, "minimum_gain": min_gain,
                      "n_heldout_scenes": len(held)})

    def summarize(rows, key):
        b = np.asarray([r["baseline_absrel"] for r in rows], dtype=float)
        x = np.asarray([r[key] for r in rows], dtype=float)
        ok = np.isfinite(b) & np.isfinite(x) & (b > 0)
        gain = (b[ok] - x[ok]) / b[ok]
        return {"mean_absrel": float(np.mean(x[ok])), "median_absrel": float(np.median(x[ok])),
                "median_relative_gain_vs_baseline": float(np.median(gain)),
                "scenes": int(ok.sum())}
    aggregate = {k: summarize(scene_rows, k) for k in
                 ("loeo_absrel", "fixed_45_absrel", "oracle_absrel")}
    with (out / "loeo_per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(scene_rows[0])); w.writeheader(); w.writerows(scene_rows)
    save_json(out / "folds.json", folds)
    save_json(out / "per_scene_candidates.json", records)
    save_json(out / "summary.json", {"experiment": "02_domain_conditioned_gate",
              "model": model.describe(), "environment": environment_info(), "n_environments": len(envs),
              "folds": folds, "aggregate": aggregate})
    lines = ["# Experiment 2 — Leave-one-environment-out domain gate", "",
             f"- Independent PanoX environments: {len(envs)}",
             f"- Candidate thresholds: {thresholds}",
             f"- Gate fallback: baseline when best calibration gain < {min_gain:.2%}", "",
             "| Strategy | Mean AbsRel | Median AbsRel | Median relative gain |",
             "|---|---:|---:|---:|"]
    for k, label in [("loeo_absrel", "LOEO-selected gate"), ("fixed_45_absrel", "Fixed 45° gate"),
                     ("oracle_absrel", "Per-environment oracle (upper bound)")]:
        q = aggregate[k]
        lines.append(f"| {label} | {q['mean_absrel']:.4f} | {q['median_absrel']:.4f} | {q['median_relative_gain_vs_baseline']:+.2%} |")
    lines += ["", "## Fold decisions", "", "| Held-out environment | Selected threshold | Train environments |",
              "|---|---:|---|"]
    for f in folds:
        lines.append(f"| {f['heldout_environment']} | {f['selected_threshold']} | {', '.join(f['train_environments'])} |")
    lines += ["", "Oracle is diagnostic only and never used as a deployable gate. All frames from one environment",
              "remain in the same fold; no frame-level random split is used.", ""]
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved", out / "REPORT.md")


if __name__ == "__main__":
    main()
