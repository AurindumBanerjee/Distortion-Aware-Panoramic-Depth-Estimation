"""Comparative Benchmarking Suite on Real Structured3D Panoramas.

Evaluates 4 distinct paradigms side-by-side on real indoor scenes:
1. Baseline ERP (frozen model)
2. Polar Tangent Plane Fusion (spatial alpha blend)
3. Method 1: Gradient-Domain Polar Fusion & Shift-Decoupled Alignment
4. Method 2: Test-Time Möbius Augmentation Ensembling
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

from evaluation.latitude_analysis import per_band_metrics
from evaluation.metrics import compute_metrics, to_metric_depth
from geometry.spherical import latitude_map
from geometry.tangent_plane import generate_tangent_plane, erp_to_tangent, tangent_to_erp

logger = logging.getLogger("BenchmarkEvaluator")


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


def run_single_benchmark_scene(
    scene_info: Dict[str, str],
    rgb: np.ndarray,
    gt_depth: np.ndarray,
    valid_gt: np.ndarray,
    model,
    m1_solver,
    m2_ensemble,
    phi_thresh: float = 45.0
) -> Dict[str, Dict]:
    """Runs all 4 methods on a real panorama and returns aligned metric evaluations."""
    H, W = gt_depth.shape
    phi_deg_map = np.abs(latitude_map(H, W))
    eq_anchor = valid_gt & (phi_deg_map < 30.0)

    # 1. Baseline ERP
    pred_erp = model.predict(rgb, kind="erp")
    m_base = align_prediction_to_gt(pred_erp, gt_depth, eq_anchor, model)
    res_base = per_band_metrics(m_base, gt_depth, valid_gt)

    # 2. Standard Tangent Polar Fusion (Spatial Cosine Ramp)
    tangent_centers = [(0.0, 90.0), (0.0, -90.0)]
    tan_preds = []
    for tc, pc in tangent_centers:
        plane = generate_tangent_plane(lon_deg=tc, lat_deg=pc, fov_deg=90.0, size=384)
        rgb_tan = erp_to_tangent(rgb, plane)
        p_tan = model.predict(rgb_tan, kind="perspective")
        warp_res = tangent_to_erp(p_tan, plane, height=H, width=W)
        p_on_erp = warp_res.values
        cos_ray = warp_res.cos_axis
        tan_preds.append((p_on_erp, cos_ray))

    # Standard spatial cosine blend
    alpha = np.clip((phi_deg_map - (phi_thresh - 10)) / 20.0, 0.0, 1.0)
    alpha = 0.5 * (1.0 - np.cos(np.pi * alpha))
    merged_tan = np.full_like(pred_erp, np.nan)
    for p_tan_erp, _ in tan_preds:
        val = np.isfinite(p_tan_erp)
        merged_tan[val] = p_tan_erp[val]

    val_tan = np.isfinite(merged_tan)
    pred_spatial_tan = np.where(val_tan, (1.0 - alpha) * pred_erp + alpha * merged_tan, pred_erp)
    m_tan = align_prediction_to_gt(pred_spatial_tan, gt_depth, eq_anchor, model)
    res_tan = per_band_metrics(m_tan, gt_depth, valid_gt)

    # 3. Method 1: Gradient-Domain Polar Fusion & Shift Alignment
    from shift_alignment import align_tangent_disparity_to_erp
    from gradient_blending import gradient_domain_polar_fuse

    aligned_t_ranges = []
    for p_tan_erp, cos_ray in tan_preds:
        al_r, _ = align_tangent_disparity_to_erp(
            tangent_disp_on_erp=p_tan_erp,
            erp_disp_baseline=pred_erp,
            cos_ray=cos_ray,
            phi_deg_map=phi_deg_map,
            anchor_max_lat=35.0
        )
        aligned_t_ranges.append(al_r)

    merged_aligned_tan = np.full_like(gt_depth, np.nan)
    for r_tan in aligned_t_ranges:
        v = np.isfinite(r_tan)
        merged_aligned_tan[v] = r_tan[v]

    pred_grad_fused = gradient_domain_polar_fuse(
        d_erp=pred_erp,
        d_tangent=merged_aligned_tan,
        weight_map=np.ones_like(pred_erp),
        phi_deg_map=phi_deg_map,
        phi_threshold=phi_thresh,
        blend_margin=10.0,
        solver_mode="sor"
    )
    m_grad = align_prediction_to_gt(pred_grad_fused, gt_depth, eq_anchor, model)
    res_grad = per_band_metrics(m_grad, gt_depth, valid_gt)

    # 4. Method 2: Möbius-TTA Ensembling
    pred_mobius, _ = m2_ensemble.predict(rgb)
    m_mob = align_prediction_to_gt(pred_mobius, gt_depth, eq_anchor, model)
    res_mob = per_band_metrics(m_mob, gt_depth, valid_gt)

    return {
        "Baseline": res_base,
        "Tangent_Spatial": res_tan,
        "Method1_GradientFusion": res_grad,
        "Method2_MobiusTTA": res_mob,
        "predictions": {
            "baseline": m_base,
            "tangent_spatial": m_tan,
            "method1_grad": m_grad,
            "method2_mobius": m_mob,
        }
    }
