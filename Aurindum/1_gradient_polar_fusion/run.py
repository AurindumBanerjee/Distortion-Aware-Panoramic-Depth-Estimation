#!/usr/bin/env python3
"""Runner for Method 1: Gradient-Domain Polar Fusion & Shift-Decoupled Alignment.

Independent execution script.
Usage:
    python run.py [--config config.yaml] [--num_scenes 6] [--blending_mode gradient_poisson]
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
from geometry.erp_projection import sample_erp
from geometry.spherical import erp_lonlat_grid, latitude_map, lonlat_to_xyz
from geometry.tangent_plane import (
    generate_tangent_plane,
    erp_to_tangent,
    tangent_to_erp,
)
from models.depth_model import EncodedDepthOracle, MiDaSWrapper

# Local modules
from gradient_blending import gradient_domain_polar_fuse
from shift_alignment import align_tangent_disparity_to_erp
from polar_views import fuse_polar, polar_predictions


def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "method1_gradient.log"

    logger = logging.getLogger("Method1_GradientPolarFusion")
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


def run_tangent_pass(
    model,
    rgb_erp: np.ndarray,
    tangent_centers: List[Tuple[float, float]],
    fov_deg: float,
    resolution: int
) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Runs perspective inference on tangent planes and projects back to ERP."""
    results = []
    H, W = rgb_erp.shape[:2]

    for theta_c, phi_c in tangent_centers:
        plane = generate_tangent_plane(lon_deg=theta_c, lat_deg=phi_c, fov_deg=fov_deg, size=resolution)
        # 1. Project ERP RGB to tangent plane
        rgb_tan = erp_to_tangent(rgb_erp, plane)

        # 2. Predict with model (in perspective mode)
        pred_tan = model.predict(rgb_tan, kind="perspective")

        # 3. Project back to ERP grid
        warp_res = tangent_to_erp(pred_tan, plane, height=H, width=W)
        pred_on_erp = warp_res.values
        cos_ray = warp_res.cos_axis
        valid_mask = warp_res.valid
        results.append((pred_on_erp, cos_ray, valid_mask))

    return results


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
    model,
    cfg: Dict,
    logger: logging.Logger
) -> Tuple[Dict, Dict, np.ndarray, np.ndarray]:
    """Runs baseline and Method 1 on a single scene, returning metrics and depth maps."""
    H, W = gt_range.shape
    phi_deg_map = np.abs(latitude_map(H, W))

    # --- 1. Baseline ERP Pass ---
    pred_erp = model.predict(rgb, kind="erp")

    # --- 2-3. Polar views (tangent or rotated ERP), aligned to the ERP prediction in fusion space ---
    tan_cfg = cfg.get("tangent", {})
    phi_thresh = tan_cfg.get("phi_threshold", 45.0)
    merged_f, fs, infos = polar_predictions(
        model, rgb, pred_erp, phi_deg_map,
        source=cfg.get("polar_source", "auto"),
        fov_deg=tan_cfg.get("fov_deg", 90.0), resolution=tan_cfg.get("resolution", 384),
        anchor_max_lat=cfg.get("alignment", {}).get("anchor_max_lat", 60.0))
    for info in infos:
        logger.debug(f"    polar view: {info}")

    # --- 4. Fusion ---
    blend_cfg = cfg.get("blending", {})
    fused_range = fuse_polar(
        pred_erp, merged_f, fs, phi_deg_map, mode=blend_cfg.get("mode", "gradient_poisson"),
        phi_threshold=phi_thresh, blend_margin=blend_cfg.get("blend_margin", 10.0), rgb=rgb,
        texture_tau=blend_cfg.get("texture_tau", 0.0), texture_gate_mode=blend_cfg.get("texture_gate_mode", "erp"))

    # --- 5. Metric Alignment & Evaluation (all protocols) ---
    ev = cfg.get("evaluation", {})
    protocols = tuple(ev.get("protocols") or default_protocols(model))
    min_d, max_d = float(ev.get("min_depth", 0.05)), float(ev.get("max_depth", 50.0))
    metrics_base, metrics_fused = {}, {}
    base_metric = fused_metric = None
    for proto in protocols:
        bm = align_to_gt(pred_erp, gt_range, valid_gt, model, protocol=proto, min_depth=min_d, max_depth=max_d)
        fm = align_to_gt(fused_range, gt_range, valid_gt, model, protocol=proto, min_depth=min_d, max_depth=max_d)
        metrics_base[proto] = per_band_metrics(bm, gt_range, valid_gt)
        metrics_fused[proto] = per_band_metrics(fm, gt_range, valid_gt)
        if base_metric is None:
            base_metric, fused_metric = bm, fm

    return metrics_base, metrics_fused, base_metric, fused_metric


def main():
    parser = argparse.ArgumentParser(description="Method 1: Gradient-Domain Polar Fusion")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--num_scenes", type=int, default=None, help="Number of test scenes")
    parser.add_argument("--blend_mode", type=str, default=None, choices=["gradient_poisson", "cosine_ramp"])
    args = parser.parse_args()

    # Load configuration
    cfg_path = SCRIPT_DIR / args.config
    if not cfg_path.exists():  # never fall back silently: a typo would run a different model/dataset
        raise FileNotFoundError(f"Config not found: {cfg_path}")

    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    if args.num_scenes:
        cfg["evaluation"]["num_scenes"] = args.num_scenes
    if args.blend_mode:
        cfg["blending"]["mode"] = args.blend_mode

    out_dir = SCRIPT_DIR / cfg["evaluation"].get("output_dir", "outputs")
    log_dir = SCRIPT_DIR / cfg["evaluation"].get("log_dir", "logs")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(log_dir)
    logger.info("=" * 70)
    logger.info("🚀 Starting Method 1: Gradient-Domain Polar Fusion & Shift Alignment")
    logger.info(f"Config: Blend Mode={cfg['blending']['mode']}, Phi Threshold={cfg['tangent']['phi_threshold']}°")
    logger.info("=" * 70)

    # Initialize model
    model = load_model(cfg.get("model", {}), logger)

    # Run over test scenes
    num_scenes = cfg["evaluation"].get("num_scenes", 6)
    H = cfg["evaluation"].get("height", 256)
    W = cfg["evaluation"].get("width", 512)

    all_base_metrics = []
    all_fused_metrics = []
    sample_vis = None
    tex_bank = _texture_bank(seed=42)

    for s_idx in range(num_scenes):
        logger.info(f"--> Rendering & evaluating Scene {s_idx + 1}/{num_scenes}...")
        rng = np.random.default_rng(s_idx + 100)
        scene = random_scene(rng, len(tex_bank))
        rgb, gt_range = render_erp(scene, tex_bank, height=H, width=W)
        valid_gt = np.isfinite(gt_range) & (gt_range > 0.05) & (gt_range < 50.0)

        m_base, m_fused, base_metric, fused_metric = evaluate_scene(
            s_idx, rgb, gt_range, valid_gt, model, cfg, logger
        )
        all_base_metrics.append(m_base)
        all_fused_metrics.append(m_fused)

        if sample_vis is None:
            sample_vis = (rgb, gt_range, fused_metric)

        hp = next(iter(m_base))
        logger.info(f"    Scene {s_idx + 1}: Polar AbsRel (75-90°, {hp}) Baseline={m_base[hp]['75-90']['abs_rel']:.4f} "
                    f"-> Method 1={m_fused[hp]['75-90']['abs_rel']:.4f}")

    protocols = list(all_base_metrics[0].keys())
    summary = summarize_methods({"Baseline": all_base_metrics, "Method1_GradientFusion": all_fused_metrics}, protocols)
    headline = protocols[0]
    for proto in protocols:
        for name in ['Method1_GradientFusion']:
            logger.info("\n" + "=" * 90)
            logger.info(f"📊 {name} vs BASELINE  [{proto}, median over {num_scenes} scenes; paired Wilcoxon + bootstrap CI]")
            for line in format_band_table(summary[proto], name):
                logger.info(line)
    logger.info("=" * 90)

    avg_base = summary[headline]["Baseline"]["median"]
    avg_fused = summary[headline]["Method1_GradientFusion"]["median"]
    metrics_record = {
        "method": "Gradient-Domain Polar Fusion",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark": "synthetic" + cfg.get("benchmark_suffix", ""),
        "config": cfg,
        "headline": {"protocol": headline, "stat": "median"},
        "baseline_metrics": avg_base,
        "method1_metrics": avg_fused,
        "summary": summary,
        "per_scene": {"Baseline": all_base_metrics, "Method1_GradientFusion": all_fused_metrics},
    }
    with open(out_dir / "metrics_summary.json", "w") as f:
        json.dump(metrics_record, f, indent=2)
    logger.info(f"Saved metrics summary to {out_dir / 'metrics_summary.json'}")

    tracker = BestModelTracker(str(AURINDUM_DIR / "best_model"), benchmark="synthetic" + cfg.get("benchmark_suffix", ""))
    is_best = tracker.update_if_best(
        method_name="Gradient-Domain Polar Fusion",
        config=cfg,
        metrics=avg_fused,
        rgb=sample_vis[0],
        gt_depth=sample_vis[1],
        pred_depth=sample_vis[2],
        notes=f"Median over {num_scenes} synthetic scenes, protocol {headline}."
    )
    if is_best:
        logger.info("🎉 NEW BEST on the synthetic benchmark: Method 1")


if __name__ == "__main__":
    main()
