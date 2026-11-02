"""Möbius Conformal Transformations on the Spherical Panorama.

Inspired by PanDA (CVPR 2025, arXiv:2406.13378).
Points on the sphere S^2 are mapped to the extended complex plane via stereographic projection:
    zeta = exp(i * theta) * tan(pi / 4 + phi / 2)

A conformal Möbius transformation is then applied:
    f(zeta) = (a * zeta + b) / (c * zeta + d)

A vertical scaling/dilation f(zeta) = lambda * zeta (with lambda > 1 or < 1) smoothly
compresses the high-distortion polar caps towards the equatorial band where standard
depth foundation models experience minimal distortion.
Because Möbius maps are strictly conformal (angle-preserving), local textures and geometric
shapes remain unskewed.
"""
from __future__ import annotations

import logging
from typing import Tuple

import cv2
import numpy as np

from geometry.erp_projection import sample_erp
from geometry.spherical import erp_lonlat_grid, latitude_map

logger = logging.getLogger("MobiusTransform")


def erp_to_stereographic(
    height: int,
    width: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Maps ERP pixel coordinates to the complex stereographic plane zeta = u + i*v."""
    lon, lat = erp_lonlat_grid(height, width)  # lon in [-pi, pi], lat in [-pi/2, pi/2]
    
    # Clip latitude away from extreme +/- pi/2 to avoid infinite tangents
    lat_clipped = np.clip(lat, -np.pi / 2.0 + 1e-4, np.pi / 2.0 - 1e-4)
    
    # Stereographic projection from south pole onto equatorial plane:
    # r = tan(pi / 4 + phi / 2)
    r = np.tan(np.pi / 4.0 + lat_clipped / 2.0)
    zeta_real = r * np.cos(lon)
    zeta_imag = r * np.sin(lon)
    
    return zeta_real, zeta_imag


def stereographic_to_erp(
    zeta_real: np.ndarray,
    zeta_imag: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Inverts stereographic projection: zeta -> (lon, lat)."""
    r = np.sqrt(zeta_real ** 2 + zeta_imag ** 2)
    lon = np.arctan2(zeta_imag, zeta_real)
    lat = 2.0 * np.arctan(r) - np.pi / 2.0
    lat = np.clip(lat, -np.pi / 2.0, np.pi / 2.0)
    return lon, lat


def apply_mobius_dilation(
    zeta_real: np.ndarray,
    zeta_imag: np.ndarray,
    scale_factor: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Applies conformal scaling f(zeta) = scale_factor * zeta."""
    return zeta_real * scale_factor, zeta_imag * scale_factor


def warp_erp_mobius(
    image: np.ndarray,
    scale_factor: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Backward-warps an ERP image according to a Möbius dilation.
    
    Args:
        image: Source ERP image [H, W] or [H, W, 3]
        scale_factor: Dilation factor lambda (>1 moves south pole up; <1 moves north pole down)
        
    Returns:
        warped_image: Conformal transformed ERP image
        effective_lat_deg: Effective latitude that the model will perceive
    """
    H, W = image.shape[:2]
    # For backward warping: we evaluate where target pixels come from in the source image
    # If target is dilated by lambda, source zeta_src = zeta_tgt / lambda
    tgt_real, tgt_imag = erp_to_stereographic(H, W)
    src_real, src_imag = apply_mobius_dilation(tgt_real, tgt_imag, 1.0 / scale_factor)
    src_lon, src_lat = stereographic_to_erp(src_real, src_imag)

    # Sample source image at (src_lon, src_lat)
    warped = sample_erp(image, src_lon, src_lat, mode="bilinear")

    # Effective latitude in degrees (where this content lives in the target image)
    effective_lat_deg = np.rad2deg(np.abs(src_lat))
    return warped, effective_lat_deg


def unwarp_depth_mobius(
    warped_depth: np.ndarray,
    scale_factor: float
) -> np.ndarray:
    """Inverts the Möbius warping on depth map back to the original ERP frame."""
    H, W = warped_depth.shape[:2]
    # To unwarp: evaluate where original ERP pixels were located in the warped frame
    # Target in original frame -> warped frame coordinate zeta_warped = lambda * zeta_orig
    orig_real, orig_imag = erp_to_stereographic(H, W)
    warped_real, warped_imag = apply_mobius_dilation(orig_real, orig_imag, scale_factor)
    warped_lon, warped_lat = stereographic_to_erp(warped_real, warped_imag)

    # Sample warped depth at (warped_lon, warped_lat)
    unwarped_depth = sample_erp(warped_depth, warped_lon, warped_lat, mode="bilinear")
    return unwarped_depth
