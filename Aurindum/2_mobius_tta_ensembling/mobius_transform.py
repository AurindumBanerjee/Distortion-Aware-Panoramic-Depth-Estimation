"""Möbius conformal transformations of an ERP panorama (PanDA-style, arXiv:2406.13378).

A Möbius transformation of the sphere is, up to a rotation, a stereographic dilation
    zeta -> lambda * zeta,     zeta = exp(i*lon) * tan(pi/4 + lat/2)
composed with a rotation of the sphere. Both parts are conformal (angle preserving),
so local texture is not sheared.

IMPORTANT (fixes over v1):
  * A pure dilation fixes BOTH poles (zeta = 0 and zeta = inf). It enlarges one cap and
    shrinks the other, but a polar pixel stays polar and keeps its ERP distortion. To
    move a pole to the low-distortion equator the pass must include a rotation
    (pitch = +/-90 deg). A pass is therefore (pitch_deg, scale).
  * v1 passed (lon, lat) in RADIANS to `sample_erp`, which expects PIXEL coordinates,
    so every warped image was a blurred sample of a ~6 x 3 pixel corner of the input.
    All coordinates now go through `lonlat_to_pixel`.

Convention (same as geometry.erp_projection.rotate_erp): the warped panorama is
    I_w(t) = I( R · S^{-1}(t) )     (S = dilation by lambda on the stereographic plane)
so the original direction o is seen in the warped frame at  t = S(R^T o).
"""
from __future__ import annotations

import logging
from typing import Tuple

import numpy as np

from geometry.erp_projection import sample_erp
from geometry.spherical import erp_lonlat_grid, lonlat_to_pixel, lonlat_to_xyz, rotation_from_ypr, xyz_to_lonlat

logger = logging.getLogger("MobiusTransform")

_EPS = 1e-6


def _grid(height: int, width: int) -> Tuple[np.ndarray, np.ndarray]:
    lon, lat = erp_lonlat_grid(height, width)
    return lon.numpy(), lat.numpy()


def _dilate(lon: np.ndarray, lat: np.ndarray, lam: float) -> Tuple[np.ndarray, np.ndarray]:
    """(lon, lat) -> (lon, lat') with stereographic radius multiplied by lam (lon unchanged)."""
    if abs(lam - 1.0) < 1e-9:
        return lon, lat
    r = np.tan(np.pi / 4.0 + np.clip(lat, -np.pi / 2 + _EPS, np.pi / 2 - _EPS) / 2.0)
    lat2 = 2.0 * np.arctan(lam * r) - np.pi / 2.0
    return lon, lat2


def _rotate(lon: np.ndarray, lat: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Direction d(lon, lat) -> R d, returned as (lon, lat)."""
    xyz = lonlat_to_xyz(lon, lat) @ np.asarray(R).T
    return xyz_to_lonlat(xyz)


def warp_sampling_lonlat(height: int, width: int, scale: float, pitch_deg: float = 0.0):
    """Source (lon, lat) for every pixel of the warped panorama: o = R · S^{-1}(t)."""
    lon_t, lat_t = _grid(height, width)
    lon_s, lat_s = _dilate(lon_t, lat_t, 1.0 / scale)
    if pitch_deg:
        lon_s, lat_s = _rotate(lon_s, lat_s, rotation_from_ypr(pitch_deg=pitch_deg))
    return lon_s, lat_s


def unwarp_sampling_lonlat(height: int, width: int, scale: float, pitch_deg: float = 0.0):
    """Warped-frame (lon, lat) of every ORIGINAL pixel: t = S(R^T o)."""
    lon_o, lat_o = _grid(height, width)
    if pitch_deg:
        lon_o, lat_o = _rotate(lon_o, lat_o, rotation_from_ypr(pitch_deg=pitch_deg).T)
    return _dilate(lon_o, lat_o, scale)


def warp_erp_mobius(image: np.ndarray, scale_factor: float, pitch_deg: float = 0.0
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Warp an ERP image by the Möbius pass (pitch, scale).

    Returns:
        warped_image: the conformally transformed ERP image
        warped_lat_deg_on_original: for every ORIGINAL pixel, |latitude| (deg) at which the
            model sees it in the warped image. This is the distortion the prediction for that
            pixel suffered and is the right quantity for fusion weights after unwarping.
    """
    H, W = image.shape[:2]
    lon_s, lat_s = warp_sampling_lonlat(H, W, scale_factor, pitch_deg)
    u, v = lonlat_to_pixel(lon_s, lat_s, H, W)
    warped = sample_erp(image.astype(np.float32), u, v, mode="bilinear")
    if image.dtype == np.uint8:
        warped = np.clip(np.rint(warped), 0, 255).astype(np.uint8)
    _, lat_w = unwarp_sampling_lonlat(H, W, scale_factor, pitch_deg)
    return warped, np.degrees(np.abs(lat_w))


def unwarp_depth_mobius(warped_depth: np.ndarray, scale_factor: float, pitch_deg: float = 0.0) -> np.ndarray:
    """Bring a prediction made on the warped panorama back to the original ERP grid.

    Range is invariant under rotations about the camera centre and under a re-mapping of
    viewing directions, so values are resampled, not rescaled. (Model-specific affine
    drift is handled by re-anchoring in tta_ensemble.)
    """
    H, W = warped_depth.shape[:2]
    lon_w, lat_w = unwarp_sampling_lonlat(H, W, scale_factor, pitch_deg)
    u, v = lonlat_to_pixel(lon_w, lat_w, H, W)
    return sample_erp(warped_depth.astype(np.float64), u, v, mode="bilinear")
