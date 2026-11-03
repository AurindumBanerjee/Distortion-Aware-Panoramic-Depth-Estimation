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


def test_dataset_subset_spread_covers_every_scene(tmp_path):
    from datasets.panorama import PanoramaDataset
    lines = [f"{s}/{s}/rgb/{i:04d}.png {s}/{s}/depth/{i:04d}.exr\n" for s in ("A", "B", "C", "D") for i in range(25)]
    (tmp_path / "test.txt").write_text("".join(lines))
    first = PanoramaDataset(str(tmp_path), "test.txt", name="panox", limit=40)
    spread = PanoramaDataset(str(tmp_path), "test.txt", name="panox", limit=40, subset="spread")
    assert {it[0].split("/")[0] for it in first.items} == {"A", "B"}
    assert {it[0].split("/")[0] for it in spread.items} == {"A", "B", "C", "D"} and len(spread) == 40
    assert len(set(spread.items)) == 40
    with pytest.raises(ValueError):
        PanoramaDataset(str(tmp_path), "test.txt", name="panox", limit=10, subset="random")


def test_three_term_alignment_removes_tangent_shift_exactly():
    from shift_alignment import align_tangent_disparity_to_erp
    rng = np.random.default_rng(1)
    H, W = 64, 128
    phi = np.abs(latitude_map(H, W))
    r = rng.uniform(1.0, 6.0, (H, W))
    cos = np.clip(np.cos(np.deg2rad(90 - phi)) + 0.0, 0.7, 1.0)   # cos varies 0.7..1 across the view
    d_t = 2.0 / (r * cos) + 0.4          # tangent: s/z + t with z = r cos, t = 0.4
    d_e = 0.8 / r + 0.05                  # ERP: s_e/r + t_e
    view = np.where(phi > 40, d_t, np.nan)
    out3, info3 = align_tangent_disparity_to_erp(view, d_e, cos, phi, shift_model="cos")
    out2, info2 = align_tangent_disparity_to_erp(view, d_e, cos, phi, shift_model="none")
    m = np.isfinite(out3)
    assert info3["shift_model_used"] == "cos"
    assert np.abs(out3[m] - d_e[m]).max() < 1e-8
    assert np.abs(out2[m] - d_e[m]).max() > 1e-3          # the legacy fit cannot represent t*cos
    _, info1 = align_tangent_disparity_to_erp(view, d_e, np.ones((H, W)), phi, shift_model="cos")
    assert info1["shift_model_used"] == "none"            # cos constant (rotated ERP view): not identifiable


def test_robust_affine_fit_negative_scale_falls_back_to_identity():
    from shift_alignment import robust_affine_fit
    x = np.linspace(1, 2, 500)
    a, b, _ = robust_affine_fit(x, 5.0 - x)                 # decreasing relation -> a < 0
    assert (a, b) == (1.0, 0.0)


# ---------- planar prior, pass synchronisation, panoramic audit wrappers ----------
def _room_range(H=64, W=128, h_floor=1.5, h_ceil=1.2, radius=3.0):
    from geometry.spherical import erp_to_sphere
    d = erp_to_sphere(H, W).numpy()
    with np.errstate(divide="ignore"):
        r_floor = np.where(d[..., 1] > 1e-6, h_floor / d[..., 1], np.inf)
        r_ceil = np.where(d[..., 1] < -1e-6, h_ceil / -d[..., 1], np.inf)
        r_wall = radius / np.maximum(np.hypot(d[..., 0], d[..., 2]), 1e-9)
    return np.minimum(np.minimum(r_floor, r_ceil), r_wall)


def test_planar_prior_recovers_floor_and_ceiling_from_the_ring():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "1_gradient_polar_fusion"))
    from planar_prior import fit_polar_planes
    from polar_views import fuse_polar
    H, W = 64, 128
    r = _room_range(H, W)
    lat = latitude_map(H, W)
    disp_true = 2.0 / r + 0.3
    rng = np.random.default_rng(0)
    noisy = disp_true * np.where(np.abs(lat) > 62, np.exp(0.3 * rng.normal(size=(H, W))), 1.0)
    plane, infos = fit_polar_planes(noisy, "disparity", agree_tol=1.0)
    assert all(i["accepted"] for i in infos), infos
    m = np.isfinite(plane) & (np.abs(lat) > 62)
    assert np.median(np.abs(plane[m] - disp_true[m]) / disp_true[m]) < 1e-6
    fused = fuse_polar(noisy, plane, "disparity", np.abs(lat), mode="gradient_poisson", phi_threshold=60, blend_margin=10)
    cap = np.abs(lat) > 62
    # noise starts at 62 deg, inside the 50-70 deg blend ramp, so some noisy gradient remains: expect >= 60% less
    assert np.mean(np.abs(fused[cap] - disp_true[cap])) < 0.4 * np.mean(np.abs(noisy[cap] - disp_true[cap]))
    # metric depth variant (DAP): range in, range out
    plane_d, infos_d = fit_polar_planes(r * np.where(np.abs(lat) > 62, 1.3, 1.0), "depth")
    md = np.isfinite(plane_d) & cap
    assert all(i["accepted"] for i in infos_d) and np.median(np.abs(plane_d[md] - r[md]) / r[md]) < 1e-6


def test_planar_prior_rejects_non_planar_rings_and_tilted_planes():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "1_gradient_polar_fusion"))
    from planar_prior import fit_polar_planes
    rng = np.random.default_rng(1)
    clutter = rng.uniform(0.2, 2.0, (64, 128))
    plane, infos = fit_polar_planes(clutter, "disparity")
    assert not any(i["accepted"] for i in infos) and not np.isfinite(plane).any()
    from geometry.spherical import erp_to_sphere
    d = erp_to_sphere(64, 128).numpy()
    n = np.array([0.7, 0.7, 0.0]) / np.hypot(0.7, 0.7)       # 45 deg tilted "floor"
    inv = np.clip(d @ n, 1e-3, None) / 1.5
    _, infos_t = fit_polar_planes(inv, "disparity")
    assert not infos_t[0]["accepted"] and "tilt" in infos_t[0].get("reason", "")


def test_joint_reanchor_recovers_known_affine_maps_and_consensus_downweights_outliers():
    from tta_ensemble import consensus_weights, joint_reanchor
    H, W = 32, 64
    lat = np.abs(latitude_map(H, W))
    truth = 1.0 + np.random.default_rng(2).uniform(0, 1, (H, W))
    seen = [lat, 90 - lat, 90 - lat]                        # two "rotated" passes see the poles at the equator
    raw = [truth, (truth - 0.2) / 2.0, (truth + 0.1) / 0.5]  # P_i such that a_i P_i + b_i = truth
    fits = joint_reanchor(raw, seen, "affine", max_lat=60)
    assert np.allclose(fits[1], (2.0, 0.2), atol=1e-6) and np.allclose(fits[2], (0.5, -0.1), atol=1e-6)
    fl = joint_reanchor([truth, truth / 3.0, truth * 2.0], seen, "logscale", max_lat=60)
    assert abs(fl[1][0] - 3.0) < 1e-6 and abs(fl[2][0] - 0.5) < 1e-6
    preds = [truth, truth.copy(), truth + 5.0]
    w = consensus_weights(preds, [np.ones((H, W))] * 3)
    assert w[2].max() < 1e-3 and w[0].min() > 0.9


def test_joint_scope_runs_end_to_end_and_identity_scope_is_unchanged():
    from tta_ensemble import MobiusTTAEnsemble
    rgb = _content_rgb()
    a, _ = MobiusTTAEnsemble(_ContentModel(), preset="rotation_only").predict(rgb)
    b, _ = MobiusTTAEnsemble(_ContentModel(), preset="rotation_only", reanchor_scope="identity").predict(rgb)
    assert np.array_equal(a, b)
    j, dj = MobiusTTAEnsemble(_ContentModel(), preset="rotation_only", reanchor_scope="joint", consensus=True).predict(rgb)
    assert np.isfinite(j).all() and len(dj) == 3
    with pytest.raises(ValueError):
        MobiusTTAEnsemble(_ContentModel(), reanchor_scope="nope")


def test_panoramic_model_builder_dispatch_and_missing_repo_errors(tmp_path):
    from models.depth_model import build_panoramic_model
    assert build_panoramic_model({"name": "dpt_hybrid_384"}, str(tmp_path)) is None
    with pytest.raises(FileNotFoundError):
        build_panoramic_model({"name": "da360"}, str(tmp_path))
    with pytest.raises(FileNotFoundError):
        build_panoramic_model({"name": "da2"}, str(tmp_path))
