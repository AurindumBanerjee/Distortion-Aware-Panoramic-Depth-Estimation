#!/usr/bin/env python3
"""Learn the capture-aware correction policy (distortions/correction.py) from the distortion-study results and test it
on data it was not chosen on. No GPU: it only reads results/study_<model>_<dataset>.json.

Selection, per model and fault, is leave-one-dataset-out: the fix (or "none") is chosen on the OTHER datasets and
scored on the held-out one. Rule: among the candidate fixes, take the one with the lowest median per-frame relative
change vs the uncorrected prediction (median over datasets of the per-dataset medians), and keep it only if that
change is below -min_gain AND it beats "none" on at least `min_win` of the training frames; otherwise "none".

The final policy (all datasets used for selection) is written to results/correction_policy.json; the held-out table
to results/CORRECTION_POLICY.md.

  python scripts/calibrate_correction.py                       # all models / datasets found in results/
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from pano.paths import ROOT
from methods.capture_faults.catalogue import CATALOGUE

FAULTS = {d.key: d for d in CATALOGUE}
# The fix choices are learned from these datasets ONLY. Stanford2D3D and NYC are external: never used to choose or
# tune anything, only to test the finished policy (scripts/run_correction.py writes their results to results/external/).
CORE_SETS = ("s3", "panox", "holo_in", "holo_out")


def metric_of(d) -> str:
    return "region" if d.region is not None else "all"


def frame_stats(rows, fault, fix, f):
    """Per-frame relative change vs no fix, win flags, and recovery (frames the fault hurt by >= 5%)."""
    rel, win, rec = [], [], []
    for r in rows:
        n, c = r.get(f"{fault}|none", {}).get(f), r.get(f"{fault}|clean", {}).get(f)
        m = n if fix == "none" else r.get(f"{fault}|{fix}", {}).get(f)
        if n is None or m is None or not (np.isfinite(n) and np.isfinite(m)) or n <= 0:
            continue
        rel.append((m - n) / n)
        win.append(m < n)
        if c is not None and np.isfinite(c) and n - c >= 0.05 * c:
            rec.append((n - m) / max(n - c, 1e-6))
    return np.array(rel), np.array(win, bool), np.array(rec)


def choose(train, fault, min_gain, min_win):
    """train: {dataset: rows}. Returns (fix, score) chosen on these datasets."""
    d = FAULTS[fault]
    f = metric_of(d)
    best = ("none", 0.0)
    for fix in d.mitigations:
        if fix == "relevel_self":  # needs no sensor but measured harmful; kept out of the deployable policy
            continue
        meds, wins = [], []
        for rows in train.values():
            rel, win, _ = frame_stats(rows, fault, fix, f)
            if len(rel):
                meds.append(np.median(rel))
                wins.append(win)
        if not meds:
            continue
        score = float(np.median(meds))
        wr = float(np.mean(np.concatenate(wins)))
        if score < -min_gain and wr >= min_win and score < best[1]:
            best = (fix, score)
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--sets", default=",".join(CORE_SETS), help="datasets the policy is learned from (default: the four core sets; "
                    "external sets stanford / nyc must not be listed)")
    ap.add_argument("--min_gain", type=float, default=0.02, help="required median improvement (fraction) on training")
    ap.add_argument("--min_win", type=float, default=0.6, help="required share of training frames improved")
    a = ap.parse_args()
    res = Path(a.results)
    sets = set(a.sets.split(","))
    data = defaultdict(dict)  # model -> dataset -> rows
    for p in sorted(res.glob("study_*.json")):
        tag = p.stem[len("study_"):]
        if tag.startswith("smoke") or "_" not in tag or tag.endswith("mini"):  # mini = early pilot runs
            continue
        model, ds = tag.split("_", 1)
        if ds not in sets:
            continue
        data[model][ds] = json.loads(p.read_text())["rows"]
    if not data:
        sys.exit(f"no study_<model>_<dataset>.json in {res}")

    faults = [d.key for d in CATALOGUE if d.mitigations]
    policy, lines = {}, []
    lines += ["# Capture-aware correction: learned policy and held-out test", "",
              f"Learned from the core datasets only: {', '.join(sorted(sets))}. Stanford2D3D / NYC are not used here "
              "(see results/EXTERNAL_stanford_nyc.md).", "",
              "Fix per (model, fault) chosen on the other datasets (leave-one-dataset-out) and scored on the held-out one. "
              f"A fix is kept only if its median change vs no fix is below -{100 * a.min_gain:.0f}% and it improves at least "
              f"{100 * a.min_win:.0f}% of training frames; otherwise no fix ('none').", "",
              "Columns per held-out dataset: chosen fix · median change vs uncorrected · frames improved · median recovery "
              "(frames hurt >= 5%). The metric is the affected region for missing-pixel faults, else the whole panorama. "
              "`relevel_known` and `wiener` need sensor data (IMU / gyro).", ""]
    summary = []
    for model in sorted(data):
        dsets = sorted(data[model])
        policy[model] = {}
        lines += [f"## {model}", "", "| fault | final policy | " + " | ".join(dsets) + " |", "|---|---|" + "---|" * len(dsets)]
        for fault in faults:
            final, _ = choose(data[model], fault, a.min_gain, a.min_win)
            if final != "none":
                policy[model][fault] = final
            cells = []
            for held in dsets:
                train = {k: v for k, v in data[model].items() if k != held}
                fix, _ = choose(train, fault, a.min_gain, a.min_win) if train else ("none", 0.0)
                rel, win, rec = frame_stats(data[model][held], fault, fix, metric_of(FAULTS[fault]))
                if fix == "none" or not len(rel):
                    cells.append("none")
                    summary.append((model, fault, held, "none", 0.0, None))
                    continue
                r = f"{100 * np.median(rec):.0f}%" if len(rec) else "n/a"
                cells.append(f"{fix} · {100 * np.median(rel):+.0f}% · {100 * win.mean():.0f}% · {r}")
                summary.append((model, fault, held, fix, float(np.median(rel)), float(win.mean())))
            lines.append(f"| {fault} | {final} | " + " | ".join(cells) + " |")
        lines.append("")

    applied = [s for s in summary if s[3] != "none"]
    harmful = [s for s in applied if s[4] > 0]
    lines += ["## Overall (held-out)", "",
              f"- (model, fault, dataset) cells: {len(summary)}; a fix was applied in {len(applied)}, left off in "
              f"{len(summary) - len(applied)}.",
              f"- Of the applied cells, {len(applied) - len(harmful)} improved the median, {len(harmful)} made it worse"
              + (": " + ", ".join(f"{m}/{f}/{d} ({100 * x:+.0f}%)" for m, f, d, _, x, _ in harmful) if harmful else "") + ".",
              f"- Median change over applied cells: {100 * np.median([s[4] for s in applied]):+.0f}%." if applied else "", ""]
    (res / "correction_policy.json").write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    (res / "CORRECTION_POLICY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("wrote", res / "correction_policy.json", "and", res / "CORRECTION_POLICY.md")


if __name__ == "__main__":
    main()
