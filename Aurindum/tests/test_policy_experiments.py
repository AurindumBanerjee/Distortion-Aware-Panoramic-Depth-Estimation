"""Same-domain split, policy sets of run_correction and the end-to-end comparison."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from policy_e2e_compare import compare  # noqa: E402
from same_domain_analysis import evaluate, fold_of  # noqa: E402


def _rows(rel, groups):
    return [{"group": g, "seam|none": {"all": 1.0}, "seam|clean": {"all": 0.5}, "seam|gain_match": {"all": 1.0 + rel}} for g in groups]


def test_folds_are_balanced_and_keep_a_cluster_together():
    groups = [f"room_{i}" for i in range(10) for _ in range(3)]
    fo = fold_of(groups)
    assert sorted(set(fo.values())) == [0, 1] and sum(v == 0 for v in fo.values()) == 5
    assert fo == fold_of(list(reversed(groups)))          # deterministic, independent of order


def test_in_domain_policy_never_sees_the_scored_fold():
    groups = [f"room_{i}" for i in range(6) for _ in range(5)]
    fo = fold_of(groups)
    # the fix helps in fold 0's clusters and hurts in fold 1's: a policy learned on the other fold is wrong for each fold
    rows = []
    for g in groups:
        rows += _rows(-0.5 if fo[g] == 0 else 0.3, [g])
    core = {"s3": _rows(-0.5, ["a"] * 10)}
    cells = {(c["fault"], c["fold"]): c for c in evaluate(core, rows)}
    c0, c1 = cells[("seam", 0)], cells[("seam", 1)]
    assert c0["core"]["fix"] == "gain_match" and abs(c0["core"]["change"] + 50.0) < 1e-6      # core policy: always on
    assert c0["in_domain"]["fix"] == "none"        # learned on fold 1 where it hurts -> off, although it would help fold 0
    assert c1["in_domain"]["fix"] == "gain_match" and abs(c1["in_domain"]["change"] - 30.0) < 1e-6   # learned on fold 0 -> on, hurts fold 1


def test_heldout_policy_uses_only_the_sets_it_is_given(tmp_path):
    from run_correction import heldout_policy
    for ds in ("s3", "panox", "stanford", "nyc"):
        (tmp_path / f"study_dap_{ds}.json").write_text(json.dumps({"rows": _rows(-0.5, ["g"] * 10)}))
    _, trained = heldout_policy("dap", "s3", tmp_path)
    assert trained == ["panox"]
    _, trained = heldout_policy("dap", "s3", tmp_path, sets=("s3", "panox", "holo_in", "holo_out", "stanford", "nyc"))
    assert trained == ["nyc", "panox", "stanford"]


def _corr(ids, pol, change):
    return {"policy": pol, "rows": [{"id": i, "tilt": {"raw": {"all": 1.0}, "fixed": {"all": 1.0 + change}, "detected": None}} for i in ids]}


def test_end_to_end_comparison_matches_frames_by_id():
    from final_summary import SCEN
    SCEN_ = SCEN  # noqa: F841
    head = _corr(["a", "b", "c"], {"tilt": "relevel_known"}, -0.4)
    alt = _corr(["b", "c", "d"], {}, 0.0)
    for c in (head, alt):                          # the other scenarios are not under test
        for r in c["rows"]:
            for s in ("nadir", "vfov", "yawblur", "jpeg", "nadir+jpeg"):
                r[s] = {"raw": {"all": 1.0, "region": 1.0}, "fixed": {"all": 1.0, "region": 1.0}, "detected": None}
    res, ph, pa, n = compare(head, alt)
    assert n == 2 and abs(res["tilt"][0]["chg"] + 40.0) < 1e-9 and abs(res["tilt"][1]["chg"]) < 1e-9
