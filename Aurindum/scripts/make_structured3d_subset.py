"""Build a small Structured3D test subset by reading panorama zips directly (no full unzip)."""
import argparse
import random
import re
import zipfile
from pathlib import Path

import cv2
import numpy as np

PAT = re.compile(r"(?:^|/)(scene_\d+)/2D_rendering/([^/]+)/panorama/full/(\w+)\.png$")


def index_zip(zf, rgb_name):
    """Return {(scene, room): (rgb_member, depth_member)} for complete pairs."""
    found = {}
    for name in zf.namelist():
        m = PAT.search(name)
        if not m:
            continue
        scene, room, stem = m.groups()
        slot = {rgb_name: 0, "depth": 1}.get(stem)
        if slot is None:
            continue
        found.setdefault((scene, room), [None, None])[slot] = name
    return {k: tuple(v) for k, v in found.items() if all(v)}


def valid(rgb_bytes, depth_bytes):
    rgb = cv2.imdecode(np.frombuffer(rgb_bytes, np.uint8), cv2.IMREAD_COLOR)
    depth = cv2.imdecode(np.frombuffer(depth_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    return (rgb is not None and depth is not None and depth.dtype == np.uint16
            and rgb.shape[:2] == depth.shape[:2] == (512, 1024) and (depth > 0).mean() > 0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", nargs="+", required=True)
    ap.add_argument("--out", default="data/structured3d")
    ap.add_argument("--per-zip", type=int, default=150)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rgb-name", default="rgb_rawlight")
    ap.add_argument("--list", action="store_true", help="print matching members and exit")
    a = ap.parse_args()

    out = Path(a.out)
    lines = []
    for zpath in a.zips:
        with zipfile.ZipFile(zpath) as zf:
            pairs = index_zip(zf, a.rgb_name)
            keys = sorted(pairs)
            print(f"{Path(zpath).name}: {len(keys)} rgb+depth pairs")
            if a.list:
                for k in keys[:10]:
                    print("  ", pairs[k][0]); print("  ", pairs[k][1])
                continue
            random.Random(a.seed).shuffle(keys)
            (out / "rgb").mkdir(parents=True, exist_ok=True)
            (out / "depth").mkdir(parents=True, exist_ok=True)
            n = 0
            for k in keys:
                if n >= a.per_zip:
                    break
                rgb_b, dep_b = (zf.read(m) for m in pairs[k])
                if not valid(rgb_b, dep_b):
                    continue
                stem = f"{k[0]}_{k[1]}"
                (out / "rgb" / f"{stem}.png").write_bytes(rgb_b)
                (out / "depth" / f"{stem}.png").write_bytes(dep_b)
                lines.append(f"rgb/{stem}.png depth/{stem}.png")
                n += 1
            print(f"  wrote {n}")
    if not a.list:
        (out / "test.txt").write_text("\n".join(lines) + "\n")
        print(f"test.txt: {len(lines)} samples -> {out}")


if __name__ == "__main__":
    main()
