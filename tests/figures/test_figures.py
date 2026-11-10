"""make_figures.py draws every figure from a synthetic results folder (no model, no GPU)."""
import json
from pathlib import Path

import numpy as np

from scripts.figures import make_figures as mf
from methods.capture_faults.catalogue import CATALOGUE


def _rows(n=4, bias=1.0):
    rows = []
    for i in range(n):
        r = {"id": f"scene_{i:05d}_x", "group": f"scene_{i:05d}", "clean": {"all": 0.1, "polar": 0.12}}
        for k in ("relevel_self", "gain_match", "flatfield", "denoise", "bilateral"):
            r[f"clean+{k}"] = {"all": 0.11, "polar": 0.13}
        for d in CATALOGUE:
            m = {"all": 0.1, "polar": 0.1, "region": 0.1}
            r[f"{d.key}|clean"] = dict(m)
            r[f"{d.key}|none"] = {k: v * 2 * bias for k, v in m.items()}
            for mk in d.mitigations:
                r[f"{d.key}|{mk}"] = {k: v * 1.4 for k, v in m.items()}
            r[f"{d.key}|best_example"] = d.mitigations[0] if d.mitigations else None
        rows.append(r)
    return rows


def _img(path):
    import cv2
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), (np.random.default_rng(0).random((32, 64, 3)) * 255).astype(np.uint8))


def test_all_figures_are_drawn_for_core_and_external_sets(tmp_path):
    mf.set_results(tmp_path)
    mf.made.clear()
    for m in ("midas", "dap"):
        for ds in ("s3", "nyc"):
            rows = _rows()
            fid = rows[0]["id"]
            names = {"rgb": "a.jpg", "clean": "a.jpg", "err_clean": "a.jpg"}
            for d in CATALOGUE:
                for suf in ("rgb", "none", "best", "err_" + d.key + "_none", "err_" + d.key + "_best"):
                    pass
                names.update({f"{d.key}_rgb": "a.jpg", f"{d.key}_none": "a.jpg", f"{d.key}_best": "a.jpg",
                              f"err_{d.key}_none": "a.jpg", f"err_{d.key}_best": "a.jpg"})
            _img(tmp_path / f"study_{m}_{ds}_img" / "a.jpg")
            (tmp_path / f"study_{m}_{ds}.json").write_text(json.dumps({"rows": rows, "examples": {fid: names}}))
            crow = [{"id": fid, **{sc: {"clean": {"all": .1, "region": .1}, "raw": {"all": .2, "region": .2},
                                        "fixed": {"all": .15, "region": .15}, "log": ["x"], "detected": None, "caps": {}}
                                   for sc in ("clean", "tilt", "nadir")}}]
            cn = {k: "a.jpg" for sc in ("clean", "tilt", "nadir") for k in (f"{sc}_input", f"{sc}_raw", f"{sc}_fixed", f"err_{sc}_raw", f"err_{sc}_fixed")}
            cn.update({"clean": "a.jpg", "err_clean": "a.jpg"})
            out = tmp_path if ds == "s3" else tmp_path / "external"
            _img(out / f"correction_{m}_{ds}_img" / "a.jpg")
            (out / f"correction_{m}_{ds}.json").write_text(json.dumps({"policy": {}, "rows": crow, "examples": {fid: cn}}))
    sw = {"summary": {"centres": [2.5, 7.5, 12.5], "ratio_global": [1.0, 1.1, 1.3]}}
    (tmp_path / "sweep_dilation_midas_nyc_all.json").write_text(json.dumps(sw))
    mf.plot_clean_error(); mf.plot_fault_cost(); mf.plot_do_no_harm(); mf.plot_correction(); mf.plot_sweeps()
    for d in CATALOGUE:
        mf.plot_fix(d)
    mf.visual_study(1); mf.visual_models(1); mf.visual_correction(1)
    made = set(mf.made)
    for want in ("fig_clean_error.png", "fig_fault_cost.png", "fig_do_no_harm.png", "fig_correction_gain.png",
                 "fig_fix_vfov.png", "fig_sweeps_dilation.png"):
        assert want in made, want
    assert any(n.startswith("visual/dap_nyc_tilt") for n in made)
    assert any(n.startswith("visual_models/nyc_nadir") for n in made)
    assert any(n.startswith("visual_correction/midas_nyc_tilt") for n in made)
    assert all((tmp_path / "figures" / n).stat().st_size > 1000 for n in made)
