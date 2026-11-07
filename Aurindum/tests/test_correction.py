"""Capture-aware correction front end (distortions/correction.py) and its policy selection."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "1_gradient_polar_fusion", ROOT / "2_mobius_tta_ensembling", ROOT / "scripts"):
    sys.path.insert(0, str(p))

from distortions.catalogue import CATALOGUE, MITIGATIONS, occlusion_mask  # noqa: E402
from distortions.correction import (JPEG_EDGE_MARGIN_DEG, CaptureMeta, _image_after, cap_fault, correct, detect_caps,  # noqa: E402
                                    grow_caps,
                                    load_policy)
from models.depth_model import EncodedDepthOracle, encode_depth_as_image  # noqa: E402
from tests.test_distortions import GT, RGB, _rel  # noqa: E402

D = {d.key: d for d in CATALOGUE}
PERFECT = EncodedDepthOracle(strength=0.0)
H, W = GT.shape


def _tex(h=128, w=256, seed=0):
    return np.random.default_rng(seed).integers(0, 256, (h, w, 3)).astype(np.uint8)


class Recorder:
    """Fake model: returns the mean intensity per pixel and remembers every image it saw."""
    name = "rec"

    def __init__(self):
        self.seen = []

    def predict(self, rgb, kind="erp"):
        self.seen.append(rgb.copy())
        return 1.0 + rgb.astype(np.float32).mean(-1) / 255.0


def test_detect_caps_reproduces_the_simulated_masks_and_ignores_clean_texture():
    img = _tex()
    assert cap_fault(detect_caps(img)) is None
    for key, fault in (("nadir", "nadir"), ("vfov", "vfov")):
        x, ctx = D[key].apply(img, {})
        caps = detect_caps(x)
        assert cap_fault(caps) == fault
        assert (occlusion_mask(128, 256, caps) == occlusion_mask(128, 256, ctx)).all()


def test_detect_caps_ignores_flat_pole_rows_of_rendered_panoramas():
    img = _tex()
    img[:2] = 200          # one 3D point stretched over the first rows (rendered ERP), < 10 deg
    img[-3:] = 30
    assert detect_caps(img) == {"zenith_from": None, "nadir_from": None}


def test_known_tilt_is_relevelled_on_a_perfect_model():
    x, ctx = D["tilt"].apply(RGB, {})
    pred, log = correct(PERFECT, x, CaptureMeta(R=ctx["R"]), {"tilt": "relevel_known"})
    assert log == ["tilt: relevel_known"]
    assert _rel(D["tilt"].to_original(pred, ctx)) < 0.01


def test_policy_none_means_plain_inference_even_when_a_fault_is_detected():
    x, _ = D["nadir"].apply(_tex(), {})
    m = Recorder()
    pred, log = correct(m, x, CaptureMeta(), {})
    assert len(m.seen) == 1 and (m.seen[0] == x).all()
    assert np.allclose(pred, 1.0 + x.astype(np.float32).mean(-1) / 255.0)
    assert log and log[0].startswith("nadir") and log[0].endswith("none")


def test_clean_image_passes_through_untouched():
    img = _tex()
    m = Recorder()
    pred, log = correct(m, img, CaptureMeta(), {"nadir": "plane_fill", "vfov": "inpaint_erp", "tilt": "relevel_known"})
    assert len(m.seen) == 1 and (m.seen[0] == img).all() and log == ["no fault detected"]


def test_detected_cap_runs_the_same_fix_as_with_the_true_mask():
    x, ctx = D["vfov"].apply(_tex(), {})
    a, _ = correct(Recorder(), x, CaptureMeta(), {"vfov": "inpaint_erp"})
    b = MITIGATIONS["inpaint_erp"][1](Recorder(), x, ctx)
    assert np.allclose(a, b)


def test_photometric_fix_feeds_its_cleaned_image_into_the_cap_fix():
    x, ctx = D["yawblur"].apply(_tex(), {})
    x[occlusion_mask(128, 256, {"nadir_from": 62.0})] = 48      # logo patch added after capture
    m = Recorder()
    _, log = correct(m, x, CaptureMeta(kernel=ctx["kernel"]), {"yawblur": "wiener", "nadir": "inpaint_erp"})
    assert log[0] == "yawblur: wiener" and log[1].startswith("nadir")
    deblurred = _image_after("wiener", x, {"kernel": ctx["kernel"]})
    expect = MITIGATIONS["inpaint_erp"][1](Recorder(), deblurred, {"nadir_from": detect_caps(x)["nadir_from"]})
    assert len(m.seen) == 1 and np.allclose(1.0 + m.seen[0].astype(np.float32).mean(-1) / 255.0, expect)


def test_image_after_matches_what_the_fix_feeds_the_model():
    x, ctx = D["yawblur"].apply(_tex(), {})
    m = Recorder()
    MITIGATIONS["wiener"][1](m, x, {"kernel": ctx["kernel"]})
    assert (m.seen[0] == _image_after("wiener", x, {"kernel": ctx["kernel"]})).all()


def test_load_policy_falls_back_to_the_default(tmp_path):
    p = tmp_path / "pol.json"
    p.write_text(json.dumps({"dap": {"nadir": "plane_fill"}}))
    assert load_policy(str(p), "dap") == {"nadir": "plane_fill"}
    assert load_policy(str(p), "midas") == {"tilt": "relevel_known", "yawblur": "wiener"}


def test_policy_selection_keeps_none_unless_a_fix_wins():
    from calibrate_correction import choose

    def rows(fix_vals, none_vals):
        return [{"seam|none": {"all": n}, "seam|clean": {"all": 0.5}, "seam|gain_match": {"all": f}}
                for f, n in zip(fix_vals, none_vals)]
    good = {"a": rows([0.5] * 10, [1.0] * 10), "b": rows([0.6] * 10, [1.0] * 10)}
    bad = {"a": rows([1.2] * 10, [1.0] * 10), "b": rows([0.9] * 3 + [1.1] * 7, [1.0] * 10)}
    assert choose(good, "seam", 0.02, 0.6)[0] == "gain_match"
    assert choose(bad, "seam", 0.02, 0.6)[0] == "none"


def test_detect_caps_survives_heavy_jpeg_with_an_edge_inside_a_block():
    from distortions.catalogue import jpeg_apply
    img = np.clip(_tex(256, 512).astype(np.int16) // 2 + 100, 0, 255).astype(np.uint8)  # scene unlike the patch colour
    for key, kw in (("nadir", {"nadir_from": 75.0}), ("vfov", {"half_vfov": 35.0})):
        x, ctx = D[key].apply(img, dict(kw))
        x, _ = jpeg_apply(x, {})
        caps = detect_caps(x)
        assert cap_fault(caps) == key
        for k in ("nadir_from", "zenith_from"):
            if ctx.get(k) is not None:
                assert abs(caps[k] - ctx[k]) < 3.0  # within half a JPEG block (8 rows = 5.6 deg at H = 256)
    assert cap_fault(detect_caps(jpeg_apply(img, {})[0])) is None


def _study_rows():
    return [{"seam|none": {"all": 1.0}, "seam|clean": {"all": 0.5}, "seam|gain_match": {"all": 0.6}} for _ in range(10)]


def test_calibration_never_reads_external_datasets(tmp_path):
    import subprocess
    for tag in ("dap_s3", "dap_panox", "dap_stanford", "dap_nyc", "dap_s3mini"):
        (tmp_path / f"study_{tag}.json").write_text(json.dumps({"rows": _study_rows()}))
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "calibrate_correction.py"), "--results", str(tmp_path)],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    text = (tmp_path / "CORRECTION_POLICY.md").read_text()
    assert "| s3 |" in text and "| panox |" in text and "stanford" not in text.split("\n## ")[1] and "nyc" not in text.split("\n## ")[1]


def test_external_runs_are_tested_with_a_policy_from_core_sets_only(tmp_path):
    from run_correction import heldout_policy
    for tag in ("dap_s3", "dap_panox", "dap_stanford", "dap_nyc"):
        (tmp_path / f"study_{tag}.json").write_text(json.dumps({"rows": _study_rows()}))
    _, trained = heldout_policy("dap", "stanford", tmp_path)
    assert trained == ["panox", "s3"]
    _, trained = heldout_policy("dap", "s3", tmp_path)
    assert trained == ["panox"]          # a core run still leaves its own dataset out, and never sees the external ones


def _wobbly_caps(h, w, cap_deg=24.6, wobble_deg=1.4, seed=0):
    """Scene with black polar caps whose edge wobbles from column to column by +-wobble_deg (real Stanford2D3D: 2.8 deg p5-p95)."""
    img = _tex(h, w, seed)
    rng = np.random.default_rng(seed)
    wob = np.round(rng.uniform(-wobble_deg, wobble_deg, w) * h / 180.0).astype(int)
    k = int(round(cap_deg * h / 180.0))
    for j in range(w):
        img[: k + wob[j], j] = 0
        img[h - k - wob[j]:, j] = 0
    return img


def test_wobbly_real_caps_are_found_at_any_resolution():
    for h, w in ((128, 256), (256, 512), (512, 1024), (1024, 2048)):
        caps = detect_caps(_wobbly_caps(h, w))
        assert cap_fault(caps) == "vfov", (h, caps)
        # the mask must cover the black pixels of (almost) every column: edge at or beyond the widest black column - 1 row
        assert caps["nadir_from"] <= 90.0 - (24.6 + 1.4) + 0.8 + 180.0 / h, (h, caps)


def test_jpeg_flag_grows_the_detected_caps():
    from distortions.correction import JPEG_EDGE_MARGIN_DEG, grow_caps
    assert grow_caps({"nadir_from": 62.0, "zenith_from": None}, JPEG_EDGE_MARGIN_DEG) == {"nadir_from": 62.0 - JPEG_EDGE_MARGIN_DEG, "zenith_from": None}
    x, _ = D["nadir"].apply(_tex(), {})
    rec = Recorder()
    caps = detect_caps(x)
    calls = []
    import distortions.correction as dc
    orig = dc.MITIGATIONS["inpaint_erp"]
    try:
        dc.MITIGATIONS["inpaint_erp"] = (orig[0], lambda m, img, ctx: calls.append(dict(ctx)) or np.zeros(img.shape[:2]))
        dc.correct(rec, x, CaptureMeta(flags={"jpeg"}), {"nadir": "inpaint_erp"})
    finally:
        dc.MITIGATIONS["inpaint_erp"] = orig
    assert calls and abs(calls[0]["nadir_from"] - (caps["nadir_from"] - JPEG_EDGE_MARGIN_DEG)) < 1e-6


def test_two_photometric_flags_both_run_in_order():
    x, ctx = D["yawblur"].apply(_tex(), {})
    m = Recorder()
    _, log = correct(m, x, CaptureMeta(kernel=ctx["kernel"], flags={"jpeg"}), {"yawblur": "wiener", "jpeg": "bilateral"})
    assert log == ["yawblur: wiener", "jpeg: bilateral"]
    expect = _image_after("bilateral", _image_after("wiener", x, {"kernel": ctx["kernel"]}), {"kernel": ctx["kernel"]})
    assert len(m.seen) == 1 and (m.seen[0] == expect).all()


def test_cap_first_fills_before_smoothing_and_the_cap_fix_runs_once_on_the_result():
    from distortions.catalogue import _inpaint_tangent
    x, _ = D["nadir"].apply(_tex(), {})
    import distortions.correction as dc
    seen, orig = [], dc.MITIGATIONS["inpaint_erp"]
    try:
        dc.MITIGATIONS["inpaint_erp"] = (orig[0], lambda m, img, c: seen.append(img.copy()) or np.zeros(img.shape[:2]))
        _, log = dc.correct(Recorder(), x, CaptureMeta(flags={"jpeg"}), {"nadir": "inpaint_erp", "jpeg": "bilateral"}, order="cap_first")
    finally:
        dc.MITIGATIONS["inpaint_erp"] = orig
    caps = grow_caps(detect_caps(x), JPEG_EDGE_MARGIN_DEG)
    pre = _inpaint_tangent(x, occlusion_mask(128, 256, caps))
    assert len(seen) == 1 and (seen[0] == _image_after("bilateral", pre, {})).all()
    assert log[0] == "jpeg: bilateral" and log[1].startswith("nadir")
