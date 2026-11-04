"""Distortion catalogue: geometry of the degradations and exactness of the mitigations on a perfect model."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "1_gradient_polar_fusion", ROOT / "2_mobius_tta_ensembling"):
    sys.path.insert(0, str(p))

from distortions.catalogue import (CATALOGUE, MITIGATIONS, estimate_down, m_gain_match, m_inpaint_tangent,  # noqa: E402
                                   m_none, m_relevel_self, occlusion_mask, rotation_between)
from geometry.spherical import erp_to_sphere, latitude_map  # noqa: E402
from models.depth_model import EncodedDepthOracle, encode_depth_as_image  # noqa: E402

H, W = 96, 192


def _room():
    d = erp_to_sphere(H, W).numpy()
    with np.errstate(divide="ignore"):
        f = np.where(d[..., 1] > 1e-6, 1.5 / d[..., 1], np.inf)
        c = np.where(d[..., 1] < -1e-6, 1.2 / -d[..., 1], np.inf)
        w = 3.0 / np.maximum(np.hypot(d[..., 0], d[..., 2]), 1e-9)
    return np.minimum(np.minimum(f, c), w)


GT = _room()
RGB = encode_depth_as_image(GT)
PERFECT = EncodedDepthOracle(strength=0.0)
D = {d.key: d for d in CATALOGUE}


def _rel(p, m=None):
    e = np.abs(p - GT) / GT
    return float(np.median(e if m is None else e[m]))


def test_rotation_between_is_a_rotation_mapping_a_to_b():
    for a, b in [((0, 1, 0), (0.2, 0.9, 0.1)), ((0, 1, 0), (0, -1, 0)), ((1, 0, 0), (1, 0, 0))]:
        a, b = np.array(a, float), np.array(b, float)
        Q = rotation_between(a, b)
        assert np.allclose(Q @ (a / np.linalg.norm(a)), b / np.linalg.norm(b), atol=1e-9)
        assert np.allclose(Q @ Q.T, np.eye(3), atol=1e-9) and np.linalg.det(Q) == pytest.approx(1.0)


def test_tilt_round_trip_and_both_relevelings_on_a_perfect_model():
    d = D["tilt"]
    rd, ctx = d.apply(RGB, {})
    assert _rel(d.to_original(m_none(PERFECT, rd, ctx), ctx)) < 0.01       # to_original undoes the tilt
    assert _rel(d.to_original(MITIGATIONS["relevel_known"][1](PERFECT, rd, ctx), ctx)) < 0.01
    p = m_relevel_self(PERFECT, rd, ctx)
    R, Q = ctx["R"], ctx["Q_est"]
    assert np.degrees(np.arccos(np.clip((R @ Q)[1, 1], -1, 1))) < 0.5      # R Q is (almost) a pure yaw: levelled
    assert _rel(d.to_original(p, ctx)) < 0.01
    down = estimate_down(PERFECT, m_none(PERFECT, rd, ctx), "depth")
    assert np.degrees(np.arccos(np.clip(down @ (R.T @ np.array([0, 1.0, 0])), -1, 1))) < 0.5


def test_self_relevel_is_harmless_on_a_level_panorama():
    ctx = {}
    p = m_relevel_self(PERFECT, RGB, ctx)
    assert np.allclose(ctx["Q_est"], np.eye(3), atol=1e-2) and _rel(p) < 0.01


@pytest.mark.parametrize("key", ["nadir", "vfov"])
def test_occlusion_mitigations_rank_and_plane_fill_is_exact_on_planar_caps(key):
    d = D[key]
    rd, ctx = d.apply(RGB, {})
    reg = d.region(H, W, ctx)
    err = {k: _rel(MITIGATIONS[k][1](PERFECT, rd, ctx), reg) for k in ["none"] + d.mitigations}
    assert err["none"] > 0.3 and err["inpaint_tangent"] < err["inpaint_erp"] < err["none"]
    assert err["plane_fill"] < 0.01
    vis = np.abs(latitude_map(H, W)) < 40          # the plane fill only touches the occluded caps and their ring
    assert np.allclose(MITIGATIONS["plane_fill"][1](PERFECT, rd, ctx)[vis], m_inpaint_tangent(PERFECT, rd, ctx)[vis])


def test_nadir_mask_is_only_the_bottom_cap():
    _, ctx = D["nadir"].apply(RGB, {})
    m = occlusion_mask(H, W, ctx)
    lat = latitude_map(H, W)
    assert m.any() and not m[lat > -60].any() and m[lat < -63].all()


def test_seam_gain_is_recovered_blindly():
    rd, ctx = D["seam"].apply(RGB, {})
    m_gain_match(PERFECT, rd, ctx)
    assert np.allclose(ctx["gain_est"], ctx["gain"], atol=0.02)


def test_yaw_blur_is_circular_and_wiener_inverts_it_on_a_textured_image():
    rng = np.random.default_rng(0)
    tex = np.clip(128 + 60 * rng.standard_normal((H, W, 3)), 0, 255).astype(np.uint8)
    rd, ctx = D["yawblur"].apply(tex, {})
    assert abs(rd.astype(float).mean() - tex.astype(float).mean()) < 0.5   # box kernel preserves the mean (circular)
    K = np.fft.rfft(ctx["kernel"])[None, :, None]
    rec = np.fft.irfft(np.fft.rfft(rd.astype(np.float32), axis=1) * np.conj(K) / (np.abs(K) ** 2 + 0.01), n=W, axis=1)
    assert np.abs(rec - tex).mean() < 0.6 * np.abs(rd.astype(float) - tex).mean()


def test_photometric_distortions_change_pixels_but_not_shape():
    for key in ("noise", "jpeg", "lowres", "seam", "yawblur"):
        rd, _ = D[key].apply(RGB, {"seed": 1})
        assert rd.shape == RGB.shape and rd.dtype == np.uint8
    rd, _ = D["noise"].apply(np.full((H, W, 3), 128, np.uint8), {"seed": 1})
    assert rd.std() > 5
