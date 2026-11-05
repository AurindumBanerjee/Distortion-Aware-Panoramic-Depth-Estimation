"""Shared utilities for the five follow-up studies.

All paths are resolved from the Lokesh project root. Results are written per run;
no existing result directories are overwritten unless --overwrite is explicit.
"""
from __future__ import annotations

import json
import os
import platform
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SHARED = Path(__file__).resolve().parent
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        # Supports {ENV:NAME} and {ENV:NAME|default}.
        pat = re.compile(r"\{ENV:([A-Za-z_][A-Za-z0-9_]*)(?:\|([^}]*))?\}")
        return pat.sub(lambda m: os.environ.get(m.group(1), m.group(2) or m.group(0)), value)
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    return value


def load_config(path: str | Path, overrides: list[str] | None = None) -> dict:
    p = Path(path)
    if not p.is_absolute():
        candidates = [Path.cwd() / p, Path(__file__).resolve().parents[1] / p]
        p = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
    if not p.exists():
        raise FileNotFoundError(f"Experiment config not found: {p}")
    cfg = _expand_env(yaml.safe_load(p.read_text(encoding="utf-8")))
    for item in overrides or []:
        key, sep, raw = item.partition("=")
        if not sep:
            raise ValueError(f"Override must be dotted.key=value, got {item!r}")
        node = cfg
        parts = key.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = _expand_env(yaml.safe_load(raw))
    cfg["_config_path"] = str(p)
    return cfg


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False


def environment_info() -> dict:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        if torch.cuda.is_available() else [],
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def load_model(model_cfg: dict):
    name = str(model_cfg.get("name", "")).lower()
    if name == "da360":
        from da360 import DA360Wrapper
        kw = {k: v for k, v in model_cfg.items() if k != "name"}
        kw.setdefault("repo", str(ROOT / "third_party" / "DA360"))
        kw.setdefault("weights", str(ROOT / "weights" / "da360" / "DA360_large.pth"))
        return DA360Wrapper(**kw)
    from models.depth_model import build_model
    return build_model(dict(model_cfg))


def load_dataset(data_cfg: dict, *, height: int | None = None, width: int | None = None,
                 limit: int | None = None):
    # Ensure ROOT is at sys.path[0] so 'datasets' always resolves to Lokesh/datasets
    if str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

    # Purge any foreign or shadowed 'datasets' module (e.g. from DA360 repo)
    if "datasets" in sys.modules:
        mod = sys.modules["datasets"]
        if getattr(mod, "__file__", None) and not str(mod.__file__).startswith(str(ROOT)):
            for m in list(sys.modules):
                if m == "datasets" or m.startswith("datasets."):
                    del sys.modules[m]

    from datasets.panorama import PanoramaDataset
    root = Path(data_cfg["root"])
    if not root.is_absolute():
        root = (ROOT / root).resolve()
    list_file = data_cfg.get("list", "test.txt")
    cap = limit if limit is not None else data_cfg.get("max_scenes", data_cfg.get("limit"))
    ds = PanoramaDataset(
        str(root), list_file,
        height=height or int(data_cfg.get("height", 512)),
        width=width or int(data_cfg.get("width", 1024)),
        name=data_cfg.get("name", data_cfg.get("dataset", "synthetic")),
        limit=cap,
        depth_scale=data_cfg.get("depth_scale"),
        max_depth=data_cfg.get("max_depth"),
        min_depth=data_cfg.get("min_depth"),
        exr_scale=data_cfg.get("exr_scale"),
    )
    if len(ds) == 0:
        raise RuntimeError(f"Dataset list produced zero samples: {root / list_file}")
    return ds


def scene_group(scene_id: str) -> str:
    """Environment/house grouping, so neighboring frames are never split across folds."""
    sid = str(scene_id).replace("\\", "/")
    m = re.match(r"(scene_\d+)", sid)
    if m:
        return m.group(1)
    m = re.match(r"((?:Indoor|Outdoor)_\d+)_", sid)
    if m:
        return m.group(1)
    m = re.match(r"(.+?)_\d+$", sid)
    if m:
        return m.group(1)
    return sid.split("/")[0]


def _fit_mask(valid: np.ndarray, protocol: str, max_lat: float = 30.0) -> np.ndarray:
    if protocol == "align-all":
        return valid.copy()
    if protocol == "align-equatorial":
        from geometry.spherical import latitude_map
        return valid & (np.abs(latitude_map(*valid.shape)) < max_lat)
    raise ValueError(f"Unknown evaluation protocol: {protocol}")


def align_prediction(pred: np.ndarray, gt: np.ndarray, valid: np.ndarray, model,
                     protocol: str = "align-all", mode: str = "auto",
                     min_depth: float = 0.1, max_depth: float = 100.0) -> np.ndarray:
    """Convert model-space output to metric range with explicit affine/scale-only options.

    For disparity p, scale-only fits 1/gt ~= s*p (no intercept).
    Affine fits 1/gt ~= s*p+t. For depth models, scale-only fits a single multiplicative factor.
    """
    from evaluation.metrics import to_metric_depth
    space = model.spec.space
    scale = model.spec.scale
    p = np.asarray(pred, dtype=np.float64)
    g = np.nan_to_num(np.asarray(gt, dtype=np.float64), nan=1.0)
    mask = _fit_mask(valid, protocol)
    if mode == "auto":
        mode = "affine" if space == "disparity" else ("none" if scale == "metric" else "scale")
    if space == "disparity" and mode == "scale":
        m = mask & np.isfinite(p) & (p > 1e-8)
        if m.sum() < 32:
            raise RuntimeError("Too few valid pixels for scale-only disparity alignment")
        target = 1.0 / np.clip(g[m], min_depth, max_depth)
        denom = float(np.dot(p[m], p[m]))
        s = float(np.dot(p[m], target) / max(denom, 1e-12))
        disp = np.clip(s * p, 1.0 / max_depth, 1.0 / min_depth)
        return 1.0 / disp
    if space == "depth" and mode == "scale":
        return to_metric_depth(p, g, mask, space="depth", mode="median",
                               min_depth=min_depth, max_depth=max_depth)[0]
    if mode == "none":
        if not (space == "depth" and scale == "metric"):
            raise ValueError("Raw/no-alignment protocol requires metric depth output")
        return np.clip(np.nan_to_num(p, nan=max_depth), min_depth, max_depth)
    if mode == "affine":
        return to_metric_depth(p, g, mask, space=space, mode="affine",
                               min_depth=min_depth, max_depth=max_depth)[0]
    if mode in ("median", "lsq"):
        return to_metric_depth(p, g, mask, space=space, mode=mode,
                               min_depth=min_depth, max_depth=max_depth)[0]
    raise ValueError(f"Unsupported alignment mode {mode!r}")


def band_metrics(pred_depth: np.ndarray, gt: np.ndarray, valid: np.ndarray,
                 min_depth: float = 0.1, max_depth: float = 100.0) -> dict:
    from evaluation.metrics import compute_metrics
    from geometry.spherical import latitude_map
    lat = np.abs(latitude_map(*gt.shape))
    valid0 = valid & np.isfinite(gt) & (gt >= min_depth) & (gt <= max_depth)
    bands = {"all": valid0}
    edges = [0, 15, 30, 45, 60, 75, 90]
    for lo, hi in zip(edges[:-1], edges[1:]):
        bands[f"{lo}-{hi}"] = valid0 & (lat >= lo) & ((lat < hi) if hi < 90 else (lat <= hi))
    return {name: compute_metrics(pred_depth, gt, mask) for name, mask in bands.items()}


def evaluate_one(pred: np.ndarray, sample, model, *, protocol: str = "align-all",
                 align: str = "auto", min_depth: float = 0.1, max_depth: float = 100.0) -> dict:
    depth = align_prediction(pred, sample.depth, sample.valid, model, protocol, align, min_depth, max_depth)
    return band_metrics(depth, sample.depth, sample.valid, min_depth, max_depth)


def cluster_bootstrap_gain(baseline: dict[str, float], method: dict[str, float],
                           groups: dict[str, str], n_boot: int = 2000, seed: int = 0) -> dict:
    """Paired cluster bootstrap on per-scene metric dictionaries; positive gain means lower error."""
    ids = sorted(set(baseline) & set(method))
    by_group: dict[str, list[float]] = {}
    for sid in ids:
        b, x = baseline[sid], method[sid]
        if np.isfinite(b) and np.isfinite(x) and b > 0:
            by_group.setdefault(groups[sid], []).append((b - x) / b)
    vals = np.asarray([np.mean(v) for v in by_group.values()], dtype=float)
    if len(vals) == 0:
        return {"n_scenes": 0, "n_groups": 0, "median_gain": float("nan"), "ci95": [float("nan"), float("nan")]}
    rng = np.random.default_rng(seed)
    boot = np.median(vals[rng.integers(0, len(vals), size=(n_boot, len(vals)))], axis=1)
    return {
        "n_scenes": len(ids), "n_groups": len(vals),
        "median_gain": float(np.median(vals)),
        "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
    }


def prepare_output(path: str | Path, overwrite: bool = False) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    if p.exists() and any(p.iterdir()) and not overwrite:
        raise FileExistsError(f"Output directory is non-empty: {p}. Pass --overwrite or choose a fresh output_dir.")
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if hasattr(x, "item") else str(x)),
                 encoding="utf-8")


def logger_for(output_dir: Path, name: str):
    import logging
    log_dir = output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    for handler in (logging.StreamHandler(sys.stdout),
                    logging.FileHandler(log_dir / "run.log", encoding="utf-8")):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger