#!/usr/bin/env python3
"""How stable is the learned policy with more training frames? (stage `study100` of scripts/run_submission.sh)

Compares the leave-one-dataset-out policy learned from the 40-frame studies (results/study_<m>_<core>.json) with the one learned
from the 100-frame studies of the same models and sets (results/policy_stability/study_s100_<m>_<core>.json), for the headline
rule: per model and fault, the fix chosen with the held-out set excluded. Output results/policy_stability/POLICY_STABILITY.md:
agreement counts and every (model, held-out set, fault) cell where the choice differs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pano.paths import ROOT
from scripts.analysis.calibrate_correction import CORE_SETS, choose
from methods.capture_faults.catalogue import CATALOGUE
RES = ROOT / "results"
OUT = RES / "policy_stability"
MODELS = ("midas", "dap", "da360", "da2")


def policy_for(studies, held, min_gain=0.02, min_win=0.6):
    train = {k: v for k, v in studies.items() if k != held}
    return {d.key: choose(train, d.key, min_gain, min_win)[0] for d in CATALOGUE if d.mitigations} if train else {}


def load(path):
    return json.loads(path.read_text())["rows"] if path.is_file() else None


def main():
    L = ["# Policy stability: 40-frame vs 100-frame studies", "",
         "Leave-one-dataset-out choice (headline rule) per model, held-out core set and fault.", "",
         "| model | cells | same choice | different | 40-frame applies | 100-frame applies |", "|---|---:|---:|---:|---:|---:|"]
    diffs = []
    for m in MODELS:
        s40, s100 = {}, {}
        for ds in CORE_SETS:
            a, b = load(RES / f"study_{m}_{ds}.json"), load(OUT / f"study_s100_{m}_{ds}.json")
            if a is not None and b is not None:
                s40[ds], s100[ds] = a, b
        if len(s40) < 2:
            continue
        n = same = a40 = a100 = 0
        for held in s40:
            p40, p100 = policy_for(s40, held), policy_for(s100, held)
            for f in p40:
                n += 1
                same += p40[f] == p100[f]
                a40 += p40[f] != "none"
                a100 += p100[f] != "none"
                if p40[f] != p100[f]:
                    diffs.append((m, held, f, p40[f], p100[f]))
        L.append(f"| {m} | {n} | {same} | {n - same} | {a40} | {a100} |")
    L += ["", "## Cells where the choice differs", "", "| model | held out | fault | 40 frames | 100 frames |", "|---|---|---|---|---|"]
    L += [f"| {m} | {h} | {f} | {a} | {b} |" for m, h, f, a, b in diffs] or ["| - | - | - | - | - |"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "POLICY_STABILITY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
