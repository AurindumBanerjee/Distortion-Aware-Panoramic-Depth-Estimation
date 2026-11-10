

#!/usr/bin/env python3
"""Preflight checks for Experiment 07 before allocating GPU time.

With --skip-cuda, only PyYAML, NumPy and OpenCV are required; this is useful
for checking a Windows data mount before moving the study to Kaggle.
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import cv2
import numpy as np
import yaml
from pano.paths import ROOT


def expand_env(value):
    if isinstance(value, str):
        pattern = re.compile(r"\{ENV:([A-Za-z_][A-Za-z0-9_]*)(?:\|([^}]*))?\}")
        return pattern.sub(
            lambda match: os.environ.get(match.group(1), match.group(2) or match.group(0)),
            value,
        )
    if isinstance(value, list):
        return [expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: expand_env(item) for key, item in value.items()}
    return value


def resolve_from_root(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "followups" / "real_nyc_20view.yaml"))
    ap.add_argument("--skip-cuda", action="store_true",
                    help="Check paths/data only; do not require or import PyTorch.")
    ap.add_argument("--decode-samples", type=int, default=3)
    args = ap.parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        raise SystemExit(f"Config not found: {config_path}")
    cfg = expand_env(yaml.safe_load(config_path.read_text(encoding="utf-8")))

    if args.decode_samples < 1:
        raise SystemExit("--decode-samples must be >=1.")

    if not args.skip_cuda:
        try:
            import torch
        except ImportError as exc:
            raise SystemExit("PyTorch is missing. Install the project environment or use --skip-cuda.") from exc
        if not torch.cuda.is_available():
            raise SystemExit("CUDA is unavailable. Enable a GPU runtime before running Experiment 07.")

    weight_path = resolve_from_root(cfg["model"]["weights"])
    if not weight_path.is_file():
        raise SystemExit(f"MiDaS weights not found: {weight_path}")

    manifest = resolve_from_root(cfg["dataset"]["manifest"])
    if not manifest.is_file():
        raise SystemExit(f"Manifest not found: {manifest}. Run scripts/create_manifest.py first.")
    rows = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 182:
        raise SystemExit(f"Expected 182 manifest records; found {len(rows)}.")

    dataset_root = resolve_from_root(cfg["dataset"]["root"])
    decoded = 0
    for line_number, row in enumerate(rows, start=1):
        columns = row.split()
        if len(columns) != 2:
            raise SystemExit(f"Manifest line {line_number} must have exactly two columns.")
        rgb_path, depth_path = (dataset_root / columns[0], dataset_root / columns[1])
        if not rgb_path.is_file():
            raise SystemExit(f"Missing RGB at manifest line {line_number}: {rgb_path}")
        if not depth_path.is_file():
            raise SystemExit(f"Missing GT at manifest line {line_number}: {depth_path}")
        if decoded < args.decode_samples:
            rgb = cv2.imread(str(rgb_path), cv2.IMREAD_COLOR)
            if rgb is None:
                raise SystemExit(f"OpenCV could not decode RGB: {rgb_path}")
            depth = np.load(depth_path, mmap_mode="r")
            if depth.ndim != 2:
                raise SystemExit(f"Expected a 2-D range map, got {depth.shape}: {depth_path}")
            if rgb.shape[1] / rgb.shape[0] < 1.9 or depth.shape[1] / depth.shape[0] < 1.9:
                raise SystemExit(
                    f"Expected approximately 2:1 ERP inputs; RGB={rgb.shape}, GT={depth.shape}."
                )
            values = np.asarray(depth)
            valid = np.isfinite(values) & (values > 0.5) & (values <= 1000.0)
            if valid.mean() < 0.01:
                raise SystemExit(f"Fewer than 1% valid GT values: {depth_path}")
            print(
                f"Decoded {rgb_path.name}: RGB {rgb.shape}, GT {depth.shape}, "
                f"valid GT {100.0 * valid.mean():.1f}%"
            )
            decoded += 1

    print("Experiment 07 data/checkpoint preflight passed.")
    print(f"Manifest records: {len(rows)}")
    print(f"Referenced files checked: {2 * len(rows)}")
    print(f"Sample pairs decoded: {decoded}")
    print(f"Dataset root: {dataset_root}")
    print(f"Model checkpoint: {weight_path}")
    if not args.skip_cuda:
        print(f"CUDA device(s): {', '.join(torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count()))}")
    else:
        print("CUDA: not checked (--skip-cuda).")


if __name__ == "__main__":
    main()