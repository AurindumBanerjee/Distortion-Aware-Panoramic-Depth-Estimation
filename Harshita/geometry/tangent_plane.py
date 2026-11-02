"""Tangent-plane (gnomonic / pinhole) projections of the sphere.

A tangent plane touches the unit sphere at the direction c = d(lon_c, lat_c). A
pinhole camera at the sphere centre looking along c with square image of N x N
pixels and field of view `fov` has intrinsics

    f  = (N / 2) / tan(fov / 2)
    cx = cy = N / 2 - 0.5                          (pixel-centre convention)

and camera->world rotation R_c = [right | down | forward] with

    forward = c
    right   = (cos lon_c, 0, -sin lon_c)          (d/d lon, never degenerate, even at poles)
    down    = forward x right

so a camera pixel (i, j) has world ray  R_c @ ((j - cx)/f, (i - cy)/f, 1).

Depth semantics. A perspective model predicts planar depth z (distance along the
optical axis) whereas ERP ground truth is Euclidean range r (distance along the ray):

    r = z * sqrt(1 + x_n^2 + y_n^2) = z / cos(angle to optical axis)

`z_to_range` / `range_to_z` implement this; forgetting it gives errors of up to
1/cos(fov/2) - 1 (41% at the corners of a 90 deg view).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from .erp_projection import _as_tensor4, _restore, sample_erp
from .spherical import erp_to_sphere, lonlat_to_xyz, sphere_to_erp


@dataclass
class TangentPlane:
    lon_deg: float
    lat_deg: float
    fov_deg: float
    size: int
    R: np.ndarray = field(repr=False)  # camera -> world rotation (columns: right, down, forward)
    roll_deg: float = 0.0

    @property
    def f(self) -> float:
        return (self.size / 2.0) / math.tan(math.radians(self.fov_deg) / 2.0)

    @property
    def c(self) -> float:
        return self.size / 2.0 - 0.5

    @property
    def K(self) -> np.ndarray:
        return np.array([[self.f, 0, self.c], [0, self.f, self.c], [0, 0, 1.0]])

    def to_dict(self):
        return dict(lon_deg=self.lon_deg, lat_deg=self.lat_deg, fov_deg=self.fov_deg, size=self.size,
                    roll_deg=self.roll_deg)


def generate_tangent_plane(lon_deg: float, lat_deg: float, fov_deg: float = 90.0, size: int = 512,
                           roll_deg: float = 0.0) -> TangentPlane:
    """Build the pinhole camera tangent to the sphere at (lon, lat)."""
    lon, lat = math.radians(lon_deg), math.radians(lat_deg)
    fwd = lonlat_to_xyz(np.array(lon), np.array(lat)).astype(np.float64)
    right = np.array([math.cos(lon), 0.0, -math.sin(lon)])
    down = np.cross(fwd, right)
    R = np.stack([right, down, fwd], axis=1)  # columns
    if roll_deg:
        a = math.radians(roll_deg)
        Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        R = R @ Rz
    return TangentPlane(lon_deg, lat_deg, fov_deg, int(size), R, roll_deg)


def tangent_camera_rays(plane: TangentPlane, device=None) -> torch.Tensor:
    """Un-normalised camera-frame rays (x_n, y_n, 1) for each tangent pixel, (N, N, 3) float64."""
    N = plane.size
    idx = torch.arange(N, dtype=torch.float64, device=device)
    xn = (idx - plane.c) / plane.f
    yy, xx = torch.meshgrid(xn, xn, indexing="ij")
    return torch.stack([xx, yy, torch.ones_like(xx)], -1)


def tangent_world_dirs(plane: TangentPlane, device=None) -> torch.Tensor:
    """Unit world directions for each tangent pixel (N, N, 3)."""
    rays = tangent_camera_rays(plane, device)
    R = torch.as_tensor(plane.R, dtype=rays.dtype, device=rays.device)
    d = rays @ R.T
    return d / d.norm(dim=-1, keepdim=True)


def ray_norm(plane: TangentPlane) -> np.ndarray:
    """sqrt(1 + x_n^2 + y_n^2) per tangent pixel, i.e. 1/cos(angle to optical axis)."""
    return tangent_camera_rays(plane).norm(dim=-1).numpy()


def z_to_range(z, plane: TangentPlane):
    """Planar (z-buffer) depth on the tangent image -> Euclidean range along each ray."""
    n = ray_norm(plane)
    return z * (torch.as_tensor(n, dtype=z.dtype, device=z.device) if isinstance(z, torch.Tensor) else n)


def range_to_z(r, plane: TangentPlane):
    n = ray_norm(plane)
    return r / (torch.as_tensor(n, dtype=r.dtype, device=r.device) if isinstance(r, torch.Tensor) else n)


def erp_to_tangent(erp, plane: TangentPlane, mode: str = "bilinear", mask=None):
    """Render the tangent-plane (perspective) view of an ERP image.

    Every tangent pixel's ray is converted to (lon, lat) and the ERP is sampled there
    with seam- and pole-aware interpolation.
    """
    t, _, _ = _as_tensor4(erp)
    H, W = t.shape[-2:]
    d = tangent_world_dirs(plane, device=t.device)
    u, v = sphere_to_erp(d, H, W)
    return sample_erp(erp, u, v, mode=mode, mask=mask)


@dataclass
class TangentToErpResult:
    values: np.ndarray  # (H, W[, C]) or tensor
    valid: np.ndarray  # (H, W) bool: ERP pixel is seen by the tangent camera
    cos_axis: np.ndarray  # (H, W) cos(angle between ERP ray and optical axis)
    radial: np.ndarray  # (H, W) max(|x_n|, |y_n|) / tan(fov/2) in [0, 1] inside the view


def tangent_geometry_on_erp(plane: TangentPlane, height: int, width: int):
    """For every ERP pixel: its continuous tangent pixel coords, visibility, cos-angle and radial position."""
    d = erp_to_sphere(height, width)  # (H,W,3)
    R = torch.as_tensor(plane.R, dtype=d.dtype)
    cam = d @ R  # row form of R^T d
    z = cam[..., 2]
    front = z > 1e-6
    zs = torch.where(front, z, torch.ones_like(z))
    xn, yn = cam[..., 0] / zs, cam[..., 1] / zs
    j = plane.f * xn + plane.c
    i = plane.f * yn + plane.c
    N = plane.size
    inside = front & (j >= -0.5) & (j <= N - 0.5) & (i >= -0.5) & (i <= N - 0.5)
    t = math.tan(math.radians(plane.fov_deg) / 2)
    radial = torch.maximum(xn.abs(), yn.abs()) / t
    cos_axis = z.clamp(min=0)  # d is unit -> z = cos(angle)
    return j, i, inside.numpy(), cos_axis.numpy(), radial.numpy()


def tangent_to_erp(tan_img, plane: TangentPlane, height: int, width: int, mode: str = "bilinear", mask=None,
                   valid_threshold: float = 0.999) -> TangentToErpResult:
    """Inverse projection: scatter a tangent-plane image back onto the ERP grid.

    Implemented as backward warping (each ERP pixel samples the tangent image), so no
    holes appear. Pixels outside the tangent frustum are marked invalid.
    """
    j, i, inside, cos_axis, radial = tangent_geometry_on_erp(plane, height, width)
    vals, vm = sample_view_on_erp(tan_img, j, i, inside, plane.size, mode, mask, valid_threshold)
    return TangentToErpResult(vals, vm, cos_axis, radial)


def sample_view_on_erp(view_img, j, i, inside, N: int, mode: str = "bilinear", mask=None,
                       valid_threshold: float = 0.999):
    """Backward-warp an N x N view image onto the ERP grid, given each ERP pixel's continuous view
    pixel coords (j, i) and its visibility `inside`. Shared by every view projection."""
    t, was_np, ndim = _as_tensor4(view_img)
    t = t.double() if t.dtype == torch.float64 else t.float()
    gx = (j + 0.5) / N * 2 - 1
    gy = (i + 0.5) / N * 2 - 1
    grid = torch.stack([gx, gy], -1)[None].to(t.dtype).to(t.device).expand(t.shape[0], -1, -1, -1)
    if mask is None:
        out = F.grid_sample(t, grid, mode=mode, padding_mode="border", align_corners=False)
        valid = torch.as_tensor(inside, device=t.device)[None, None]
    else:
        m, _, _ = _as_tensor4(mask)
        m = m.to(t.device).to(t.dtype)
        if mode == "nearest":
            out = F.grid_sample(t, grid, mode="nearest", padding_mode="zeros", align_corners=False)
            mv = F.grid_sample(m, grid, mode="nearest", padding_mode="zeros", align_corners=False)
            valid = (mv > 0.5)
        else:
            num = F.grid_sample(t * m, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
            den = F.grid_sample(m, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
            valid = den >= valid_threshold
            out = torch.where(den > 1e-8, num / den.clamp_min(1e-8), torch.zeros_like(num))
        valid = valid & torch.as_tensor(inside, device=t.device)[None, None]
    out = out * valid
    return _restore(out, was_np, ndim), valid[0, 0].cpu().numpy()


# ----------------------------------------------------------------------------
# Layouts of tangent planes for polar correction
# ----------------------------------------------------------------------------


def polar_tangent_layout(lat_threshold_deg: float, views_per_pole: int = 1, poles: Tuple[str, ...] = ("north", "south"),
                         fov_deg: Optional[float] = None, ring_fov_deg: Optional[float] = None, size: int = 512,
                         margin_deg: float = 10.0, max_fov_deg: float = 130.0,
                         ring_lon_offset_deg: float = 0.0, ensure_coverage: bool = True) -> List[TangentPlane]:
    """Tangent planes that cover the polar caps |lat| > lat_threshold.

    views_per_pole = 1: one view centred on the pole, fov chosen so the half-FOV
        along the image axes reaches (90 - threshold) + margin degrees.
    views_per_pole = k > 1: one pole view plus (k-1) views on a ring at latitude
        between the threshold and the pole, evenly spaced in longitude. The ring
        views cover the band near the threshold where the pole view is most
        stretched (gnomonic stretch grows like 1/cos^2 off-axis).

    `fov_deg`/`ring_fov_deg` override the automatic choices. All choices are
    heuristics and are recorded in the experiment logs.
    """
    planes: List[TangentPlane] = []
    cap = 90.0 - lat_threshold_deg
    pole_fov = fov_deg if fov_deg is not None else min(2 * (cap + margin_deg), max_fov_deg)
    k_ring = max(views_per_pole - 1, 0)
    ring_lat = lat_threshold_deg + 0.4 * cap
    if k_ring:
        if ring_fov_deg is None:
            along = 360.0 / k_ring * math.cos(math.radians(ring_lat))  # arc spacing on the ring
            ring_fov = min(max(along + 2 * margin_deg, cap + 2 * margin_deg, 60.0), 110.0)
        else:
            ring_fov = ring_fov_deg
        # with a ring present, the pole view only needs to cover the upper cap
        if fov_deg is None:
            pole_fov = min(2 * ((90 - ring_lat) + margin_deg), max_fov_deg)
    def build(pf, rf, rlat=None):
        rlat = ring_lat if rlat is None else rlat
        out = []
        for pole in poles:
            s = 1.0 if pole == "north" else -1.0
            out.append(generate_tangent_plane(0.0, s * 90.0, pf, size))
            for k in range(k_ring):
                lon = -180.0 + ring_lon_offset_deg + (k + 0.5) * 360.0 / k_ring
                out.append(generate_tangent_plane(lon, s * rlat, rf, size))
        return out

    rf = ring_fov if k_ring else None
    planes = build(pole_fov, rf)
    if ensure_coverage and fov_deg is None and (ring_fov_deg is None or not k_ring):
        # Grow automatic FOVs (5 deg steps) until the caps are covered on a coarse grid.
        for _ in range(40):
            if _cap_coverage(planes, lat_threshold_deg) >= 0.999:
                break
            if k_ring and rf < 120.0:
                rf = min(rf + 5.0, 120.0)
            elif k_ring and ring_lat > lat_threshold_deg + 3.0:
                ring_lat -= 3.0  # move the ring towards the threshold band
            else:
                pole_fov = min(pole_fov + 5.0, max_fov_deg + 20.0)
            planes = build(pole_fov, rf, ring_lat)
    return planes


def _cap_coverage(planes: List[TangentPlane], lat_threshold_deg: float, H: int = 128, W: int = 256) -> float:
    lat = np.degrees(np.arcsin(-erp_to_sphere(H, W).numpy()[..., 1]))
    cover = np.zeros((H, W), bool)
    for p in planes:
        cover |= tangent_geometry_on_erp(p, H, W)[2]
    poles = {("north" if p.lat_deg > 0 else "south") for p in planes}
    cap = np.zeros_like(cover)
    if "north" in poles:
        cap |= lat >= lat_threshold_deg
    if "south" in poles:
        cap |= lat <= -lat_threshold_deg
    return float(cover[cap].mean())


def auto_tangent_size(fov_deg: float, erp_width: int) -> int:
    """Tangent resolution that matches the ERP equatorial angular resolution at the view centre."""
    f = erp_width / (2 * math.pi)
    return int(round(2 * f * math.tan(math.radians(fov_deg) / 2)))
