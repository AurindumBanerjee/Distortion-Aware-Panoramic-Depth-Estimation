"""Data preparation and loader for real Structured3D panoramic data.

Extracts a curated subset of indoor panoramas directly from Structured3D_panorama_15.zip
without needing to unpack all 14 GB of archive files.
Converts 16-bit PNG depth to metric range in meters.
"""
from __future__ import annotations

import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger("Structured3D_Loader")


def extract_curated_structured3d_scenes(
    zip_path: Path,
    out_dir: Path,
    max_scenes: int = 5
) -> List[Dict[str, str]]:
    """Inspects Structured3D zip, extracts complete panorama pairs (RGB rawlight + depth.png)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = out_dir / "scenes_manifest.json"

    # If already extracted and manifest exists, return cached list
    if manifest_file.exists():
        with open(manifest_file, "r") as f:
            manifest = json.load(f)
        if len(manifest) >= max_scenes:
            logger.info(f"Loaded {len(manifest)} cached Structured3D scenes from {manifest_file}.")
            return manifest[:max_scenes]

    if not zip_path.exists():
        logger.warning(f"Zip file {zip_path} not found.")
        return []

    logger.info(f"Scanning archive {zip_path.name} for panorama pairs...")
    scenes: List[Dict[str, str]] = []

    with zipfile.ZipFile(str(zip_path), "r") as z:
        all_files = z.namelist()
        
        # Look for full/rgb_rawlight.png and corresponding depth.png
        rgb_candidates = [
            f for f in all_files 
            if "panorama/full/rgb_rawlight.png" in f or "panorama/empty/rgb_rawlight.png" in f
        ]

        logger.info(f"Found {len(rgb_candidates)} panoramic rendering candidates in archive.")

        for rgb_member in rgb_candidates:
            if len(scenes) >= max_scenes:
                break

            depth_member = rgb_member.replace("rgb_rawlight.png", "depth.png")
            if depth_member not in all_files:
                continue

            # Parse scene and room identifiers
            parts = rgb_member.split("/")
            scene_id = parts[1] if len(parts) > 1 else "scene"
            room_id = parts[3] if len(parts) > 3 else "room"
            variant = parts[5] if len(parts) > 5 else "full"
            prefix = f"{scene_id}_{room_id}_{variant}"

            rgb_out_name = f"{prefix}_rgb.png"
            depth_out_name = f"{prefix}_depth.png"
            rgb_dest = out_dir / rgb_out_name
            depth_dest = out_dir / depth_out_name

            if not rgb_dest.exists():
                with z.open(rgb_member) as src, open(rgb_dest, "wb") as dst:
                    dst.write(src.read())

            if not depth_dest.exists():
                with z.open(depth_member) as src, open(depth_dest, "wb") as dst:
                    dst.write(src.read())

            scenes.append({
                "id": prefix,
                "rgb_path": str(rgb_dest),
                "depth_path": str(depth_dest)
            })
            logger.info(f"Extracted scene [{prefix}] -> {rgb_out_name}")

    with open(manifest_file, "w") as f:
        json.dump(scenes, f, indent=2)

    logger.info(f"Successfully extracted {len(scenes)} Structured3D panorama pairs.")
    return scenes


def load_structured3d_pair(
    rgb_path: str,
    depth_path: str,
    target_hw: Optional[Tuple[int, int]] = (256, 512)
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Loads RGB and converts 16-bit PNG depth into metric range in meters.
    
    Structured3D depth convention:
    - 16-bit uint PNG where value is millimeter: depth_meters = uint16 / 1000.0.
    """
    bgr = cv2.imread(rgb_path, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    raw_depth_u16 = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)
    if raw_depth_u16 is None:
        raise FileNotFoundError(f"Could not load depth image: {depth_path}")

    # Structured3D is in millimeters
    depth_m = raw_depth_u16.astype(np.float32) / 1000.0
    valid_mask = (depth_m > 0.05) & (depth_m < 30.0)

    if target_hw is not None and target_hw != rgb.shape[:2]:
        H, W = target_hw
        rgb = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA)
        depth_m = cv2.resize(depth_m, (W, H), interpolation=cv2.INTER_NEAREST)
        valid_mask = (depth_m > 0.05) & (depth_m < 30.0)

    return rgb, depth_m, valid_mask
