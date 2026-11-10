"""Geometry unit tests. Run: pytest -q tests/"""
import math

import numpy as np
import pytest
import torch

from pano.geometry.erp_projection import rotate_erp, sample_erp
from pano.geometry.spherical import (erp_to_sphere, lonlat_to_xyz, rotation_from_ypr, sphere_to_erp, xyz_to_lonlat)
from pano.geometry.tangent_plane import (erp_to_tangent, generate_tangent_plane, polar_tangent_layout, range_to_z,
                                    tangent_to_erp, z_to_range)
from pano.geometry.validation import image_level, point_level, smooth_field


def test_pixel_sphere_roundtrip():
    H, W = 64, 128
    d = erp_to_sphere(H, W)
    u, v = sphere_to_erp(d, H, W)
    uu, vv = torch.meshgrid(torch.arange(H, dtype=torch.float64), torch.arange(W, dtype=torch.float64), indexing="ij")
    assert torch.allclose(u, vv, atol=1e-9) and torch.allclose(v, uu, atol=1e-9)


def test_conventions():
    # centre of the ERP looks forward (+z); top row looks up (-y)
    d = lonlat_to_xyz(np.array(0.0), np.array(0.0))
    assert np.allclose(d, [0, 0, 1])
    d = lonlat_to_xyz(np.array(0.0), np.array(math.pi / 2))
    assert np.allclose(d, [0, -1, 0])
    lon, lat = xyz_to_lonlat(np.array([1.0, 0, 0]))
    assert np.isclose(lon, math.pi / 2) and np.isclose(lat, 0)


def test_point_level_exact():
    for name, r in point_level(n=2000).items():
        assert r["max_angle_err_deg"] < 1e-9, name
        assert r["max_pixel_err"] < 1e-8, name
        assert r["max_rel_depth_err"] < 1e-10, name


def test_image_level_interpolation_bounded():
    for name, r in image_level(H=256, W=512, size=192).items():
        assert r["roundtrip_mean_rel_err"] < 1e-4, name
        assert r["plane_range_max_rel_err"] < 1e-2, name
        assert r["plane_range_err_if_z_used_as_range_max"] > 0.3, name  # sanity: conversion matters


def test_seam_continuity():
    H, W = 32, 64
    f = smooth_field(erp_to_sphere(H, W).numpy())
    # sampling exactly at the seam (between last and first column) = average of both
    val = sample_erp(f, np.array([[W - 0.5]]), np.array([[10.0]]))
    assert np.isclose(val[0, 0], 0.5 * (f[10, -1] + f[10, 0]))


def test_pole_padding():
    H, W = 64, 128
    f = smooth_field(erp_to_sphere(H, W).numpy())
    val = sample_erp(f, np.array([[3.0, 70.0]]), np.array([[-0.5, -0.5]]))  # exactly at the north pole
    pole = smooth_field(np.array([0.0, -1.0, 0.0]))
    assert np.allclose(val, pole, atol=2e-3)


def test_yaw_is_column_shift():
    H, W = 32, 64
    f = np.random.default_rng(0).normal(size=(H, W))
    rot = rotate_erp(f, rotation_from_ypr(90, 0, 0))
    assert np.allclose(rot, np.roll(f, -W // 4, axis=1), atol=1e-6)


def test_pitch90_brings_north_pole_to_centre():
    H, W = 128, 256
    d = erp_to_sphere(H, W).numpy()
    f = -d[..., 1]  # = sin(lat): 1 at north pole
    rot = rotate_erp(f, rotation_from_ypr(0, 90, 0))
    assert rot[H // 2, W // 2] > 0.99


def test_masked_sampling_never_uses_invalid():
    H, W = 32, 64
    depth = np.full((H, W), 5.0)
    mask = np.ones((H, W), bool)
    depth[10:20, 20:30] = 1000.0
    mask[10:20, 20:30] = False
    plane = generate_tangent_plane(0, 0, 90, 64)
    vals, valid = erp_to_tangent(depth, plane, mode="bilinear", mask=mask)
    assert np.all(vals[valid] < 5.0 + 1e-6)


def test_z_range_inverse():
    plane = generate_tangent_plane(10, 70, 100, 64)
    z = np.random.default_rng(0).uniform(1, 5, (64, 64))
    assert np.allclose(range_to_z(z_to_range(z, plane), plane), z)


@pytest.mark.parametrize("thr", [30, 45, 60, 75])
@pytest.mark.parametrize("k", [1, 3, 5])
def test_polar_layout_covers_caps(thr, k):
    H, W = 128, 256
    planes = polar_tangent_layout(thr, views_per_pole=k, size=64)
    cover = np.zeros((H, W), bool)
    for p in planes:
        cover |= tangent_to_erp(np.ones((64, 64)), p, H, W).valid
    lat = np.degrees(np.arcsin(-erp_to_sphere(H, W).numpy()[..., 1]))
    assert cover[np.abs(lat) >= thr].mean() > 0.999
