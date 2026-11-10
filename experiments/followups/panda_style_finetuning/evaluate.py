#!/usr/bin/env python3
"""Evaluate the distilled student against its frozen DA360 teacher on held-out PanoX GT."""
from __future__ import annotations
import argparse, csv, json, time
from pathlib import Path
import cv2
import numpy as np
import torch
from pano.paths import ROOT
from experiments.followups.shared.common import (band_metrics, environment_info, load_config, load_dataset, load_model,
                    prepare_output, save_json, align_prediction, scene_group)
from experiments.followups.panda_style_finetuning.student_model import StudentDepthNet
from pano.models.depth_model import OutputSpec


class StudentAdapter:
    spec = OutputSpec(space="disparity", scale="affine",
                      geometry_erp="range", geometry_perspective="range")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "followups" / "panda_style_finetuning.yaml"))
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--all-scenes", action="store_true", help="evaluate all PanoX environments, not only held-out ones")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    cfg = load_config(a.config, a.set)
    if not torch.cuda.is_available():
        raise SystemExit("CUDA required.")
    ckpt_path = Path(a.checkpoint).resolve()
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    split_file = ckpt_path.parent / "config_environment.json"
    heldout_groups = None
    if not a.all_scenes:
        if not split_file.exists():
            raise FileNotFoundError(f"Missing training split record next to checkpoint: {split_file}")
        heldout_groups = set(json.loads(split_file.read_text(encoding="utf-8"))["validation_environments"])
    out = prepare_output(Path(cfg["output_dir"]) / ("evaluation_" + time.strftime("%Y%m%d_%H%M%S")), a.overwrite)
    ds = load_dataset(cfg["dataset"], limit=a.limit)
    if heldout_groups is not None:
        ds = [s for s in ds if scene_group(s.id) in heldout_groups]
        if not ds:
            raise RuntimeError(f"No evaluation samples matched held-out environments: {sorted(heldout_groups)}")
    teacher = load_model(cfg["teacher"])
    student = StudentDepthNet().cuda()
    student.load_state_dict(ck["state_dict"])
    student.eval()
    protocols = cfg["evaluation"].get("protocols", ["align-all", "align-equatorial"])
    adapter = StudentAdapter()
    lo, hi = float(cfg["evaluation"]["min_depth"]), float(cfg["evaluation"]["max_depth"])
    rows, scene = [], {}
    with torch.no_grad():
        for i, s in enumerate(ds):
            teacher_pred = teacher.predict(s.rgb, kind="erp")
            rgb = cv2.resize(s.rgb, (int(cfg["dataset"]["width"]), int(cfg["dataset"]["height"])),
                             interpolation=cv2.INTER_AREA)
            x = torch.from_numpy((rgb.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]).cuda()
            student_pred = student(x)[0, 0].float().cpu().numpy()
            scene[s.id] = {}
            for proto in protocols:
                scene[s.id][proto] = {}
                for name, pred, model, align in (
                    ("teacher_da360", teacher_pred, teacher, cfg["evaluation"].get("teacher_alignment", "scale")),
                    ("student", student_pred, adapter, cfg["evaluation"].get("student_alignment", "affine")),
                ):
                    depth = align_prediction(pred, s.depth, s.valid, model, proto, align, lo, hi)
                    m = band_metrics(depth, s.depth, s.valid, lo, hi)
                    scene[s.id][proto][name] = m
                    for band, q in m.items():
                        rows.append({"scene": s.id, "environment": scene_group(s.id),
                                     "protocol": proto, "method": name, "band": band, **q})
            if (i + 1) % 10 == 0 or i + 1 == len(ds):
                print(f"[{i+1}/{len(ds)}] {s.id}")
    with (out / "per_scene.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    save_json(out / "summary.json", {"experiment": "03_panda_style_finetuning_evaluation",
              "student_checkpoint": str(ckpt_path), "heldout_environments": sorted(heldout_groups) if heldout_groups else "all",
              "environment": environment_info(), "num_scenes": len(ds), "per_scene": scene})
    lines = ["# Student/teacher evaluation", "",
             "GT is used only in this evaluation stage, not by train.py.",
             f"Evaluated scenes: {len(ds)}; held-out groups: {sorted(heldout_groups) if heldout_groups else 'all'}", ""]
    for proto in protocols:
        lines += [f"## {proto}", "", "| band | DA360 median AbsRel | student median AbsRel |",
                  "|---|---:|---:|"]
        for band in ("all", "60-75", "75-90"):
            t = [scene[s][proto]["teacher_da360"][band]["abs_rel"] for s in scene]
            x = [scene[s][proto]["student"][band]["abs_rel"] for s in scene]
            lines.append(f"| {band} | {np.nanmedian(t):.4f} | {np.nanmedian(x):.4f} |")
        lines.append("")
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved", out / "REPORT.md")


if __name__ == "__main__":
    main()
