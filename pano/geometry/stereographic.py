"""Stereographic (conformal) views of the sphere.

A stereographic view centred on the direction c uses the same camera frame as a tangent plane,
R_c = [right | down | forward] (see tangent_plane.py). A unit direction with camera coordinates
(x, y, z) maps to the view plane as

    (x_s, y_s) = 2 (x, y) / (1 + z)              radius  rho = 2 tan(alpha / 2)

where alpha is the angle to the optical axis. The inverse is

    d = (4 x_s, 4 y_s, 4 - rho^2) / (4 + rho^2).

An N x N image whose full field of view along the image axes is `fov` has

    f  = (N / 2) / (2 tan(fov / 4)),   cx = cy = N / 2 - 0.5,   pixel = f * (x_s, y_s) + c.

Why this projection. Stereographic projection is conformal: around every point it is an
*isotropic* scaling by

    k(alpha) = 1 + rho^2 / 4 = sec^2(alpha / 2) = 2 / (1 + cos alpha)

relative to the view centre (k = 2 at 90 deg off-axis, i.e. on the horizon of a hemisphere
view). Shapes are preserved locally; only apparent size changes. For comparison, a gnomonic
view stretches by sec^2(alpha) radially and sec(alpha) tangentially (4x by 2x at 60 deg), and an
ERP stretches by 1/cos(lat) horizontally only (3.9x at 75 deg). A 180 deg stereographic view of a
pole therefore shows the whole polar hemisphere, with its surrounding walls as context, at
most 2x magnified and never sheared.

Depth semantics. A learned model infers distance partly from apparent size. A region magnified
by k looks k times closer (the scaling law used by Depth Any Camera, Guo et al. 2025:
Z' = Z u / u'), so the prediction is modelled as range / k. `magnification` returns k per pixel so
that callers can undo it. Whether the law holds for a given model is an empirical question; the
ablation `acgf|nolaw` switches it off.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch

from .erp_projection import _as_tensor4, sample_erp
from .spherical import erp_to_sphere, sphere_to_erp
from .tangent_plane import generate_tangent_plane, sample_view_on_erp


@dataclass
class StereoView:
    lon_deg: float
    lat_deg: float
    fov_deg: float
    size: int
    R: np.ndarray = field(repr=False)  # camera -> world rotation (columns: right, down, forward)
    roll_deg: float = 0.0

    @property
    def f(self) -> float:
        return (self.size / 2.0) / (2.0 * math.tan(math.radians(self.fov_deg) / 4.0))

    @property
    def c(self) -> float:
        return self.size / 2.0 - 0.5

    def to_dict(self):
        return dict(kind="stereo", lon_deg=self.lon_deg, lat_deg=self.lat_deg, fov_deg=self.fov_deg, size=self.size,
                    roll_deg=self.roll_deg)


def generate_stereo_view(lon_deg: float, lat_deg: float, fov_deg: float = 180.0, size: int = 384,
                         roll_deg: float = 0.0) -> StereoView:
    """Stereographic camera centred on (lon, lat); same orientation convention as a tangent plane."""
    if not 0.0 < fov_deg < 360.0:
        raise ValueError(f"stereographic fov must be in (0, 360), got {fov_deg}")
    R = generate_tangent_plane(lon_deg, lat_deg, 90.0, size, roll_deg).R
    return StereoView(lon_deg, lat_deg, fov_deg, int(size), R, roll_deg)


def stereo_world_dirs(view: StereoView, device=None) -> torch.Tensor:
    """Unit world directions for each view pixel (N, N, 3), float64."""
    idx = torch.arange(view.size, dtype=torch.float64, device=device)
    xs = (idx - view.c) / view.f
    yy, xx = torch.meshgrid(xs, xs, indexing="ij")
    rho2 = xx * xx + yy * yy
    cam = torch.stack([4 * xx, 4 * yy, 4 - rho2], -1) / (4 + rho2)[..., None]
    R = torch.as_tensor(view.R, dtype=cam.dtype, device=cam.device)
    return cam @ R.T


def erp_to_stereo(erp, view: StereoView, mode: str = "bilinear", mask=None):
    """Render the stereographic view of an ERP image (seam- and pole-aware sampling)."""
    t, _, _ = _as_tensor4(erp)
    H, W = t.shape[-2:]
    u, v = sphere_to_erp(stereo_world_dirs(view, device=t.device), H, W)
    return sample_erp(erp, u, v, mode=mode, mask=mask)


@dataclass
class StereoToErpResult:
    values: np.ndarray  # (H, W[, C])
    valid: np.ndarray  # (H, W) bool: ERP pixel is seen by the view
    alpha_deg: np.ndarray  # (H, W) angle between the ERP ray and the optical axis
    magnification: np.ndarray  # (H, W) k = sec^2(alpha / 2), isotropic scale relative to the view centre
    radial: np.ndarray  # (H, W) max(|x_s|, |y_s|) / (2 tan(fov / 4)), in [0, 1] inside the view


def stereo_geometry_on_erp(view: StereoView, height: int, width: int, max_alpha_deg: float = 150.0):
    """For every ERP pixel: continuous view pixel coords, visibility, off-axis angle, magnification, radial."""
    d = erp_to_sphere(height, width)
    cam = d @ torch.as_tensor(view.R, dtype=d.dtype)  # row form of R^T d
    x, y, z = cam[..., 0], cam[..., 1], cam[..., 2]
    one_z = (1 + z).clamp_min(1e-9)
    xs, ys = 2 * x / one_z, 2 * y / one_z
    j = view.f * xs + view.c
    i = view.f * ys + view.c
    N = view.size
    alpha = torch.rad2deg(torch.arccos(z.clamp(-1, 1)))
    inside = (alpha < max_alpha_deg) & (j >= -0.5) & (j <= N - 0.5) & (i >= -0.5) & (i <= N - 0.5)
    k = 2.0 / one_z
    radial = torch.maximum(xs.abs(), ys.abs()) / (2 * math.tan(math.radians(view.fov_deg) / 4))
    return j, i, inside.numpy(), alpha.numpy(), k.numpy(), radial.numpy()


def stereo_to_erp(img, view: StereoView, height: int, width: int, mode: str = "bilinear", mask=None,
                  valid_threshold: float = 0.999) -> StereoToErpResult:
    """Inverse projection by backward warping (each ERP pixel samples the view image)."""
    j, i, inside, alpha, k, radial = stereo_geometry_on_erp(view, height, width)
    vals, vm = sample_view_on_erp(img, j, i, inside, view.size, mode, mask, valid_threshold)
    return StereoToErpResult(vals, vm, alpha, k, radial)


def magnification(alpha_deg) -> np.ndarray:
    """Isotropic stereographic scale factor sec^2(alpha/2) relative to the view centre."""
    return 1.0 / np.cos(np.radians(np.asarray(alpha_deg, dtype=np.float64)) / 2.0) ** 2
