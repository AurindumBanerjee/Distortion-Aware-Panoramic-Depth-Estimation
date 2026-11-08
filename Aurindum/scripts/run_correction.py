#!/usr/bin/env python3
"""End-to-end test of the capture-aware correction front end (distortions/correction.py) on a real model.

For every frame and scenario, the degraded panorama goes through correct() exactly as it would in deployment: cap
occlusions are DETECTED from the image (not taken from the simulator), tilt and shake come as sensor metadata, JPEG
as a file flag. The policy is the leave-one-dataset-out one: chosen from results/study_<model>_*.json WITHOUT the
dataset being tested (--model_key / --dataset_key), so this is a held-out test.

  python scripts/run_correction.py --config 3_structured3d_benchmark/config_dap.yaml --tag dap_s3 \
      --model_key dap --dataset_key s3 --max_scenes 40
Writes results/correction_<tag>.json and results/CORRECTION_<tag>.md (results/external/ for stanford / nyc, which are
never used to choose a fix: their policy comes from the four core datasets).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import ROOT, add_common_args, depth_range, load_config, load_dataset, load_model  # noqa: E402
from calibrate_correction import CORE_SETS, choose  # noqa: E402
from distortions.catalogue import CATALOGUE, jpeg_apply  # noqa: E402
from distortions.correction import CaptureMeta, cap_fault, correct, detect_caps  # noqa: E402
from distortion_study import save_examples, score  # noqa: E402

EXTERNAL_SETS = ("stanford", "nyc")
FAULT = {d.key: d for d in CATALOGUE}
SCENARIOS = ["clean", "tilt", "nadir", "vfov", "yawblur", "jpeg", "nadir+jpeg"]


def heldout_policy(model_key: str, dataset_key: str, res: Path, min_gain=0.02, min_win=0.6, sets=CORE_SETS):
    """Policy chosen on the core datasets other than dataset_key. External sets (stanford / nyc) are never training
    data, so an external run is a pure test of the policy learned on the core sets."""
    train = {}
    for ds in sets:
        p = res / f"study_{model_key}_{ds}.json"
        if ds != dataset_key and p.is_file():
            train[ds] = json.loads(p.read_text())["rows"]
    if not train:
        sys.exit(f"no study_{model_key}_<core dataset>.json in {res}: run the distortion study first")
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
    ap.add_argument("--examples", type=int, default=3, help="frames for which before / after images are saved")
    ap.add_argument("--order", default="photometric_first", choices=["photometric_first", "cap_first"],
                    help="with a photometric fix AND a cap fix: smooth first (default) or fill the caps first")
    ap.add_argument("--policy_mode", default="core", choices=["core", "all_loo"],
                    help="core (headline): fixes chosen on the other CORE sets only. all_loo: on every other set incl. stanford / nyc "
                         "(separate experiment, needs --out_dir)")
    ap.add_argument("--out_dir", default=None, help="output folder (default results/ or results/external/)")
    ap.set_defaults(split="all", max_scenes=40)
    a = ap.parse_args()
    res = ROOT / "results"
    # core datasets keep their results in results/; external ones (stanford / nyc) are kept apart in results/external/
    out = Path(a.out_dir) if a.out_dir else (res if a.dataset_key in CORE_SETS else res / "external")
    if a.policy_mode != "core" and not a.out_dir:
        sys.exit("--policy_mode all_loo writes a separate experiment: give --out_dir so the headline results are not overwritten")
    out.mkdir(parents=True, exist_ok=True)
    policy, trained_on = heldout_policy(a.model_key, a.dataset_key, res, sets=CORE_SETS if a.policy_mode == "core" else CORE_SETS + EXTERNAL_SETS)
    print("held-out policy:", policy, "chosen on", trained_on, flush=True)
    cfg = load_config(a.config, a.overrides)
    model = load_model(cfg)
    ds = load_dataset(cfg, a.split, a.max_scenes)
    min_d, max_d = depth_range(cfg)
    rows, examples = [], {}
    img_dir = out / f"correction_{a.tag}_img"
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        H, W = gt.shape
        rec = {"id": smp.id}
        clean_pred = np.asarray(model.predict(smp.rgb, kind="erp"), dtype=np.float64)
        ex = i < a.examples
        imgs = {"rgb": smp.rgb} if ex else {}
        err = lambda al: np.abs(al - gt) / np.where(gt > 0, gt, 1)
        for scen in SCENARIOS:
            x, meta, ctx, d = degrade(smp.rgb, scen, i, np.where(valid, gt, 2.0))
            back = (lambda p: d.to_original(p, ctx)) if d is not None else (lambda p: p)
            region = d.region(H, W, ctx) if (d is not None and d.region) else None
            raw = clean_pred if scen == "clean" else np.asarray(model.predict(x, kind="erp"), dtype=np.float64)
            fixed, log = correct(model, x, meta, policy, order=a.order)
            s_clean, al_clean = score(clean_pred, gt, valid, model, region, min_d, max_d)
            s_raw, al_raw = score(back(raw), gt, valid, model, region, min_d, max_d)
            s_fix, al_fix = score(back(fixed), gt, valid, model, region, min_d, max_d)
            caps = detect_caps(x)
            rec[scen] = {"clean": s_clean, "raw": s_raw, "fixed": s_fix, "log": log, "detected": cap_fault(caps),
                         "caps": caps}
            if ex:
                imgs.update({f"{scen}_input": x, f"{scen}_raw": al_raw, f"{scen}_fixed": al_fix,
                             f"err_{scen}_raw": err(al_raw), f"err_{scen}_fixed": err(al_fix)})
                if scen == "clean":
                    imgs.update({"clean": al_clean, "err_clean": err(al_clean)})
        if ex:
            examples[smp.id] = save_examples(img_dir, smp.id.replace("/", "_"), {"gt": gt, "valid": valid, "images": imgs})
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
    (out / f"correction_{a.tag}.json").write_text(json.dumps({"tag": a.tag, "policy": policy, "trained_on": trained_on,
                                                               "rows": rows, "examples": examples}), encoding="utf-8")
    (out / f"CORRECTION_{a.tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
