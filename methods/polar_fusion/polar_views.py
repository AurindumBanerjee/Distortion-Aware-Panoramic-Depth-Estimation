"""Polar views for Method 1, for any frozen model (relative-disparity or metric-depth).

Two ways to obtain a low-distortion prediction of each polar cap:
  * 'tangent'     : perspective tangent view centred on the pole (perspective models: MiDaS, DAv2)
  * 'rotated_erp' : rotate the panorama by pitch = +/-90 deg so the pole lies on the equator, run the
                    model on the full rotated ERP, rotate the prediction back (ERP-native models: DAP,
                    which was trained on panoramas only; a square perspective crop is out of distribution)
'auto' picks 'rotated_erp' for metric ERP depth models and 'tangent' otherwise.

All alignment and fusion happen in a FUSION SPACE chosen by the model's output:
  * disparity models (affine-invariant): ERP disparity; each polar view is affinely aligned to the
    ERP prediction (DA360-style shift handling, see shift_alignment.py)
  * depth models: log depth; a global scale error becomes an additive offset, removed by a robust
    (median) offset fit on the anchor ring -> no shift term, so metric scale is preserved
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from pano.geometry.erp_projection import rotate_erp, rotated_latitude
from pano.geometry.spherical import rotation_from_ypr
from pano.geometry.tangent_plane import erp_to_tangent, generate_tangent_plane, tangent_to_erp
from methods.polar_fusion.shift_alignment import align_tangent_disparity_to_erp

logger = logging.getLogger("PolarViews")


def _spec(model):
    spec = getattr(model, "spec", None)
    space = getattr(model, "space", getattr(spec, "space", "depth"))
    scale = getattr(model, "scale", getattr(spec, "scale", "metric"))
    persp = getattr(spec, "geometry_perspective", "planar")
    return space, scale, persp


def fusion_space(model) -> str:
    return "disparity" if _spec(model)[0] == "disparity" else "logdepth"


def to_fusion(pred: np.ndarray, fs: str) -> np.ndarray:
    pred = np.asarray(pred, dtype=np.float64)
    if fs == "disparity":
        return pred
    return np.where(np.isfinite(pred) & (pred > 0), np.log(np.clip(pred, 1e-4, None)), np.nan)


def from_fusion(x: np.ndarray, fs: str) -> np.ndarray:
    return x if fs == "disparity" else np.exp(x)


def resolve_source(model, source: str = "auto") -> str:
    if source != "auto":
        return source
    space, scale, _ = _spec(model)
    return "rotated_erp" if (space == "depth" and scale == "metric") else "tangent"


def _offset_fit(x: np.ndarray, ref: np.ndarray, anchor: np.ndarray) -> Tuple[float, int]:
    m = anchor & np.isfinite(x) & np.isfinite(ref)
    if m.sum() < 50:
        return 0.0, int(m.sum())
    return float(np.median(ref[m] - x[m])), int(m.sum())


def _align(view_f: np.ndarray, base_f: np.ndarray, cos_ray: np.ndarray, phi: np.ndarray, fs: str,
           anchor_max_lat: float, view_is_planar_disp: bool, shift_model: str = "cos") -> Tuple[np.ndarray, Dict]:
    """Align one polar view (already on the ERP grid, in fusion space) to the ERP prediction."""
    if fs == "disparity":
        cr = cos_ray if view_is_planar_disp else np.ones_like(view_f)
        # a rotated ERP view has cos = 1 everywhere: the cos term is not identifiable and is skipped automatically
        return align_tangent_disparity_to_erp(view_f, base_f, cr, phi, anchor_max_lat=anchor_max_lat,
                                              shift_model=shift_model)
    overlap = np.isfinite(view_f) & np.isfinite(base_f)
    anchor = overlap & (phi <= anchor_max_lat)
    if anchor.sum() < 200 and overlap.any():
        anchor = overlap & (phi <= np.percentile(phi[overlap], 20.0))
    b, n = _offset_fit(view_f, base_f, anchor)
    return view_f + b, {"log_offset": b, "scale": float(np.exp(b)), "anchor_pixels": n}


def polar_predictions(model, rgb: np.ndarray, pred_erp: np.ndarray, phi_deg_map: np.ndarray,
                      source: str = "auto", fov_deg: float = 90.0, resolution: int = 384,
                      anchor_max_lat: float = 60.0, rotated_max_seen_lat: float = 50.0, shift_model: str = "cos"
                      ) -> Tuple[np.ndarray, str, List[Dict]]:
    """Aligned polar-view prediction merged on the ERP grid, in fusion space (NaN where no view).

    Returns (merged_fusion, fusion_space, per-view info).
    """
    H, W = pred_erp.shape
    fs = fusion_space(model)
    space, scale, persp = _spec(model)
    src = resolve_source(model, source)
    base_f = to_fusion(pred_erp, fs)
    merged = np.full((H, W), np.nan)
    infos = []
    lat_signed = None
    for sign in (+1, -1):
        if src == "tangent":
            plane = generate_tangent_plane(lon_deg=0.0, lat_deg=90.0 * sign, fov_deg=fov_deg, size=resolution)
            p_tan = model.predict(erp_to_tangent(rgb, plane), kind="perspective")
            wr = tangent_to_erp(p_tan, plane, height=H, width=W)
            vals = np.where(wr.valid, wr.values, np.nan).astype(np.float64)
            cos_ray = wr.cos_axis
            if fs == "logdepth":
                if persp == "planar":  # z-buffer -> range
                    vals = vals / np.clip(cos_ray, 1e-3, None)
                view_f = to_fusion(vals, fs)
            else:
                view_f = vals  # planar disparity, converted inside the alignment
            al, info = _align(view_f, base_f, cos_ray, phi_deg_map, fs, anchor_max_lat, view_is_planar_disp=True,
                               shift_model=shift_model)
        elif src == "rotated_erp":
            R = rotation_from_ypr(pitch_deg=90.0 * sign)
            rgb_rot = np.clip(np.rint(np.asarray(rotate_erp(rgb, R))), 0, 255).astype(np.uint8)
            p_rot = model.predict(rgb_rot, kind="erp")
            back = np.asarray(rotate_erp(np.asarray(p_rot, dtype=np.float64), R.T), dtype=np.float64)
            seen = np.abs(rotated_latitude(H, W, R))
            if lat_signed is None:
                from pano.geometry.spherical import latitude_map
                lat_signed = latitude_map(H, W)
            keep = (np.sign(lat_signed) == sign) & (seen <= rotated_max_seen_lat)
            view_f = np.where(keep, to_fusion(back, fs), np.nan)
            al, info = _align(view_f, base_f, np.ones((H, W)), phi_deg_map, fs, anchor_max_lat,
                              view_is_planar_disp=False)
        else:
            raise ValueError(f"unknown polar source {src!r}")
        info.update(source=src, pole="north" if sign > 0 else "south")
        infos.append(info)
        v = np.isfinite(al)
        merged[v] = al[v]
    return merged, fs, infos


def fuse_polar(pred_erp: np.ndarray, merged_f: np.ndarray, fs: str, phi_deg_map: np.ndarray, mode: str = "gradient_poisson",
               phi_threshold: float = 45.0, blend_margin: float = 10.0, rgb: Optional[np.ndarray] = None,
               texture_tau: float = 0.0, texture_gate_mode: str = "erp", fill_depth: float = 100.0) -> np.ndarray:
    """Fuse ERP prediction and aligned polar views in fusion space; return in the model's output space.

    mode: 'gradient_poisson' (Method 1) | 'cosine_ramp' (spatial blend baseline, Tangent_Spatial)
    NaN pixels of the ERP prediction (e.g. DAP sky mask) are filled with `fill_depth` for the solve and
    restored as NaN afterwards.
    """
    from methods.polar_fusion.gradient_blending import gradient_domain_polar_fuse

    base_f = to_fusion(pred_erp, fs)
    holes = ~np.isfinite(base_f)
    if holes.any():
        base_f = np.where(holes, to_fusion(np.array(fill_depth), fs), base_f)
    if mode == "gradient_poisson":
        out_f = gradient_domain_polar_fuse(
            d_erp=base_f, d_tangent=merged_f, weight_map=np.ones_like(base_f), phi_deg_map=phi_deg_map,
            phi_threshold=phi_threshold, blend_margin=blend_margin, rgb=rgb, texture_tau=texture_tau,
            texture_gate_mode=texture_gate_mode, positive=(fs == "disparity"))
    else:
        a = np.clip((phi_deg_map - (phi_threshold - blend_margin)) / (2 * blend_margin), 0.0, 1.0)
        a = 0.5 * (1.0 - np.cos(np.pi * a))
        v = np.isfinite(merged_f)
        out_f = np.where(v, (1.0 - a) * base_f + a * np.nan_to_num(merged_f), base_f)
    out = from_fusion(out_f, fs)
    if holes.any():
        out = np.where(holes & ~np.isfinite(merged_f), np.nan, out)
    return out
