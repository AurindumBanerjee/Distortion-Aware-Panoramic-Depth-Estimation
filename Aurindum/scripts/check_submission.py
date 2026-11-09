#!/usr/bin/env python3
"""Completeness check of the submission runs (scripts/run_submission.sh): DA2 median-fit corrections and sweeps, nadir + JPEG
diagnosis files, strict-rule end-to-end files. Exits 1 and lists every problem if anything is missing, short, duplicated or NaN-only.
Usage: python scripts/check_submission.py [results_dir]"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ("s3", "panox", "holo_in", "holo_out")
EXTERNAL = ("stanford", "nyc")
MODELS = ("midas", "dap", "da360", "da2")
SCEN = ("clean", "tilt", "nadir", "vfov", "yawblur", "jpeg", "nadir+jpeg")
SWEEP_SETS = ("s3_eval", "panox_all", "holo_in_all", "holo_out_all", "nyc_all")
CORE_AVAILABLE = {"s3": 100, "panox": 100, "holo_in": 100, "holo_out": 71}
DIAG_ROWS = {"dap_nyc": 147, "dap_holo_out": 71, "dap_s3": 40, "dap_panox": 40, "dap_holo_in": 40, "dap_stanford": 40,
             "midas_nyc": 40, "midas_s3": 40, "da360_nyc": 40, "da360_s3": 40, "da2_nyc": 40, "da2_s3": 40, "da2m_nyc": 40}
STRICT_ROWS = {"stanford": 100, "nyc": 147}


def _load(p: Path, problems: list[str]):
    if not p.is_file():
        problems.append(f"missing: {p}")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        problems.append(f"unreadable {p}: {e}")
        return None


def _finite(v) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(v)


def _has_finite(v) -> bool:
    """True if a cell (number, or nested dict/list of numbers) holds at least one finite number."""
    if isinstance(v, dict):
        return any(_has_finite(x) for x in v.values())
    if isinstance(v, list):
        return any(_has_finite(x) for x in v)
    return _finite(v)


def check_rows(rows, name: str, min_rows: int, problems: list[str], scenarios=SCEN, exact: int | None = None):
    """Row count, duplicate ids, empty rows and NaN-only scenario columns of a list of per-frame rows."""
    if exact is not None and len(rows) != exact:
        problems.append(f"{name}: {len(rows)} rows, expected {exact}")
    elif len(rows) < min_rows:
        problems.append(f"{name}: {len(rows)} rows, expected >= {min_rows}")
    ids = [r.get("id") for r in rows]
    if len(set(ids)) != len(ids):
        problems.append(f"{name}: duplicate ids")
    if any(not r or r.get("id") is None for r in rows):
        problems.append(f"{name}: empty row or row without id")
    for s in scenarios:
        vals = [r.get(s) for r in rows]
        ok = any(_has_finite(v) for v in vals)
        if rows and not ok:
            problems.append(f"{name}: scenario column '{s}' has no finite value")


def check(res: Path) -> list[str]:
    problems: list[str] = []
    # DA2 median fit, core sets
    for d in CORE:
        j = _load(res / f"correction_da2m_{d}.json", problems)
        if j:
            check_rows(j["rows"], f"correction_da2m_{d}", min(100, CORE_AVAILABLE[d]), problems)
    # sweeps
    for mode in ("rotation", "dilation"):
        for s in SWEEP_SETS:
            j = _load(res / f"sweep_{mode}_da2m_{s}.json", problems)
            if j:
                n = j["summary"]["n_frames"]
                if not 60 <= n <= 100:
                    problems.append(f"sweep_{mode}_da2m_{s}: n_frames {n}, expected about 80")
    # diagnosis ladder
    for tag, n in DIAG_ROWS.items():
        j = _load(res / "diag" / f"nadir_jpeg_{tag}.json", problems)
        if j:
            check_rows(j["rows"], f"diag/nadir_jpeg_{tag}", n, problems, scenarios=("clean", "nadir", "nadir+jpeg"), exact=n)
    # strict rule end to end, ids a subset of the headline
    for m in MODELS:
        for d in EXTERNAL:
            j = _load(res / "threshold_sweep" / "e2e_s5w70" / f"correction_{m}_{d}.json", problems)
            h = _load(res / "external" / f"correction_{m}_{d}.json", problems)
            if not j:
                continue
            check_rows(j["rows"], f"e2e_s5w70/{m}_{d}", STRICT_ROWS[d], problems, exact=STRICT_ROWS[d])
            if set(j.get("trained_on", [])) & set(EXTERNAL):
                problems.append(f"e2e_s5w70/{m}_{d}: external set in trained_on {j.get('trained_on')}")
            if h:
                missing = {r["id"] for r in j["rows"]} - {r["id"] for r in h["rows"]}
                if missing:
                    problems.append(f"e2e_s5w70/{m}_{d}: {len(missing)} ids not in the headline file")
    return problems


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    res = Path(argv[0]) if argv else ROOT / "results"
    problems = check(res)
    for p in problems:
        print("PROBLEM:", p)
    print(f"{len(problems)} problem(s)" if problems else "submission files complete")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
