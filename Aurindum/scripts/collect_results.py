"""Collect every series' result JSON into one markdown summary.

    python scripts/collect_results.py [--out results/SUMMARY_<timestamp>.md]

Reads 1_*/outputs*/metrics_summary.json, 2_*/outputs*/metrics_summary.json and
3_*/outputs*/benchmark_summary.json (one folder per config: outputs, outputs_dap, outputs_panox, ...)
and writes, per run and protocol, the median table with win rate, gain [95% CI] and Wilcoxon p.
"""
import argparse
import datetime
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evaluation.protocol import format_band_table, format_table  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=None)
a = ap.parse_args()
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out = a.out or os.path.join(ROOT, "results", f"SUMMARY_{ts}.md")
os.makedirs(os.path.dirname(out), exist_ok=True)

files = sorted(glob.glob(os.path.join(ROOT, "[123]_*", "outputs*", "*_summary.json")))
lines = [f"# Experiment summary ({ts})", "",
         "Median over scenes. `win` = share of scenes beating the baseline at 75-90°, `gain` = median relative "
         "AbsRel reduction with 95% bootstrap CI, `p` = paired two-sided Wilcoxon. Claim a gain only if the CI "
         "excludes 0 and p < 0.05 under both protocols, with 0-30° not worse.", ""]
for f in files:
    try:
        rec = json.load(open(f))
    except Exception as e:  # noqa: BLE001
        lines += [f"## {os.path.relpath(f, ROOT)}", f"(unreadable: {e})", ""]
        continue
    summ = rec.get("summary")
    rel = os.path.relpath(f, ROOT)
    if not summ:
        lines += [f"## {rel}", "(old format without paired statistics: produced before the v2 fixes; ignore)", ""]
        continue
    cfg = rec.get("config", {})
    model = cfg.get("model", {}).get("name", "?")
    bench = rec.get("benchmark", "?")
    n = rec.get("num_scenes") or len(next(iter(rec.get("per_scene", {}).values()), []))
    lines += [f"## {rel}", f"model `{model}` · benchmark `{bench}` · {n} scenes · {rec.get('timestamp', '')}", ""]
    for proto, table in summ.items():
        lines += [f"**Protocol `{proto}`**", "", "```"] + format_table(table, "median") + ["```", ""]
        for name in table:
            if name != "Baseline":
                lines += [f"<details><summary>{name}: per band ({proto})</summary>", "", "```"]
                lines += format_band_table(table, name) + ["```", "</details>", ""]
open(out, "w", encoding="utf-8").write("\n".join(lines))
print(f"Wrote {out} ({len(files)} result files)")
