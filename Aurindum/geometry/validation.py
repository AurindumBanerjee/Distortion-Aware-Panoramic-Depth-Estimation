"""Quantitative validation of the projection pipeline (Section 13 of the project spec).

Run:  python -m geometry.validation  -> prints a table and writes results/geometry_validation.json

Two families of checks:

1. Point-level (exact maths, no interpolation): random 3-D points with known depth are
   projected  sphere -> ERP pixel -> sphere -> tangent pixel -> sphere -> ERP pixel  and the
   angular / pixel / depth errors are measured. These must be ~1e-12.

2. Image-level (includes interpolation): a smooth analytic field f(direction) and an analytic
   planar depth scene are rendered to ERP, re-sampled to a tangent plane and back, and
   compared to the analytic values. These errors are bounded by interpolation error and
   shrink with resolution.
"""
from __future__ import annotations

import json
import math
import os
from typing import Dict

import numpy as np
import torch

from .erp_projection import rotate_erp, sample_erp
from .spherical import (angular_distance, erp_to_sphere, lonlat_to_xyz, rotation_from_ypr, sphere_to_erp,
                        xyz_to_lonlat)
from .tangent_plane import (erp_to_tangent, generate_tangent_plane, tangent_to_erp, tangent_world_dirs,
                            z_to_range)

TEST_CENTRES = {
    "centre (0,0)": (0.0, 0.0),
    "equator (120,0)": (120.0, 0.0),
    "mid-lat (45,35)": (45.0, 35.0),
    "high-lat (-60,65)": (-60.0, 65.0),
    "near-pole (10,85)": (10.0, 85.0),
    "north pole (0,90)": (0.0, 90.0),
    "south pole (0,-90)": (0.0, -90.0),
    "wrap (179,20)": (179.0, 20.0),
    "wrap (-178,-50)": (-178.0, -50.0),
}


def smooth_field(xyz: np.ndarray) -> np.ndarray:
    """Smooth, non-symmetric test function on the sphere (no singularity at the poles)."""
    x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    return 3.0 + np.sin(2.0 * x + 0.3) * np.cos(1.5 * y) + 0.5 * z + 0.25 * x * y


def point_level(n: int = 20000, seed: int = 0, H: int = 512, W: int = 1024) -> Dict[str, Dict[str, float]]:
    rng = np.random.default_rng(seed)
    out = {}
    for name, (lon_c, lat_c) in TEST_CENTRES.items():
        plane = generate_tangent_plane(lon_c, lat_c, fov_deg=90.0, size=512)
        # sample directions inside the tangent frustum: random camera rays, random ranges
        xn = rng.uniform(-0.99, 0.99, n)
        yn = rng.uniform(-0.99, 0.99, n)
        cam = np.stack([xn, yn, np.ones(n)], -1)
        d = cam @ plane.R.T
        d /= np.linalg.norm(d, axis=-1, keepdims=True)
        rng_m = rng.uniform(0.5, 20.0, n)  # known Euclidean depth (range)
        P = d * rng_m[:, None]  # 3-D points
        # 3-D -> ERP pixel
        u, v = sphere_to_erp(P, H, W)
        # ERP pixel -> sphere
        lon = (u + 0.5) / W * 2 * math.pi - math.pi
        lat = math.pi / 2 - (v + 0.5) / H * math.pi
        d1 = lonlat_to_xyz(lon, lat)
        # sphere -> tangent pixel (perspective projection with K, R)
        c = d1 @ plane.R
        j = plane.f * c[:, 0] / c[:, 2] + plane.c
        i = plane.f * c[:, 1] / c[:, 2] + plane.c
        # tangent pixel + planar depth z -> 3-D -> ERP
        z = rng_m * (d @ plane.R)[:, 2]  # planar depth of the true point
        cam2 = np.stack([(j - plane.c) / plane.f, (i - plane.c) / plane.f, np.ones(n)], -1)
        P2 = (cam2 * z[:, None]) @ plane.R.T
        u2, v2 = sphere_to_erp(P2, H, W)
        du = np.abs(u2 - u)
        du = np.minimum(du, W - du)  # wrap-aware
        out[name] = {
            "max_angle_err_deg": float(np.degrees(angular_distance(P2, P)).max()),
            "max_pixel_err": float(np.maximum(du, np.abs(v2 - v)).max()),
            "max_rel_depth_err": float((np.abs(np.linalg.norm(P2, axis=-1) - rng_m) / rng_m).max()),
        }
    return out


def image_level(H: int = 512, W: int = 1024, size: int = 384, fov: float = 90.0) -> Dict[str, Dict[str, float]]:
    """ERP -> tangent -> ERP with interpolation, measured against analytic values."""
    d_erp = erp_to_sphere(H, W).numpy()
    f_erp = smooth_field(d_erp)
    out = {}
    for name, (lon_c, lat_c) in TEST_CENTRES.items():
        plane = generate_tangent_plane(lon_c, lat_c, fov_deg=fov, size=size)
        # (a) ERP -> tangent, vs analytic field at the tangent rays
        tan = erp_to_tangent(f_erp, plane, mode="bilinear")
        f_tan = smooth_field(tangent_world_dirs(plane).numpy())
        e_fwd = np.abs(tan - f_tan) / np.abs(f_tan)
        # (b) analytic tangent image -> ERP, vs analytic ERP field
        back = tangent_to_erp(f_tan, plane, H, W, mode="bilinear")
        m = back.valid
        e_bwd = np.abs(back.values - f_erp)[m] / np.abs(f_erp)[m]
        # (c) full round trip ERP -> tangent -> ERP
        rt = tangent_to_erp(tan, plane, H, W, mode="bilinear")
        e_rt = np.abs(rt.values - f_erp)[rt.valid] / np.abs(f_erp)[rt.valid]
        # (d) planar depth scene: plane orthogonal to the optical axis at distance D.
        #     Perspective model output would be z == D everywhere; converted to range and
        #     reprojected it must equal the analytic ERP range D / cos(angle).
        D = 3.0
        z_img = np.full((size, size), D)
        r_img = z_to_range(z_img, plane)
        rb = tangent_to_erp(r_img, plane, H, W, mode="bilinear")
        cos_ax = np.clip(d_erp @ plane.R[:, 2], 1e-6, None)
        r_true = D / cos_ax
        e_depth = np.abs(rb.values - r_true)[rb.valid] / r_true[rb.valid]
        # z/range confusion that the conversion avoids (for reference)
        e_noconv = np.abs(D - r_true)[rb.valid] / r_true[rb.valid]
        out[name] = {
            "erp2tan_mean_rel_err": float(e_fwd.mean()), "erp2tan_max_rel_err": float(e_fwd.max()),
            "tan2erp_mean_rel_err": float(e_bwd.mean()), "tan2erp_max_rel_err": float(e_bwd.max()),
            "roundtrip_mean_rel_err": float(e_rt.mean()), "roundtrip_max_rel_err": float(e_rt.max()),
            "plane_range_max_rel_err": float(e_depth.max()),
            "plane_range_err_if_z_used_as_range_max": float(e_noconv.max()),
            "erp_pixels_covered": int(rb.valid.sum()),
        }
    return out


def rotation_level(H: int = 512, W: int = 1024) -> Dict[str, Dict[str, float]]:
    d_erp = erp_to_sphere(H, W).numpy()
    f = smooth_field(d_erp)
    lat = np.degrees(np.arcsin(-d_erp[..., 1]))
    res = {}
    # yaw by a multiple of 360/W must equal an exact column shift
    R = rotation_from_ypr(90, 0, 0)
    rot = rotate_erp(f, R)
    res["yaw90_vs_column_roll_max_abs"] = {"value": float(np.abs(rot - np.roll(f, -W // 4, axis=1)).max())}
    for yaw, pitch in [(0, 90), (0, -90), (30, 45), (0, 60), (90, 90)]:
        R = rotation_from_ypr(yaw, pitch, 0)
        rot = rotate_erp(f, R)
        analytic = smooth_field(d_erp @ R.T)  # I_rot(d) = f(R d)
        back = rotate_erp(rot, R.T)
        e1 = np.abs(rot - analytic) / np.abs(analytic)
        e2 = np.abs(back - f) / np.abs(f)
        res[f"yaw{yaw}_pitch{pitch}"] = {
            "rotate_mean_rel_err": float(e1.mean()), "rotate_max_rel_err": float(e1.max()),
            "roundtrip_mean_rel_err": float(e2.mean()), "roundtrip_max_rel_err": float(e2.max()),
            "roundtrip_mean_rel_err_|lat|>75": float(e2[np.abs(lat) > 75].mean()),
        }
    return res


def run_all(save_path: str = "results/geometry_validation.json") -> dict:
    torch.set_default_dtype(torch.float64)
    res = {"point_level": point_level(), "image_level": image_level(), "rotation": rotation_level()}
    torch.set_default_dtype(torch.float32)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(res, f, indent=2)
    return res


if __name__ == "__main__":
    import pandas as pd

    r = run_all()
    for k, v in r.items():
        print(f"\n=== {k} ===")
        print(pd.DataFrame(v).T.to_string(float_format=lambda x: f"{x:.3e}"))
