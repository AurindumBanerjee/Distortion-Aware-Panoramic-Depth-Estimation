#!/usr/bin/env python3
"""DA2 under both alignment protocols (least squares = tag da2, median fit = tag da2m), side by side -> results/DA2_PROTOCOLS.md.

  1. Clean AbsRel per dataset under each protocol (matched frame ids).
  2. Correction per scenario: median per-frame change, both protocols, matched ids, with the share of frames improved / worse.
  3. Which fix the held-out policy chose per fault under each protocol, and the scenarios whose median change is worse than +1%.
  4. Rotation and dilation sweeps (onset, mean excess error at 75-90 deg, ratio) when sweep files exist for both tags.
Missing files are skipped. CPU only.
"""
from __future__ import annotations

import json

import numpy as np

from pano.paths import BENCHMARK_RESULTS
from scripts.analysis.final_summary import CORE, EXT, SCEN, cell, fmt

RES = BENCHMARK_RESULTS
PAIRS = (("lsq", "da2"), ("median", "da2m"))
SWEEP_SETS = ("s3_eval", "panox_all", "holo_in_all", "holo_out_all", "nyc_all")


def load_json(model_tag, ds):
    p = (RES if ds in CORE else RES / "external") / f"correction_{model_tag}_{ds}.json"
    return json.loads(p.read_text()) if p.is_file() else None


def matched(a, b):
    """Rows of both runs restricted to the frame ids they share, in the same order."""
    ids = [r["id"] for r in a["rows"] if r["id"] in {x["id"] for x in b["rows"]}]
    ia = {r["id"]: r for r in a["rows"]}
    ib = {r["id"]: r for r in b["rows"]}
    return [ia[i] for i in ids], [ib[i] for i in ids]


def clean_median(rows):
    v = np.array([r["clean"]["raw"]["all"] for r in rows], float)
    return float(np.nanmedian(v)) if len(v) else float("nan")


def harmful_cells(rows, policy=None, thr=1.0):
    """Scenarios whose median change is worse than +thr % (a fix, or a cap fix triggered by a real or simulated cap, hurt)."""
    out = []
    for sc in SCEN[1:]:
        if not rows or sc not in rows[0]:
            continue
        c = cell(rows, sc, n_boot=200)
        if c and c["chg"] > thr:
            out.append((sc, c["chg"]))
    return out


def sweep_row(path):
    if not path.is_file():
        return None
    s = json.loads(path.read_text())["summary"]
    c = np.array(s["centres"])
    j = c >= 75
    return {"onset": s["onset_global"], "de": float(np.nanmean(np.array(s["de_global"]["mean"], float)[j])),
            "ratio": float(np.nanmean(np.array(s["ratio_global"], float)[j])), "n": s["n_frames"]}


def sweep_path(mode, tag_model, ds):
    if mode == "rotation" and not ds.startswith("nyc"):
        a = RES / f"sweep_rotation_{tag_model}_{ds}.json"
        return a if a.is_file() else RES / f"sweep_{tag_model}_{ds}.json"
    return RES / f"sweep_{mode}_{tag_model}_{ds}.json"


def main():
    L = ["# DA2 under both alignment protocols", "",
         "`lsq`: least-squares scale fit (core protocol, tag `da2`). `median`: median scale fit (tag `da2m`; the policy is learned from "
         "`study_da2m_<core>.json` under the same protocol). All comparisons use the frame ids both runs contain.", ""]
    L += ["## 1. Clean AbsRel (median over frames)", "", "| dataset | frames | lsq | median |", "|---|---:|---:|---:|"]
    runs = {}
    for ds in CORE + EXT:
        a, b = load_json("da2", ds), load_json("da2m", ds)
        if a and b:
            ra, rb = matched(a, b)
            runs[ds] = (ra, rb, a.get("policy", {}), b.get("policy", {}))
            L.append(f"| {ds} | {len(ra)} | {clean_median(ra):.3f} | {clean_median(rb):.3f} |")
    L += ["", "## 2. Correction per scenario: median change [95% CI] (% improved / % worse)", ""]
    for ds, (ra, rb, pa, pb) in runs.items():
        L += [f"### {ds}", "", "| protocol | " + " | ".join(SCEN[1:]) + " |", "|---|" + "---|" * (len(SCEN) - 1)]
        for name, rows in (("lsq", ra), ("median", rb)):
            L.append(f"| {name} | " + " | ".join(fmt(cell(rows, s)) for s in SCEN[1:]) + " |")
        L.append("")
    L += ["## 3. Policy chosen per fault (held-out) and harmful cells", "",
          "| dataset | lsq policy | median policy | harmful under lsq | harmful under median |", "|---|---|---|---|---|"]
    for ds, (ra, rb, pa, pb) in runs.items():
        hl, hm = harmful_cells(ra, pa), harmful_cells(rb, pb)
        f = lambda h: ", ".join(f"{s} {c:+.1f}%" for s, c in h) or "none"
        L.append(f"| {ds} | `{json.dumps(pa)}` | `{json.dumps(pb)}` | {f(hl)} | {f(hm)} |")
    L += ["", "## 4. Sweeps (global estimator): onset, mean excess error 75-90 deg, ratio", "",
          "| mode | dataset | lsq onset | lsq dE | lsq ratio | median onset | median dE | median ratio |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for mode in ("rotation", "dilation", "flip"):
        for ds in SWEEP_SETS:
            a, b = sweep_row(sweep_path(mode, "da2", ds)), sweep_row(sweep_path(mode, "da2m", ds))
            if a and b:
                L.append(f"| {mode} | {ds} | {a['onset']} | {a['de']:.3f} | {a['ratio']:.2f} | {b['onset']} | {b['de']:.3f} | {b['ratio']:.2f} |")
    (RES / "DA2_PROTOCOLS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
