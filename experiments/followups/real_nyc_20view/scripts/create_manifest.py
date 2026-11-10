

#!/usr/bin/env python3
"""Create a deterministic RGB/GT manifest for Experiment 07.

Two panoramas (offsets 4 and 14) are sampled from each complete 20-ID block,
starting at ID 80. IDs 0..74 are excluded because they were used by an
earlier 75-frame NYC run. The full collection yields 91 blocks x 2 = 182 frames.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

from pano.paths import ROOT, DATA

HERE = Path(__file__).resolve().parent
EXPERIMENT_DIR = HERE.parent
DEFAULT_DAP_ROOT = DATA / "dap_selected"
EXPECTED_TOTAL = 1908
BLOCK_SIZE = 20
OFFSETS = (4, 14)
EXCLUDE_BEFORE = 75


def indexed_files(folder: Path, pattern: str) -> dict[int, Path]:
    found: dict[int, Path] = {}
    regex = re.compile(pattern)
    for path in folder.iterdir():
        match = regex.fullmatch(path.name)
        if match and path.is_file():
            found[int(match.group(1))] = path
    return found


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dap-root", type=Path,
                    default=Path(os.environ.get("DAP_SELECTED_ROOT", DEFAULT_DAP_ROOT)))
    ap.add_argument("--expected-total", type=int, default=EXPECTED_TOTAL,
                    help="Expected paired NYC RGB/depth IDs; use 0 to disable exact-count validation.")
    ap.add_argument("--output", type=Path,
                    default=EXPERIMENT_DIR / "manifests" / "nyc_holdout_182.txt")
    args = ap.parse_args()

    root = args.dap_root.expanduser().resolve()
    rgb_dir = root / "nyc_raw_images_panorama"
    depth_dir = root / "nyc_distance_panorama_npy"
    if not rgb_dir.is_dir() or not depth_dir.is_dir():
        raise SystemExit(
            f"Expected nyc_raw_images_panorama/ and nyc_distance_panorama_npy/ under {root}. "
            "Check --dap-root."
        )

    rgbs = indexed_files(rgb_dir, r"panorama_(\d+)\.png")
    depths = indexed_files(depth_dir, r"erp_distance_(\d+)\.npy")
    common = set(rgbs) & set(depths)
    rgb_only = sorted(set(rgbs) - set(depths))
    depth_only = sorted(set(depths) - set(rgbs))
    if rgb_only or depth_only:
        raise SystemExit(
            f"Unpaired data: {len(rgb_only)} RGB-only IDs and {len(depth_only)} depth-only IDs. "
            f"Examples: RGB-only={rgb_only[:5]}, depth-only={depth_only[:5]}"
        )
    if args.expected_total and len(common) != args.expected_total:
        raise SystemExit(
            f"Expected {args.expected_total} paired IDs, found {len(common)}. "
            "Inspect the mounted dataset; do not silently alter the sampling population."
        )
    if not common or min(common) != 0:
        raise SystemExit("Expected a non-empty dataset with numeric panorama IDs starting at 0.")

    chosen: list[int] = []
    skipped_blocks: list[int] = []
    max_block_start = (max(common) // BLOCK_SIZE) * BLOCK_SIZE
    first_block_start = (EXCLUDE_BEFORE // BLOCK_SIZE + 1) * BLOCK_SIZE
    for block_start in range(first_block_start, max_block_start + 1, BLOCK_SIZE):
        candidates = [block_start + off for off in OFFSETS]
        if all(i in common for i in candidates):
            chosen.extend(candidates)
        else:
            skipped_blocks.append(block_start // BLOCK_SIZE)

    if len(chosen) != 182 or len(chosen) % 2:
        raise SystemExit(
            f"Expected exactly 182 selected frames in 91 complete blocks, found {len(chosen)}. "
            f"Skipped blocks: {skipped_blocks}."
        )
    if min(chosen) <= 74:
        raise SystemExit("Sampling overlap detected with the earlier NYC IDs 0..74.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"nyc_raw_images_panorama/panorama_{i}.png "
        f"nyc_distance_panorama_npy/erp_distance_{i}.npy"
        for i in chosen
    ]
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    metadata = {
        "experiment": "07_real_nyc_20view",
        "dataset_root_name": root.name,
        "rgb_directory": "nyc_raw_images_panorama",
        "depth_directory": "nyc_distance_panorama_npy",
        "source_rgb_count": len(rgbs),
        "source_depth_count": len(depths),
        "paired_id_count": len(common),
        "selected_count": len(chosen),
        "cluster_count": len({i // BLOCK_SIZE for i in chosen}),
        "cluster_definition": "floor(panorama_id / 20); contiguous 20-ID blocks",
        "selection_rule": {
            "excluded_ids": "0..74 (used by earlier 75-frame NYC run)",
            "block_size": BLOCK_SIZE,
            "offsets_within_each_block": list(OFFSETS),
            "first_block_start": first_block_start,
            "last_block_start": max(i // BLOCK_SIZE * BLOCK_SIZE for i in chosen),
        },
        "sample_ids": chosen,
        "manifest_file": args.output.name,
        "manifest_sha256": sha256(args.output),
        "limitations": [
            "20-ID blocks are an assumed grouping, not verified route/session IDs.",
            "This is a held-out frame subset relative to an earlier 75-frame NYC evaluation, "
            "not a newly collected dataset or an independent benchmark release."
        ],
    }
    metadata_path = args.output.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Manifest: {args.output}")
    print(f"Paired source IDs: {len(common)}")
    print(f"Selected frames: {len(chosen)} across {metadata['cluster_count']} assumed blocks")
    print(f"Selected ID range: {chosen[0]}..{chosen[-1]}")
    print(f"SHA256: {metadata['manifest_sha256']}")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    main()