#!/usr/bin/env python3
"""Sweep numbers quoted in the report, recomputed from results/sweep_<mode>_<model>_<set>.json.
Per (mode, model, set): onset (global / local), 75-90 deg mean dE and ratio (global), local dE at 77.5 / 87.5 deg,
local ratio at 82.5 deg and its maximum, log magnification at 77.5 / 87.5 deg. Prints markdown to stdout.

  python scripts/sweep_numbers.py > results/SWEEP_NUMBERS.md
"""
import json
from pathlib import Path

import numpy as np

RES = Path(__file__).resolve().parent.parent / "results"
SETS = ("s3_eval", "panox_all", "holo_in_all", "holo_out_all", "nyc_all")
MODELS = ("midas", "dap", "da360", "da2")


def at(s, key, c, field="mean"):
    cs = np.array(s["centres"]); i = int(np.argmin(np.abs(cs - c)))
    return float(np.array(s[key][field] if isinstance(s[key], dict) else s[key], float)[i])


def main():
    print("# Sweep numbers (recomputed)\n")
    print("dE75-90 = mean over bins >= 75 deg of the global excess error; ratio = mean global ratio there; onset in degrees (None = no onset). "
          "local dE and local ratio use the estimator that re-fits the scale per latitude bin.\n")
    for mode in ("rotation", "dilation", "flip"):
        print(f"## {mode}\n")
        print("| model | set | frames/clusters | onset global | onset local | dE 75-90 | ratio 75-90 | local dE 77.5 | local dE 87.5 | local ratio 82.5 | max local ratio | log mag 77.5 / 87.5 |")
        print("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for m in MODELS:
            for ds in SETS:
                p = RES / (f"sweep_{m}_{ds}.json" if mode == "rotation" and ds != "nyc_all" else f"sweep_{mode}_{m}_{ds}.json")
                if mode == "rotation" and ds == "nyc_all":
                    p = RES / f"sweep_rotation_{m}_{ds}.json"
                if mode == "rotation" and ds != "nyc_all":
                    p = RES / f"sweep_{m}_{ds}.json"
                if not p.is_file():
                    continue
                s = json.loads(p.read_text())["summary"]
                c = np.array(s["centres"]); j = c >= 75
                de = float(np.nanmean(np.array(s["de_global"]["mean"], float)[j]))
                ra = float(np.nanmean(np.array(s["ratio_global"], float)[j]))
                rl = np.array(s["ratio_local"], float)
                lm = s.get("log_mag", {}).get("mean")
                lms = f"{at(s, 'log_mag', 77.5):+.2f} / {at(s, 'log_mag', 87.5):+.2f}" if lm else "–"
                print(f"| {m} | {ds} | {s['n_frames']}/{s['n_clusters']} | {s['onset_global']} | {s['onset_local']} | {de:.3f} | {ra:.2f} | "
                      f"{at(s, 'de_local', 77.5):+.3f} | {at(s, 'de_local', 87.5):+.3f} | {at(s, 'ratio_local', 82.5):.2f} | {np.nanmax(rl):.2f} | {lms} |")
        print()


if __name__ == "__main__":
    main()
