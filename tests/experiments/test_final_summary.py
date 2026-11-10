"""scripts/final_summary.py: per-cell statistics of the correction results."""
from pathlib import Path

import numpy as np

from scripts.analysis.final_summary import cell


def _rows(raw, fixed, det="nadir", scen="nadir"):
    f = "region" if scen in ("nadir", "vfov", "nadir+jpeg") else "all"
    return [{scen: {"raw": {f: u}, "fixed": {f: x}, "detected": det}} for u, x in zip(raw, fixed)]


def test_cell_reports_median_change_share_improved_and_detection():
    rows = _rows([1.0, 1.0, 1.0, 1.0], [0.5, 0.5, 1.0, 1.2])
    c = cell(rows, "nadir")
    assert c["n"] == 4 and abs(c["chg"] - (-25.0)) < 1e-9          # median of -50, -50, 0, +20
    assert c["better"] == 0.5 and c["worse"] == 0.25 and c["det"] == 1.0
    assert c["lo"] <= c["chg"] <= c["hi"]


def test_cell_uses_whole_image_for_photometric_scenarios_and_skips_nonfinite_frames():
    rows = _rows([1.0, np.nan, 2.0], [0.9, 0.5, 1.0], det=None, scen="jpeg")
    c = cell(rows, "jpeg")
    assert c["n"] == 2 and abs(c["chg"] - (-30.0)) < 1e-9 and np.isnan(c["det"])
