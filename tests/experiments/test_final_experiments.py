"""Threshold sweep (stricter do-no-harm rules) and the nadir + JPEG diagnosis ladder."""

import numpy as np

from scripts.run import nadir_jpeg_diagnosis as nd
from scripts.analysis import threshold_sweep as ts
from methods.capture_faults.catalogue import nadir_apply


def _rows(rel, n=10):
    return [{"seam|none": {"all": 1.0}, "seam|clean": {"all": 0.5}, "seam|gain_match": {"all": 1.0 + rel}} for _ in range(n)]


def test_headline_rule_matches_calibrate_choose():
    from scripts.analysis.calibrate_correction import choose
    train = {"a": _rows(-0.1), "b": _rows(-0.1), "c": _rows(-0.1)}
    assert ts.choose_rule(train, "seam", 0.02, 0.6)[0] == choose(train, "seam", 0.02, 0.6)[0] == "gain_match"
    train = {"a": _rows(+0.1), "b": _rows(+0.1)}
    assert ts.choose_rule(train, "seam", 0.02, 0.6)[0] == choose(train, "seam", 0.02, 0.6)[0] == "none"


def test_consistency_rule_rejects_a_fix_that_hurts_one_training_set():
    train = {"a": _rows(-0.2), "b": _rows(-0.2), "c": _rows(+0.05)}   # median of medians is -0.2, one set is worse
    assert ts.choose_rule(train, "seam", 0.02, 0.6, all_sets=False)[0] == "gain_match"
    assert ts.choose_rule(train, "seam", 0.02, 0.6, all_sets=True)[0] == "none"


def test_stricter_thresholds_only_remove_fixes():
    train = {"a": _rows(-0.04), "b": _rows(-0.04)}
    assert ts.choose_rule(train, "seam", 0.02, 0.6)[0] == "gain_match"
    assert ts.choose_rule(train, "seam", 0.05, 0.6)[0] == "none"           # gain below 5%
    mixed = [dict(r) for r in _rows(-0.1, 7)] + _rows(+0.1, 3)             # 70% of frames improve
    train = {"a": mixed, "b": mixed}
    assert ts.choose_rule(train, "seam", 0.02, 0.6)[0] == "gain_match"
    assert ts.choose_rule(train, "seam", 0.02, 0.8)[0] == "none"           # win share below 80%


def test_evaluate_counts_harm_and_never_trains_on_the_scored_set():
    data = {"m": {"s3": _rows(-0.2), "panox": _rows(-0.2), "holo_in": _rows(-0.2), "holo_out": _rows(-0.2), "nyc": _rows(+0.1)}}
    r = ts.evaluate(data, (0.02, 0.6, False), ["seam"])
    assert r["core"]["applied"] == 4 and r["core"]["harmful"] == 0
    assert r["external"]["applied"] == 1 and r["external"]["harmful"] == 1       # chosen on core, harmful on NYC
    assert abs(r["external"]["mean_change"] - 0.1) < 1e-9
    r2 = ts.evaluate({**data, "da2m": data["m"]}, (0.02, 0.6, False), ["seam"])
    assert r2["core"]["cells"] == r["core"]["cells"]                             # da2m is not pooled twice


class _Flat:
    name = "flat"

    def predict(self, rgb, kind="erp"):
        return np.full(rgb.shape[:2], 3.0)


def _scene(h=128, w=256):
    rng = np.random.default_rng(0)
    return rng.integers(0, 256, (h, w, 3)).astype(np.uint8)


def test_region_masks_partition_the_panorama():
    m = nd.region_masks(128, 256)
    assert not (m["region"] & m["outside"]).any() and (m["region"] | m["outside"]).all()
    assert m["ring"].any() and not (m["ring"] & m["region"]).any()


def test_score_variant_is_zero_for_the_truth_and_measures_the_region():
    gt = np.full((128, 256), 3.0)
    valid = np.ones_like(gt, bool)
    m = nd.region_masks(128, 256)
    s = nd.score_variant(gt.copy(), gt, valid, _Flat(), m, "none", 0.1, 10.0)
    assert s["region"] == 0 and s["outside"] == 0 and abs(s["bias"] - 1.0) < 1e-9
    pred = gt.copy()
    pred[m["region"]] = 6.0
    s = nd.score_variant(pred, gt, valid, _Flat(), m, "none", 0.1, 10.0)
    assert abs(s["region"] - 1.0) < 1e-9 and s["outside"] == 0


def test_variant_ladder_has_every_rung_and_the_pipeline_paths_agree_with_correct():
    x, ctx = nadir_apply(_scene(), {})
    caps = {"nadir_from": ctx["nadir_from"], "zenith_from": None}
    out, info = nd.build_variants(_Flat(), x, "nadir", caps)
    assert info["detected"] == "nadir" and abs(info["nadir_from_detected"] - 62.0) < 2.5
    for f in nd.CAP_FIXES:
        for k in ("oracle", "oracle+1.5", "detected", "detected+1.5", "pipe"):
            assert f"{k}:{f}" in out and out[f"{k}:{f}"].shape == (128, 256)


def test_jpeg_ladder_adds_deblocking_and_both_orders():
    import cv2
    x, ctx = nadir_apply(_scene(), {})
    ok, buf = cv2.imencode(".jpg", cv2.cvtColor(x, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 8])
    xj = cv2.cvtColor(cv2.imdecode(buf, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    caps = {"nadir_from": ctx["nadir_from"], "zenith_from": None}
    out, _ = nd.build_variants(_Flat(), xj, "nadir+jpeg", caps)
    assert "bilateral_only" in out
    for f in nd.CAP_FIXES:
        for k in ("deblock_oracle", "pipe_photometric", "pipe_cap_first"):
            assert f"{k}:{f}" in out


def test_summarize_reports_change_against_raw():
    rows = []
    for i in range(8):
        e = {"region": 0.2, "outside": 0.1, "ring": 0.1, "all": 0.1, "bias": 1.0}
        better = {**e, "region": 0.1}
        rows.append({"nadir": {"none": {"raw": e, "fix": better}}})
    raw, tab = nd.summarize(rows, "nadir", "none", "region")
    assert abs(raw - 0.2) < 1e-9 and tab[0][0] == "fix"
    assert abs(tab[0][2] + 0.5) < 1e-9 and tab[0][3] == 1.0 and tab[0][4] <= tab[0][2] <= tab[0][5]


def test_run_correction_policy_rule_options(tmp_path):
    import json
    from scripts.run.run_correction import heldout_policy
    for ds, rel in (("s3", -0.2), ("panox", -0.2), ("holo_in", +0.05), ("holo_out", -0.2)):
        (tmp_path / f"study_dap_{ds}.json").write_text(json.dumps({"rows": _rows(rel)}))
    pol, _ = heldout_policy("dap", "stanford", tmp_path)
    assert pol.get("seam") == "gain_match"                                   # headline rule: median of medians is negative
    pol, _ = heldout_policy("dap", "stanford", tmp_path, all_sets=True)
    assert "seam" not in pol                                                 # one training set is worse: stricter rule says no
    pol, _ = heldout_policy("dap", "stanford", tmp_path, min_gain=0.25)
    assert "seam" not in pol


def test_da2_protocol_report_helpers():
    from scripts.analysis import da2_protocol_report as dr
    a = {"rows": [{"id": str(i), "clean": {"raw": {"all": 0.5}}} for i in range(5)]}
    b = {"rows": [{"id": str(i), "clean": {"raw": {"all": 0.2}}} for i in (3, 1, 9)]}
    ra, rb = dr.matched(a, b)
    assert [r["id"] for r in ra] == [r["id"] for r in rb] == ["1", "3"]
    assert abs(dr.clean_median(ra) - 0.5) < 1e-9 and abs(dr.clean_median(rb) - 0.2) < 1e-9
    rows = [{"tilt": {"raw": {"all": 1.0}, "fixed": {"all": 1.2}, "detected": None}} for _ in range(6)]
    h = dr.harmful_cells(rows)
    assert len(h) == 1 and h[0][0] == "tilt" and abs(h[0][1] - 20.0) < 1e-6
    rows = [{"tilt": {"raw": {"all": 1.0}, "fixed": {"all": 0.8}, "detected": None}} for _ in range(6)]
    assert dr.harmful_cells(rows) == []


def test_strict_summary_and_policy_stability(tmp_path):
    from scripts.analysis import strict_compare as sc
    ok = {"chg": -10.0}
    bad = {"chg": 5.0}
    s = sc.summarize([(bad, ok), (ok, ok), (None, ok)])
    assert s["headline"]["harmful"] == 1 and s["strict"]["harmful"] == 0 and s["headline"]["n"] == 2
    from scripts.analysis import policy_stability as ps
    studies = {d: _rows(-0.2) for d in ("s3", "panox", "holo_in")}
    p = ps.policy_for(studies, "s3")
    assert p["seam"] == "gain_match" and ps.policy_for({}, "s3") == {}
