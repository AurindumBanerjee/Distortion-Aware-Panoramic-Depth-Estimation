#!/usr/bin/env python3
"""Rescue Kaggle experiment outputs into the repository's central artifact tree.

This utility only copies files. It never stages, commits, changes remotes, pushes,
or deletes source files. Existing destination files are left untouched unless
--overwrite is explicitly supplied.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "artifacts" / "results" / "followups"
LOGS = ROOT / "artifacts" / "logs" / "followups"

ALIASES = {
    "01": "scale_only_protocol",
    "02": "domain_conditioned_gate",
    "03": "panda_style_finetuning",
    "04": "mono360_20view",
    "05": "fov_resolution_sweep",
    "06": "structure_at_poles_gate",
    "07": "real_nyc_20view",
    "08": "paired_panox_analysis",
}


def copy_tree(source: Path, destination: Path, overwrite: bool) -> int:
    copied = 0
    if not source.exists():
        return copied
    for item in source.rglob("*"):
        if not item.is_file():
            continue
        target = destination / item.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not overwrite:
            continue
        shutil.copy2(item, target)
        copied += 1
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", help="Experiment key: 01..08 or canonical name")
    parser.add_argument("source", type=Path, help="Extracted Kaggle output folder")
    parser.add_argument("--overwrite", action="store_true", help="Replace matching destination files")
    args = parser.parse_args()

    key = args.experiment
    name = ALIASES.get(key, key)
    source = args.source.expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source directory does not exist: {source}")

    # Accept either a stage folder containing outputs/logs or a run folder.
    output_source = source / "outputs" if (source / "outputs").is_dir() else source
    log_source = source / "logs"
    output_count = copy_tree(output_source, RESULTS / name / "outputs", args.overwrite)
    log_count = copy_tree(log_source, LOGS / name, args.overwrite)

    print(f"Experiment: {name}")
    print(f"Output files copied: {output_count}")
    print(f"Log files copied: {log_count}")
    print("Git operations: disabled (no add, commit, remote change, or push).")


if __name__ == "__main__":
    main()
