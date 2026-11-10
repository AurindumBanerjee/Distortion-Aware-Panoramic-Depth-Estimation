"""Baseline: run the frozen model once on the full ERP panorama."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np

from pano.geometry.spherical import latitude_map
from pano.models.depth_model import DepthModelWrapper


@dataclass
class ViewPrediction:
    """A prediction resampled onto the ERP grid of the input panorama, in the fusion space."""
    source: str  # 'baseline' | 'tangent' | 'rotation'
    values: np.ndarray  # (H, W) float, NaN where undefined
    valid: np.ndarray  # (H, W) bool
    view_lat: np.ndarray  # (H, W) latitude (deg) of each pixel *inside the image the model saw*
    # (for a pinhole view: the off-axis angle, which plays the same "distortion" role)
    meta: Dict = field(default_factory=dict)
    cos_axis: Optional[np.ndarray] = None  # tangent views only
    view_lon: Optional[np.ndarray] = None  # longitude (deg) inside an ERP input (baseline / rotated views)


def run_baseline(model: DepthModelWrapper, rgb: np.ndarray) -> ViewPrediction:
    H, W = rgb.shape[:2]
    pred = model.predict(rgb, kind="erp").astype(np.float64)
    valid = np.isfinite(pred)
    from pano.geometry.spherical import erp_lonlat_grid
    lon = np.degrees(erp_lonlat_grid(H, W)[0].numpy())
    return ViewPrediction("baseline", pred, valid, latitude_map(H, W), meta={"model_calls": 1}, view_lon=lon)
