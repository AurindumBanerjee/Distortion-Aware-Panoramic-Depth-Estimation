#!/usr/bin/env python3
"""Report on the EXTERNAL datasets (Stanford2D3D, NYC), kept apart from the core results.

External sets are never used to choose or tune anything: the fix per (model, fault) comes from the four core datasets
(scripts/calibrate_correction.py, CORE_SETS), so these numbers are a pure test of the finished policy.
Reads results/study_<model>_{stanford,nyc}.json (fault costs) and results/external/correction_<model>_<set>.json
(end-to-end pipeline); writes results/EXTERNAL_stanford_nyc.md. Nothing in results/ for the core sets is read or written.

  python scripts/external_report.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MODELS = ("midas", "dap", "da360", "da2")
EXTERNAL = ("stanford", "nyc")
FAULTS = ("tilt", "nadir", "vfov", "yawblur", "jpeg", "noise", "lowres")
REGION_SCEN = ("nadir", "vfov", "nadir+jpeg")


def med(x):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    return float(np.median(x)) if len(x) else float("nan")


def f4(v):
    return "–" if not np.isfinite(v) else f"{v:.4f}"


def main():
    res = ROOT / "results"
    lines = ["# External datasets: Stanford2D3D and NYC", "",
             "Run, analysed and reported independently of the core datasets (Structured3D, PanoX, Holo360D). Nothing here "
             "was used to choose or tune a fix: the policy comes from the four core datasets only.", ""]
    found = False
    for ds in EXTERNAL:
        lines += [f"## {ds}", ""]
        # ---- fault costs (study) ----
        tab = {}
        for m in MODELS:
            p = res / f"study_{m}_{ds}.json"
            if not p.is_file():
                continue
            rows = json.loads(p.read_text())["rows"]
            tab[m] = rows
        if tab:
            found = True
            lines += [f"**What each fault costs** (median AbsRel on the whole panorama, clean -> faulty; {len(next(iter(tab.values())))} frames)", "",
                      "| model | clean | " + " | ".join(FAULTS) + " |", "|---|---:|" + "---:|" * len(FAULTS)]
            for m, rows in tab.items():
                cells = []
                for fa in FAULTS:
                    c = med([r.get(f"{fa}|clean", {}).get("all") for r in rows])
                    n = med([r.get(f"{fa}|none", {}).get("all") for r in rows])
                    cells.append(f"{c:.3f} -> {n:.3f}" if np.isfinite(n) else "–")
                lines.append(f"| {m} | {f4(med([r['clean']['all'] for r in rows]))} | " + " | ".join(cells) + " |")
            if ds == "stanford":
                lines += ["", "*Stanford frames are already black above |lat| 65 deg (limited vertical FOV), so the simulated "
                          "`nadir` / `vfov` faults mostly fall inside real occlusion and are not a meaningful fault test here.*"]
            lines.append("")
        else:
            lines += [f"(no study_<model>_{ds}.json yet)", ""]
        # ---- end-to-end correction ----
        cor = {}
        for m in MODELS:
            p = res / "external" / f"correction_{m}_{ds}.json"
            if p.is_file():
                cor[m] = json.loads(p.read_text())
        if not cor:
            lines += [f"(no results/external/correction_<model>_{ds}.json yet)", ""]
            continue
        found = True
        lines += ["**End-to-end correction** (fixes detected and chosen as in deployment; policy learned on the core sets). "
                  "Metric: affected region for cap faults, whole panorama otherwise. change = median per-frame change in error "
                  "vs uncorrected; better / worse = share of frames improved / worse by >1%.", "",
                  "| model | scenario | uncorrected | corrected | change | better | worse | policy |", "|---|---|---:|---:|---:|---:|---:|---|"]
        for m, d in cor.items():
            rows = d["rows"]
            for scen in rows[0]:
                if scen == "id":
                    continue
                f = "region" if scen in REGION_SCEN else "all"
                u = np.array([r[scen]["raw"][f] for r in rows], float)
                x = np.array([r[scen]["fixed"][f] for r in rows], float)
                ok = np.isfinite(u) & np.isfinite(x) & (u > 0)
                u, x = u[ok], x[ok]
                if not len(u):
                    continue
                lines.append(f"| {m} | {scen} | {np.median(u):.4f} | {np.median(x):.4f} | {100 * np.median((x - u) / u):+.1f}% | "
                             f"{100 * np.mean(x < u * 0.999):.0f}% | {100 * np.mean(x > u * 1.01):.0f}% | "
                             f"{', '.join(f'{k}:{v}' for k, v in d['policy'].items()) or 'none'} |")
        if ds == "stanford":
            lines += ["", "*The `clean` row is the real-occlusion test: Stanford's own black caps are detected and filled "
                      "(whole-panorama error; detection rate is not meaningful there because every frame has caps).*"]
        lines.append("")
    if not found:
        sys.exit("no external results yet (results/study_<model>_{stanford,nyc}.json)")
    (res / "EXTERNAL_stanford_nyc.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
