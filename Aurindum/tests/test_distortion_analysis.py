"""Round-3 Part A / B: distortion sweep, latitude profile, calibration split, curve-driven correction (do no harm)."""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "1_gradient_polar_fusion", ROOT / "2_mobius_tta_ensembling", ROOT / "3_structured3d_benchmark"):
    sys.path.insert(0, str(p))

from evaluation.distortion_analysis import (curve_gate_range, curve_ratio, frame_profile, in_split, load_curve,  # noqa: E402
                                            onset_from_curve, split_of, summarize_sweep, sweep_frame)
from geometry.spherical import erp_to_sphere  # noqa: E402
from models.depth_model import EncodedDepthOracle, encode_depth_as_image  # noqa: E402

H, W = 64, 128


def _room(seed=0):
    rng = np.random.default_rng(seed)
    d = erp_to_sphere(H, W).numpy()
    with np.errstate(divide="ignore"):
        rf = np.where(d[..., 1] > 1e-6, 1.4 / d[..., 1], np.inf)
        rc = np.where(d[..., 1] < -1e-6, 1.3 / -d[..., 1], np.inf)
        rw = 2.5 * (1 + 0.2 * rng.uniform()) / np.maximum(np.hypot(d[..., 0], d[..., 2]), 1e-9)
    return np.minimum(np.minimum(rf, rc), rw)


class _ContentErrorModel(EncodedDepthOracle):
    """Error tied to CONTENT (near surfaces, i.e. floor / ceiling below / above the camera), wherever it is seen."""

    def _forward(self, images, kind):
        out = []
        for im in images:
            x = im[..., 0].astype(float) / 255.0
            d = np.exp(np.log(self.dmin) + x * (np.log(self.dmax) - np.log(self.dmin)))
            out.append((d * np.where(d < 1.6, 1.3, 1.0)).astype(np.float32))
        return out


def _sweep(model, n=5, bin_deg=10.0):
    frames, ids = [], []
    for s in range(n):
        gt = _room(s)
        valid = np.isfinite(gt) & (gt < 30)
        rgb = encode_depth_as_image(np.where(valid, gt, 30.0))
        fr = sweep_frame(model, rgb, gt, valid, bin_deg=bin_deg, min_depth=0.1, max_depth=30.0)
        assert fr is not None
        frames.append(fr)
        ids.append(f"scene_{s:05d}_0")
    return summarize_sweep(frames, ids, bin_deg, n_boot=300), frames, ids


def test_sweep_finds_a_pure_distortion_effect():
    S, _, _ = _sweep(EncodedDepthOracle(strength=0.6, power=3.0))
    de = np.array(S["de_global"]["mean"])
    assert S["onset_global"] is not None and 15 <= S["onset_global"] <= 40
    assert de[-1] > 10 * max(abs(de[0]), 1e-4) and np.all(np.diff(de[2:]) > 0)  # grows with latitude
    assert S["ratio_global"][-1] > 5 and abs(S["ratio_global"][0] - 1) < 0.05


def test_sweep_attributes_a_content_effect_to_content_not_distortion():
    model = _ContentErrorModel(strength=0.0)
    S, _, _ = _sweep(model)
    # the plain profile shows a big polar deficit ...
    prof = []
    for s in range(5):
        gt = _room(s)
        valid = np.isfinite(gt) & (gt < 30)
        rgb = encode_depth_as_image(np.where(valid, gt, 30.0))
        prof.append(frame_profile(model.predict(rgb), gt, valid, model, ["none"], bin_deg=10, max_depth=30.0)["none"]["mean"])
    prof = np.nanmean(np.array(prof), 0)
    assert prof[-1] > 20 * prof[0]
    # ... but the content-paired sweep finds no distortion effect (global estimator, which drives Part B)
    assert S["onset_global"] is None
    assert np.nanmax(np.abs(S["de_global"]["mean"])) < 0.01


def test_perfect_model_has_no_onset_and_only_resampling_floor():
    S, _, _ = _sweep(EncodedDepthOracle(strength=0.0))
    assert S["onset_global"] is None and S["onset_local"] is None
    assert np.nanmax(np.abs(S["de_global"]["mean"])) < 0.005
    assert np.nanmax(S["floor"]["mean"]) < 0.01


def test_every_pixel_has_a_low_latitude_pass_with_default_pitches():
    from evaluation.distortion_analysis import DEFAULT_PITCHES
    from geometry.erp_projection import rotated_latitude
    from geometry.spherical import latitude_map, rotation_from_ypr
    seen = [np.abs(latitude_map(H, W)) if p == 0 else np.abs(rotated_latitude(H, W, rotation_from_ypr(pitch_deg=p)))
            for p in DEFAULT_PITCHES]
    assert np.min(np.stack(seen), axis=0).max() <= 15.0 + 1.5  # within one pixel row of 15 deg


def test_onset_rule_needs_practical_and_significant_excess():
    c = [5, 15, 25, 35, 45]
    ref = [0.1] * 5
    assert onset_from_curve(c, [0, 0.001, 0.001, 0.001, 0.001], ref=ref, rel_min=0.1) is None   # tiny but "significant"
    assert onset_from_curve(c, [0, 0, 0.02, 0.03, 0.05], ref=ref, rel_min=0.1) == 20.0
    assert onset_from_curve(c, [0, 0, 0.02, 0.0, 0.05], ref=ref, rel_min=0.1) is None           # needs 2 consecutive bins


def test_split_is_by_cluster_deterministic_and_roughly_balanced():
    ids = [f"scene_{h:05d}_{r}" for h in range(400) for r in range(3)]
    parts = {split_of(i) for i in ids if i.startswith("scene_00007_")}
    assert len(parts) == 1                                                   # one house, one side
    calib = sum(split_of(f"scene_{h:05d}_0") == "calib" for h in range(400))
    assert 150 < calib < 250
    assert in_split("x", None) and in_split("x", "all")
    assert split_of("Diner50_0002") == split_of("Diner50_0100")              # PanoX environment stays together


def test_dataset_split_is_applied_before_the_spread_subset(tmp_path):
    from datasets.panorama import PanoramaDataset
    lines = [f"{e}/{e}/rgb/{i:04d}.png {e}/{e}/depth/{i:04d}.exr\n" for e in ("Env", "Diner50", "Big_Room", "Yard")
             for i in range(10)]
    (tmp_path / "test.txt").write_text("".join(lines))
    ds = PanoramaDataset(str(tmp_path), "test.txt", name="panox", limit=6, subset="spread",
                         id_filter=lambda s: split_of(s) == "calib")
    envs = {it[0].split("/")[0] for it in ds.items}
    expect = {e for e in ("Env", "Diner50", "Big_Room", "Yard") if split_of(f"{e}_0000") == "calib"}
    assert envs == expect and len(ds) == min(6, 10 * len(expect))
    assert all(ds.sample_id(i).split("_")[0] in {e.split("_")[0] for e in expect} for i in range(len(ds)))


def _curve(onset, ratio_end=9.0):
    c = list(np.arange(2.5, 90, 5.0))
    r = list(np.interp(c, [0, 30, 90], [1.0, 1.0, ratio_end]))
    return {"centres": c, "ratio": r, "onset": onset}


def test_curve_ratio_gate_and_load(tmp_path):
    cur = _curve(30.0)
    lat = np.array([0.0, 30.0, 60.0, 89.0])
    r = curve_ratio(cur, lat)
    assert r[0] == 1.0 and r[1] == pytest.approx(1.0, abs=0.2) and r[3] > r[2] > 1.5
    assert curve_gate_range(cur) == (30.0, 45.0) and curve_gate_range(_curve(None)) is None
    S, _, _ = _sweep(EncodedDepthOracle(strength=0.6, power=3.0), n=3)
    (tmp_path / "s.json").write_text(json.dumps({"summary": S}))
    lc = load_curve(str(tmp_path / "s.json"))
    assert lc["onset"] == S["onset_global"] and lc["ratio"] == S["ratio_global"]


class _CountingModel(EncodedDepthOracle):
    def _forward(self, images, kind):
        return super()._forward(images, kind)


def test_do_no_harm_mobius_returns_identity_bit_for_bit_without_extra_passes():
    from tta_ensemble import MobiusTTAEnsemble
    gt = _room(1)
    rgb = encode_depth_as_image(gt)
    m = _CountingModel(strength=0.3)
    base = m.predict(rgb)
    calls = m.n_calls
    ens = MobiusTTAEnsemble(m, preset="rotation_only", curve=_curve(None), curve_gate=True, curve_weights=True)
    out, d = ens.predict(rgb, identity_pred=base)
    assert np.array_equal(out, base.astype(np.float64)) and m.n_calls == calls and d[0]["identity_only"]
    ens2 = MobiusTTAEnsemble(m, preset="rotation_only", curve=_curve(30.0), curve_gate=True, curve_weights=True)
    assert ens2.gate_lat == (30.0, 45.0) and not ens2.identity_only
    out2, _ = ens2.predict(rgb, identity_pred=base)
    lat = np.abs(np.degrees(np.arcsin(-erp_to_sphere(H, W).numpy()[..., 1])))
    assert np.array_equal(out2[lat < 30], base.astype(np.float64)[lat < 30])     # below the measured onset: untouched
    with pytest.raises(ValueError):
        MobiusTTAEnsemble(m, curve_gate=True)


def test_do_no_harm_tangent_and_method1_return_the_baseline_when_no_onset():
    from benchmark_evaluator import run_single_benchmark_scene
    from tta_ensemble import MobiusTTAEnsemble
    gt = _room(2)
    valid = np.isfinite(gt) & (gt < 30)
    rgb = encode_depth_as_image(np.where(valid, gt, 30.0))
    m = EncodedDepthOracle(strength=0.3)
    ens = MobiusTTAEnsemble(m, preset="rotation_only", curve=_curve(None), curve_gate=True)
    res = run_single_benchmark_scene({"id": "scene_00001_0"}, rgb, gt, valid, m, None, ens, protocols=("none",),
                                     min_depth=0.1, max_depth=30.0, m1_cfg={"curve_gate": True},
                                     methods=("Tangent_Spatial", "Method1_GradientFusion", "Method2_MobiusTTA"),
                                     curve=_curve(None))
    for name in ("Tangent_Spatial", "Method1_GradientFusion", "Method2_MobiusTTA"):
        assert res[name] == res["Baseline"], name
    with pytest.raises(ValueError):
        run_single_benchmark_scene({"id": "s"}, rgb, gt, valid, m, None, ens, protocols=("none",), min_depth=0.1,
                                   max_depth=30.0, m1_cfg={"curve_gate": True}, methods=("Tangent_Spatial",), curve=None)


# ---------- round 3b: dilation and flip sweeps separate distortion from orientation ----------
def _room_floor_only(seed=0):
    rng = np.random.default_rng(seed)
    d = erp_to_sphere(H, W).numpy()
    with np.errstate(divide="ignore"):
        rf = np.where(d[..., 1] > 1e-6, 1.4 / d[..., 1], np.inf)
        rc = np.where(d[..., 1] < -1e-6, 4.0 / -d[..., 1], np.inf)
        rw = 3.0 * (1 + 0.2 * rng.uniform()) / np.maximum(np.hypot(d[..., 0], d[..., 2]), 1e-9)
    return np.minimum(np.minimum(rf, rc), rw)


class _OrientationModel(EncodedDepthOracle):
    """Near content (the floor, < 2 m) is right in the LOWER half of the input image and 30% wrong in the upper half:
    a model with a 'floor is below' prior and no distortion sensitivity at all."""

    def _forward(self, images, kind):
        out = []
        for im in images:
            x = im[..., 0].astype(float) / 255.0
            d = np.exp(np.log(self.dmin) + x * (np.log(self.dmax) - np.log(self.dmin)))
            top = (np.arange(d.shape[0]) < d.shape[0] // 2)[:, None]
            out.append((d * np.where((d < 2.0) & top, 1.3, 1.0)).astype(np.float32))
        return out


def _sweep_mode(model, mode, n=4):
    frames, ids = [], []
    for s in range(n):
        gt = _room_floor_only(s)
        valid = np.isfinite(gt) & (gt < 30)
        fr = sweep_frame(model, encode_depth_as_image(np.where(valid, gt, 30.0)), gt, valid, bin_deg=10.0,
                         min_depth=0.1, max_depth=30.0, mode=mode)
        frames.append(fr)
        ids.append(f"scene_{s:05d}_0")
    return summarize_sweep(frames, ids, 10.0, n_boot=300)


def test_three_sweep_modes_separate_orientation_from_distortion():
    orient, dist = _OrientationModel(strength=0.0), EncodedDepthOracle(strength=0.6, power=3.0)
    # orientation-only model: rotation sweep goes NEGATIVE at the poles (as on real data), dilation sees nothing,
    # flip sees a large penalty
    r, d, f = (_sweep_mode(orient, m) for m in ("rotation", "dilation", "flip"))
    assert np.nanmean(np.array(r["de_global"]["mean"])[-3:]) < -0.03 and r["onset_global"] is None
    assert np.nanmax(np.abs(d["de_global"]["mean"])) < 0.02 and d["onset_global"] is None
    assert np.nanmean(np.array(f["de_global"]["mean"])[-3:]) > 0.1 and f["onset_global"] is not None
    # distortion-only model: rotation and dilation agree, flip sees nothing
    r2, d2, f2 = (_sweep_mode(dist, m) for m in ("rotation", "dilation", "flip"))
    assert r2["onset_global"] is not None and d2["onset_global"] is not None
    assert abs(r2["de_global"]["mean"][-2] - d2["de_global"]["mean"][-2]) < 0.01
    assert f2["onset_global"] is None and np.nanmax(np.abs(f2["de_global"]["mean"])) < 0.015


def test_dilation_magnification_and_flip_latitude_bookkeeping():
    d = _sweep_mode(EncodedDepthOracle(strength=0.0), "dilation", n=2)
    lm = np.array(d["log_mag"]["mean"])
    assert lm[0] > 0 > lm[-1]          # equator content seen at high latitude was shrunk, polar content seen low magnified
    f = _sweep_mode(EncodedDepthOracle(strength=0.0), "flip", n=2)
    c = np.array(f["centres"])
    assert np.allclose(np.array(f["ref_lat"]["mean"]), c, atol=4.0)  # flip: reference seen at the SAME |latitude|
    assert f["mode"] == "flip" and d["mode"] == "dilation"
    with pytest.raises(ValueError):
        sweep_frame(EncodedDepthOracle(), np.zeros((H, W, 3), np.uint8), np.ones((H, W)), np.ones((H, W), bool),
                    mode="dilation", values=[2.0, 4.0])


def test_nonplanar_onset_and_curve_loading_by_estimator(tmp_path):
    frames, ids = [], []
    model = EncodedDepthOracle(strength=0.6, power=3.0)
    for s in range(4):
        gt = _room(s)
        valid = np.isfinite(gt) & (gt < 30)
        rgb = encode_depth_as_image(np.where(valid, gt, 30.0))
        lat = np.abs(np.degrees(np.arcsin(-erp_to_sphere(H, W).numpy()[..., 1])))
        frames.append(sweep_frame(model, rgb, gt, valid, bin_deg=10.0, min_depth=0.1, max_depth=30.0,
                                  planar_mask=lat > 60))
        ids.append(f"scene_{s:05d}_0")
    S = summarize_sweep(frames, ids, 10.0, n_boot=300)
    assert "onset_nonplanar" in S and S["onset_nonplanar"] is not None and len(S["ratio_nonplanar"]) == 9
    (tmp_path / "s.json").write_text(json.dumps({"summary": S}))
    assert load_curve(str(tmp_path / "s.json"), "nonplanar")["onset"] == S["onset_nonplanar"]
    with pytest.raises(KeyError):
        load_curve(str(tmp_path / "s.json"), "bogus")


def test_uniform_weights_average_all_passes_equally():
    from tta_ensemble import MobiusTTAEnsemble
    m = EncodedDepthOracle(strength=0.0)
    rgb = encode_depth_as_image(_room(3))
    ens = MobiusTTAEnsemble(m, preset="rotation_only", weight_power=0.0, min_weight=1.0, reanchor="none")
    out, d = ens.predict(rgb)
    P = np.stack([x["unwarped_pred"] for x in d])
    assert all(np.all(x["weight"][np.isfinite(x["unwarped_pred"])] == 1.0) for x in d)
    ok = np.all(np.isfinite(P), 0)
    assert np.allclose(out[ok], P.mean(0)[ok])
