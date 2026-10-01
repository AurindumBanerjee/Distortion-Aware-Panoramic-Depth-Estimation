"""Build a split list for Stanford2D3D panoramas.

Expected layout (official release):  <root>/area_5a/pano/rgb/camera_..._rgb.png
                                      <root>/area_5a/pano/depth/camera_..._depth.png
Standard protocol (UniFuse, PanoFormer, DAP): train on areas 1,2,3,4,6, test on area 5 (5a + 5b).

    python scripts/make_stanford_list.py --root data/stanford2d3d --areas area_5a area_5b --out test_area5.txt
"""
import argparse
import glob
import os

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--areas", nargs="+", default=["area_5a", "area_5b"])
ap.add_argument("--out", default="test_area5.txt")
a = ap.parse_args()
lines = []
for area in a.areas:
    for rgb in sorted(glob.glob(os.path.join(a.root, area, "pano", "rgb", "*_rgb.png"))):
        dep = rgb.replace(os.sep + "rgb" + os.sep, os.sep + "depth" + os.sep).replace("_rgb.png", "_depth.png")
        if os.path.exists(dep):
            lines.append(f"{os.path.relpath(rgb, a.root)} {os.path.relpath(dep, a.root)}")
with open(os.path.join(a.root, a.out), "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"{len(lines)} pairs -> {os.path.join(a.root, a.out)}")
