"""Regression tests for the three method series. Run: pytest -q tests/test_methods.py

These pin down the bugs found in the first GPU run (Nov 2026):
  * Möbius warp sampled radians as pixel coordinates; pure dilations never move the poles
  * Poisson fusion: inconsistent stencils, pole wrap-around, unconverged SOR
  * tangent alignment returned range and was fused against disparity
  * equatorial-only alignment + unbounded clip exploded polar depth
"""
import os
import sys

import pytest
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


def test_paired_test_detects_consistent_gain():
    from evaluation.protocol import paired_test
    base = [{"75-90": {"abs_rel": 0.5 + 0.01 * i}} for i in range(12)]
    better = [{"75-90": {"abs_rel": 0.4 + 0.01 * i}} for i in range(12)]
    r = paired_test(base, better, "75-90")
    assert r["p_wilcoxon"] < 0.01 and r["ci_low"] > 0 and r["n"] == 12


def test_float_rgb_is_rescaled_for_models():
    from models.depth_model import as_uint8_rgb
    f = np.full((4, 4, 3), 0.5, np.float32)
    assert as_uint8_rgb(f).max() == 128  # v1 Structured3D loader passed [0,1] floats -> near-black input
    u = np.full((4, 4, 3), 200, np.uint8)
    assert as_uint8_rgb(u) is u


def test_protocol_none_only_for_metric_models():
    import pytest
    from evaluation.protocol import align_to_gt, default_protocols

    class Metric:
        space, scale = "depth", "metric"

    class Rel:
        space, scale = "disparity", "affine"
    gt = np.full((8, 16), 2.0)
    out = align_to_gt(np.full_like(gt, 2.2), gt, np.ones_like(gt, bool), Metric(), "none", 0.1, 10.0)
    assert np.allclose(out, 2.2)
    assert default_protocols(Metric())[0] == "none" and default_protocols(Rel())[0] == "align-all"
    with pytest.raises(ValueError):
        align_to_gt(gt, gt, np.ones_like(gt, bool), Rel(), "none")


def test_logdepth_polar_fusion_removes_view_scale_error():
    sys.path.insert(0, str(ROOT / "1_gradient_polar_fusion"))
    from polar_views import fuse_polar, to_fusion
    H, W = 32, 64
    phi = np.abs(latitude_map(H, W))
    D = 2.0 + np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    view = np.where(phi > 40, to_fusion(D * 1.3, "logdepth"), np.nan)  # polar view with a 30% scale error
    out = fuse_polar(D, view, "logdepth", phi, mode="gradient_poisson")
    assert np.abs(out / D - 1).max() < 1e-6


def test_as_uint8_rgb_integer_valued_floats_are_not_rescaled():
    from models.depth_model import as_uint8_rgb
    almost_black = np.zeros((4, 4, 3), np.float32)
    almost_black[0, 0] = 1.0  # 0/1-valued 0..255 image (e.g. a dark rotated crop), NOT a [0,1] image
    assert as_uint8_rgb(almost_black).max() == 1
    assert as_uint8_rgb(np.full((4, 4, 3), 0.25, np.float32)).max() == 64


def test_tracker_replaces_nan_record(tmp_path):
    from best_model.tracker import BestModelTracker
    t = BestModelTracker(str(tmp_path))
    t.best_record = {"metrics": {"all": {"abs_rel": float("nan")}, "75-90": {"abs_rel": float("nan")}}}
    assert t.is_better({"all": {"abs_rel": 0.3}, "75-90": {"abs_rel": 0.4}})
    t.best_record = {"metrics": {"all": {"abs_rel": 0.3}, "75-90": {"abs_rel": 0.4}}}
    assert not t.is_better({"all": {"abs_rel": 0.2}, "75-90": {"abs_rel": float("nan")}})


def test_missing_config_is_fatal(tmp_path):
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "3_structured3d_benchmark" / "run.py"), "--config", "nope.yaml"],
                       capture_output=True, text=True, cwd=str(tmp_path))
    assert r.returncode != 0 and "Config not found" in r.stderr


class _ScaledModel:
    """Metric ERP 'model': returns a function of the image; non-identity passes get a wrong scale."""
    space, scale = "depth", "metric"

    def __init__(self, factor_for_warped=1.0):
        self.calls = 0
        self.factor = factor_for_warped

    def predict(self, rgb, kind="erp"):
        self.calls += 1
        base = 2.0 + 0.0 * rgb[..., 0].astype(np.float64)
        return base * (1.0 if self.calls == 1 else self.factor)


def test_robust_fit_logscale_recovers_multiplicative_factor():
    from tta_ensemble import _robust_fit
    x = np.random.default_rng(0).uniform(1, 5, 5000)
    a, b = _robust_fit(x, 1.7 * x * np.exp(np.random.default_rng(1).normal(0, 0.02, 5000)), "logscale")
    assert abs(a - 1.7) < 0.03 and b == 0.0


def test_auto_reanchor_for_metric_model_is_logscale():
    from tta_ensemble import MobiusTTAEnsemble
    assert MobiusTTAEnsemble(_ScaledModel(), passes=[{"pitch": 90, "scale": 1.0}]).reanchor == "logscale"


def test_gate_makes_output_identity_below_lo_and_uses_passes_above():
    from tta_ensemble import MobiusTTAEnsemble
    H, W = 64, 128
    rgb = np.zeros((H, W, 3), np.uint8)
    ens = MobiusTTAEnsemble(_ScaledModel(1.0), passes=[{"pitch": 90, "scale": 1.0}], reanchor="none",
                            gate_lat=[30, 55])
    ident = np.full((H, W), 2.0)
    ens.model.calls = 1  # identity pass is supplied, so the next call is a warped pass
    ens.model.factor = 3.0  # the warped pass is deliberately wrong (6.0 instead of 2.0)
    fused, _ = ens.predict(rgb, identity_pred=ident)
    lat = np.abs(latitude_map(H, W))
    assert np.allclose(fused[lat < 30], 2.0)          # gate closed: identical to the baseline
    assert fused[lat > 60].max() > 2.5                 # gate open: the wrong pass leaks in (so the gate is what protects)
    ens_off = MobiusTTAEnsemble(_ScaledModel(), passes=[{"pitch": 90, "scale": 1.0}], reanchor="none", gate_lat=None)
    assert ens_off.gate_lat is None


def test_group_of_clusters_by_house_environment_and_holo_scene():
    from evaluation.protocol import group_of
    assert group_of("scene_03370_994351") == "scene_03370"
    assert group_of("ClothingStore_0028") == "ClothingStore"
    assert group_of("Indoor_016_1753495960.845721") == "Indoor_016"
    assert group_of("Outdoor_001_1752225730.993451") == "Outdoor_001"
    assert group_of("something") == "something"


def test_panorama_dataset_applies_mask_column_and_keeps_metres(tmp_path):
    import cv2
    from datasets.panorama import PanoramaDataset
    (tmp_path / "S" / "S" / "rgb").mkdir(parents=True)
    (tmp_path / "S" / "S" / "mask").mkdir(parents=True)
    (tmp_path / "S" / "S" / "depth").mkdir(parents=True)
    rgb = np.full((32, 64, 3), 128, np.uint8)
    mask = np.full((32, 64), 255, np.uint8)
    mask[24:, :] = 0                                   # operator at the south pole
    depth = np.full((32, 64), 2.5, np.float32)
    depth[:4] = np.nan                                 # sky
    cv2.imwrite(str(tmp_path / "S/S/rgb/a.jpg"), rgb)
    cv2.imwrite(str(tmp_path / "S/S/mask/a.png"), mask)
    np.save(tmp_path / "S/S/depth/a.npy", depth)
    (tmp_path / "t.txt").write_text("S/S/rgb/a.jpg S/S/depth/a.npy S/S/mask/a.png\n")
    s = PanoramaDataset(str(tmp_path), "t.txt", height=32, width=64, name="holo360d")[0]
    assert s.id == "S_a"
    assert not s.valid[:4].any() and not s.valid[24:].any() and s.valid[8:20].all()
    assert np.allclose(s.depth[s.valid], 2.5)          # holo360d preset: EXR/npy already in metres (no cm scaling)


class _ConstMetric:
    space, scale = "depth", "metric"

    def predict(self, rgb, kind="erp"):
        return np.full(rgb.shape[:2], 3.0)


def test_benchmark_evaluator_methods_filter_skips_unrequested_methods():
    sys.path.insert(0, str(ROOT / "3_structured3d_benchmark"))
    from benchmark_evaluator import run_single_benchmark_scene
    from tta_ensemble import MobiusTTAEnsemble
    H, W = 32, 64
    model = _ConstMetric()
    rgb = np.zeros((H, W, 3), np.uint8)
    gt = np.full((H, W), 3.0)
    valid = np.ones((H, W), bool)
    ens = MobiusTTAEnsemble(model, passes=[{"pitch": 90, "scale": 1.0}], reanchor="none")
    kw = dict(scene_info={"id": "x"}, rgb=rgb, gt_depth=gt, valid_gt=valid, model=model, m1_solver=None,
              m2_ensemble=ens, phi_thresh=45.0, protocols=["none"], min_depth=0.1, max_depth=10.0)
    out = run_single_benchmark_scene(methods=("Method2_MobiusTTA", "Control_YawEnsemble"), **kw)
    assert set(out) == {"Baseline", "Method2_MobiusTTA", "Control_YawEnsemble", "predictions"}
    assert set(out["predictions"]) == {"baseline", "method2_mobius", "control_yaw"}
    assert out["Method2_MobiusTTA"]["none"]["all"]["abs_rel"] < 1e-6


# ---------- rotation-only preset, fit guard, re-anchor diagnostic ----------
class _ContentModel:
    """Disparity-like model whose output depends on the image, so rotated passes carry real structure."""
    space, scale = "disparity", "affine"

    def predict(self, rgb, kind="erp"):
        g = rgb[..., 0].astype(np.float64) / 255.0
        return 0.5 + g


def _content_rgb(H=64, W=128):
    lat = np.abs(latitude_map(H, W))
    lon = np.linspace(0, 2 * np.pi, W)[None, :]
    return (255 * (0.5 + 0.4 * np.sin(3 * lon) * np.cos(np.deg2rad(lat)))).astype(np.uint8)[..., None].repeat(3, -1)


def test_preset_overrides_passes_and_rejects_unknown():
    from tta_ensemble import MobiusTTAEnsemble
    ens = MobiusTTAEnsemble(_ContentModel(), passes=[{"pitch": 0, "scale": 1.6}], preset="rotation_only")
    assert sorted(p for p, _ in ens.passes) == [-90.0, 0.0, 90.0] and all(abs(s - 1.0) < 1e-9 for _, s in ens.passes)
    with pytest.raises(ValueError):
        MobiusTTAEnsemble(_ContentModel(), preset="nope")


def test_fit_quality_and_guard_weight():
    from tta_ensemble import fit_quality, guard_weight
    rng = np.random.default_rng(0)
    x = rng.uniform(0.5, 2.0, 2000)
    assert fit_quality(x, 2 * x + 1, 2.0, 1.0, "affine") < 1e-9               # perfect fit
    assert fit_quality(x, rng.permutation(x), 1.0, 0.0, "affine") > 0.5        # unrelated -> large residual
    assert guard_weight(0.0, 1.0, 0.5, 4.0) == 1.0
    assert guard_weight(2.0, 1.0, 0.5, 4.0) < 1e-3
    assert guard_weight(0.0, 10.0, 0.5, 4.0) == 0.0 and guard_weight(0.0, 0.1, 0.5, 4.0) == 0.0
    assert guard_weight(float("nan"), 1.0, 0.5, 4.0) == 1.0


def test_guard_off_is_bitwise_unchanged_and_bad_pass_falls_back_to_identity():
    from tta_ensemble import MobiusTTAEnsemble
    rgb = _content_rgb()
    base = MobiusTTAEnsemble(_ContentModel(), preset="rotation_only")
    off, d_off = base.predict(rgb)
    assert np.isfinite(off).all() and all(d["guard_w"] == 1.0 for d in d_off)
    # tau -> 0 kills every pass with a non-zero residual: output equals the identity prediction
    strict = MobiusTTAEnsemble(_ContentModel(), preset="rotation_only", fit_guard={"tau": 1e-9, "a_max": 4.0})
    out, d = strict.predict(rgb)
    resid = [x["anchor_res"] for x in d[1:]]
    if min(resid) > 1e-6:
        assert np.allclose(out, _ContentModel().predict(rgb), atol=1e-6)
    assert all(np.isfinite(x["anchor_n"]) for x in d)


def test_diagnose_frame_and_summary_run_on_a_fake_model():
    import importlib.util
    spec = importlib.util.spec_from_file_location("diag", os.path.join(os.path.dirname(__file__), "..", "scripts", "diagnose_reanchor.py"))
    diag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diag)
    H, W = 64, 128
    rgb = _content_rgb(H, W)
    gt = 1.0 / (0.5 + rgb[..., 0].astype(np.float64) / 255.0) * 2.0
    valid = np.ones((H, W), bool)
    rows = diag.diagnose_frame(_ContentModel(), rgb, gt, valid, [{"pitch": 90.0, "scale": 1.0}, {"pitch": -90.0, "scale": 1.0}],
                               min_depth=0.1, max_depth=10.0)
    assert len(rows) == 2
    for r in rows:
        assert np.isfinite(r["intrinsic_gain"]) and np.isfinite(r["realised_gain"]) and r["n_anchor"] > 0
        r["frame"] = "f0"
    txt = diag.summarize(rows * 3, "unit")
    assert "intrinsic gain" in txt and "AUC" in txt
    assert diag._auc(np.array([3., 4., 1., 2.]), np.array([True, True, False, False])) == 1.0
    assert abs(diag._auc(np.array([1., 1., 1., 1.]), np.array([True, True, False, False])) - 0.5) < 1e-9
