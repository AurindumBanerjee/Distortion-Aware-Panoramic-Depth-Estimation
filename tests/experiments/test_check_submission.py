"""scripts/check_submission.py on a synthetic results tree."""
import json
import numpy as np
from pathlib import Path

from scripts.analysis import check_submission as cs


def _cell(v=0.2):
    return {"clean": v, "raw": v, "fixed": v}


def _rows(n, ids=None, scen=cs.SCEN):
    ids = ids or [f"f{i}" for i in range(n)]
    return [dict({"id": i}, **{s: _cell() for s in scen}) for i in ids]


def _w(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))


def _tree(res):
    for d in cs.CORE:
        _w(res / f"correction_da2m_{d}.json", {"rows": _rows(cs.CORE_AVAILABLE[d])})
    for mode in ("rotation", "dilation"):
        for s in cs.SWEEP_SETS:
            _w(res / f"sweep_{mode}_da2m_{s}.json", {"summary": {"n_frames": 80}})
    for tag, n in cs.DIAG_ROWS.items():
        _w(res / "diag" / f"nadir_jpeg_{tag}.json", {"rows": _rows(n, scen=("clean", "nadir", "nadir+jpeg"))})
    for m in cs.MODELS:
        for d, n in cs.STRICT_ROWS.items():
            _w(res / "external" / f"correction_{m}_{d}.json", {"rows": _rows(147 if d == "nyc" else 373)})
            _w(res / "threshold_sweep" / "e2e_s5w70" / f"correction_{m}_{d}.json",
               {"rows": _rows(n), "trained_on": list(cs.CORE)})


def test_complete_tree_passes(tmp_path):
    _tree(tmp_path)
    assert cs.check(tmp_path) == []


def test_problems_are_reported(tmp_path):
    _tree(tmp_path)
    (tmp_path / "sweep_rotation_da2m_nyc_all.json").unlink()
    _w(tmp_path / "correction_da2m_s3.json", {"rows": _rows(40)})                       # too short
    rows = _rows(40, scen=("clean", "nadir", "nadir+jpeg"))
    rows[1]["id"] = rows[0]["id"]                                                         # duplicate id
    _w(tmp_path / "diag" / "nadir_jpeg_dap_s3.json", {"rows": rows})
    bad = _rows(100)
    for r in bad:
        r["jpeg"] = {"clean": float("nan"), "raw": float("nan")}                         # NaN-only column
    bad[0]["id"] = "not_in_headline"
    _w(tmp_path / "threshold_sweep" / "e2e_s5w70" / "correction_dap_stanford.json", {"rows": bad, "trained_on": ["s3", "nyc"]})
    text = "\n".join(cs.check(tmp_path))
    for key in ("missing", "correction_da2m_s3", "duplicate", "'jpeg'", "external set in trained_on", "not in the headline"):
        assert key in text, key


def test_submission_figures_on_synthetic_data(tmp_path):
    from scripts.figures import make_submission_figures as mf
    rng = np.random.default_rng(0)

    def row(i):
        kinds = {}
        for kind in ("nadir", "nadir+jpeg"):
            prot = {}
            for p in ("none", "align-all"):
                d = {"raw": {"region": 0.3, "outside": 0.1, "ring": 0.1, "all": 0.15, "bias": 0.7}}
                for v in ("oracle", "oracle+1.5", "detected", "detected+1.5", "pipe", "bilateral_only", "deblock_oracle",
                          "pipe_photometric", "pipe_cap_first"):
                    name = v if v == "bilateral_only" else f"{v}:plane_fill"
                    d[name] = {"region": 0.3 * (0.6 + 0.2 * rng.random()), "outside": 0.1, "ring": 0.1, "all": 0.14, "bias": 0.9}
                prot[p] = d
            kinds[kind] = prot
        return dict({"id": f"f{i}"}, **kinds)
    rows = [row(i) for i in range(12)]
    vals = mf.ladder_values(rows, "none", "plane_fill")
    assert set(vals) == {"nadir", "nadir+jpeg"} and vals["nadir"]["oracle"][0] < 0
    mf.fig_diag([("a", rows, "none", "plane_fill"), ("b", rows, "align-all", "plane_fill")], tmp_path / "d.png")
    data = {d: {"frames": 10, "lsq": dict({"clean": 0.2}, **{s: -5.0 for s in mf.SCEN[1:]}),
                "median": dict({"clean": 0.1}, **{s: -8.0 for s in mf.SCEN[1:]})} for d in ("holo_out", "stanford", "nyc")}
    mf.fig_da2_protocols(data, tmp_path / "p.png")
    thr = {"0.02|0.6|0": {"core": {"harmful": 8, "mean_change": -0.05}, "external": {"harmful": 5, "mean_change": -0.08}},
           "0.05|0.7|0": {"core": {"harmful": 2, "mean_change": -0.035}, "external": {"harmful": 2, "mean_change": -0.079}}}
    mf.fig_strict_rules(thr, tmp_path / "s.png")
    x = np.linspace(0, 90, 19)
    mf.fig_da2_sweeps({("rotation", "s3_eval"): {"lsq": (x, x * 0.001), "median": (x, -x * 0.001)}}, tmp_path / "w.png")
    for n in "dpsw":
        assert (tmp_path / f"{n}.png").stat().st_size > 1000
