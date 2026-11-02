"""Build split lists for Holo360D sequences.

Expected layout:  <root>/<Scene>/<Scene>/rgb/<timestamp>.jpg
                  <root>/<Scene>/<Scene>/depth/mesh_depth/<timestamp>.exr   (float metres, NaN = sky / no mesh)
                  <root>/<Scene>/<Scene>/mask/<timestamp>.jpg               (white = valid; masks the operator / mount)
Writes test.txt (all scenes), test_indoor.txt and test_outdoor.txt with `rgb depth mask` lines.

    python scripts/make_holo360d_list.py --root data/holo360d
"""
import argparse
import glob
import os

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="data/holo360d")
a = ap.parse_args()
lines = {"test.txt": [], "test_indoor.txt": [], "test_outdoor.txt": []}
for scene_dir in sorted(glob.glob(os.path.join(a.root, "*", "*", "rgb"))):
    base = os.path.dirname(scene_dir)
    kind = "test_outdoor.txt" if os.path.basename(base).lower().startswith("outdoor") else "test_indoor.txt"
    for rgb in sorted(glob.glob(os.path.join(scene_dir, "*.jpg"))):
        stem = os.path.splitext(os.path.basename(rgb))[0]
        dep = os.path.join(base, "depth", "mesh_depth", stem + ".exr")
        msk = os.path.join(base, "mask", stem + ".jpg")
        if not os.path.exists(dep):
            continue
        parts = [rgb, dep] + ([msk] if os.path.exists(msk) else [])
        line = " ".join(os.path.relpath(p, a.root).replace(os.sep, "/") for p in parts)
        lines["test.txt"].append(line)
        lines[kind].append(line)
for name, ls in lines.items():
    with open(os.path.join(a.root, name), "w") as f:
        f.write("\n".join(ls) + "\n")
    print(f"{len(ls)} samples -> {os.path.join(a.root, name)}")
