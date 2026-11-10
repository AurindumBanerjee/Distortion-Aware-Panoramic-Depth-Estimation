"""scripts/policy_comparison.py: which sets train each policy, and the evaluation of the chosen fix."""

from scripts.analysis.policy_comparison import ALL_SETS, evaluate, train_sets


def test_training_sets_of_each_policy():
    assert train_sets("core_loo", "nyc") == ["s3", "panox", "holo_in", "holo_out"]       # external sets never train
    assert train_sets("core_loo", "s3") == ["panox", "holo_in", "holo_out"]
    assert "stanford" in train_sets("all_loo", "s3") and "s3" not in train_sets("all_loo", "s3")
    assert set(train_sets("all_loo", "nyc")) == set(ALL_SETS) - {"nyc"}
    assert set(train_sets("all_in", "nyc")) == set(ALL_SETS)


def _rows(rel, n=10):   # fix changes the 'seam' metric by `rel` relative to no fix
    return [{"seam|none": {"all": 1.0}, "seam|clean": {"all": 0.5}, "seam|gain_match": {"all": 1.0 + rel}} for _ in range(n)]


def test_policies_differ_only_through_their_training_sets():
    good, bad = _rows(-0.5), _rows(0.2)
    per = {"s3": good, "panox": good, "holo_in": bad, "holo_out": bad, "stanford": bad, "nyc": bad}
    cells = {(c["fault"], c["test"]): c for c in evaluate({"m": per})}
    c = cells[("seam", "holo_out")]
    assert c["core_loo"]["fix"] == "gain_match" and abs(c["core_loo"]["change"] - 20.0) < 1e-6   # trained on s3, panox, holo_in: median -0.5
    assert c["all_loo"]["fix"] == "none" and c["all_loo"]["change"] == 0.0                       # median of the five others is +0.2
    assert c["all_in"]["fix"] == "none"
    assert cells[("seam", "s3")]["core_loo"]["fix"] == "none"                                    # panox good, holo_in / holo_out bad
