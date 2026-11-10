#!/usr/bin/env python3
"""End-to-end comparison of the headline (core-trained) policy with the all-sets leave-one-out policy.

Reads the headline results (results/correction_<m>_<core>.json, results/external/correction_<m>_<ext>.json) and the separate
all_loo runs (results/policy_comparison/e2e_allloo/correction_<m>_<set>.json, from run_correction.py --policy_mode all_loo),
matches frames by id and compares the median change per scenario. Output: results/policy_comparison/E2E_ALLLOO.md
"""
from __future__ import annotations

import json


from pano.paths import BENCHMARK_RESULTS
from scripts.analysis.final_summary import CORE, EXT, SCEN, cell

RES = BENCHMARK_RESULTS
ALLLOO = RES / "policy_comparison" / "e2e_allloo"


def load_rows(path):
    return json.loads(path.read_text()) if path.is_file() else None


def compare(head, alt):
    """head, alt: loaded correction JSONs. Frames are matched by id. Returns {scenario: (head cell, alt cell, n)}."""
    ids = set(r["id"] for r in head["rows"]) & set(r["id"] for r in alt["rows"])
    h = [r for r in head["rows"] if r["id"] in ids]
    a = [r for r in alt["rows"] if r["id"] in ids]
    h.sort(key=lambda r: r["id"])
    a.sort(key=lambda r: r["id"])
    return {s: (cell(h, s), cell(a, s), len(h)) for s in SCEN[1:]}, head["policy"], alt["policy"], len(ids)


def main():
    fm = lambda c: "n/a" if c is None else f"{c['chg']:+.1f}%"
    L = ["# End-to-end: headline policy (core sets only) vs all-sets leave-one-out", "",
         "Same frames (matched by id), same code; only the fixes chosen differ. The all_loo policy is trained on every other set incl. "
         "Stanford2D3D and NYC. Cells: median per-frame change of AbsRel (headline / all_loo).", "",
         "| set | model | frames | policy differs in | " + " | ".join(SCEN[1:]) + " |", "|---|---|---:|---|" + "---|" * (len(SCEN) - 1)]
    for ds in CORE + EXT:
        for m in ("midas", "dap", "da360", "da2"):
            hp = (RES if ds in CORE else RES / "external") / f"correction_{m}_{ds}.json"
            head, alt = load_rows(hp), load_rows(ALLLOO / f"correction_{m}_{ds}.json")
            if head is None or alt is None:
                continue
            res, ph, pa, n = compare(head, alt)
            diff = ", ".join(f"{k}: {ph.get(k, 'none')}->{pa.get(k, 'none')}" for k in sorted(set(ph) | set(pa)) if ph.get(k) != pa.get(k)) or "-"
            L.append(f"| {ds} | {m} | {n} | {diff} | " + " | ".join(f"{fm(res[s][0])} / {fm(res[s][1])}" for s in SCEN[1:]) + " |")
    ALLLOO.mkdir(parents=True, exist_ok=True)
    (RES / "policy_comparison" / "E2E_ALLLOO.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
