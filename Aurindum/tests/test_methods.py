"""Regression tests for the three method series. Run: pytest -q tests/test_methods.py

These pin down the bugs found in the first GPU run (Nov 2026):
  * Möbius warp sampled radians as pixel coordinates; pure dilations never move the poles
  * Poisson fusion: inconsistent stencils, pole wrap-around, unconverged SOR
  * tangent alignment returned range and was fused against disparity
  * equatorial-only alignment + unbounded clip exploded polar depth
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for sub in ("", "1_gradient_polar_fusion", "2_mobius_tta_ensembling"):
    p = str(ROOT / sub) if sub else str(ROOT)
    if p not in sys.path:
        sys.path.insert(0, p)

import gradient_blending as gb  # noqa: E402
from geometry.spherical import latitude_map  # noqa: E402
from mobius_transform import unwarp_depth_mobius, warp_erp_mobius  # noqa: E402
from shift_alignment import align_tangent_disparity_to_erp  # noqa: E402
from evaluation.protocol import align_to_gt  # noqa: E402


def _lat_img(H=64, W=128):
    return latitude_map(H, W).astype(np.float32)


def test_mobius_roundtrip_is_identity():
    lat = _lat_img()
    for pitch, sc in [(0, 1.6), (0, 0.625), (90, 1.0), (-90, 1.0), (90, 1.3)]:
        w, _ = warp_erp_mobius(lat, sc, pitch)
        back = unwarp_depth_mobius(w, sc, pitch)
        m = np.abs(lat) < 75
        assert np.median(np.abs(back - lat)[m]) < 0.05, (pitch, sc)


def test_mobius_pitch_moves_pole_to_centre_and_dilation_does_not():
    H, W = 64, 128
    lat = _lat_img(H, W)
    w, seen = warp_erp_mobius(lat, 1.0, 90.0)
    assert w[H // 2, W // 2] > 80          # north-pole content at the image centre
    assert seen[0].mean() < 5              # ...so the pole row is seen near the equator
    _, seen_d = warp_erp_mobius(lat, 1.6, 0.0)
    assert seen_d[0].mean() > 85           # a pure dilation keeps the pole at the pole


def test_poisson_integrates_exactly():
    H, W = 32, 64
    phi = np.abs(latitude_map(H, W))
    D = 1 + 0.5 * np.sin(np.linspace(0, 6, W))[None] + np.linspace(0, 1, H)[:, None]
    gx, gy = gb._edge_gradients(D)
    out = gb.solve_screened_poisson_sparse(np.where(phi < 30, D, 0), gx, gy, phi < 30)
    assert np.abs(out - D).max() < 1e-9


def test_gradient_fusion_is_shift_invariant_to_tangent_offset():
    H, W = 32, 64
    phi = np.abs(latitude_map(H, W))
    D = 1 + np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    f = gb.gradient_domain_polar_fuse(D, D + 0.3, np.ones_like(D), phi)
    assert np.abs(f - D).max() < 1e-9


def test_tangent_alignment_returns_disparity_space():
    H, W = 32, 64
    phi = np.abs(latitude_map(H, W))
    erp = 0.5 + np.random.default_rng(0).uniform(0, 1, (H, W))
    cos = np.full((H, W), 0.8)
    tan = np.where(phi > 40, (erp - 0.1) / (2.0 * 0.8), np.nan)  # erp = 2*cos*tan + 0.1
    al, info = align_tangent_disparity_to_erp(tan, erp, cos, phi, anchor_max_lat=60.0, min_anchor_pixels=10)
    m = np.isfinite(al)
    assert np.allclose(al[m], erp[m], rtol=1e-6)


def test_alignment_is_clamped():
    class M:
        space, scale = "disparity", "affine"
    gt = np.full((16, 32), 2.0)
    pred = np.full((16, 32), 1.0)
    pred[:2] = -5.0  # would map to a negative / huge depth
    out = align_to_gt(pred, gt, np.ones_like(gt, bool), M(), "align-equatorial", 0.1, 10.0)
    assert out.max() <= 10.0 and out.min() >= 0.1
