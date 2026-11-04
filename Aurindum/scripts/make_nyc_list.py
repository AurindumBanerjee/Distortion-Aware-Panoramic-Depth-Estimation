#!/usr/bin/env python3
"""Split list for the DAP NYC outdoor panoramas (Lokesh's experiment), for datasets/panorama.py preset 'nyc_dap'.

Expected layout:  <root>/rgb/panorama_<n>.png  and  <root>/depth/erp_distance_<n>.npy   (copy or symlink the two
folders nyc_raw_images_panorama -> rgb, nyc_distance_panorama_npy -> depth). Writes <root>/test.txt with paths relative
to <root>, naturally sorted (panorama_2 before panorama_10), and reports RGB files without depth.

    python scripts/make_nyc_list.py --root data/nyc_dap
"""
import argparse
import os
import re

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="data/nyc_dap")
a = ap.parse_args()
rgb_dir, dep_dir = os.path.join(a.root, "rgb"), os.path.join(a.root, "depth")
if not (os.path.isdir(rgb_dir) and os.path.isdir(dep_dir)):
    raise SystemExit(f"need {rgb_dir}/ and {dep_dir}/ (copy or symlink nyc_raw_images_panorama and nyc_distance_panorama_npy)")
ids = []
for f in os.listdir(rgb_dir):
    m = re.fullmatch(r"panorama_(\d+)\.png", f)
    if m:
        ids.append(int(m.group(1)))
lines, missing = [], 0
for n in sorted(ids):
    if os.path.isfile(os.path.join(dep_dir, f"erp_distance_{n}.npy")):
        lines.append(f"rgb/panorama_{n}.png depth/erp_distance_{n}.npy\n")
    else:
        missing += 1
with open(os.path.join(a.root, "test.txt"), "w") as fh:
    fh.writelines(lines)
print(f"{len(lines)} pairs -> {os.path.join(a.root, 'test.txt')} ({missing} RGB files without depth skipped)")
