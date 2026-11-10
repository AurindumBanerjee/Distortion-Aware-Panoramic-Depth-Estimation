"""Generic ERP RGB-D dataset loader driven by a split list file.

List file format (one sample per line, paths relative to root):
    rgb/scene_0000.png depth/scene_0000.npy [mask/scene_0000.jpg]

The optional third column is a validity mask (pixel > 127 = valid), ANDed with
depth validity. Holo360D uses this to exclude the camera operator / rig.

Supported depth formats:
  .npy / .npz      float metres
  .png / .tif      uint16, divided by depth_scale
  .exr             float, multiplied by exr_scale (default 1 = metres; PanoX 0.01 = cm)

All GT depth is treated as Euclidean range. RGB is resized with INTER_AREA/CUBIC;
depth and masks use INTER_NEAREST to avoid interpolation across discontinuities.
"""
from __future__ import annotations

import os
os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

import cv2
import numpy as np

PRESETS = {
    "synthetic": dict(depth_scale=1.0, max_depth=100.0, min_depth=0.05),
    "stanford2d3d": dict(depth_scale=512.0, max_depth=16.0, min_depth=0.1),
    "matterport3d": dict(depth_scale=4000.0, max_depth=10.0, min_depth=0.1),
    "structured3d": dict(depth_scale=1000.0, max_depth=10.0, min_depth=0.1),
    # PanoX (UE5): float32 EXR range in centimetres.
    "panox": dict(depth_scale=1.0, max_depth=100.0, min_depth=0.05, exr_scale=0.01),
    # Holo360D: float32 EXR mesh range in metres; third list column excludes operator / rig.
    "holo360d": dict(depth_scale=1.0, max_depth=10.0, min_depth=0.1, exr_scale=1.0),
    # DAP NYC distance panoramas: float64 .npy range in metres.
    "nyc_dap": dict(depth_scale=1.0, max_depth=1000.0, min_depth=0.5),
}


def _read_exr_fallback(path: str) -> Optional[np.ndarray]:
    """Read a single-channel EXR with the OpenEXR package when OpenCV lacks EXR support."""
    try:
        import OpenEXR  # type: ignore
        channels = OpenEXR.File(path).channels()
        key = "Y" if "Y" in channels else ("R" if "R" in channels else next(iter(channels)))
        return np.asarray(channels[key].pixels, dtype=np.float32)
    except Exception:
        return None


@dataclass
class Sample:
    id: str
    rgb: np.ndarray
    depth: np.ndarray
    valid: np.ndarray


class PanoramaDataset:
    def __init__(self, root: str, list_file: str, height: int = 512, width: int = 1024, name: str = "synthetic",
                 depth_scale: Optional[float] = None, max_depth: Optional[float] = None,
                 min_depth: Optional[float] = None, limit: Optional[int] = None, exr_scale: Optional[float] = None):
        p = dict(PRESETS.get(name, PRESETS["synthetic"]))
        if depth_scale is not None:
            p["depth_scale"] = depth_scale
        if max_depth is not None:
            p["max_depth"] = max_depth
        if min_depth is not None:
            p["min_depth"] = min_depth
        if exr_scale is not None:
            p["exr_scale"] = exr_scale
        self.exr_scale = p.get("exr_scale", 1.0)
        self.root, self.h, self.w, self.name = root, height, width, name
        self.depth_scale, self.max_depth, self.min_depth = p["depth_scale"], p["max_depth"], p["min_depth"]
        lf = list_file if os.path.isabs(list_file) else os.path.join(root, list_file)
        with open(lf, encoding="utf-8") as f:
            self.items: List[Tuple[str, ...]] = [tuple(line.split()[:3]) for line in f if line.strip()]
        if limit:
            self.items = self.items[:limit]

    def __len__(self):
        return len(self.items)

    def _read_depth(self, path: str) -> np.ndarray:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".npy":
            d = np.load(path).astype(np.float32)
        elif ext == ".npz":
            z = np.load(path)
            d = z[z.files[0]].astype(np.float32)
        else:
            d = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED)
            if d is None and ext == ".exr":
                d = _read_exr_fallback(path)
            if d is None:
                hint = " (install the optional 'openexr' package if OpenCV lacks EXR support)" if ext == ".exr" else ""
                raise IOError(path + hint)
            if d.ndim == 3:
                d = d[..., 0]
            d = d.astype(np.float32)
            d = d / self.depth_scale if ext != ".exr" else d * self.exr_scale
        return d

    def __getitem__(self, i: int) -> Sample:
        rgb_rel, depth_rel = self.items[i][:2]
        mask_rel = self.items[i][2] if len(self.items[i]) > 2 else None
        bgr = cv2.imread(os.path.join(self.root, rgb_rel), cv2.IMREAD_COLOR)
        if bgr is None:
            raise IOError(rgb_rel)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        depth = self._read_depth(os.path.join(self.root, depth_rel))

        if rgb.shape[:2] != (self.h, self.w):
            interp = cv2.INTER_AREA if rgb.shape[0] > self.h else cv2.INTER_CUBIC
            rgb = cv2.resize(rgb, (self.w, self.h), interpolation=interp)
        if depth.shape != (self.h, self.w):
            depth = cv2.resize(depth, (self.w, self.h), interpolation=cv2.INTER_NEAREST)

        valid = np.isfinite(depth) & (depth > self.min_depth) & (depth <= self.max_depth)
        if mask_rel is not None:
            mask = cv2.imread(os.path.join(self.root, mask_rel), cv2.IMREAD_GRAYSCALE)
            if mask is None:
                raise IOError(mask_rel)
            if mask.shape != (self.h, self.w):
                mask = cv2.resize(mask, (self.w, self.h), interpolation=cv2.INTER_NEAREST)
            valid &= mask > 127

        depth = np.where(valid, depth, np.nan).astype(np.float32)
        sid = os.path.splitext(os.path.basename(rgb_rel))[0]
        parts = rgb_rel.replace("\\", "/").split("/")
        if len(parts) > 2:
            sid = f"{parts[0]}_{sid}"
        return Sample(sid, rgb, depth, valid)

    def __iter__(self) -> Iterator[Sample]:
        for i in range(len(self)):
            yield self[i]
