#!/usr/bin/env python3
"""Runner for Method 2: Test-Time Möbius Augmentation & Equator-to-Pole Ensembling.

Independent execution script.
Usage:
    python run.py [--config config.yaml] [--num_scenes 6] [--fusion_mode distortion_weighted]
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml

# Add Aurindum root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
AURINDUM_DIR = SCRIPT_DIR.parent
if str(AURINDUM_DIR) not in sys.path:
    sys.path.insert(0, str(AURINDUM_DIR))

from best_model.tracker import BestModelTracker
from datasets.synthetic import _texture_bank, random_scene, render_erp
from evaluation.latitude_analysis import per_band_metrics
from evaluation.metrics import compute_metrics, to_metric_depth
from evaluation.protocol import BANDS, align_to_gt, default_protocols, format_band_table, summarize_methods
from geometry.spherical import latitude_map
from models.depth_model import EncodedDepthOracle, MiDaSWrapper

# Local modules
from mobius_transform import unwarp_depth_mobius, warp_erp_mobius
from tta_ensemble import MobiusTTAEnsemble


def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "method2_mobius.log"

    logger = logging.getLogger("Method2_MobiusTTA")
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


def align_prediction_to_gt(pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, model) -> np.ndarray:
    """Helper that adapts to depth/disparity and metric/affine model specifications."""
    space = getattr(model, "space", getattr(model.spec, "space", "depth"))
    if space == "disparity":
        mode = "affine"
    else:
        scale = getattr(model, "scale", getattr(model.spec, "scale", "metric"))
        mode = "none" if scale == "metric" else "lsq"
    aligned, _ = to_metric_depth(pred, gt, mask, space=space, mode=mode)
    return aligned


def evaluate_scene(
    scene_idx: int,
    rgb: np.ndarray,
    gt_range: np.ndarray,
    valid_gt: np.ndarray,
    ensemble: MobiusTTAEnsemble,
    cfg: Dict,
    logger: logging.Logger
) -> Tuple[Dict, Dict, np.ndarray, np.ndarray]:
    """Runs baseline and Method 2 on a single scene, returning metrics and depth maps."""
    H, W = gt_range.shape
    phi_deg_map = np.abs(latitude_map(H, W))

    # --- 1. Baseline ERP Pass ---
    pred_erp = ensemble.model.predict(rgb, kind="erp")

    # --- 2. Möbius TTA Multi-Pass Ensembling (identity pass reuses the baseline prediction) ---
    pred_mobius, diagnostics = ensemble.predict(rgb, identity_pred=pred_erp)
    for d in diagnostics[1:]:
        logger.debug(f"    pass pitch={d['pitch']:+.0f} scale={d['scale']:.3f} anchor a={d['anchor_a']:.4f} b={d['anchor_b']:.4f}")

    # --- 3. Metric Alignment & Evaluation (all protocols) ---
    ev = cfg.get("evaluation", {})
    protocols = tuple(ev.get("protocols") or default_protocols(ensemble.model))
    min_d, max_d = float(ev.get("min_depth", 0.05)), float(ev.get("max_depth", 50.0))
    from tta_ensemble import yaw_shift_ensemble
    pred_yaw = yaw_shift_ensemble(ensemble.model, rgb, n_passes=len(ensemble.passes), identity_pred=pred_erp,
                                  reanchor=ensemble.reanchor, anchor_max_lat=ensemble.anchor_max_lat)
    metrics_base, metrics_mobius, metrics_yaw = {}, {}, {}
    base_metric = mobius_metric = None
    for proto in protocols:
        ym = align_to_gt(pred_yaw, gt_range, valid_gt, ensemble.model, protocol=proto, min_depth=min_d, max_depth=max_d)
        metrics_yaw[proto] = per_band_metrics(ym, gt_range, valid_gt)
        bm = align_to_gt(pred_erp, gt_range, valid_gt, ensemble.model, protocol=proto, min_depth=min_d, max_depth=max_d)
        mm = align_to_gt(pred_mobius, gt_range, valid_gt, ensemble.model, protocol=proto, min_depth=min_d, max_depth=max_d)
        metrics_base[proto] = per_band_metrics(bm, gt_range, valid_gt)
        metrics_mobius[proto] = per_band_metrics(mm, gt_range, valid_gt)
        if base_metric is None:
            base_metric, mobius_metric = bm, mm

    return metrics_base, (metrics_mobius, metrics_yaw), base_metric, mobius_metric


def main():
    parser = argparse.ArgumentParser(description="Method 2: Test-Time Möbius Augmentation Ensembling")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--num_scenes", type=int, default=None, help="Number of test scenes")
    parser.add_argument("--fusion_mode", type=str, default=None, choices=["distortion_weighted", "median", "mean"])
    args = parser.parse_args()

    # Load configuration
    cfg_path = SCRIPT_DIR / args.config
    if not cfg_path.exists():  # never fall back silently: a typo would run a different model/dataset
        raise FileNotFoundError(f"Config not found: {cfg_path}")

    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    if args.num_scenes:
        cfg["evaluation"]["num_scenes"] = args.num_scenes
    if args.fusion_mode:
        cfg["mobius_tta"]["fusion_mode"] = args.fusion_mode

    out_dir = SCRIPT_DIR / cfg["evaluation"].get("output_dir", "outputs")
    log_dir = SCRIPT_DIR / cfg["evaluation"].get("log_dir", "logs")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(log_dir)
    logger.info("=" * 70)
    logger.info("🚀 Starting Method 2: Test-Time Möbius Augmentation (Möbius-TTA)")
    logger.info(f"Passes: {cfg['mobius_tta'].get('passes', cfg['mobius_tta'].get('scales'))}, Fusion: {cfg['mobius_tta']['fusion_mode']}")
    logger.info("=" * 70)

    # Initialize model and ensemble
    model = load_model(cfg.get("model", {}), logger)
    ensemble = MobiusTTAEnsemble(
        model=model,
        passes=cfg["mobius_tta"].get("passes"),
        scales=cfg["mobius_tta"].get("scales", [1.0]),
        fusion_mode=cfg["mobius_tta"].get("fusion_mode", "distortion_weighted"),
        reanchor=cfg["mobius_tta"].get("reanchor", "auto"),
        anchor_max_lat=cfg["mobius_tta"].get("anchor_max_lat", 30.0),
        gate_lat=cfg["mobius_tta"].get("gate_lat"),
    )

    # Run over test scenes
    num_scenes = cfg["evaluation"].get("num_scenes", 6)
    H = cfg["evaluation"].get("height", 256)
    W = cfg["evaluation"].get("width", 512)

    all_base_metrics = []
    all_mobius_metrics = []
    all_yaw_metrics = []
    sample_vis = None
    tex_bank = _texture_bank(seed=42)

    for s_idx in range(num_scenes):
        logger.info(f"--> Rendering & evaluating Scene {s_idx + 1}/{num_scenes}...")
        rng = np.random.default_rng(s_idx + 200)
        scene = random_scene(rng, len(tex_bank))
        rgb, gt_range = render_erp(scene, tex_bank, height=H, width=W)
        valid_gt = np.isfinite(gt_range) & (gt_range > 0.05) & (gt_range < 50.0)

        m_base, m_mob, base_metric, mob_metric = evaluate_scene(
            s_idx, rgb, gt_range, valid_gt, ensemble, cfg, logger
        )
        all_base_metrics.append(m_base)
        m_mob, m_yaw = m_mob
        all_mobius_metrics.append(m_mob)
        all_yaw_metrics.append(m_yaw)

        if sample_vis is None:
            sample_vis = (rgb, gt_range, mob_metric)

        hp = next(iter(m_base))
        logger.info(f"    Scene {s_idx + 1}: Polar AbsRel (75-90°, {hp}) Baseline={m_base[hp]['75-90']['abs_rel']:.4f} "
                    f"-> Möbius-TTA={m_mob[hp]['75-90']['abs_rel']:.4f}")

    protocols = list(all_base_metrics[0].keys())
    summary = summarize_methods({"Baseline": all_base_metrics, "Method2_MobiusTTA": all_mobius_metrics,
                                 "Control_YawEnsemble": all_yaw_metrics}, protocols)
    headline = protocols[0]
    for proto in protocols:
        for name in ['Method2_MobiusTTA', 'Control_YawEnsemble']:
            logger.info("\n" + "=" * 90)
            logger.info(f"📊 {name} vs BASELINE  [{proto}, median over {num_scenes} scenes; paired Wilcoxon + bootstrap CI]")
            for line in format_band_table(summary[proto], name):
                logger.info(line)
    logger.info("=" * 90)

    avg_base = summary[headline]["Baseline"]["median"]
    avg_mob = summary[headline]["Method2_MobiusTTA"]["median"]
    metrics_record = {
        "method": "Mobius TTA Ensembling",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark": "synthetic" + cfg.get("benchmark_suffix", ""),
        "config": cfg,
        "headline": {"protocol": headline, "stat": "median"},
        "baseline_metrics": avg_base,
        "mobius_metrics": avg_mob,
        "summary": summary,
        "per_scene": {"Baseline": all_base_metrics, "Method2_MobiusTTA": all_mobius_metrics,
                      "Control_YawEnsemble": all_yaw_metrics},
    }
    with open(out_dir / "metrics_summary.json", "w") as f:
        json.dump(metrics_record, f, indent=2)
    logger.info(f"Saved metrics summary to {out_dir / 'metrics_summary.json'}")

    tracker = BestModelTracker(str(AURINDUM_DIR / "best_model"), benchmark="synthetic" + cfg.get("benchmark_suffix", ""))
    is_best = tracker.update_if_best(
        method_name="Mobius TTA Ensembling",
        config=cfg,
        metrics=avg_mob,
        rgb=sample_vis[0],
        gt_depth=sample_vis[1],
        pred_depth=sample_vis[2],
        notes=f"Median over {num_scenes} synthetic scenes, protocol {headline}. Rotation+dilation Möbius passes, "
              f"equatorial re-anchoring, distortion-weighted fusion."
    )
    if is_best:
        logger.info("🎉 NEW BEST on the synthetic benchmark: Method 2")


if __name__ == "__main__":
    main()
