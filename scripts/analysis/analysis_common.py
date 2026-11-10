"""Shared setup for the round-3 analysis scripts (distortion_sweep.py, latitude_profile.py).

Loads a series-3 benchmark config (data + model + evaluation block), applies --set overrides, builds the model with
the benchmark's own loader (so DAP / DA360 / DA^2 / MiDaS are created exactly as in the benchmark) and the dataset
with the calibration / evaluation split applied before the frame cap ('spread' subset).
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Tuple

import yaml

from pano.paths import ROOT


def add_common_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--config", required=True, help="series-3 config, e.g. 3_structured3d_benchmark/config.yaml")
    ap.add_argument("--tag", required=True, help="output name: results/<kind>_<tag>.json/.md/.png")
    ap.add_argument("--split", default="calib", choices=["calib", "eval", "all"], help="cluster-hash split (default calib)")
    ap.add_argument("--max_scenes", type=int, default=80, help="frame cap, taken evenly over the (split) list")
    ap.add_argument("--set", dest="overrides", action="append", default=[], help="dotted.key=YAML value (repeatable)")


def load_config(path: str, overrides) -> Dict:
    p = Path(path)
    p = p if p.is_absolute() or p.exists() else ROOT / path
    cfg = yaml.safe_load(open(p))
    for ov in overrides:
        key, _, val = ov.partition("=")
        node = cfg
        for k in key.split(".")[:-1]:
            node = node.setdefault(k, {})
        node[key.split(".")[-1]] = yaml.safe_load(val)
    return cfg


def load_model(cfg: Dict):
    from experiments.benchmark.run import load_model as s3_load_model
    return s3_load_model(cfg.get("model", {}), logging.getLogger("analysis"))


def load_dataset(cfg: Dict, split: str, max_scenes: int):
    from pano.datasets.panorama import PanoramaDataset
    from pano.evaluation.distortion_analysis import in_split
    d = cfg["data"]
    name = d.get("dataset", "structured3d")
    lst = d.get("list", "test.txt")
    for cand in [ROOT / d.get("root", f"data/{name}"), ROOT.parent.parent / "Data" / name, ROOT.parent / "Data" / name]:
        if (cand / lst).is_file():
            return PanoramaDataset(str(cand), lst, height=d.get("height", 256), width=d.get("width", 512), name=name,
                                   limit=max_scenes, subset="spread", id_filter=lambda sid: in_split(sid, split))
    raise FileNotFoundError(f"no {lst} for dataset {name}")


def depth_range(cfg: Dict) -> Tuple[float, float]:
    ev = cfg.get("evaluation", {})
    return float(ev.get("min_depth", 0.1)), float(ev.get("max_depth", 10.0))
