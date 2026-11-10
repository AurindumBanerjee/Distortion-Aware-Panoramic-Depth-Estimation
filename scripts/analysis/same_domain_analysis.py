#!/usr/bin/env python3
"""Same-domain policy experiment (separate from the headline): is a policy learned on real Stanford2D3D / NYC frames better on
held-out rooms / street blocks of the same dataset than the policy learned on the core sets?

Input : results/policy_comparison/same_domain/study_sd_<model>_<set>.json  (full fault study, own tag, own folder)
        results/study_<model>_<core set>.json                              (the headline policy's training data)
Method: the clusters (room / block of 20 ids) of one external set are split into two folds by a hash. For each fold the
        in-domain policy is learned on the OTHER fold and the core policy on the core sets; both are scored on the fold.
        No frame is ever scored with a policy that saw its own cluster. Faults are scored one at a time (no model runs).
Output: results/policy_comparison/same_domain/SAME_DOMAIN.md and same_domain.json
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

from pano.paths import BENCHMARK_RESULTS
from scripts.analysis.calibrate_correction import CORE_SETS, FAULTS, choose, frame_stats, metric_of

MODELS = ("midas", "dap", "da360", "da2")
EXTERNAL = ("stanford", "nyc")
POLICIES = ("core", "in_domain")
OUT = BENCHMARK_RESULTS / "policy_comparison" / "same_domain"


def fold_of(groups, k=2):
    """cluster -> fold, balanced and deterministic (clusters ordered by a hash of their id)."""
    uniq = sorted(set(groups), key=lambda g: hashlib.md5(str(g).encode()).hexdigest())
    return {g: i % k for i, g in enumerate(uniq)}


def evaluate(core_rows, rows, min_gain=0.02, min_win=0.6, k=2):
    """core_rows: {core set: rows}; rows: one external set's study rows (each with 'group').
    Returns cells {fault, fold, n, core: {fix, change}, in_domain: {fix, change}}."""
    fo = fold_of([r["group"] for r in rows], k)
    cells = []
    for fold in range(k):
        test = [r for r in rows if fo[r["group"]] == fold]
        train = [r for r in rows if fo[r["group"]] != fold]
        for fault, d in FAULTS.items():
            if not d.mitigations or not test or not train:
                continue
            f = metric_of(d)
            cell = {"fault": fault, "fold": fold, "n": len(test)}
            for pol, tr in (("core", core_rows), ("in_domain", {"fold": train})):
                fix = choose(tr, fault, min_gain, min_win)[0]
                if fix == "none":
                    cell[pol] = {"fix": "none", "change": 0.0}
                else:
                    rel, _, _ = frame_stats(test, fault, fix, f)
                    cell[pol] = {"fix": fix, "change": float(100 * np.median(rel)) if len(rel) else float("nan")}
            cells.append(cell)
    return cells


def summarise(cells, pol, hurt=1.0):
    ch = np.array([c[pol]["change"] for c in cells], float)
    ch = ch[np.isfinite(ch)]
    return {"cells": len(ch), "applied": int(sum(c[pol]["fix"] != "none" for c in cells)), "improved": int((ch < -hurt).sum()),
            "worse": int((ch > hurt).sum()), "mean_change": float(ch.mean()) if len(ch) else float("nan")}


def main():
    res = BENCHMARK_RESULTS
    allc, L = [], ["# Same-domain policy experiment", "",
                   "Clusters (Stanford: room; NYC: 20 consecutive ids, an assumed grouping) are split into two folds. `in_domain`: fixes chosen on "
                   "the other fold of the same dataset. `core`: fixes chosen on the four core sets (the headline policy). Both are scored on "
                   "the held-out fold, one fault at a time; a cell is (model, fault, fold). Improved / worse: change below -1% / above +1%. "
                   "Stanford's real black caps overlap the simulated nadir / vfov faults, so those two faults are weakly informative there.", "",
                   "| set | model | frames | clusters | " + " | ".join(f"{p}: applied / improved / worse / mean %" for p in POLICIES) + " |",
                   "|---|---|---:|---:|" + "---|" * len(POLICIES)]
    for ds in EXTERNAL:
        for m in MODELS:
            p = OUT / f"study_sd_{m}_{ds}.json"
            if not p.is_file():
                continue
            rows = json.loads(p.read_text())["rows"]
            core = {c: json.loads((res / f"study_{m}_{c}.json").read_text())["rows"] for c in CORE_SETS if (res / f"study_{m}_{c}.json").is_file()}
            cells = evaluate(core, rows)
            for c in cells:
                c.update(model=m, set=ds)
            allc += cells
            L.append(f"| {ds} | {m} | {len(rows)} | {len(set(r['group'] for r in rows))} | " + " | ".join(
                "{applied} / {improved} / {worse} / {mean_change:+.2f}".format(**summarise(cells, pol)) for pol in POLICIES) + " |")
    L += ["", "## Cells where the two policies choose differently", "", "| set | model | fault | fold | core | in_domain |", "|---|---|---|---:|---|---|"]
    fmt = lambda x: f"{x['fix']} ({x['change']:+.1f}%)" if x["fix"] != "none" else "none"
    for c in allc:
        if c["core"]["fix"] != c["in_domain"]["fix"]:
            L.append(f"| {c['set']} | {c['model']} | {c['fault']} | {c['fold']} | {fmt(c['core'])} | {fmt(c['in_domain'])} |")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "SAME_DOMAIN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "same_domain.json").write_text(json.dumps(allc), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
