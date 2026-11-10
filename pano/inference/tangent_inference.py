"""Selective tangent-plane inference for the distorted polar caps.

ERP -> sphere -> tangent (gnomonic) images of the polar caps only -> frozen model ->
inverse projection to ERP -> (z->range conversion) -> alignment to the baseline on trusted
pixels -> per-view ViewPrediction objects ready for fusion.
"""
from __future__ import annotations

import math
from typing import List, Optional

import numpy as np

from pano.geometry.spherical import latitude_map
from pano.geometry.tangent_plane import TangentPlane, erp_to_tangent, tangent_to_erp
from pano.models.depth_model import DepthModelWrapper

from .alignment import align_view_to_reference
from .baseline import ViewPrediction


def render_tangent_images(rgb: np.ndarray, planes: List[TangentPlane]) -> List[np.ndarray]:
    """Bilinear, seam/pole-aware resampling of the ERP into each tangent view (uint8 RGB)."""
    imgs = []
    for p in planes:
        t = erp_to_tangent(rgb.astype(np.float32), p, mode="bilinear")
        imgs.append(np.clip(t + 0.5, 0, 255).astype(np.uint8))
    return imgs


def predict_tangent_raw(model: DepthModelWrapper, rgb: np.ndarray, planes: List[TangentPlane],
                        batch_size: int = 4) -> List[np.ndarray]:
    """Model outputs on the tangent images (in the tangent pixel grid, model-native units)."""
    if not planes:
        return []
    by_size = {}
    for k, p in enumerate(planes):  # batch only views with equal size
        by_size.setdefault(p.size, []).append(k)
    out: List[Optional[np.ndarray]] = [None] * len(planes)
    imgs = render_tangent_images(rgb, planes)
    for _, idx in by_size.items():
        preds = model.predict_batch([imgs[k] for k in idx], kind="perspective", batch_size=batch_size)
        for k, pr in zip(idx, preds):
            out[k] = pr
    return out


def reproject_tangent_predictions(raw: List[np.ndarray], planes: List[TangentPlane], model: DepthModelWrapper,
                                  baseline: ViewPrediction, lat_threshold: float, align_mode: str,
                                  anchor_view_radial: float = 0.85, geometry_override: Optional[str] = None,
                                  min_anchor: int = 200) -> List[ViewPrediction]:
    """Inverse-project each tangent prediction to ERP and align it to the baseline.

    Anchor pixels for alignment: baseline trusted (|lat| < threshold) AND inside the inner part
    of the tangent view (radial < anchor_view_radial). No ground truth is used.
    """
    H, W = baseline.values.shape
    lat = latitude_map(H, W)
    geometry = geometry_override or model.geometry("perspective")
    views = []
    for pr, plane in zip(raw, planes):
        mask = np.isfinite(pr)
        r = tangent_to_erp(np.nan_to_num(pr, nan=0.0).astype(np.float64), plane, H, W, mode="bilinear",
                           mask=mask)
        valid = r.valid & np.isfinite(baseline.values)
        anchor = valid & (np.abs(lat) < lat_threshold) & (r.radial < anchor_view_radial)
        aligned, info = align_view_to_reference(
            np.where(valid, r.values, np.nan), baseline.values, anchor, space=model.spec.space, mode=align_mode,
            geometry=geometry, cos_axis=r.cos_axis, min_anchor=min_anchor, fallback=valid)
        if model.spec.space == "disparity":
            aligned = np.where(aligned > 1e-6, aligned, np.nan)  # non-positive disparity is meaningless
        valid = valid & np.isfinite(aligned)
        off_axis = np.degrees(np.arccos(np.clip(r.cos_axis, 0, 1)))
        views.append(ViewPrediction("tangent", np.where(valid, aligned, np.nan), valid, off_axis,
                                    meta={"plane": plane.to_dict(), "align": info}, cos_axis=r.cos_axis))
    return views
