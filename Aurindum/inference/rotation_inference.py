"""Rotation-based inference ensemble.

The sphere is rotated (true SO(3) rotation, resampled with seam/pole-aware interpolation,
not a pixel shift) so that a polar region lands near the equator of a new ERP; the frozen
model is run on the rotated ERP and the prediction is rotated back. Range is invariant to
rotations about the camera centre, so depth values need no conversion.

Every pixel then has several predictions, each made at a different latitude *inside the
panorama the model saw* (`view_lat`); fusion can prefer the least distorted one.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np

from geometry.erp_projection import rotate_erp, rotated_lonlat
from geometry.spherical import latitude_map, rotation_from_ypr
from models.depth_model import DepthModelWrapper

from .alignment import align_view_to_reference
from .baseline import ViewPrediction


def rotation_matrices(angles: Sequence[Sequence[float]]) -> List[np.ndarray]:
    """angles: list of (yaw, pitch, roll) in degrees."""
    return [rotation_from_ypr(*a) for a in angles]


def predict_rotated_raw(model: DepthModelWrapper, rgb: np.ndarray, angles: Sequence[Sequence[float]],
                        batch_size: int = 2) -> List[np.ndarray]:
    imgs = []
    for R in rotation_matrices(angles):
        r = rotate_erp(rgb.astype(np.float32), R, mode="bilinear")
        imgs.append(np.clip(r + 0.5, 0, 255).astype(np.uint8))
    return model.predict_batch(imgs, kind="erp", batch_size=batch_size) if imgs else []


def unrotate_predictions(raw: List[np.ndarray], angles: Sequence[Sequence[float]], model: DepthModelWrapper,
                         baseline: ViewPrediction, lat_threshold: float, align_mode: str,
                         min_anchor: int = 200, seam_width: float = 20.0) -> List[ViewPrediction]:
    """Rotate each prediction back to the original frame and align it to the baseline.

    Anchors: pixels trusted in BOTH frames (|lat| < threshold in the original and in the
    rotated panorama, and away from the rotated panorama's left/right seam), so that neither
    side's polar distortion or seam artefacts leak into the fit.
    """
    H, W = baseline.values.shape
    lat = latitude_map(H, W)
    views = []
    for pr, ang in zip(raw, angles):
        R = rotation_from_ypr(*ang)
        mask = np.isfinite(pr)
        back, valid = rotate_erp(np.nan_to_num(pr, nan=0.0).astype(np.float64), R.T, mode="bilinear", mask=mask)
        vlon, vlat = rotated_lonlat(H, W, R)
        valid = valid & np.isfinite(baseline.values)
        anchor = (valid & (np.abs(lat) < lat_threshold) & (np.abs(vlat) < lat_threshold)
                  & (np.abs(vlon) < 180.0 - seam_width))
        aligned, info = align_view_to_reference(np.where(valid, back, np.nan), baseline.values, anchor,
                                                space=model.spec.space, mode=align_mode,
                                                geometry=model.geometry("erp"), min_anchor=min_anchor,
                                                fallback=valid & (np.abs(lat) < lat_threshold))
        if model.spec.space == "disparity":
            aligned = np.where(aligned > 1e-6, aligned, np.nan)
        valid = valid & np.isfinite(aligned)
        views.append(ViewPrediction("rotation", np.where(valid, aligned, np.nan), valid, vlat,
                                    meta={"ypr": list(ang), "align": info}, view_lon=vlon))
    return views


def default_polar_rotations(include_yaw: bool = False) -> List[Tuple[float, float, float]]:
    """A pitch of +-90 deg maps the vertical axis onto the horizontal z axis, so BOTH poles land on
    the equator of the rotated panorama: for +90 the north pole lands at the centre and the south
    pole on the seam (lon = 180), for -90 the reverse. Using both lets each pole be seen at the
    centre once; the seam prior in fusion down-weights the copy that sits on a seam. Yaw-only
    rotations do not change latitude and serve as a control (ensembling without un-distorting)."""
    rots = [(0.0, 90.0, 0.0), (0.0, -90.0, 0.0)]
    if include_yaw:
        rots += [(90.0, 0.0, 0.0), (180.0, 0.0, 0.0), (270.0, 0.0, 0.0)]
    return rots
