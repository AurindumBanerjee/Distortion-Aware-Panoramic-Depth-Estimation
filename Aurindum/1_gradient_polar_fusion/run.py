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
            logger.warning(f"Could not load DAP ({e}); trying MiDaS...")

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

    # --- 2. Tangent Passes for North and South Poles ---
    tan_cfg = cfg.get("tangent", {})
    fov = tan_cfg.get("fov_deg", 90.0)
    res = tan_cfg.get("resolution", 384)
    phi_thresh = tan_cfg.get("phi_threshold", 45.0)

    # Tangent centers: North Pole (0, 90) and South Pole (0, -90)
    tangent_centers = [(0.0, 90.0), (0.0, -90.0)]
    tan_results = run_tangent_pass(model, rgb, tangent_centers, fov, res)

    # --- 3. Align Tangent Disparities to Baseline ---
    aligned_ranges = []
    for pred_tan_erp, cos_ray, valid_mask in tan_results:
        aligned_r, fit_info = align_tangent_disparity_to_erp(
            tangent_disp_on_erp=pred_tan_erp,
            erp_disp_baseline=pred_erp,
            cos_ray=cos_ray,
            phi_deg_map=phi_deg_map,
            anchor_max_lat=cfg.get("alignment", {}).get("anchor_max_lat", 35.0)
        )
        aligned_ranges.append(aligned_r)

    # Merge tangent views
    merged_tangent = np.full_like(gt_range, np.nan)
    for r_tan in aligned_ranges:
        valid_t = np.isfinite(r_tan)
        merged_tangent[valid_t] = r_tan[valid_t]

    # --- 4. Gradient-Domain Fusion ---
    blend_cfg = cfg.get("blending", {})
    blend_mode = blend_cfg.get("mode", "gradient_poisson")

    if blend_mode == "gradient_poisson":
        fused_range = gradient_domain_polar_fuse(
            d_erp=pred_erp,
            d_tangent=merged_tangent,
            weight_map=np.ones_like(pred_erp),
            phi_deg_map=phi_deg_map,
            phi_threshold=phi_thresh,
            blend_margin=blend_cfg.get("blend_margin", 10.0),
            solver_mode=blend_cfg.get("poisson_solver", "sor")
        )
    else:
        # Standard cosine blending fallback
        alpha = np.clip((phi_deg_map - (phi_thresh - 10)) / 20.0, 0.0, 1.0)
        alpha = 0.5 * (1.0 - np.cos(np.pi * alpha))
        valid_t = np.isfinite(merged_tangent)
        fused_range = np.where(valid_t, (1.0 - alpha) * pred_erp + alpha * merged_tangent, pred_erp)

    # --- 5. Metric Alignment & Evaluation ---
    proto = cfg.get("evaluation", {}).get("align_protocol", "align-equatorial")
    eq_mask = valid_gt & (phi_deg_map < 30.0)

    # Align baseline and fused to GT
    base_metric = align_prediction_to_gt(pred_erp, gt_range, eq_mask, model)
    fused_metric = align_prediction_to_gt(fused_range, gt_range, eq_mask, model)

    metrics_base = per_band_metrics(base_metric, gt_range, valid_gt)
    metrics_fused = per_band_metrics(fused_metric, gt_range, valid_gt)

    return metrics_base, metrics_fused, base_metric, fused_metric


def main():
    parser = argparse.ArgumentParser(description="Method 1: Gradient-Domain Polar Fusion")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--num_scenes", type=int, default=None, help="Number of test scenes")
    parser.add_argument("--blend_mode", type=str, default=None, choices=["gradient_poisson", "cosine_ramp"])
    args = parser.parse_args()

    # Load configuration
    cfg_path = SCRIPT_DIR / args.config
    if not cfg_path.exists():
        cfg_path = SCRIPT_DIR / "config.yaml"

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

        logger.info(f"    Scene {s_idx + 1}: Polar AbsRel (75-90°) Baseline={m_base['75-90']['abs_rel']:.4f} "
                    f"-> Method 1={m_fused['75-90']['abs_rel']:.4f}")

    # Aggregate metrics across scenes
    def average_metrics(list_m: List[Dict]) -> Dict:
        avg = {}
        keys = list_m[0].keys()
        for k in keys:
            avg[k] = {}
            subkeys = list_m[0][k].keys()
            for sk in subkeys:
                avg[k][sk] = float(np.mean([m[k][sk] for m in list_m]))
        return avg

    avg_base = average_metrics(all_base_metrics)
    avg_fused = average_metrics(all_fused_metrics)

    logger.info("\n" + "=" * 70)
    logger.info("📊 SUMMARY RESULTS ACROSS ALL SCENES")
    logger.info(f"{'Band':<15} | {'Baseline AbsRel':<18} | {'Method 1 AbsRel':<18} | {'Improvement':<12}")
    logger.info("-" * 70)

    bands = ["all", "0-15", "15-30", "30-45", "45-60", "60-75", "75-90"]
    for b in bands:
        b_val = avg_base[b]["abs_rel"]
        f_val = avg_fused[b]["abs_rel"]
        imp = ((b_val - f_val) / b_val) * 100.0
        logger.info(f"{b:<15} | {b_val:<18.4f} | {f_val:<18.4f} | {imp:>+9.2f}%")
    logger.info("=" * 70)

    # Save metrics JSON
    metrics_record = {
        "method": "Gradient-Domain Polar Fusion",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config": cfg,
        "baseline_metrics": avg_base,
        "method1_metrics": avg_fused,
    }
    with open(out_dir / "metrics_summary.json", "w") as f:
        json.dump(metrics_record, f, indent=2)
    logger.info(f"Saved metrics summary to {out_dir / 'metrics_summary.json'}")

    # Check and update BestModelTracker
    tracker = BestModelTracker(str(AURINDUM_DIR / "best_model"))
    is_best = tracker.update_if_best(
        method_name="Gradient-Domain Polar Fusion",
        config=cfg,
        metrics=avg_fused,
        rgb=sample_vis[0],
        gt_depth=sample_vis[1],
        pred_depth=sample_vis[2],
        notes="Poisson gradient-domain polar blending with shift-decoupled disparity alignment."
    )
    if is_best:
        logger.info("🎉 NEW GLOBAL BEST ACHIEVED by Method 1!")


if __name__ == "__main__":
    main()
