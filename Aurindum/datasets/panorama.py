"""Generic ERP RGB-D dataset loader driven by a split list file.

List file format (one sample per line, paths relative to `root`):
    rgb/scene_0000.png depth/scene_0000.npy [mask/scene_0000.jpg]
The optional 3rd column is a validity mask image (pixel > 127 = valid), ANDed with the depth validity.

Supported depth formats:
  .npy / .npz      float metres
  .png / .tif      uint16, divided by `depth_scale`
                     Stanford2D3D: depth_scale=512, invalid = 65535 (-> > max_depth)
                     Matterport3D (Zioulis / UniFuse ERP release): depth_scale=4000
                     Structured3D: depth_scale=1000
  .exr             float, multiplied by `exr_scale` (default 1 = metres; PanoX 0.01 = cm) (needs OpenCV built with OpenEXR; set OPENCV_IO_ENABLE_OPENEXR=1)

All GT depth is treated as Euclidean range (distance along the ray), which is the
convention of all ERP benchmarks above. RGB is resized with INTER_AREA/CUBIC, depth with
INTER_NEAREST (never interpolate across depth discontinuities or invalid pixels).
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
    # PanoX (UE5): float32 EXR range in CENTIMETRES (UE units; floor-plane check gives camera heights ~95-140 in
    # the raw numbers). Sky/infinity = ~65504 (float16 max) -> becomes 655 m and is masked by max_depth.
    "panox": dict(depth_scale=1.0, max_depth=100.0, min_depth=0.05, exr_scale=0.01),
    # Holo360D (real LiDAR-mesh GT): float32 EXR range in METRES, NaN where the mesh has no data (sky). List file
    # carries a 3rd column with the per-frame mask jpg (value > 127 = valid; excludes the operator / rig).
    "holo360d": dict(depth_scale=1.0, max_depth=100.0, min_depth=0.1, exr_scale=1.0),
}


def _read_exr_fallback(path: str) -> Optional[np.ndarray]:
    """Read a single-channel (or first-channel) EXR with the `OpenEXR` package (pip install openexr)."""
    try:
        import OpenEXR  # type: ignore
        ch = OpenEXR.File(path).channels()
        key = "Y" if "Y" in ch else ("R" if "R" in ch else next(iter(ch)))
        return np.asarray(ch[key].pixels, dtype=np.float32)
    except Exception:  # noqa: BLE001
        return None


@dataclass
class Sample:
    id: str
    rgb: np.ndarray  # HxWx3 uint8 RGB
    depth: np.ndarray  # HxW float32 metres (range), NaN where invalid
    valid: np.ndarray  # HxW bool


class PanoramaDataset:
    def __init__(self, root: str, list_file: str, height: int = 512, width: int = 1024, name: str = "synthetic",
                 depth_scale: Optional[float] = None, max_depth: Optional[float] = None,
                 min_depth: Optional[float] = None, limit: Optional[int] = None, exr_scale: Optional[float] = None,
                 subset: str = "first", id_filter=None):
        p = dict(PRESETS.get(name, PRESETS["synthetic"]))
        if depth_scale is not None:
            p["depth_scale"] = depth_scale
        if max_depth is not None:
            p["max_depth"] = max_depth
        if min_depth is not None:
            p["min_depth"] = min_depth
        if exr_scale is not None:
            p["exr_scale"] = exr_scale
        self.exr_scale = p.get("exr_scale", 1.0)  # multiplier applied to .exr depth to get metres
        self.root, self.h, self.w, self.name = root, height, width, name
        self.depth_scale, self.max_depth, self.min_depth = p["depth_scale"], p["max_depth"], p["min_depth"]
        lf = list_file if os.path.isabs(list_file) else os.path.join(root, list_file)
        with open(lf) as f:
            self.items: List[Tuple[str, ...]] = [tuple(l.split()[:3]) for l in f if l.strip()]
        if id_filter is not None:  # e.g. calibration / evaluation split; applied BEFORE the subset so 'spread' stays inside it
            self.items = [it for i, it in enumerate(self.items) if id_filter(self.sample_id(i))]
        if limit and limit < len(self.items):
            # 'first' : the first N lines (reproduces earlier runs). Split lists are ordered by scene, so this covers
            #           only the first few houses / environments (e.g. 60 PanoX frames = 3 of 8 environments).
            # 'spread': N evenly spaced lines over the whole list -> every scene is represented. Deterministic.
            if subset == "spread":
                n = len(self.items)
                self.items = [self.items[(i * n) // limit] for i in range(limit)]
            elif subset == "first":
                self.items = self.items[:limit]
            else:
                raise ValueError(f"unknown subset mode {subset!r} (first | spread)")

    def __len__(self):
        return len(self.items)

    def sample_id(self, i: int) -> str:
        """Id of sample i without reading any file (same rule as __getitem__)."""
        rgb_rel = self.items[i][0]
        sid = os.path.splitext(os.path.basename(rgb_rel))[0]
        parts = rgb_rel.replace("\\", "/").split("/")
        if len(parts) > 2:  # nested layouts (PanoX: <scene>/<scene>/rgb/0002.png) -> ids must be unique across scenes
            sid = f"{parts[0]}_{sid}"
        return sid

    def keep(self, predicate) -> "PanoramaDataset":
        """Restrict to samples whose id satisfies predicate(id) (e.g. a calibration / evaluation split). In place."""
        self.items = [it for i, it in enumerate(self.items) if predicate(self.sample_id(i))]
        return self

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
                d = _read_exr_fallback(path)  # OpenCV built without OpenEXR support
            if d is None:
                raise IOError(path)
            if d.ndim == 3:
                d = d[..., 0]
            d = d.astype(np.float32)
            if ext != ".exr":
                d = d / self.depth_scale
            else:
                d = d * self.exr_scale
        return d

    def __getitem__(self, i: int) -> Sample:
        rgb_rel, d_rel = self.items[i][:2]
        mask_rel = self.items[i][2] if len(self.items[i]) > 2 else None
        bgr = cv2.imread(os.path.join(self.root, rgb_rel), cv2.IMREAD_COLOR)
        if bgr is None:
            raise IOError(rgb_rel)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        d = self._read_depth(os.path.join(self.root, d_rel))
        if rgb.shape[:2] != (self.h, self.w):
            interp = cv2.INTER_AREA if rgb.shape[0] > self.h else cv2.INTER_CUBIC
            rgb = cv2.resize(rgb, (self.w, self.h), interpolation=interp)
        if d.shape != (self.h, self.w):
            d = cv2.resize(d, (self.w, self.h), interpolation=cv2.INTER_NEAREST)
        valid = np.isfinite(d) & (d > self.min_depth) & (d <= self.max_depth)
        if mask_rel is not None:
            mk = cv2.imread(os.path.join(self.root, mask_rel), cv2.IMREAD_GRAYSCALE)
            if mk is None:
                raise IOError(mask_rel)
            if mk.shape != (self.h, self.w):
                mk = cv2.resize(mk, (self.w, self.h), interpolation=cv2.INTER_NEAREST)
            valid &= mk > 127
        d = np.where(valid, d, np.nan).astype(np.float32)
        return Sample(self.sample_id(i), rgb, d, valid)

    def __iter__(self) -> Iterator[Sample]:
        for i in range(len(self)):
            yield self[i]
