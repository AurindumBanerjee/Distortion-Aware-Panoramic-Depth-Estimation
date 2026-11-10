#!/usr/bin/env python3
"""Redraw every per-model sweep plot (results/sweep_*.png) from its JSON summary with the labelled layout of
distortion_sweep.figure(). CPU only, no model runs.  Usage: python scripts/replot_sweeps.py"""
from __future__ import annotations

import json

from pano.paths import BENCHMARK_RESULTS  # noqa: E402
from scripts.run.distortion_sweep import figure

MODEL = {"midas": "MiDaS", "dap": "DAP", "da360": "DA360", "da2": "DA²", "da2m": "DA² (median fit)"}
SET = {"s3": "Structured3D", "panox": "PanoX", "holo_in": "Holo360D indoor", "holo_out": "Holo360D outdoor",
       "stanford": "Stanford2D3D", "nyc": "NYC"}
SPLIT = {"eval": "evaluation split", "calib": "calibration split", "all": "all frames"}


def main():
    n = 0
    for p in sorted((BENCHMARK_RESULTS).glob("sweep_*.json")):
        d = json.loads(p.read_text())
        s = d.get("summary", d)
        if "centres" not in s:
            continue
        tag = p.stem[len("sweep_"):]
        mode = "rotation"
        for md in ("dilation", "flip", "rotation"):
            if tag.startswith(md + "_"):
                mode, tag = md, tag[len(md) + 1:]
        parts = tag.split("_")
        m, split, ds = parts[0], parts[-1], "_".join(parts[1:-1])
        title = (f"{mode.capitalize()} sweep · {MODEL.get(m, m)} · {SET.get(ds, ds)} ({SPLIT.get(split, split)}) · "
                 f"{s.get('n_frames', '?')} frames / {s.get('n_clusters', '?')} clusters")
        figure(s, p.with_suffix(".png"), title)
        n += 1
    print(f"redrew {n} sweep plots")


if __name__ == "__main__":
    main()
