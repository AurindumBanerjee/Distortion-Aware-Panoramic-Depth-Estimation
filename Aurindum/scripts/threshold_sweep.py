#!/usr/bin/env python3
"""Stricter 'do no harm' rules for the learned correction policy, tested offline (no GPU) on the study files.

The headline rule keeps a fix for a (model, fault) only if, on the training datasets, its median per-dataset change
vs no fix is below -min_gain (2%) and it improves at least min_win (60%) of the training frames. That guarantees
nothing on a new dataset (MiDaS Stanford tilt +0.6%, DA2 Stanford JPEG +8%, DA2 NYC tilt +14%). This script scans stricter
rules and reports what they cost:

  min_gain  in {0, 2, 5, 10}%        required median improvement
  min_win   in {50, 60, 70, 80, 90}% required share of improved training frames
  all_sets  False / True             True: the median change must be negative in EVERY training dataset (consistency)

Each rule is evaluated two ways, with the choice always made on core datasets only:
  core LOO   policy chosen on the other core sets, scored on the held-out core set (s3, panox, holo_in, holo_out)
  external   policy chosen on all four core sets, scored on Stanford2D3D and NYC (study files, 40 frames)
Reported per rule (all models pooled over (model, fault, dataset) cells): cells where a fix is applied, applied cells
whose median change is worse than +1% ('harmful'), mean change per cell (no fix counts as 0) and the gain that is forgone
compared with the headline rule. Rules are ranked on the core LOO numbers only; external numbers are a test.

  python scripts/threshold_sweep.py            # writes results/threshold_sweep/THRESHOLDS.md and thresholds.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from distortions.catalogue import CATALOGUE  # noqa: E402
from calibrate_correction import CORE_SETS, FAULTS, frame_stats, metric_of  # noqa: E402

EXTERNAL = ("stanford", "nyc")
HARM = 0.01
POOL_SKIP = "da2m"
GAINS = (0.0, 0.02, 0.05, 0.10)
WINS = (0.5, 0.6, 0.7, 0.8, 0.9)
HEADLINE = (0.02, 0.6, False)


def choose_rule(train, fault, min_gain, min_win, all_sets=False):
    """Same as calibrate_correction.choose, plus the optional requirement that every training dataset improves."""
    d = FAULTS[fault]
    f = metric_of(d)
    best = ("none", 0.0)
    for fix in d.mitigations:
        if fix == "relevel_self":
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
        if all_sets and max(meds) >= 0:
            continue
        if score < -min_gain and wr >= min_win and score < best[1]:
            best = (fix, score)
    return best


def load_study(res: Path):
    data = defaultdict(dict)
    for p in sorted(res.glob("study_*.json")):
        tag = p.stem[len("study_"):]
        if tag.startswith("smoke") or "_" not in tag or tag.endswith("mini"):
            continue
        model, ds = tag.split("_", 1)
        if ds in CORE_SETS + EXTERNAL:
            data[model][ds] = json.loads(p.read_text())["rows"]
    return data


def cell_change(rows, fault, fix):
    """Median per-frame relative change of `fix` vs no fix on one dataset (None if no data)."""
    rel, _, _ = frame_stats(rows, fault, fix, metric_of(FAULTS[fault]))
    return float(np.median(rel)) if len(rel) else None


def evaluate(data, rule, faults):
    """{'core': stats, 'external': stats}; stats = dict(cells, applied, harmful, mean_change, cells_detail)."""
    gain, win, alls = rule
    res = {}
    for part, held_sets in (("core", CORE_SETS), ("external", EXTERNAL)):
        cells = []
        for model, ds_rows in sorted(data.items()):
            for held in held_sets:
                if held not in ds_rows:
                    continue
                train = {k: v for k, v in ds_rows.items() if k in CORE_SETS and k != held}
                if not train:
                    continue
                for fault in faults:
                    fix, _ = choose_rule(train, fault, gain, win, alls)
                    ch = cell_change(ds_rows[held], fault, fix) if fix != "none" else 0.0
                    if ch is None:
                        continue
                    cells.append({"model": model, "dataset": held, "fault": fault, "fix": fix, "change": ch})
        pooled = [c for c in cells if c["model"] != POOL_SKIP]      # da2m is DA2 under another protocol: not pooled twice
        app = [c for c in pooled if c["fix"] != "none"]
        res[part] = {"cells": len(pooled), "applied": len(app), "harmful": sum(c["change"] > HARM for c in app),
                     "mean_change": float(np.mean([c["change"] for c in pooled])) if pooled else float("nan"),
                     "detail": cells}
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--out", default=str(ROOT / "results" / "threshold_sweep"))
    a = ap.parse_args()
    data = load_study(Path(a.results))
    if not data:
        sys.exit("no study files")
    faults = [d.key for d in CATALOGUE if d.mitigations]
    rules = list(itertools.product(GAINS, WINS, (False, True)))
    table = {r: evaluate(data, r, faults) for r in rules}
    base = table[HEADLINE]
    L = ["# Stricter do-no-harm rules: offline threshold test", "",
         "Choice always made on core datasets only. 'core LOO' = policy learned on the other three core sets, scored on the held-out core set; "
         "'external' = policy learned on all four core sets, scored on Stanford2D3D and NYC (40-frame study files). Cells are (model, fault, dataset); "
         "a cell counts as harmful if an applied fix has median change above +1%. Mean change counts 'no fix' as 0. "
         f"Models: {', '.join(sorted(data))}; pooled totals leave out da2m (DA2 under the median fit, core sets only) so that DA2 is not counted twice. Headline rule: min_gain 2%, min_win 60%, no per-dataset consistency requirement.", ""]
    L += ["| min_gain | min_win | every set better | core: applied | core: harmful | core: mean change | external: applied | external: harmful | external: mean change | core mean change minus headline (+ = less gain) |",
          "|---:|---:|:---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rules:
        t = table[r]
        mark = " (headline)" if r == HEADLINE else ""
        L.append(f"| {100 * r[0]:.0f}%{mark} | {100 * r[1]:.0f}% | {'yes' if r[2] else 'no'} | {t['core']['applied']} | {t['core']['harmful']} | "
                 f"{100 * t['core']['mean_change']:+.2f}% | {t['external']['applied']} | {t['external']['harmful']} | "
                 f"{100 * t['external']['mean_change']:+.2f}% | {100 * (t['core']['mean_change'] - base['core']['mean_change']):+.2f} pts |")
    # Pareto front on core LOO only: no other rule has both fewer harmful cells and a lower (better) mean change
    key = lambda r: (table[r]["core"]["harmful"], table[r]["core"]["mean_change"])
    front = [r for r in rules if not any(key(o)[0] <= key(r)[0] and key(o)[1] <= key(r)[1] and key(o) != key(r) for o in rules)]
    front = sorted({key(r): r for r in front}.values(), key=lambda r: key(r)[0])
    L += ["", "## Pareto front on core LOO only (harmful cells against mean change; no rule beats these on both)", "",
          "| min_gain | min_win | every set better | core harmful | core mean change | external harmful | external mean change |", "|---:|---:|:---:|---:|---:|---:|---:|"]
    for r in front:
        t = table[r]
        L.append(f"| {100 * r[0]:.0f}% | {100 * r[1]:.0f}% | {'yes' if r[2] else 'no'} | {t['core']['harmful']} | {100 * t['core']['mean_change']:+.2f}% | "
                 f"{t['external']['harmful']} | {100 * t['external']['mean_change']:+.2f}% |")
    # the known harmful external cells under the headline rule and what each rule does to them
    harm_cells = [c for c in base["external"]["detail"] if c["fix"] != "none" and c["change"] > HARM]
    L += ["", "## External cells that are harmful under the headline rule", "",
          "| model | dataset | fault | headline fix | change | " + " | ".join(f"{100*g:.0f}/{100*w:.0f}{'+all' if al else ''}" for g, w, al in
                                                                       [(0.05, 0.8, False), (0.10, 0.8, False), (0.02, 0.9, False), (0.02, 0.6, True), (0.05, 0.7, True)]) + " |",
          "|---|---|---|---|---:|" + "---:|" * 5]
    probes = [(0.05, 0.8, False), (0.10, 0.8, False), (0.02, 0.9, False), (0.02, 0.6, True), (0.05, 0.7, True)]
    for c in harm_cells:
        cols = []
        for p in probes:
            m = [x for x in table[p]["external"]["detail"] if (x["model"], x["dataset"], x["fault"]) == (c["model"], c["dataset"], c["fault"])]
            cols.append("none" if m and m[0]["fix"] == "none" else (f"{m[0]['fix']} {100 * m[0]['change']:+.1f}%" if m else "n/a"))
        L.append(f"| {c['model']} | {c['dataset']} | {c['fault']} | {c['fix']} | {100 * c['change']:+.1f}% | " + " | ".join(cols) + " |")
    # per-model view for the headline rule and the strictest consistent rule
    for name, r in (("headline", HEADLINE), ("5% / 80% / every set better", (0.05, 0.8, True))):
        L += ["", f"## Per model, {name}", "", "| model | core applied | core harmful | core mean | external applied | external harmful | external mean |", "|---|---:|---:|---:|---:|---:|---:|"]
        for m in sorted(data):
            row = []
            for part in ("core", "external"):
                cs = [c for c in table[r][part]["detail"] if c["model"] == m]
                ap_ = [c for c in cs if c["fix"] != "none"]
                row += [str(len(ap_)), str(sum(c["change"] > HARM for c in ap_)), f"{100 * np.mean([c['change'] for c in cs]):+.2f}%" if cs else "n/a"]
            L.append(f"| {m} | " + " | ".join(row) + " |")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "THRESHOLDS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "thresholds.json").write_text(json.dumps({f"{g}|{w}|{int(al)}": {p: {k: v for k, v in t[p].items() if k != "detail"} for p in t}
                                                      for (g, w, al), t in table.items()}), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
