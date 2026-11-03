#!/usr/bin/env python3
"""Runner for Method 3: Structured3D Real-World Foundation Benchmark.

Independent execution script.
Usage:
    python run.py [--config config.yaml] [--max_scenes 5]
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")  # PanoX distance maps are EXR; must precede `import cv2`
import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml

# Add paths
SCRIPT_DIR = Path(__file__).resolve().parent
AURINDUM_DIR = SCRIPT_DIR.parent
METHOD1_DIR = AURINDUM_DIR / "1_gradient_polar_fusion"
METHOD2_DIR = AURINDUM_DIR / "2_mobius_tta_ensembling"

for p in [AURINDUM_DIR, METHOD1_DIR, METHOD2_DIR]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from best_model.tracker import BestModelTracker
from datasets.synthetic import _texture_bank, random_scene, render_erp
from models.depth_model import EncodedDepthOracle, MiDaSWrapper
from tta_ensemble import MobiusTTAEnsemble
from evaluation.protocol import group_of, default_protocols, format_band_table, format_table, summarize_methods

# Local modules
from benchmark_evaluator import run_single_benchmark_scene
from prepare_data import find_structured3d_data, load_structured3d_pair


def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "method3_benchmark.log"

    logger = logging.getLogger("Method3_Structured3DBenchmark")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    fh = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def load_model(cfg_model: Dict, logger: logging.Logger):
    """Loads depth model wrapper with automatic fallback and server path resolution."""
    model_name = str(cfg_model.get("name", "dpt_hybrid_384")).lower()
    logger.info(f"Initializing model wrapper: {model_name}...")

    # Check for DAP on GPU server
    if "dap" in model_name:
        try:
            from models.depth_model import DAPWrapper
            repo = cfg_model.get("repo", "third_party/DAP")
            weights = cfg_model.get("weights", "weights/dap/model.pth")
            repo_path = str(AURINDUM_DIR / repo) if not os.path.isabs(repo) else repo
            weights_path = str(AURINDUM_DIR / weights) if not os.path.isabs(weights) else weights
            device = cfg_model.get("device", "cuda" if torch.cuda.is_available() else "cpu")
            wrapper = DAPWrapper(repo=repo_path, weights=weights_path, device=device)
            logger.info(f"Loaded DAP foundation model from {weights_path} ({device}).")
            return wrapper
        except Exception as e:
            if not cfg_model.get("allow_model_fallback", False):
                raise RuntimeError(f"Could not load DAP: {e} (set model.allow_model_fallback to fall back to MiDaS)") from e
            logger.warning(f"Could not load DAP ({e}); falling back to MiDaS (allow_model_fallback=true).")

    try:
        wrapper = MiDaSWrapper(
            model_type=cfg_model.get("name", "dpt_hybrid_384"),
            weights=str(AURINDUM_DIR / cfg_model.get("weights", f"weights/{cfg_model.get('name', 'dpt_hybrid_384')}.pt")),
            device=cfg_model.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        )
        logger.info(f"Loaded MiDaS wrapper successfully.")
        return wrapper
    except Exception as e:
        if not cfg_model.get("allow_oracle_fallback", False):
            raise RuntimeError(f"Could not load model {model_name}: {e} (set model.allow_oracle_fallback to use the oracle)") from e
        logger.warning(f"Could not load MiDaS ({e}); falling back to EncodedDepthOracle.")
        return EncodedDepthOracle(strength=0.3, power=2.0)


def main():
    parser = argparse.ArgumentParser(description="Method 3: Real Structured3D Panoramic Benchmark")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--max_scenes", type=int, default=None, help="Number of real scenes to evaluate")
    parser.add_argument("--set", dest="overrides", action="append", default=[],
                        help="Override a config value, dotted key=YAML value (repeatable), "
                             "e.g. --set mobius_tta.gate_lat=[30,55]")
    parser.add_argument("--tag", type=str, default=None,
                        help="Suffix appended to the output folder and tracker benchmark name (ablations)")
    args = parser.parse_args()

    cfg_path = SCRIPT_DIR / args.config
    if not cfg_path.exists():  # never fall back silently: a typo would run a different model/dataset
        raise FileNotFoundError(f"Config not found: {cfg_path}")

    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    for ov in args.overrides:
        key, _, val = ov.partition("=")
        node = cfg
        parts = key.split(".")
        for k in parts[:-1]:
            node = node.setdefault(k, {})
        node[parts[-1]] = yaml.safe_load(val)
    if args.tag:
        cfg["evaluation"]["output_dir"] = cfg["evaluation"].get("output_dir", "outputs") + "_" + args.tag
        cfg["evaluation"]["log_dir"] = cfg["evaluation"].get("log_dir", "logs") + "_" + args.tag
        cfg["benchmark_suffix"] = cfg.get("benchmark_suffix", "") + "_" + args.tag
    if args.max_scenes:
        cfg["data"]["max_scenes"] = args.max_scenes

    out_dir = SCRIPT_DIR / cfg["evaluation"].get("output_dir", "outputs")
    log_dir = SCRIPT_DIR / cfg["evaluation"].get("log_dir", "logs")
    curated_dir = SCRIPT_DIR / cfg["data"].get("curated_dir", "data/curated_scenes")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(log_dir)
    logger.info("=" * 75)
    logger.info(f"🚀 Starting Method 3: Comparative Benchmark on {cfg['data'].get('dataset', 'structured3d')} panoramas")
    logger.info("=" * 75)

    # 1. Discover the evaluation panoramas.
    #    data.dataset: 'structured3d' (default) | 'panox' | any datasets/panorama.py preset.
    #    If a split list (data.list, default test.txt) exists under the dataset root, the generic
    #    PanoramaDataset loader is used (presets carry units, valid range and PanoX sky masking);
    #    otherwise the legacy Structured3D discovery below. data.max_scenes: null = all.
    dataset_name = cfg["data"].get("dataset", "structured3d")
    data_root = cfg["data"].get("root", f"data/{dataset_name}")
    list_name = cfg["data"].get("list", "test.txt")
    max_scenes = cfg["data"].get("max_scenes")
    pano_ds = None
    for cand in [AURINDUM_DIR / data_root, AURINDUM_DIR.parent.parent / "Data" / dataset_name,
                 AURINDUM_DIR.parent / "Data" / dataset_name]:
        if (cand / list_name).is_file():
            from datasets.panorama import PanoramaDataset
            pano_ds = PanoramaDataset(str(cand), list_name, height=cfg["data"].get("height", 256),
                                      width=cfg["data"].get("width", 512), name=dataset_name,
                                      limit=max_scenes)
            logger.info(f"Loaded {len(pano_ds)} {dataset_name} panoramas from {cand / list_name}")
            break
    if pano_ds is not None:
        scenes = [{"id": f"{dataset_name}_{i}", "index": i} for i in range(len(pano_ds))]
    elif dataset_name == "structured3d":
        scenes = find_structured3d_data(AURINDUM_DIR, cfg_root=data_root, max_scenes=max_scenes or 10 ** 6)
    else:
        raise FileNotFoundError(f"No split list {list_name} found for dataset {dataset_name} (root {data_root})")

    # Fallback to procedural scenes if not found
    using_synthetic_fallback = len(scenes) == 0
    if using_synthetic_fallback and not cfg["data"].get("allow_synthetic_fallback", False):
        raise FileNotFoundError(
            f"No {dataset_name} panoramas found (root '{data_root}', list '{list_name}'). Refusing to substitute "
            f"procedural scenes silently; set data.allow_synthetic_fallback: true for a smoke test.")
    if using_synthetic_fallback:
        logger.warning(f"No {dataset_name} scenes found in {data_root}; falling back to procedural scenes.")
        scenes = [{"id": f"synthetic_{i}"} for i in range(max_scenes or 10)]

    # 2. Initialize models and ensemble
    model = load_model(cfg.get("model", {}), logger)
    m2_cfg = cfg.get("mobius_tta", {})
    m2_ensemble = MobiusTTAEnsemble(
        model=model,
        passes=m2_cfg.get("passes"),
        scales=m2_cfg.get("scales", [1.0]),
        fusion_mode=m2_cfg.get("fusion_mode", "distortion_weighted"),
        reanchor=m2_cfg.get("reanchor", "auto"),
        anchor_max_lat=m2_cfg.get("anchor_max_lat", 30.0),
        gate_lat=m2_cfg.get("gate_lat"),
    )
    ev_cfg = cfg.get("evaluation", {})
    protocols = tuple(ev_cfg.get("protocols") or default_protocols(model))
    min_depth = float(ev_cfg.get("min_depth", 0.1))
    max_depth = float(ev_cfg.get("max_depth", 10.0))

    # 3. Benchmark evaluation
    H = cfg["data"].get("height", 256)
    W = cfg["data"].get("width", 512)

    all_methods = ["Baseline", "Tangent_Spatial", "Method1_GradientFusion", "Method2_MobiusTTA", "Control_YawEnsemble"]
    sel = cfg["evaluation"].get("methods")
    method_keys = [m for m in all_methods if m == "Baseline" or not sel or m in sel]
    accumulators: Dict[str, List[Dict]] = {m: [] for m in method_keys}
    sample_vis = None
    tex_bank = _texture_bank(seed=42)

    for idx, sc in enumerate(scenes):
        scene_id = sc["id"]
        logger.info(f"--> Evaluating Panorama [{idx + 1}/{len(scenes)}]: {scene_id}...")

        if pano_ds is not None:
            smp = pano_ds[sc["index"]]
            sc["id"] = smp.id
            rgb, gt_depth, valid_gt = smp.rgb, np.nan_to_num(smp.depth, nan=0.0), smp.valid
            valid_gt = valid_gt & (gt_depth >= min_depth) & (gt_depth <= max_depth)
        elif not using_synthetic_fallback:
            rgb, gt_depth, valid_gt = load_structured3d_pair(
                sc["rgb_path"], sc["depth_path"], target_hw=(H, W)
            )
            valid_gt = valid_gt & (gt_depth >= min_depth) & (gt_depth <= max_depth)
        else:
            rng = np.random.default_rng(idx + 300)
            sc_obj = random_scene(rng, len(tex_bank))
            rgb, gt_depth = render_erp(sc_obj, tex_bank, height=H, width=W)
            valid_gt = np.isfinite(gt_depth) & (gt_depth > 0.05) & (gt_depth < 50.0)

        scene_results = run_single_benchmark_scene(
            scene_info=sc,
            rgb=rgb,
            gt_depth=gt_depth,
            valid_gt=valid_gt,
            model=model,
            m1_solver=None,
            m2_ensemble=m2_ensemble,
            phi_thresh=cfg.get("method1", {}).get("phi_threshold", 45.0),
            protocols=protocols,
            min_depth=min_depth,
            max_depth=max_depth,
            m1_cfg=cfg.get("method1", {}),
            methods=cfg["evaluation"].get("methods"),
        )

        for m_name in method_keys:
            accumulators[m_name].append(scene_results[m_name])

        if sample_vis is None:
            sample_vis = {"rgb": rgb, "gt": gt_depth, "preds": scene_results["predictions"]}

        hp = protocols[0]
        pol = {m: scene_results[m][hp]["75-90"]["abs_rel"] for m in method_keys}
        logger.info(f"    Polar AbsRel (75-90°, {hp}): " + " | ".join(f"{m.split('_')[0]}={v:.4f}" for m, v in pol.items()))

    # Scenes from the same house / environment are correlated: bootstrap and Wilcoxon run over clusters.
    groups = [group_of(sc["id"]) for sc in scenes]
    logger.info(f"Statistics are cluster-robust: {len(scenes)} scenes in {len(set(groups))} groups")
    summary = summarize_methods(accumulators, protocols, groups=groups)
    headline = protocols[0]
    for proto in protocols:
        for stat in ("median", "mean"):
            logger.info("\n" + "=" * 95)
            logger.info(f"🏆 {dataset_name.upper()} BENCHMARK  [{proto}, {stat} over {len(scenes)} scenes, depth clamp "
                        f"{min_depth}-{max_depth} m]")
            for line in format_table(summary[proto], stat):
                logger.info(line)
    for name in method_keys[1:]:
        logger.info(f"\n--- {name} vs Baseline, per band [{protocols[0]}, median] ---")
        for line in format_band_table(summary[protocols[0]], name):
            logger.info(line)
    logger.info("=" * 95)

    record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark": (dataset_name if not using_synthetic_fallback else "synthetic_fallback") + cfg.get("benchmark_suffix", ""),
        "num_scenes": len(scenes),
        "scene_ids": [sc["id"] for sc in scenes],
        "config": cfg,
        "summary": summary,
        "per_scene": {m: accumulators[m] for m in method_keys},
    }
    with open(out_dir / "benchmark_summary.json", "w") as f:
        json.dump(record, f, indent=2)

    csv_lines = ["Protocol,Stat,Method,Global_AbsRel,Polar_60_75_AbsRel,Polar_75_90_AbsRel,Delta1,WinRate_75_90,"
                 "Gain_75_90_median,Gain_CI_low,Gain_CI_high,P_Wilcoxon_75_90"]
    for proto in protocols:
        for stat in ("median", "mean"):
            for m_name in method_keys:
                m = summary[proto][m_name][stat]
                wr = summary[proto][m_name]["win_rate_vs_baseline"].get("75-90", float("nan"))
                pt = summary[proto][m_name].get("paired_vs_baseline", {}).get("75-90", {})
                g = [pt.get(k, float("nan")) for k in ("rel_gain_median", "ci_low", "ci_high", "p_wilcoxon")]
                csv_lines.append(f"{proto},{stat},{m_name},{m['all']['abs_rel']:.4f},{m['60-75']['abs_rel']:.4f},"
                                 f"{m['75-90']['abs_rel']:.4f},{m['all']['d1']:.4f},{wr:.3f},"
                                 f"{g[0]:.4f},{g[1]:.4f},{g[2]:.4f},{g[3]:.4g}")
    with open(out_dir / "benchmark_table.csv", "w") as f:
        f.write("\n".join(csv_lines) + "\n")
    logger.info(f"Saved benchmark results to {out_dir / 'benchmark_summary.json'}")

    winner_name = min(method_keys, key=lambda m: summary[headline][m]["median"]["75-90"]["abs_rel"])
    logger.info(f"🏆 Best polar (75-90°) method on this benchmark [{headline}, median]: {winner_name}")

    tracker = BestModelTracker(str(AURINDUM_DIR / "best_model"), benchmark=record["benchmark"])
    win_pred_key = {"Baseline": "baseline", "Tangent_Spatial": "tangent_spatial",
                    "Method1_GradientFusion": "method1_grad", "Method2_MobiusTTA": "method2_mobius",
                    "Control_YawEnsemble": "control_yaw"}[winner_name]
    tracker.update_if_best(
        method_name=f"Structured3D: {winner_name}",
        config=cfg,
        metrics=summary[headline][winner_name]["median"],
        rgb=sample_vis["rgb"],
        gt_depth=sample_vis["gt"],
        pred_depth=sample_vis["preds"][win_pred_key],
        notes=f"Median over {len(scenes)} Structured3D panoramas, protocol {headline}."
    )


if __name__ == "__main__":
    main()
