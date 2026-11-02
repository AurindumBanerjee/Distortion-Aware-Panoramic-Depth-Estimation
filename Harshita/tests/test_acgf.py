"""Tests for the stereographic projection, ACGF and the 360MonoDepth-style baseline.

Oracles (never reported as results):
  * EncodedDepthOracle: metric range, latitude-dependent noise on ERP inputs only.
  * AffineDisparityOracle: the same, returned as disparity with a random scale and shift per call
    (like MiDaS), to exercise the gradient-domain fit of affine models.
  * NoisyViewsOracle: a perfect ERP baseline but noisy pole views, to test the "do no harm" gate.
"""
import math

import numpy as np
import pytest
import torch

from datasets.synthetic import _texture_bank, random_scene, render_erp
from evaluation.latitude_analysis import per_band_metrics
from evaluation.metrics import to_metric_depth
from experiments.common import build_plan, load_config
from geometry.spherical import erp_to_sphere
from geometry.stereographic import (erp_to_stereo, generate_stereo_view, magnification, stereo_geometry_on_erp,
                                    stereo_to_erp, stereo_world_dirs)
from geometry.validation import smooth_field
from inference.pipeline import DistortionAwareInference, MethodConfig
from models.depth_model import EncodedDepthOracle, OutputSpec, encode_depth_as_image


class AffineDisparityOracle(EncodedDepthOracle):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "affine_disparity_oracle"
        self.spec = OutputSpec(space="disparity", scale="affine", geometry_erp="range", geometry_perspective="range")
        self._rng = np.random.default_rng(7)

    def _forward(self, images, kind):
        out = []
        for d in super()._forward(images, kind):
            s, t = self._rng.uniform(0.5, 2.0), self._rng.uniform(0.0, 0.5)
            out.append((s / d + t).astype(np.float32))
        return out


class NoisyViewsOracle(EncodedDepthOracle):
    """Exact on ERP input; independent multiplicative noise on every perspective view."""

    def _forward(self, images, kind):
        outs = []
        for k, im in enumerate(images):
            x = im[..., 0].astype(np.float64) / 255.0
            d = np.exp(np.log(self.dmin) + x * (np.log(self.dmax) - np.log(self.dmin)))
            if kind != "erp":
                import cv2
                rng = np.random.default_rng(1000 + self.n_calls + k)
                d = d * np.exp(0.3 * cv2.GaussianBlur(rng.normal(0, 1, d.shape), (0, 0), 3) * 3)
            outs.append(d.astype(np.float32))
        return outs


@pytest.fixture(scope="module")
def scene():
    bank = _texture_bank(0)
    sc = random_scene(np.random.default_rng(3), len(bank))
    _, depth = render_erp(sc, bank, 128, 256, ss=1)
    return depth


# ---------------------------------------------------------------- geometry

def test_stereo_pixel_roundtrip():
    v = generate_stereo_view(30.0, 70.0, 180.0, 64)
    d = stereo_world_dirs(v)
    cam = d @ torch.as_tensor(v.R)
    j = v.f * 2 * cam[..., 0] / (1 + cam[..., 2]) + v.c
    i = v.f * 2 * cam[..., 1] / (1 + cam[..., 2]) + v.c
    I, J = torch.meshgrid(torch.arange(64.0, dtype=torch.float64), torch.arange(64.0, dtype=torch.float64), indexing="ij")
    assert float((j - J).abs().max()) < 1e-9 and float((i - I).abs().max()) < 1e-9


def test_stereo_is_conformal_with_known_magnification():
    v = generate_stereo_view(0.0, 0.0, 180.0, 401)
    d = stereo_world_dirs(v).numpy()
    for (i, j) in [(200, 200), (200, 330), (60, 60), (200, 395)]:
        ang = lambda a, b: math.acos(float(np.clip(a @ b, -1, 1)))
        dx, dy = ang(d[i, j], d[i, j + 1 if j < 400 else j - 1]), ang(d[i, j], d[i + 1, j])
        assert abs(dx / dy - 1) < 1e-2  # isotropic (conformal)
        alpha = math.degrees(math.acos(float(np.clip(d[i, j] @ v.R[:, 2], -1, 1))))
        d0 = ang(d[200, 200], d[200, 201])
        assert abs(d0 / dx - magnification(alpha)) < 2e-2 * magnification(alpha)
    assert np.allclose(magnification([0.0, 90.0]), [1.0, 2.0])


def test_stereo_erp_roundtrip_and_coverage():
    H, W = 128, 256
    f = smooth_field(erp_to_sphere(H, W).numpy())
    v = generate_stereo_view(0.0, -90.0, 180.0, 256)
    r = stereo_to_erp(erp_to_stereo(f, v), v, H, W)
    lat = 90 - (np.arange(H) + 0.5) / H * 180
    assert r.valid[lat < -1].all()  # a 180 deg view of the south pole sees the whole southern hemisphere
    m = r.valid
    assert np.abs(r.values[m] - f[m]).mean() / np.abs(f[m]).mean() < 1e-3


# ---------------------------------------------------------------- ACGF

def _run(model, depth, cfgs):
    rgb = encode_depth_as_image(depth)
    dai = DistortionAwareInference(model, batch_size=4)
    return [dai.run(rgb, "s", c, return_views=True) for c in cfgs]


def _bands(pred, depth, space):
    valid = np.isfinite(depth)
    if space == "disparity":
        pred, _ = to_metric_depth(pred, np.nan_to_num(depth, nan=1.0), valid, "disparity", "affine")
    return per_band_metrics(pred, depth, valid)


@pytest.mark.parametrize("domain", ["gradient", "value"])
@pytest.mark.parametrize("screen", ["baseline", "value"])
def test_acgf_reduces_polar_error_and_keeps_equator(scene, domain, screen):
    base, out = _run(EncodedDepthOracle(strength=0.4), scene,
                     [MethodConfig("baseline"), MethodConfig("acgf", tangent_size=128, acgf_domain=domain,
                                                            acgf_screen=screen)])
    mb, mc = _bands(base["pred"], scene, "depth"), _bands(out["pred"], scene, "depth")
    assert mc["75-90"]["abs_rel"] < 0.4 * mb["75-90"]["abs_rel"]
    assert mc["60-75"]["abs_rel"] < 0.6 * mb["60-75"]["abs_rel"]
    assert np.array_equal(out["pred"][48:80], base["pred"][48:80])  # |lat| < 22.5: untouched
    assert np.all(out["pred"] > 0)


def test_acgf_affine_disparity_model(scene):
    base, out = _run(AffineDisparityOracle(strength=0.4), scene,
                     [MethodConfig("baseline"), MethodConfig("acgf", tangent_size=128, acgf_screen="value")])
    mb, mc = _bands(base["pred"], scene, "disparity"), _bands(out["pred"], scene, "disparity")
    assert mc["75-90"]["abs_rel"] < 0.6 * mb["75-90"]["abs_rel"]
    assert all(vi.get("coef", [0])[0] > 0 for vi in out["view_info"])


def test_gate_does_no_harm_when_views_are_unreliable(scene):
    base, gated, ungated = _run(NoisyViewsOracle(), scene, [
        MethodConfig("baseline"), MethodConfig("acgf", tangent_size=128, acgf_screen="value"),
        MethodConfig("acgf", tangent_size=128, acgf_screen="value", acgf_gate=False)])
    mb, mg, mu = (_bands(r["pred"], scene, "depth") for r in (base, gated, ungated))
    for b in ("60-75", "75-90"):
        assert mg[b]["abs_rel"] < 0.5 * mu[b]["abs_rel"]  # gate removes most of the damage
        assert mg[b]["abs_rel"] < mb[b]["abs_rel"] + 0.02
    lat = 90 - (np.arange(128) + 0.5) / 128 * 180
    assert gated["gamma"][np.abs(lat) > 60].mean() < 0.3


def test_mono360_aligns_affine_views(scene):
    (out,) = _run(AffineDisparityOracle(strength=0.0), scene, [MethodConfig("mono360", tangent_size=96)])
    assert out["model_calls"] == 20
    m = _bands(out["pred"], scene, "disparity")
    assert m["all"]["abs_rel"] < 0.08


def test_plan_contains_acgf_methods():
    cfg = load_config("configs/acgf_structured3d.yaml")
    names = [mc.name for _, mc in build_plan(cfg)]
    assert len(names) == len(set(names))
    assert "acgf" in names and "acgf|nogate" in names and "mono360" in names


def test_acgf_with_rotation_views(scene):
    base, out = _run(EncodedDepthOracle(strength=0.4), scene,
                     [MethodConfig("baseline"), MethodConfig("acgf", tangent_size=128,
                                                            acgf_rotations=[[0, 90, 0], [0, -90, 0]])])
    mb, mc = _bands(base["pred"], scene, "depth"), _bands(out["pred"], scene, "depth")
    assert mc["75-90"]["abs_rel"] < 0.4 * mb["75-90"]["abs_rel"]
    assert out["model_calls"] == 1 + 4 + 2
    assert sum(vi["kind"] == "rotation" for vi in out["view_info"]) == 4  # 2 passes x 2 hemispheres
