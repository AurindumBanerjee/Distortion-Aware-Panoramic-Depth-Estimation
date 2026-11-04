"""Sampling ERP images at arbitrary spherical locations, and spherical rotations of ERP images.

The key subtlety is the topology of the ERP domain:
  * longitude wraps around (column -1 is column W-1);
  * crossing a pole (row -1) lands on row 0 at longitude + pi (column + W/2).
`sample_erp` pads the image accordingly before calling `grid_sample`, so
bilinear / bicubic interpolation is correct across the seam and the poles.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from .spherical import erp_to_sphere, sphere_to_erp

_PAD = 2  # enough for bicubic


def _as_tensor4(img) -> Tuple[torch.Tensor, bool, int]:
    """Accept (H,W), (H,W,C) numpy / (B,C,H,W) torch. Returns (B,C,H,W) float tensor."""
    if isinstance(img, np.ndarray):
        if img.ndim == 2:
            t = torch.from_numpy(img)[None, None]
            return t.double() if img.dtype == np.float64 else t.float(), True, 2
        t = torch.from_numpy(np.ascontiguousarray(img.transpose(2, 0, 1)))[None]
        return t.double() if img.dtype == np.float64 else t.float(), True, 3
    if img.dim() == 2:
        return img[None, None], False, 2
    if img.dim() == 3:
        return img[None], False, 3
    return img, False, 4


def _restore(t: torch.Tensor, was_np: bool, ndim: int):
    if ndim == 2:
        t = t[0, 0]
    elif ndim == 3:
        t = t[0]
    if was_np:
        t = t.cpu().numpy()
        if ndim == 3:
            t = t.transpose(1, 2, 0)
    return t


def pad_erp(img: torch.Tensor, pad: int = _PAD) -> torch.Tensor:
    """Pad a (B,C,H,W) ERP so that interpolation is correct across the seam and the poles."""
    B, C, H, W = img.shape
    shift = W // 2
    # Across the north pole: row -k  ==  row k-1 rotated by 180 deg in longitude.
    top = torch.roll(img[:, :, :pad, :].flip(-2), shifts=shift, dims=-1)
    bottom = torch.roll(img[:, :, H - pad:, :].flip(-2), shifts=shift, dims=-1)
    img = torch.cat([top, img, bottom], dim=-2)
    # Longitude wrap-around
    img = torch.cat([img[..., -pad:], img, img[..., :pad]], dim=-1)
    return img


def sample_erp(img, u, v, mode: str = "bilinear", mask=None, valid_threshold: float = 0.999):
    """Sample an ERP image at continuous pixel coordinates (u, v).

    Args:
        img:  (B,C,H,W) tensor, or numpy (H,W)/(H,W,C).
        u, v: tensors/arrays of identical shape (Ho, Wo) (or (B,Ho,Wo)); pixel coordinates
              in the ERP frame (u may lie outside [0, W): it is wrapped).
        mode: 'bilinear' | 'nearest' | 'bicubic'.
        mask: optional validity mask with the same spatial size as img. If given, invalid
              pixels never contribute; returns (values, valid) where `valid` marks output
              pixels whose interpolation support is (almost) fully valid.
    """
    t, was_np, ndim = _as_tensor4(img)
    B, C, H, W = t.shape
    dev = t.device
    u = torch.as_tensor(u, device=dev, dtype=torch.float64)
    v = torch.as_tensor(v, device=dev, dtype=torch.float64)
    if u.dim() == 2:
        u = u[None].expand(B, -1, -1)
        v = v[None].expand(B, -1, -1)
    u = torch.remainder(u + 0.5, W) - 0.5  # wrap longitude
    v = torch.clamp(v, -0.5, H - 0.5)
    P = _PAD
    Hp, Wp = H + 2 * P, W + 2 * P
    gx = (u + P + 0.5) / Wp * 2 - 1
    gy = (v + P + 0.5) / Hp * 2 - 1
    grid = torch.stack([gx, gy], -1).to(t.dtype)

    if mask is None:
        out = F.grid_sample(pad_erp(t), grid, mode=mode, padding_mode="border", align_corners=False)
        return _restore(out, was_np, ndim)

    m, _, _ = _as_tensor4(mask)
    m = m.to(dev).to(t.dtype)
    if m.shape[1] != 1:
        m = m[:, :1]
    if mode == "nearest":
        out = F.grid_sample(pad_erp(t), grid, mode="nearest", padding_mode="border", align_corners=False)
        mv = F.grid_sample(pad_erp(m), grid, mode="nearest", padding_mode="border", align_corners=False)
        valid = mv > 0.5
        out = out * valid
    else:
        # Normalised (masked) interpolation: sum(w*m*x) / sum(w*m)
        num = F.grid_sample(pad_erp(t * m), grid, mode="bilinear", padding_mode="border", align_corners=False)
        den = F.grid_sample(pad_erp(m), grid, mode="bilinear", padding_mode="border", align_corners=False)
        valid = den >= valid_threshold
        out = torch.where(den > 1e-8, num / den.clamp_min(1e-8), torch.zeros_like(num)) * valid
    valid = valid[:, :1]
    if was_np:
        vm = valid[0, 0].cpu().numpy()
    else:
        vm = valid[0, 0] if ndim == 2 else (valid[0] if ndim == 3 else valid)
    return _restore(out, was_np, ndim), vm


def rotation_sampling_coords(height: int, width: int, R: np.ndarray, src_hw: Optional[Tuple[int, int]] = None,
                             device=None):
    """Pixel coordinates in the *source* ERP for every pixel of the rotated ERP.

    Convention: I_rot(d) = I_src(R @ d)  (the rotated panorama is what a camera
    rotated by R would see). Undo with R.T.
    """
    Hs, Ws = src_hw if src_hw is not None else (height, width)
    d = erp_to_sphere(height, width, device=device)  # (H,W,3), float64
    Rt = torch.as_tensor(R, dtype=d.dtype, device=d.device)
    src = d @ Rt.T  # row-vector form of R @ d
    return sphere_to_erp(src, Hs, Ws)


def rotate_erp(img, R: np.ndarray, mode: str = "bilinear", mask=None, out_hw: Optional[Tuple[int, int]] = None):
    """Rotate an ERP panorama on the sphere (NOT a pixel shift, except for pure yaw).

    Values are sampled with `sample_erp`, so the seam and poles are handled
    correctly. Depth *values* are invariant under rotation about the camera centre
    (range is rotation invariant), so depth maps can be rotated with the same call.
    """
    t, _, _ = _as_tensor4(img)
    H, W = t.shape[-2:]
    Ho, Wo = out_hw if out_hw is not None else (H, W)
    u, v = rotation_sampling_coords(Ho, Wo, R, src_hw=(H, W), device=t.device)
    return sample_erp(img, u, v, mode=mode, mask=mask)


def rotated_latitude(height: int, width: int, R: np.ndarray) -> np.ndarray:
    """Latitude (degrees) that each ORIGINAL ERP pixel has inside the panorama rotated by R.

    If I_rot(d) = I(R d), the original pixel with direction d appears in the rotated
    frame at direction R^T d. Used for distortion-aware weighting of rotated views.
    """
    d = erp_to_sphere(height, width).numpy()
    d_rot = d @ np.asarray(R)  # row form of R^T d
    return np.degrees(np.arcsin(np.clip(-d_rot[..., 1], -1, 1)))


def rotated_lonlat(height: int, width: int, R: np.ndarray):
    """(lon, lat) in degrees that each ORIGINAL ERP pixel has inside the panorama rotated by R."""
    d = erp_to_sphere(height, width).numpy()
    d_rot = d @ np.asarray(R)
    lon = np.degrees(np.arctan2(d_rot[..., 0], d_rot[..., 2]))
    lat = np.degrees(np.arcsin(np.clip(-d_rot[..., 1], -1, 1)))
    return lon, lat


def seam_factor(lon_deg: np.ndarray, seam_width_deg: float) -> np.ndarray:
    """0 at the ERP seam (lon = +-180), ramping to 1 at seam_width degrees away from it.

    Most networks process an ERP as a flat image without circular padding, so the left and right
    borders of their input are predicted without context and are mutually inconsistent.
    """
    if seam_width_deg <= 0:
        return np.ones_like(lon_deg)
    return np.clip((180.0 - np.abs(lon_deg)) / seam_width_deg, 0.0, 1.0)
