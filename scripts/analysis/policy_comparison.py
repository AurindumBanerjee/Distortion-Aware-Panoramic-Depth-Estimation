#!/usr/bin/env python3
"""Compare three ways of learning the correction policy, offline, from the capture-fault study files.

  core_loo  fixes chosen on the core sets other than the tested set (external sets never train)  -> the headline policy
  all_loo   fixes chosen on ALL other sets (core + Stanford2D3D + NYC), tested set left out
  all_in    fixes chosen on ALL sets including the tested one -> in-sample, an optimistic upper bound, not a held-out result

For every (model, fault, tested set) the chosen fix is scored on the tested set's per-frame study results
(median relative change of the fault metric vs no fix; 0 when no fix is chosen). The study files hold every fix on every
frame, so no model is run. This evaluates faults one at a time; the combined pipeline (scripts/run_correction.py) is not
re-run. Output: results/policy_comparison/ (own folder; nothing here feeds correction_policy.json, the headline
(core_loo) results or any figure).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from pano.paths import ROOT
from scripts.analysis.calibrate_correction import CORE_SETS, FAULTS, choose, frame_stats, metric_of

ALL_SETS = CORE_SETS + ("stanford", "nyc")
MODELS = ("midas", "dap", "da360", "da2")
POLICIES = ("core_loo", "all_loo", "all_in")


def train_sets(policy, test):
    if policy == "core_loo":
        return [d for d in CORE_SETS if d != test]
    if policy == "all_loo":
        return [d for d in ALL_SETS if d != test]
    if policy == "all_in":
        return list(ALL_SETS)
    raise ValueError(policy)


def evaluate(studies, min_gain=0.02, min_win=0.6):
    """studies: {model: {dataset: rows}}. Returns a list of cells
    {model, fault, test, policy: {fix, change, win}} (change in %, median relative change on the tested set)."""
    cells = []
    for m, per in studies.items():
        for test, rows in per.items():
            for fault, d in FAULTS.items():
                if not d.mitigations:
                    continue
                f = metric_of(d)
                cell = {"model": m, "fault": fault, "test": test}
                for pol in POLICIES:
                    train = {ds: per[ds] for ds in train_sets(pol, test) if ds in per}
                    fix = choose(train, fault, min_gain, min_win)[0] if train else "none"
                    if fix == "none":
                        cell[pol] = {"fix": "none", "change": 0.0, "win": float("nan")}
                        continue
                    rel, win, _ = frame_stats(rows, fault, fix, f)
                    cell[pol] = {"fix": fix, "change": float(100 * np.median(rel)) if len(rel) else float("nan"),
                                 "win": float(np.mean(win)) if len(win) else float("nan")}
                cells.append(cell)
    return cells


def aggregate(cells, pol, hurt=1.0):
    ch = np.array([c[pol]["change"] for c in cells], float)
    ch = ch[np.isfinite(ch)]
    app = np.array([c[pol]["fix"] != "none" for c in cells])
    return {"cells": len(ch), "applied": int(app.sum()), "improved": int((ch < -hurt).sum()), "worse": int((ch > hurt).sum()),
            "mean_change": float(ch.mean()) if len(ch) else float("nan"),
            "sum_gain": float(-ch[ch < 0].sum()) if len(ch) else 0.0, "sum_loss": float(ch[ch > 0].sum()) if len(ch) else 0.0}


def main():
    res = ROOT / "results"
    studies = {}
    for m in MODELS:
        for ds in ALL_SETS:
            p = res / f"study_{m}_{ds}.json"
            if p.is_file():
                studies.setdefault(m, {})[ds] = json.loads(p.read_text())["rows"]
    cells = evaluate(studies)
    L = ["# Policy comparison (offline, from the capture-fault study files)", "",
         "`core_loo`: fixes chosen on the other core sets only (headline, external sets never train). `all_loo`: chosen on every other "
         "set incl. Stanford2D3D and NYC. `all_in`: chosen on all sets incl. the tested one (in-sample, optimistic, not held out). "
         "A cell is one (model, fault, tested set); its value is the median per-frame change of the fault metric when the chosen "
         "fix is applied (0 = no fix). Improved / worse: change below -1% / above +1%. Faults are scored one at a time; the "
         "combined pipeline is not rerun here.", "",
         "## All cells", "", "| policy | cells | fix applied | improved | worse | mean change (%) | summed gain | summed loss |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for pol in POLICIES:
        a = aggregate(cells, pol)
        L.append(f"| {pol} | {a['cells']} | {a['applied']} | {a['improved']} | {a['worse']} | {a['mean_change']:+.2f} | {a['sum_gain']:.0f} | {a['sum_loss']:.0f} |")
    for title, sel in (("Per model", lambda c, k: c["model"] == k), ("Per tested set", lambda c, k: c["test"] == k)):
        keys = MODELS if title == "Per model" else ALL_SETS
        L += ["", f"## {title}", "", "| " + title.split()[-1] + " | " + " | ".join(f"{p}: applied / improved / worse / mean %" for p in POLICIES) + " |",
              "|---|" + "---|" * len(POLICIES)]
        for k in keys:
            sub = [c for c in cells if sel(c, k)]
            if sub:
                L.append(f"| {k} | " + " | ".join(
                    "{applied} / {improved} / {worse} / {mean_change:+.2f}".format(**aggregate(sub, p)) for p in POLICIES) + " |")
    L += ["", "## Cells where core_loo and all_loo choose differently", "",
          "| model | fault | tested | core_loo | all_loo | all_in |", "|---|---|---|---|---|---|"]
    fmt = lambda x: f"{x['fix']} ({x['change']:+.1f}%)" if x["fix"] != "none" else "none"
    for c in cells:
        if c["core_loo"]["fix"] != c["all_loo"]["fix"]:
            L.append(f"| {c['model']} | {c['fault']} | {c['test']} | {fmt(c['core_loo'])} | {fmt(c['all_loo'])} | {fmt(c['all_in'])} |")
    out = res / "policy_comparison"
    out.mkdir(exist_ok=True)
    (out / "POLICY_COMPARISON.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "policy_comparison.json").write_text(json.dumps(cells), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
