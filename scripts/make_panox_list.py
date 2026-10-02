"""Pair PanoX RGB and distance files into a split list for datasets/panorama.py.

    python scripts/make_panox_list.py --root data/panox --out test.txt

Matching: within each scene, files are grouped by their 4-digit instance id; the RGB file is the
one whose path contains rgb/image/color, the GT the one containing distance/depth. Prints the
detected value range of the first GT file so the unit (metres vs normalised) can be checked;
set dataset.depth_scale in configs/dap_panox.yaml accordingly.
"""
import os
os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")  # must precede any cv2 import
import argparse
import re
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="data/panox")
ap.add_argument("--out", default="test.txt")
a = ap.parse_args()

IMG = (".png", ".jpg", ".jpeg", ".exr", ".npy", ".npz", ".tif", ".tiff")
groups = defaultdict(dict)
for r, _, fs in os.walk(a.root):
    for f in fs:
        if not f.lower().endswith(IMG):
            continue
        p = os.path.relpath(os.path.join(r, f), a.root).replace("\\", "/")
        m = re.findall(r"(?:^|[/_-])(\d{4})(?=[/_.-])", "/" + p)
        if not m:
            continue
        scene = p.split("/")[0]
        key = (scene, m[-1])
        low = p.lower()
        if "distance" in low or "depth" in low:
            groups[key]["gt"] = p
        elif any(k in low for k in ("rgb", "image", "color")):
            groups[key]["rgb"] = p
pairs = [(v["rgb"], v["gt"]) for k, v in sorted(groups.items()) if "rgb" in v and "gt" in v]
with open(os.path.join(a.root, a.out), "w") as f:
    f.write("".join(f"{x} {y}\n" for x, y in pairs))
print(f"{len(pairs)} pairs -> {os.path.join(a.root, a.out)} (unpaired groups: {len(groups) - len(pairs)})")
if pairs:
    import numpy as np
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    import cv2
    p = os.path.join(a.root, pairs[0][1])
    d = np.load(p) if p.endswith(".npy") else cv2.imread(p, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED)
    d = d[..., 0] if d is not None and d.ndim == 3 else d
    if d is not None:
        print(f"first GT {pairs[0][1]}: dtype {d.dtype}, shape {d.shape}, range {np.nanmin(d):.4g}-{np.nanmax(d):.4g}")
