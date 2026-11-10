"""Distortion catalogue: geometry of the degradations and exactness of the mitigations on a perfect model."""
from pathlib import Path

import numpy as np
import pytest

from methods.capture_faults.catalogue import (CATALOGUE, MITIGATIONS, estimate_down, m_gain_match, m_inpaint_tangent,
                                   m_none, m_relevel_self, occlusion_mask, rotation_between)
from pano.geometry.spherical import erp_to_sphere, latitude_map
from pano.models.depth_model import EncodedDepthOracle, encode_depth_as_image
from pano.paths import ROOT

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


# ---------- parallax and vignetting ----------
def _tex(seed=0):
    rng = np.random.default_rng(seed)
    t = cv2.resize(rng.integers(0, 255, (H // 4, W // 4, 3)).astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)
    return t


import cv2  # noqa: E402


def test_parallax_is_identity_for_points_on_the_stitching_sphere_and_zero_baseline():
    from methods.capture_faults.catalogue import parallax_apply
    tex = _tex()
    out, _ = parallax_apply(tex, {"depth": np.full((H, W), 2.0), "d_stitch": 2.0, "baseline": 0.05})
    assert np.abs(out.astype(float) - tex).mean() < 1.0                 # everything on the stitching sphere: no shift
    out0, _ = parallax_apply(tex, {"depth": np.full((H, W), 0.5), "baseline": 0.0})
    assert np.abs(out0.astype(float) - tex).mean() < 1.0                # no baseline: no parallax at any depth


def test_parallax_displaces_near_content_and_doubles_it_at_the_seam():
    from methods.capture_faults.catalogue import _parallax_view
    from pano.geometry.spherical import erp_lonlat_grid
    lon, lat = (np.degrees(x.numpy()) for x in erp_lonlat_grid(H, W))
    tex = np.zeros((H, W, 3), np.uint8)
    # vertical stripes: at the stitch line the displacement runs along longitude (away from the lens axis), so only
    # structure that varies with longitude reveals it
    tex[((lon // 8).astype(int) % 2) == 0] = 255
    depth = np.full((H, W), 0.3)
    front = _parallax_view(tex, depth, 0.10, 2.0, +1)
    back = _parallax_view(tex, depth, 0.10, 2.0, -1)
    # the lenses see the near band from different centres: at the stitch line the two images disagree
    seam = (np.abs(np.abs(lon) - 90) < 3) & (np.abs(lat) < 25)
    assert np.abs(front[seam].astype(float) - back[seam]).mean() > 5
    # the displacement grows with the angle from the lens axis (~ sin): next to the axis it is far smaller than at the
    # seam (90 deg off-axis), where it is about (b/2)(1/r - 1/D0) = 0.14 rad = 8 deg here
    def shift_deg(img, rows, lon_lo, lon_hi):
        m = (lon[0] > lon_lo) & (lon[0] < lon_hi)
        a, b = tex[rows][:, m, 0].astype(float).mean(0), img[rows][:, m, 0].astype(float).mean(0)
        best = min(range(-12, 13), key=lambda k: np.abs(np.roll(a, k) - b).mean())
        return abs(best) * 360.0 / W
    rows = slice(H // 2 - 2, H // 2 + 2)
    assert shift_deg(front, rows, 60, 120) > 5 and shift_deg(front, rows, -20, 20) <= 2


def test_vignetting_darkens_the_seams_and_flatfield_undoes_it_blindly():
    from methods.capture_faults.catalogue import _lens_angle_deg, m_flatfield, vignette_apply
    tex = _tex(1)
    out, ctx = vignette_apply(tex, {})
    th = _lens_angle_deg(H, W)
    assert out[th > 80].mean() < 0.65 * tex[th > 80].mean() and abs(out[th < 10].mean() - tex[th < 10].mean()) < 3
    c = {}
    m_flatfield(PERFECT, out, c)
    assert c["flatfield_gain_edge"] == pytest.approx(1 / ctx["vignette"][th > 85].mean(), rel=0.15)


def test_parallax_and_vignette_are_in_the_catalogue_with_their_fixes():
    keys = {d.key: d for d in CATALOGUE}
    assert keys["parallax"].mitigations == ["seam_inpaint"] and keys["vignette"].mitigations == ["flatfield"]
    _, ctx = keys["parallax"].apply(_tex(), {"depth": np.full((H, W), 1.0)})
    m = keys["parallax"].region(H, W, ctx)
    assert 0.05 < m.mean() < 0.2


def test_estimate_down_refuses_implausible_tilts(monkeypatch):
    from methods.polar_fusion import planar_prior
    from methods.capture_faults.catalogue import estimate_down, tilt_apply
    # the real failure (MiDaS, one Structured3D frame): the fitted floor normal points UP, i.e. 'down' ~180 deg from the
    # image's down. Such an estimate must be refused, or re-levelling turns the panorama upside down.
    flipped = lambda *a, **k: (None, [{"pole": "floor", "c": [0.0, -1.0, 0.1], "inlier_share": 0.9},
                                      {"pole": "ceiling", "c": [0.0, 1.0, 0.0], "inlier_share": 0.9}])
    monkeypatch.setattr(planar_prior, "fit_polar_planes", flipped)
    assert estimate_down(PERFECT, np.ones((H, W)), "depth") is None
    monkeypatch.undo()
    # a moderate tilt is still estimated exactly (and the limit is configurable)
    tilted, ctx = tilt_apply(RGB, {"pitch": 20.0, "roll": 10.0})
    est = estimate_down(PERFECT, m_none(PERFECT, tilted, ctx), "depth")
    assert est is not None and np.degrees(np.arccos(np.clip(est @ (ctx["R"].T @ np.array([0, 1.0, 0])), -1, 1))) < 1.0
    assert estimate_down(PERFECT, m_none(PERFECT, tilted, ctx), "depth", max_dev_deg=10.0) is None


def test_study_recovery_counts_only_frames_where_the_fault_hurt():
    src = (ROOT / "scripts" / "run" / "distortion_study.py").read_text()
    assert ">= 0.05 * r[" in src and '"flatfield"' in src
