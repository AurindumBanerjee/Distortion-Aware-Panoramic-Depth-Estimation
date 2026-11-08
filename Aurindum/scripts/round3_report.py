#!/usr/bin/env python3
"""Collect the round-3 Part A outputs (results/SWEEP_*.json, results/profile_*.json) into results/ROUND3_ANALYSIS.md:
one row per model x dataset with the causal onset (sweep), the descriptive onset (profile, per protocol), the polar
excess dE at 75-90 deg and the error ratio there. Part B statistics come from scripts/collect_results.py."""
import glob
import json
import os
import warnings

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)  # empty bins (e.g. no non-planar cap pixels) -> n/a
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "results", "ROUND3_ANALYSIS.md")
lines = ["# Round 3, Part A: distortion analysis", "",
         "Causal onset: first seen-latitude bin (sweep, content fixed per pixel) whose excess error is significant "
         "(cluster CI) and >= 10% of the equator-seen error. `None` = no measurable distortion effect: Part B then leaves "
         "this model unchanged.", "",
         "Modes: rotation (tips the scene), dilation (keeps up, magnifies), flip (same latitude upside down: dE is the "
         "orientation penalty). A distortion effect should appear in BOTH rotation and dilation; an orientation effect makes "
         "rotation dE negative, dilation ~0 and flip dE positive.", "",
         "| sweep tag | mode | model | frames / clusters | onset (deg) | onset non-planar | dE 75-90 [95% CI] | ratio 75-90 | dE 75-90 planar / non-planar |",
         "|---|---|---|---:|---:|---:|---:|---:|---:|"]
f = lambda v: "n/a" if v is None or not np.isfinite(v) else f"{v:.4f}"
for p in sorted(glob.glob(os.path.join(ROOT, "results", "sweep_*.json"))):
    r = json.load(open(p))
    s = r["summary"]
    c = np.array(s["centres"])
    j = c >= 75
    de = s["de_global"]
    m = float(np.nanmean(np.array(de["mean"], float)[j]))
    lo = float(np.nanmean(np.array(de["ci_lo"], float)[j]))
    hi = float(np.nanmean(np.array(de["ci_hi"], float)[j]))
    ratio = float(np.nanmean(np.array(s["ratio_global"], float)[j]))
    pl = "n/a"
    if "de_global_planar" in s:
        pl = f"{f(float(np.nanmean(np.array(s['de_global_planar']['mean'], float)[j])))} / " \
             f"{f(float(np.nanmean(np.array(s['de_global_nonplanar']['mean'], float)[j])))}"
    lines.append(f"| {r['tag']} | {s.get('mode', r.get('mode', 'rotation'))} | {r.get('model', '?')} | {s['n_frames']} / "
                 f"{s['n_clusters']} | {s['onset_global']} | {s.get('onset_nonplanar', 'n/a')} | "
                 f"{f(m)} [{f(lo)}, {f(hi)}] | {ratio:.2f} | {pl} |")
lines += ["", "Descriptive onset (plain ERP latitude profile; mixes distortion, content and protocol):", "",
          "| profile tag | model | protocol | onset (deg) | AbsRel 0-15 | AbsRel 75-90 |", "|---|---|---|---:|---:|---:|"]
for p in sorted(glob.glob(os.path.join(ROOT, "results", "profile_*.json"))):
    r = json.load(open(p))
    s = r["summary"]
    c = np.array(s["centres"])
    for proto, rec in s["protocols"].items():
        mm = np.array(rec["profile"]["mean"], float)
        lines.append(f"| {r['tag']} | {r.get('model', '?')} | {proto} | {rec['onset']} | {f(float(np.nanmean(mm[c < 15])))} | "
                     f"{f(float(np.nanmean(mm[c >= 75])))} |")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"wrote {out}")
