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
    methods: Optional[Tuple[str, ...]] = None,
    curve: Optional[Dict] = None,
) -> Dict[str, Dict]:
    """Runs all 4 methods on a panorama. Returns {method: {protocol: per-band metrics}}.

    All fusion happens in the model's ERP output space (disparity for MiDaS): tangent views
    are first aligned to the ERP prediction with `align_tangent_disparity_to_erp` (v1 blended
    raw tangent disparity with arbitrary per-crop (s, t) into the ERP map -> AbsRel ~146).
    """
    from polar_views import fuse_polar, polar_predictions

    m1_cfg = m1_cfg or {}
    want = set(methods) if methods else {"Tangent_Spatial", "Method1_GradientFusion", "Method2_MobiusTTA",
                                         "Control_YawEnsemble"}  # Baseline is always evaluated; PlanarPrior opt-in
    H, W = gt_depth.shape
    phi_deg_map = np.abs(latitude_map(H, W))
    ev = lambda p: evaluate_all_protocols(p, gt_depth, valid_gt, model, protocols, min_depth, max_depth)

    # 1. Baseline ERP
    pred_erp = model.predict(rgb, kind="erp").astype(np.float64)
    res_base, m_base = ev(pred_erp)

    res_tan = m_tan = res_grad = m_grad = None
    m1_gate = None  # method1.curve_gate: ramp from the measured onset; no onset -> both tangent methods return the baseline
    if (m1_cfg or {}).get("curve_gate"):
        if curve is None:
            raise ValueError("method1.curve_gate needs a measured curve (config key distortion_curve)")
        m1_gate = "identity" if curve.get("onset") is None else float(curve["onset"])
    if m1_gate == "identity":
        if "Tangent_Spatial" in want:
            res_tan, m_tan = res_base, m_base
        if "Method1_GradientFusion" in want:
            res_grad, m_grad = res_base, m_base
    elif want & {"Tangent_Spatial", "Method1_GradientFusion"}:
        # Polar views (tangent for perspective models, rotated ERP for ERP-native metric models such as DAP),
        # aligned to the ERP prediction in the fusion space (disparity or log depth). Shared by 2 and 3.
        merged_f, fs, infos = polar_predictions(
            model, rgb, pred_erp, phi_deg_map, source=m1_cfg.get("polar_source", "auto"),
            fov_deg=m1_cfg.get("fov_deg", 90.0), resolution=m1_cfg.get("resolution", 384),
            anchor_max_lat=m1_cfg.get("anchor_max_lat", 60.0), shift_model=m1_cfg.get("shift_model", "cos"))
        for info in infos:
            logger.debug(f"polar view: {info}")
        margin = m1_cfg.get("blend_margin", 10.0)
        # with a measured onset the fusion ramp STARTS at the onset (ramp = phi_threshold -/+ margin)
        common = dict(phi_threshold=(phi_thresh if m1_gate is None else m1_gate + margin), blend_margin=margin)

        # 2. Spatial cosine-ramp blend of the ALIGNED polar views
        if "Tangent_Spatial" in want:
            pred_spatial_tan = fuse_polar(pred_erp, merged_f, fs, phi_deg_map, mode="cosine_ramp", **common)
            res_tan, m_tan = ev(pred_spatial_tan)

        # 3. Method 1: gradient-domain fusion of the same aligned views
        if "Method1_GradientFusion" in want:
            pred_grad = fuse_polar(pred_erp, merged_f, fs, phi_deg_map, mode="gradient_poisson", rgb=rgb,
                                   texture_tau=m1_cfg.get("texture_tau", 0.0),
                                   texture_gate_mode=m1_cfg.get("texture_gate_mode", "erp"), **common)
            res_grad, m_grad = ev(pred_grad)

    res_pp = m_pp = None
    pinfo = None
    if "Method1_PlanarPrior" in want:
        # 3b. Training-free floor / ceiling plane prior, fused in the gradient domain (no extra forward pass)
        from planar_prior import fit_polar_planes
        from polar_views import fuse_polar, fusion_space, to_fusion
        pp = (m1_cfg or {}).get("planar_prior", {})
        space = "disparity" if fusion_space(model) == "disparity" else "depth"
        plane, pinfo = fit_polar_planes(pred_erp, space, ring=tuple(pp.get("ring", (40.0, 60.0))),
                                        cap_from=pp.get("cap_from", 40.0), min_inlier=pp.get("min_inlier", 0.6),
                                        inlier_tol=pp.get("inlier_tol", 0.05), max_tilt_deg=pp.get("max_tilt_deg", 20.0),
                                        agree_tol=pp.get("agree_tol", 0.5))
        for info in pinfo:
            logger.debug(f"planar prior: {info}")
        fs = fusion_space(model)
        pred_pp = fuse_polar(pred_erp, to_fusion(plane, fs), fs, phi_deg_map, mode="gradient_poisson", rgb=rgb,
                             phi_threshold=pp.get("phi_threshold", 60.0), blend_margin=pp.get("blend_margin", 10.0))
        res_pp, m_pp = ev(pred_pp)

    res_mob = m_mob = res_yaw = m_yaw = None
    if "Method2_MobiusTTA" in want:
        # 4. Method 2: Möbius TTA (reuses the baseline forward pass as the identity pass)
        pred_mobius, _ = m2_ensemble.predict(rgb, identity_pred=pred_erp)
        res_mob, m_mob = ev(pred_mobius)
    if "Control_YawEnsemble" in want:
        # 5. Compute-matched control: same number of passes as Möbius-TTA, longitude shifts only
        from tta_ensemble import yaw_shift_ensemble
        pred_yaw = yaw_shift_ensemble(model, rgb, n_passes=len(m2_ensemble.passes), identity_pred=pred_erp,
                                      reanchor=m2_ensemble.reanchor, anchor_max_lat=m2_ensemble.anchor_max_lat)
        res_yaw, m_yaw = ev(pred_yaw)

    out = {"Baseline": res_base, "predictions": {"baseline": m_base}}
    if pinfo is not None:
        out["planar_info"] = [{k: v for k, v in i.items() if k != "c"} for i in pinfo]  # per-pole accept / reject record
    for name, res, key, pred in (("Tangent_Spatial", res_tan, "tangent_spatial", m_tan),
                                 ("Method1_GradientFusion", res_grad, "method1_grad", m_grad),
                                 ("Method1_PlanarPrior", res_pp, "method1_planar", m_pp),
                                 ("Method2_MobiusTTA", res_mob, "method2_mobius", m_mob),
                                 ("Control_YawEnsemble", res_yaw, "control_yaw", m_yaw)):
        if res is not None:
            out[name] = res
            out["predictions"][key] = pred
    return out
