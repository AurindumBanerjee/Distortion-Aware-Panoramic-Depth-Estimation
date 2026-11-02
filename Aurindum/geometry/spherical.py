"""Spherical coordinate conventions used throughout the project.

Conventions (fixed everywhere, tested in tests/test_geometry.py)
------------------------------------------------------------------
Camera / world frame (OpenCV style):  x -> right,  y -> down,  z -> forward.

Equirectangular (ERP) image of size H x W, pixel *centres* at integer (u, v):
    longitude  theta = ((u + 0.5) / W) * 2*pi - pi        in (-pi, pi)
    latitude   phi   = pi/2 - ((v + 0.5) / H) * pi         in (-pi/2, pi/2)
so the top row is the north pole (phi -> +pi/2, "up", -y) and the image
centre (theta = 0, phi = 0) looks along +z.

Unit direction for (theta, phi):
    x =  cos(phi) * sin(theta)
    y = -sin(phi)
    z =  cos(phi) * cos(theta)

Inverse:
    theta = atan2(x, z),   phi = asin(-y)

Rotations: a rotation matrix R (3x3) acts on directions as d' = R @ d.
"""
from __future__ import annotations

import math
from typing import Tuple

import numpy as np
import torch

# ----------------------------------------------------------------------------
# Pixel <-> angle
# ----------------------------------------------------------------------------


def erp_lonlat_grid(height: int, width: int, device=None, dtype=torch.float64) -> Tuple[torch.Tensor, torch.Tensor]:
    """Longitude / latitude (radians) of every ERP pixel centre, each (H, W)."""
    u = torch.arange(width, device=device, dtype=dtype) + 0.5
    v = torch.arange(height, device=device, dtype=dtype) + 0.5
    lon = u / width * 2 * math.pi - math.pi
    lat = math.pi / 2 - v / height * math.pi
    lat_g, lon_g = torch.meshgrid(lat, lon, indexing="ij")
    return lon_g, lat_g


def latitude_map(height: int, width: int, degrees: bool = True) -> np.ndarray:
    """(H, W) latitude map in degrees (default) or radians, as numpy float64."""
    _, lat = erp_lonlat_grid(height, width)
    lat = lat.numpy()
    return np.degrees(lat) if degrees else lat


def pixel_to_lonlat(u, v, height: int, width: int):
    """Continuous pixel coordinates -> (lon, lat) radians. Works on numpy/torch."""
    lon = (u + 0.5) / width * 2 * math.pi - math.pi
    lat = math.pi / 2 - (v + 0.5) / height * math.pi
    return lon, lat


def lonlat_to_pixel(lon, lat, height: int, width: int):
    """(lon, lat) radians -> continuous pixel coordinates (u, v).

    u is NOT wrapped here; callers that sample must wrap (see erp_projection.sample_erp).
    """
    u = (lon + math.pi) / (2 * math.pi) * width - 0.5
    v = (math.pi / 2 - lat) / math.pi * height - 0.5
    return u, v


# ----------------------------------------------------------------------------
# Angle <-> unit sphere
# ----------------------------------------------------------------------------


def lonlat_to_xyz(lon, lat):
    """(lon, lat) -> unit vectors stacked on the last dim (..., 3)."""
    lib = torch if isinstance(lon, torch.Tensor) else np
    cl = lib.cos(lat)
    x = cl * lib.sin(lon)
    y = -lib.sin(lat)
    z = cl * lib.cos(lon)
    return lib.stack([x, y, z], -1) if lib is torch else np.stack([x, y, z], -1)


def xyz_to_lonlat(xyz):
    """(..., 3) direction (need not be unit) -> (lon, lat) in radians."""
    lib = torch if isinstance(xyz, torch.Tensor) else np
    n = lib.sqrt((xyz ** 2).sum(-1))
    x, y, z = xyz[..., 0] / n, xyz[..., 1] / n, xyz[..., 2] / n
    lon = lib.arctan2(x, z) if lib is np else torch.atan2(x, z)
    lat = lib.arcsin(lib.clip(-y, -1.0, 1.0)) if lib is np else torch.asin(torch.clamp(-y, -1.0, 1.0))
    return lon, lat


def erp_to_sphere(height: int, width: int, device=None, dtype=torch.float64) -> torch.Tensor:
    """Unit-sphere direction of every ERP pixel centre, (H, W, 3)."""
    lon, lat = erp_lonlat_grid(height, width, device=device, dtype=dtype)
    return lonlat_to_xyz(lon, lat)


def sphere_to_erp(xyz, height: int, width: int):
    """Directions (..., 3) -> continuous ERP pixel coordinates (u, v), u wrapped to [-0.5, W-0.5)."""
    lon, lat = xyz_to_lonlat(xyz)
    u, v = lonlat_to_pixel(lon, lat, height, width)
    # wrap u into [-0.5, W - 0.5): longitude is periodic
    u = (u + 0.5) % width - 0.5
    return u, v


# ----------------------------------------------------------------------------
# Rotations
# ----------------------------------------------------------------------------


def rot_x(a: float) -> np.ndarray:
    """Rotation about the x (right) axis. Positive `a` maps +z (forward) towards -y (up)."""
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_y(a: float) -> np.ndarray:
    """Rotation about the y (down / vertical) axis: a pure change of longitude."""
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def rot_z(a: float) -> np.ndarray:
    """Rotation about the z (forward) axis (camera roll)."""
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def rotation_from_ypr(yaw_deg: float = 0.0, pitch_deg: float = 0.0, roll_deg: float = 0.0) -> np.ndarray:
    """R = R_yaw @ R_pitch @ R_roll (applied to view directions).

    With the sampling convention I_rot(d) = I(R d) used in erp_projection.rotate_erp:
      * yaw   shifts longitude  (rot_y(yaw) maps forward to lon = yaw)
      * pitch = +90 brings the original NORTH pole to the centre of the rotated ERP
      * pitch = -90 brings the SOUTH pole to the centre.
    """
    return rot_y(math.radians(yaw_deg)) @ rot_x(math.radians(pitch_deg)) @ rot_z(math.radians(roll_deg))


def angular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Great-circle angle (radians) between direction arrays (..., 3)."""
    a = a / np.linalg.norm(a, axis=-1, keepdims=True)
    b = b / np.linalg.norm(b, axis=-1, keepdims=True)
    # atan2 formulation is numerically stable for tiny angles
    cross = np.linalg.norm(np.cross(a, b), axis=-1)
    dot = (a * b).sum(-1)
    return np.arctan2(cross, dot)


def erp_area_weights(height: int, width: int) -> np.ndarray:
    """Solid angle of each ERP pixel (H, W); proportional to cos(latitude).

    Used for solid-angle-weighted metrics (each pixel near the pole covers far less
    of the sphere than an equatorial pixel).
    """
    lat = latitude_map(height, width, degrees=False)
    dlon = 2 * math.pi / width
    dlat = math.pi / height
    return np.cos(lat) * dlon * dlat


def erp_horizontal_stretch(height: int, width: int) -> np.ndarray:
    """ERP horizontal stretch factor 1/cos(latitude) per pixel (H, W): a scalar 'distortion' measure.

    An ERP pixel row at latitude phi samples a circle of circumference 2*pi*cos(phi)
    with W pixels, i.e. it is stretched horizontally by 1/cos(phi) relative to the
    equator (Tissot indicatrix: a=1/cos(phi), b=1).
    """
    lat = latitude_map(height, width, degrees=False)
    return 1.0 / np.cos(lat)
