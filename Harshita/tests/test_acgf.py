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


def test_acgf_v2_linear_work_and_value_gate(scene):
    v2 = dict(tangent_size=128, acgf_work="auto", acgf_gate_mode="value")
    base, out = _run(AffineDisparityOracle(strength=0.4), scene, [MethodConfig("baseline"), MethodConfig("acgf", **v2)])
    mb, mc = _bands(base["pred"], scene, "disparity"), _bands(out["pred"], scene, "disparity")
    assert mc["75-90"]["abs_rel"] < 0.6 * mb["75-90"]["abs_rel"]
    assert np.array_equal(out["pred"][48:80], base["pred"][48:80])
    assert np.all(out["pred"] >= base["pred"].min())  # linear work space keeps the baseline's floor
    base, gated = _run(NoisyViewsOracle(), scene, [MethodConfig("baseline"), MethodConfig("acgf", **v2)])
    mb, mg = _bands(base["pred"], scene, "depth"), _bands(gated["pred"], scene, "depth")
    assert mg["75-90"]["abs_rel"] < mb["75-90"]["abs_rel"] + 0.02


# ---------------------------------------------------------------- acgf|ico (E12)

from inference.conformal_fusion import ACGFParams, ErpView, ico_erp_views, ico_view_products, view_products
from inference.mono360 import icosahedron_planes


class DriftDisparityOracle(AffineDisparityOracle):
    """Affine disparity per call, plus a smooth scale drift across every perspective view (1 + 0.4 x, x in [-1, 1]):
    what a single affine fit cannot remove and mono360's deformable grids can."""

    def _forward(self, images, kind):
        out = super()._forward(images, kind)
        if kind == "erp":
            return out
        return [(o * (1.0 + 0.4 * np.linspace(-1, 1, o.shape[1])[None, :])).astype(np.float32) for o in out]


def _ico_inputs(model, depth, size=64):
    rgb = encode_depth_as_image(depth)
    dai = DistortionAwareInference(model, batch_size=4)
    base = dai.run(rgb, "s", MethodConfig("baseline"))["pred"]
    planes = icosahedron_planes(size, 0.3)
    raw = [e["out"] for e in dai.tangent_raw_batch(rgb, "s", planes)]
    return base, raw, planes


def test_acgf_v2_reproduces_pre_ico_outputs(scene):
    """v2 must not change: outputs of the code before acgf|ico was added (tests/data/acgf_v2_oracle_ref.npz)."""
    ref = np.load("tests/data/acgf_v2_oracle_ref.npz")
    v2 = MethodConfig("acgf", tangent_size=128, acgf_work="auto", acgf_gate_mode="value")
    for key, model in (("enc", EncodedDepthOracle(strength=0.4)), ("aff", AffineDisparityOracle(strength=0.4))):
        (out,) = _run(model, scene, [v2])
        assert np.allclose(out["pred"], ref[key], rtol=1e-10, atol=0, equal_nan=True)


def test_view_products_shapes_and_view_noise():
    """sigma_n^2 from n views with pixel-iid noise N(0, s^2) estimates the variance of one view's edge differences,
    2 s^2, whatever n; v_bar is the mean of the views; n_eff counts them.

    Known quirk, kept so that v1/v2 reproduce bit-for-bit: edges_to_pixels counts the two horizontal edges of a pixel
    as one (bool + bool is OR), so per-pixel edge statistics are scaled by 4/3 in the interior. The factor is common
    to sigma_n^2 and the baseline excess and cancels in gamma."""
    H, W, s = 64, 128, 0.05
    lat = np.radians(90 - (np.arange(H) + 0.5) / H * 180)[:, None]
    truth = np.cos(lat) * np.sin(np.radians(np.arange(W) * 360 / W))[None, :] + 2.0
    rng = np.random.default_rng(0)
    p = ACGFParams(work="linear", gate_mode="value")
    for n in (2, 5):
        ev = [ErpView(f"v{k}", 0, truth + rng.normal(0, s, (H, W)), np.ones((H, W), bool), np.zeros((H, W)))
              for k in range(n)]
        prod = view_products(truth, ev, p, sigma_px=3.0)
        assert prod.gamma.shape == prod.u_v.shape == prod.t_h.shape == prod.w_h.shape == (H, W)
        assert prod.t_v.shape == prod.w_v.shape == (H - 1, W)
        assert prod.n_views == n
        assert abs(np.median(prod.view_noise) / (4 / 3 * 2 * s ** 2) - 1) < 0.1
        assert np.allclose(prod.n_eff[8:-8], n, atol=1e-6)
        assert np.allclose(prod.u_v, np.mean([v.u for v in ev], 0))
        assert np.allclose(prod.t_v, np.mean([v.u[1:] - v.u[:-1] for v in ev], 0))
        # gate: baseline = truth -> views add nothing (gamma ~ 0); baseline with a structured error -> gamma ~ 1
        assert np.median(prod.gamma) < 0.2
        bad = truth + 1.0 * np.sin(np.radians(np.arange(W) * 360 / W * 6))[None, :]  # error >> view noise
        assert np.median(view_products(bad, ev, p, sigma_px=3.0).gamma) > 0.8


def test_ico_adapter_aligns_each_view_to_the_baseline(scene):
    """Every icosahedral view gets its own random scale / shift from the model; the adapter's robust pinhole fit on
    the trusted band puts each one back on the baseline (exact at strength 0)."""
    model = AffineDisparityOracle(strength=0.0)
    base, raw, planes = _ico_inputs(model, scene)
    p = ACGFParams(work="auto", gate_mode="value")
    ev, _ = ico_erp_views(base, raw, planes, model, p, align="affine")
    assert len(ev) == 20 and all(v.info["coef"][0] > 0 for v in ev)
    lat = np.abs(90 - (np.arange(base.shape[0]) + 0.5) / base.shape[0] * 180)[:, None] * np.ones((1, base.shape[1]))
    for v in ev:
        m = v.valid & (lat < 45)
        if m.sum() > 50:
            assert np.median(np.abs(v.u[m] - base[m]) / base[m]) < 0.05  # resampling + 8-bit encoding
    prod, extra = ico_view_products(base, raw, planes, model, p, align="affine")
    assert prod.n_views == 20 and len(extra["view_info"]) == 20
    assert prod.t_h.shape == base.shape and prod.t_v.shape == (base.shape[0] - 1, base.shape[1])
    assert prod.n_eff[lat > 60].min() > 1.5  # several views per polar pixel


def test_ico_grid_removes_within_view_drift(scene):
    """A smooth scale drift inside each view survives the affine fit; the baseline-anchored grids remove most of it
    (with a soft enough grid: lam_smooth 4 here; how stiff it should be is chosen on validation)."""
    model = DriftDisparityOracle(strength=0.0)
    base, raw, planes = _ico_inputs(model, scene)
    p = ACGFParams(work="auto", gate_mode="value")
    lat = np.abs(90 - (np.arange(base.shape[0]) + 0.5) / base.shape[0] * 180)[:, None] * np.ones((1, base.shape[1]))

    def err(ev):
        return np.mean([np.median(np.abs(v.u[m] - base[m]) / base[m]) for v in ev
                        for m in [v.valid & (lat < 45)] if m.sum() > 50])
    aff, _ = ico_erp_views(base, raw, planes, model, p, align="affine")
    grid, gi = ico_erp_views(base, raw, planes, model, p, align="grid",
                             grid={"grids": ((4, 3), (8, 7)), "lam_smooth": 4.0, "lam_scale": 0.007})
    assert gi["n_refined"] > 10
    assert err(grid) < 0.5 * err(aff)


@pytest.mark.parametrize("align", ["affine", "grid"])
def test_acgf_ico_reduces_polar_error(scene, align):
    cfgs = [MethodConfig("baseline")] + [
        MethodConfig("acgf", tangent_size=64, acgf_work="auto", acgf_gate_mode="value", acgf_source="ico",
                     acgf_ico_align=align, acgf_scope=sc) for sc in ("polar", "sphere")]
    base, polar, sphere = _run(AffineDisparityOracle(strength=0.4), scene, cfgs)
    mb = _bands(base["pred"], scene, "disparity")
    for out in (polar, sphere):
        mc = _bands(out["pred"], scene, "disparity")
        assert mc["75-90"]["abs_rel"] < 0.6 * mb["75-90"]["abs_rel"]
        assert out["model_calls"] == 21
    assert np.array_equal(polar["pred"][48:80], base["pred"][48:80])  # polar scope: |lat| < 22.5 untouched


def test_acgf_ico_sphere_gate_protects_equator(scene):
    """Sphere scope gives up the fixed equator; with a perfect baseline and noisy views the gate has to keep it."""
    cfgs = [MethodConfig("baseline"), MethodConfig("acgf", tangent_size=64, acgf_work="auto", acgf_gate_mode="value",
                                                   acgf_source="ico", acgf_scope="sphere")]
    base, sphere = _run(NoisyViewsOracle(), scene, cfgs)
    mb, ms = _bands(base["pred"], scene, "depth"), _bands(sphere["pred"], scene, "depth")
    for b in ("0-15", "15-30", "75-90"):
        assert ms[b]["abs_rel"] < mb[b]["abs_rel"] + 0.02


def test_plan_contains_acgf_ico():
    names = [mc.name for _, mc in build_plan(load_config("configs/acgf_ico.yaml"))]
    assert len(names) == len(set(names))
    for n in ("acgf|ico-affine|polar", "acgf|ico-affine|sphere", "acgf|ico-grid|polar", "acgf|ico-grid|sphere"):
        assert n in names
