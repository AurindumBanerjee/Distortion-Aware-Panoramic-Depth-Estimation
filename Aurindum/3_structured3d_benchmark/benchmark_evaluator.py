"""Comparative Benchmarking Suite on Real Structured3D Panoramas.

Evaluates 4 distinct paradigms side-by-side on real indoor scenes:
1. Baseline ERP (frozen model)
2. Polar Tangent Plane Fusion (spatial alpha blend)
3. Method 1: Gradient-Domain Polar Fusion & Shift-Decoupled Alignment
4. Method 2: Test-Time Möbius Augmentation Ensembling
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from evaluation.latitude_analysis import per_band_metrics
from evaluation.protocol import align_to_gt
from geometry.spherical import latitude_map
from geometry.tangent_plane import generate_tangent_plane, erp_to_tangent, tangent_to_erp

logger = logging.getLogger("BenchmarkEvaluator")


def evaluate_all_protocols(pred, gt, valid, model, protocols, min_depth, max_depth):
    """{protocol: per-band metrics} plus the aligned depth for the first protocol."""
    out, first = {}, None
    for proto in protocols:
        d = align_to_gt(pred, gt, valid, model, protocol=proto, min_depth=min_depth, max_depth=max_depth)
        out[proto] = per_band_metrics(d, gt, valid)
        if first is None:
            first = d
    return out, first


def run_single_benchmark_scene(
    scene_info: Dict[str, str],
    rgb: np.ndarray,
    gt_depth: np.ndarray,
    valid_gt: np.ndarray,
    model,
    m1_solver,
    m2_ensemble,
    phi_thresh: float = 45.0,
    protocols: Tuple[str, ...] = ("align-all", "align-equatorial"),
    min_depth: float = 0.1,
    max_depth: float = 10.0,
    m1_cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict]:
    """Runs all 4 methods on a panorama. Returns {method: {protocol: per-band metrics}}.

    All fusion happens in the model's ERP output space (disparity for MiDaS): tangent views
    are first aligned to the ERP prediction with `align_tangent_disparity_to_erp` (v1 blended
    raw tangent disparity with arbitrary per-crop (s, t) into the ERP map -> AbsRel ~146).
    """
    from polar_views import fuse_polar, polar_predictions

    m1_cfg = m1_cfg or {}
    H, W = gt_depth.shape
    phi_deg_map = np.abs(latitude_map(H, W))
    ev = lambda p: evaluate_all_protocols(p, gt_depth, valid_gt, model, protocols, min_depth, max_depth)

    # 1. Baseline ERP
    pred_erp = model.predict(rgb, kind="erp").astype(np.float64)
    res_base, m_base = ev(pred_erp)

    # Polar views (tangent for perspective models, rotated ERP for ERP-native metric models such as DAP),
    # aligned to the ERP prediction in the fusion space (disparity or log depth). Shared by 2 and 3.
    merged_f, fs, infos = polar_predictions(
        model, rgb, pred_erp, phi_deg_map, source=m1_cfg.get("polar_source", "auto"),
        fov_deg=m1_cfg.get("fov_deg", 90.0), resolution=m1_cfg.get("resolution", 384),
        anchor_max_lat=m1_cfg.get("anchor_max_lat", 60.0))
    for info in infos:
        logger.debug(f"polar view: {info}")
    common = dict(phi_threshold=phi_thresh, blend_margin=m1_cfg.get("blend_margin", 10.0))

    # 2. Spatial cosine-ramp blend of the ALIGNED polar views
    pred_spatial_tan = fuse_polar(pred_erp, merged_f, fs, phi_deg_map, mode="cosine_ramp", **common)
    res_tan, m_tan = ev(pred_spatial_tan)

    # 3. Method 1: gradient-domain fusion of the same aligned views
    pred_grad = fuse_polar(pred_erp, merged_f, fs, phi_deg_map, mode="gradient_poisson", rgb=rgb,
                           texture_tau=m1_cfg.get("texture_tau", 0.0),
                           texture_gate_mode=m1_cfg.get("texture_gate_mode", "erp"), **common)
    res_grad, m_grad = ev(pred_grad)

    # 4. Method 2: Möbius TTA (reuses the baseline forward pass as the identity pass)
    pred_mobius, _ = m2_ensemble.predict(rgb, identity_pred=pred_erp)
    res_mob, m_mob = ev(pred_mobius)

    # 5. Compute-matched control: same number of passes as Möbius-TTA, longitude shifts only
    from tta_ensemble import yaw_shift_ensemble
    pred_yaw = yaw_shift_ensemble(model, rgb, n_passes=len(m2_ensemble.passes), identity_pred=pred_erp,
                                  reanchor=m2_ensemble.reanchor, anchor_max_lat=m2_ensemble.anchor_max_lat)
    res_yaw, m_yaw = ev(pred_yaw)

    return {
        "Baseline": res_base,
        "Tangent_Spatial": res_tan,
        "Method1_GradientFusion": res_grad,
        "Method2_MobiusTTA": res_mob,
        "Control_YawEnsemble": res_yaw,
        "predictions": {
            "baseline": m_base,
            "tangent_spatial": m_tan,
            "method1_grad": m_grad,
            "method2_mobius": m_mob,
            "control_yaw": m_yaw,
        },
    }
