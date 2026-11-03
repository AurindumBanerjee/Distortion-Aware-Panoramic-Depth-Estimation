"""Build split lists for Holo360D (real LiDAR-mesh GT) for datasets/panorama.py (preset 'holo360d').

    python scripts/make_holo360d_list.py --root ../Data/holo360d         # or data/holo360d on the server

Layout expected: <root>/<Scene>/<Scene>/{rgb,mask,sky_mask}/<ts>.jpg and <root>/<Scene>/<Scene>/depth/mesh_depth/<ts>.exr
Writes test.txt (all), indoor.txt, outdoor.txt with lines  "rgb depth mask"  (mesh depth only: point-cloud depth
is too sparse near the poles). Frames missing any of the three files are skipped and reported.
Note: the `sky_mask` image is NOT needed - it is exactly the depth-validity mask (mesh depth is NaN in the sky).
"""
import argparse
import os

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="data/holo360d")
a = ap.parse_args()
rows = {"test": [], "indoor": [], "outdoor": []}
skipped = 0
for scene in sorted(os.listdir(a.root)):
    base = os.path.join(a.root, scene, scene)
    if not os.path.isdir(os.path.join(base, "rgb")):
        continue
    for f in sorted(os.listdir(os.path.join(base, "rgb"))):
        st = os.path.splitext(f)[0]
        rgb, dep, msk = (f"{scene}/{scene}/rgb/{f}", f"{scene}/{scene}/depth/mesh_depth/{st}.exr", f"{scene}/{scene}/mask/{f}")
        if not all(os.path.isfile(os.path.join(a.root, p)) for p in (rgb, dep, msk)):
            skipped += 1
            continue
        line = f"{rgb} {dep} {msk}\n"
        rows["test"].append(line)
        rows["indoor" if scene.lower().startswith("indoor") else "outdoor"].append(line)
for k, v in rows.items():
    with open(os.path.join(a.root, f"{k}.txt"), "w") as fh:
        fh.writelines(v)
    print(f"{k}.txt: {len(v)} frames")
print(f"skipped incomplete frames: {skipped}")
