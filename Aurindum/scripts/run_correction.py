#!/usr/bin/env python3
"""End-to-end test of the capture-aware correction front end (distortions/correction.py) on a real model.

For every frame and scenario, the degraded panorama goes through correct() exactly as it would in deployment: cap
occlusions are DETECTED from the image (not taken from the simulator), tilt and shake come as sensor metadata, JPEG
as a file flag. The policy is the leave-one-dataset-out one: chosen from results/study_<model>_*.json WITHOUT the
dataset being tested (--model_key / --dataset_key), so this is a held-out test.

  python scripts/run_correction.py --config 3_structured3d_benchmark/config_dap.yaml --tag dap_s3 \
      --model_key dap --dataset_key s3 --max_scenes 40
Writes results/correction_<tag>.json and results/CORRECTION_<tag>.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import ROOT, add_common_args, depth_range, load_config, load_dataset, load_model  # noqa: E402
from calibrate_correction import choose  # noqa: E402
from distortions.catalogue import CATALOGUE, jpeg_apply  # noqa: E402
from distortions.correction import CaptureMeta, cap_fault, correct, detect_caps  # noqa: E402
from distortion_study import score  # noqa: E402

FAULT = {d.key: d for d in CATALOGUE}
SCENARIOS = ["clean", "tilt", "nadir", "vfov", "yawblur", "jpeg", "nadir+jpeg"]


def heldout_policy(model_key: str, dataset_key: str, res: Path, min_gain=0.02, min_win=0.6):
    train = {}
    for p in sorted(res.glob(f"study_{model_key}_*.json")):
        ds = p.stem[len(f"study_{model_key}_"):]
        if ds != dataset_key and not ds.endswith("mini"):
            train[ds] = json.loads(p.read_text())["rows"]
    if not train:
        sys.exit(f"no study_{model_key}_<other dataset>.json in {res}: run the distortion study first")
    pol = {}
    for d in CATALOGUE:
        if d.mitigations:
            fix, _ = choose(train, d.key, min_gain, min_win)
            if fix != "none":
                pol[d.key] = fix
    return pol, sorted(train)


def degrade(rgb, scen, seed, depth):
    """Degraded image, metadata a real pipeline would have, simulator context (for scoring only)."""
    ctx = {"seed": seed, "depth": depth}
    if scen == "clean":
        return rgb, CaptureMeta(), ctx, None
    if scen == "nadir+jpeg":
        x, ctx = FAULT["nadir"].apply(rgb, ctx)
        x, _ = jpeg_apply(x, ctx)
        return x, CaptureMeta(flags={"jpeg"}), ctx, FAULT["nadir"]
    d = FAULT[scen]
    x, ctx = d.apply(rgb, ctx)
    meta = CaptureMeta()
    if scen == "tilt":
        meta.R = ctx["R"]
    elif scen == "yawblur":
        meta.kernel = ctx["kernel"]
    elif scen == "jpeg":
        meta.flags = {"jpeg"}
    return x, meta, ctx, d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(ap)
    ap.add_argument("--model_key", required=True, help="model part of the study tags: midas / dap / da360 / da2")
    ap.add_argument("--dataset_key", required=True, help="dataset part of the study tag held out from the policy")
    ap.set_defaults(split="all", max_scenes=40)
    a = ap.parse_args()
    res = ROOT / "results"
    policy, trained_on = heldout_policy(a.model_key, a.dataset_key, res)
    print("held-out policy:", policy, "chosen on", trained_on, flush=True)
    cfg = load_config(a.config, a.overrides)
    model = load_model(cfg)
    ds = load_dataset(cfg, a.split, a.max_scenes)
    min_d, max_d = depth_range(cfg)
    rows = []
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        H, W = gt.shape
        rec = {"id": smp.id}
        clean_pred = np.asarray(model.predict(smp.rgb, kind="erp"), dtype=np.float64)
        for scen in SCENARIOS:
            x, meta, ctx, d = degrade(smp.rgb, scen, i, np.where(valid, gt, 2.0))
            back = (lambda p: d.to_original(p, ctx)) if d is not None else (lambda p: p)
            region = d.region(H, W, ctx) if (d is not None and d.region) else None
            raw = clean_pred if scen == "clean" else np.asarray(model.predict(x, kind="erp"), dtype=np.float64)
            fixed, log = correct(model, x, meta, policy)
            s_clean, _ = score(clean_pred, gt, valid, model, region, min_d, max_d)
            s_raw, _ = score(back(raw), gt, valid, model, region, min_d, max_d)
            s_fix, _ = score(back(fixed), gt, valid, model, region, min_d, max_d)
            caps = detect_caps(x)
            rec[scen] = {"clean": s_clean, "raw": s_raw, "fixed": s_fix, "log": log, "detected": cap_fault(caps),
                         "caps": caps}
        rows.append(rec)
        print(f"[{i + 1}/{len(ds)}] {smp.id}: " + ", ".join(f"{s} {rec[s]['raw']['all']:.3f}->{rec[s]['fixed']['all']:.3f}"
                                                          for s in SCENARIOS), flush=True)

    expect = {"clean": None, "tilt": None, "yawblur": None, "jpeg": None, "nadir": "nadir", "vfov": "vfov", "nadir+jpeg": "nadir"}
    lines = [f"# Capture-aware correction, end to end: {a.tag}", "",
             f"model `{getattr(model, 'name', '?')}` · {len(rows)} frames · policy chosen on {', '.join(trained_on)} "
             f"(held out: {a.dataset_key}): `{json.dumps(policy)}`", "",
             "Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. "
             "Metric: AbsRel on the occluded region for cap faults, else the whole panorama.", "",
             "| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for scen in SCENARIOS:
        f = "region" if scen in ("nadir", "vfov", "nadir+jpeg") else "all"
        c = np.array([r[scen]["clean"][f] for r in rows])
        u = np.array([r[scen]["raw"][f] for r in rows])
        x = np.array([r[scen]["fixed"][f] for r in rows])
        ok = np.isfinite(c) & np.isfinite(u) & np.isfinite(x)
        c, u, x = c[ok], u[ok], x[ok]
        det = np.mean([r[scen]["detected"] == expect[scen] for r in rows])
        hurt = u - c >= 0.05 * c
        rec_s = f"{100 * np.median((u[hurt] - x[hurt]) / np.maximum(u[hurt] - c[hurt], 1e-6)):.0f}%" if hurt.any() else "n/a"
        lines.append(f"| {scen} | {100 * det:.0f}% | {np.median(c):.4f} | {np.median(u):.4f} | {np.median(x):.4f} | "
                     f"{100 * np.median((x - u) / u):+.1f}% | {100 * np.mean(x < u * 0.999):.0f}% | "
                     f"{100 * np.mean(x > u * 1.01):.0f}% | {rec_s} |")
    (res / f"correction_{a.tag}.json").write_text(json.dumps({"tag": a.tag, "policy": policy, "trained_on": trained_on,
                                                               "rows": rows}), encoding="utf-8")
    (res / f"CORRECTION_{a.tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
