#!/usr/bin/env python3
"""Evaluate the structure-at-the-poles gate (see gate.py, README.md).

Compares three strategies on the same scenes/model/protocol used by
experiments 01/02/04: always apply the two-pole rotation correction, never
apply it, and apply it only where gate.should_correct() says the cap has
real structure to correct. Composition is done per-pixel using the same
polar-cap row slices the gate itself scores, so "gated" is a hard swap
between the fully-corrected and fully-baseline prediction within each cap --
no soft fusion band, to keep the comparison to gate.py's binary decision
honest (the existing cosine-fusion band in inference/pipeline.py is a
different, already-tested mechanism; see experiment 04).

NOTE: this is the first pass described in README.md's "What would make this
a real result" -- a pooled always/never/gated comparison, not yet the LOEO
transfer test. Run this first to sanity-check the gate and to produce a
calibration slice for gate.calibrate_thresholds(), then extend to LOEO the
same way run.py extended 02's pilot to the full environment split.
"""
from __future__ import annotations
import argparse, csv, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
sys.path.insert(0, str(HERE))
import numpy as np
import torch
from common import (environment_info, load_config, load_dataset, load_model, prepare_output,
                    save_json, scene_group, evaluate_one)
from inference.pipeline import DistortionAwareInference, MethodConfig
from gate import compute_cap_scores, should_correct, _cap_slice


def _as_disparity(raw: np.ndarray, model) -> np.ndarray:
    """Gate heuristics assume higher value = nearer camera (disparity convention).
    Converts depth-space model output to a pseudo-disparity for scoring only;
    the actual predictions used for evaluation are untouched."""
    if model.spec.space == "depth":
        return 1.0 / np.clip(raw, 1e-3, None)
    return raw


def _normalize_rgb(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=np.float64)
    return rgb / 255.0 if rgb.max() > 1.5 else rgb


def compose_gated(baseline_pred: np.ndarray, corrected_pred: np.ndarray, scores: dict) -> np.ndarray:
    h = baseline_pred.shape[0]
    out = baseline_pred.copy()
    for pole in ("north", "south"):
        if should_correct(scores[pole]):
            sl = _cap_slice(h, 75.0, 90.0, pole)
            out[sl] = corrected_pred[sl]
    return out


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
    ds = load_dataset(cfg["dataset"], limit=a.limit)
    model = load_model(cfg["model"])
    out = prepare_output(Path(a.output_dir or cfg["output_dir"]) /
                         ("run_" + time.strftime("%Y%m%d_%H%M%S")), a.overwrite)
    inf, ev = cfg["inference"], cfg["evaluation"]
    protocol, align = ev.get("protocol", "align-all"), ev.get("alignment", "scale")
    lo, hi = float(ev["min_depth"]), float(ev["max_depth"])
    lat_lo, lat_hi = cfg.get("gate", {}).get("score_band", [75, 90])

    dai = DistortionAwareInference(model, batch_size=int(inf.get("batch_size", 4)), use_cache=True)
    rotation_cfg = MethodConfig(
        method="rotation", lat_threshold=45.0,
        rotations=[list(map(float, x)) for x in inf["rotations"]],
        fusion=inf.get("fusion", "cosine"), band=float(inf.get("band", 20)),
        power=float(inf.get("power", 2)), align=inf.get("align_views", "scale"),
        name="rotation_fixed45",
    )

    print("Model:", model.describe(), "| scenes:", len(ds))
    scene_rows, gate_log = [], []
    for i, sample in enumerate(ds):
        sid, group = sample.id, scene_group(sample.id)
        base = dai.run(sample.rgb, sid, MethodConfig(method="baseline", name="baseline"))
        corr = dai.run(sample.rgb, sid, rotation_cfg)

        disp_for_scoring = _as_disparity(base["baseline"], model)
        valid = sample.valid if hasattr(sample, "valid") else np.isfinite(disp_for_scoring)
        scores = compute_cap_scores(_normalize_rgb(sample.rgb), disp_for_scoring, valid,
                                    lat_lo=float(lat_lo), lat_hi=float(lat_hi))
        gated_pred = compose_gated(base["pred"], corr["pred"], scores)

        bm = evaluate_one(base["pred"], sample, model, protocol=protocol, align=align, min_depth=lo, max_depth=hi)
        cm = evaluate_one(corr["pred"], sample, model, protocol=protocol, align=align, min_depth=lo, max_depth=hi)
        gm = evaluate_one(gated_pred, sample, model, protocol=protocol, align=align, min_depth=lo, max_depth=hi)

        row = {"scene": sid, "environment": group}
        for band in ("all", "60-75", "75-90"):
            row[f"baseline_{band}"] = bm[band]["abs_rel"]
            row[f"always_correct_{band}"] = cm[band]["abs_rel"]
            row[f"gated_{band}"] = gm[band]["abs_rel"]
        row["north_applied"] = should_correct(scores["north"])
        row["south_applied"] = should_correct(scores["south"])
        scene_rows.append(row)
        gate_log.append({"scene": sid, "north": scores["north"].as_dict(), "south": scores["south"].as_dict()})
        dai.clear_cache()
        if (i + 1) % 10 == 0 or i + 1 == len(ds):
            print(f"[{i+1}/{len(ds)}] {sid} ({group}) "
                 f"gate N={row['north_applied']} S={row['south_applied']}")

    def summarize(key):
        vals = np.asarray([r[key] for r in scene_rows], dtype=float)
        vals = vals[np.isfinite(vals)]
        return float(np.median(vals)), float(np.mean(vals))

    bands = ("all", "60-75", "75-90")
    aggregate = {}
    for band in bands:
        b_med, b_mean = summarize(f"baseline_{band}")
        c_med, c_mean = summarize(f"always_correct_{band}")
        g_med, g_mean = summarize(f"gated_{band}")
        aggregate[band] = {
            "baseline": {"median": b_med, "mean": b_mean},
            "always_correct": {"median": c_med, "mean": c_mean,
                               "median_gain_vs_baseline": (b_med - c_med) / b_med},
            "gated": {"median": g_med, "mean": g_mean,
                     "median_gain_vs_baseline": (b_med - g_med) / b_med,
                     "median_gain_vs_always_correct": (c_med - g_med) / c_med},
        }
    frac_applied = {
        "north": float(np.mean([r["north_applied"] for r in scene_rows])),
        "south": float(np.mean([r["south_applied"] for r in scene_rows])),
    }

    with (out / "per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(scene_rows[0])); w.writeheader(); w.writerows(scene_rows)
    save_json(out / "gate_scores.json", gate_log)
    save_json(out / "summary.json", {"experiment": "06_structure_at_poles_gate",
              "model": model.describe(), "environment": environment_info(),
              "n_scenes": len(scene_rows), "aggregate": aggregate, "fraction_gate_applied": frac_applied})

    lines = ["# Experiment 6 — Structure-at-the-poles gate", "",
             f"- Scenes: {len(scene_rows)}",
             f"- Gate applied (correction used) on north cap: {frac_applied['north']:.1%} of scenes",
             f"- Gate applied (correction used) on south cap: {frac_applied['south']:.1%} of scenes", "",
             "| band | baseline | always-correct | gated | gated vs baseline | gated vs always-correct |",
             "|---|---:|---:|---:|---:|---:|"]
    for band in bands:
        a = aggregate[band]
        lines.append(f"| {band} | {a['baseline']['median']:.4f} | {a['always_correct']['median']:.4f} | "
                     f"{a['gated']['median']:.4f} | {a['gated']['median_gain_vs_baseline']:+.2%} | "
                     f"{a['gated']['median_gain_vs_always_correct']:+.2%} |")
    lines += ["", "`gated vs baseline` > 0 means the gate beats doing nothing; `gated vs always-correct` > 0",
             "means being selective beats blindly correcting every scene (the failure mode experiment 02",
             "exposed for Mountain_Environment_Set / ClothingStore). Per-scene gate scores are in",
             "gate_scores.json for calibrating gate.py's thresholds before a LOEO-style follow-up.", ""]
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved", out / "REPORT.md")


if __name__ == "__main__":
    main()
