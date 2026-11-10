#!/usr/bin/env python3
"""Ground-truth colour scales for the stored example images (CPU, needs the datasets under data/ or ../../Data).

The example depth maps in results/*_img were written by distortion_study.save_examples as
turbo(1 - x), x = log depth scaled between the 2nd and 98th percentile of the frame's valid ground truth, and the
error maps as magma(min(AbsRel, 0.5) / 0.5). The percentiles were not stored, so this script recomputes them from the
same frames, at the same resolution and with the same valid range, and also writes the ground-truth depth itself
with the same colour scale. The app and make_figures.py use them to label the colour bars in metres.

Writes results/figures/example_gt.json and results/figures/example_gt/<set>/<frame>_<H>.jpg
Usage: python scripts/example_gt.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import ROOT, depth_range, load_config  # noqa: E402

RES = ROOT / "results"
OUT = RES / "figures" / "example_gt"
MODELS = ("midas", "dap", "da360", "da2")
CORE = ("s3", "panox", "holo_in", "holo_out")
EXT = ("stanford", "nyc")
CONFIG = {"s3": "config.yaml", "panox": "config_panox.yaml", "holo_in": "config_holo360d_indoor.yaml",
          "holo_out": "config_holo360d_outdoor.yaml", "stanford": "config_stanford2d3d.yaml", "nyc": "config_nyc.yaml"}


def wanted():
    """{set: {height: {frame ids}}} for every stored example of the studies and the end-to-end correction."""
    import cv2
    need = {}
    for ds in CORE + EXT:
        for m in MODELS:
            for p, img in ((RES / f"study_{m}_{ds}.json", RES / f"study_{m}_{ds}_img"),
                           ((RES if ds in CORE else RES / "external") / f"correction_{m}_{ds}.json",
                            (RES if ds in CORE else RES / "external") / f"correction_{m}_{ds}_img")):
                if not p.is_file():
                    continue
                ex = json.loads(p.read_text()).get("examples", {})
                for fid, names in ex.items():
                    f = img / (names.get("clean") or next(iter(names.values())))
                    im = cv2.imread(str(f)) if f.is_file() else None
                    if im is not None:
                        need.setdefault(ds, {}).setdefault(im.shape[0], set()).add(fid)
    return need


def main():
    import cv2
    from matplotlib import cm
    from datasets.panorama import PanoramaDataset
    need = wanted()
    out = {}
    for ds, by_h in need.items():
        cfg = load_config(str(ROOT / "3_structured3d_benchmark" / CONFIG[ds]), [])
        d = cfg["data"]
        name, lst = d.get("dataset", "structured3d"), d.get("list", "test.txt")
        root = next((c for c in [ROOT / d.get("root", f"data/{name}"), ROOT.parent.parent / "Data" / name,
                                 ROOT.parent / "Data" / name] if (c / lst).is_file()), None)
        if root is None:
            print(f"{ds}: no data found, skipped")
            continue
        min_d, max_d = depth_range(cfg)
        for H, ids in by_h.items():
            dset = PanoramaDataset(str(root), lst, height=H, width=2 * H, name=name, id_filter=lambda sid: sid in ids)
            for i in range(len(dset)):
                smp = dset[i]
                gt = np.nan_to_num(smp.depth, nan=0.0)
                valid = smp.valid & (gt >= min_d) & (gt <= max_d)
                if not valid.any():
                    continue
                lo, hi = (float(v) for v in np.percentile(gt[valid], [2, 98]))
                x = np.clip((np.log(np.clip(gt, 1e-3, None)) - np.log(lo)) / (np.log(hi) - np.log(lo)), 0, 1)
                rgb = (cm.turbo(1 - x)[..., :3] * 255).astype(np.uint8)
                rgb[~valid] = 40
                f = OUT / ds / f"{smp.id.replace('/', '_')}_{H}.jpg"
                f.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(f), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
                out.setdefault(ds, {}).setdefault(smp.id, {})[str(H)] = {
                    "lo": lo, "hi": hi, "min_depth": min_d, "max_depth": max_d,
                    "valid_share": float(valid.mean()), "gt": f.relative_to(RES).as_posix()}
            got = sum(1 for fid in ids if str(H) in out.get(ds, {}).get(fid, {}))
            print(f"{ds} H={H}: {got}/{len(ids)} frames")
    (RES / "figures").mkdir(parents=True, exist_ok=True)
    (RES / "figures" / "example_gt.json").write_text(json.dumps(out, indent=1))
    print("wrote results/figures/example_gt.json")


if __name__ == "__main__":
    main()
