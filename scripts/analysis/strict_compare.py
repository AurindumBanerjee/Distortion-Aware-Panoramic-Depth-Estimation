#!/usr/bin/env python3
"""End-to-end test of the stricter do-no-harm rules (scripts/run_submission.sh stage `strict`) against the headline policy.

Reads results/external/correction_<m>_<set>.json (headline) and results/threshold_sweep/e2e_<rule>/correction_<m>_<set>.json (rule
`s<gain>w<win>` = min_gain %, min_win %; the policy is chosen on the four core sets only), matches frames by id and writes
results/threshold_sweep/E2E_STRICT.md: per rule, set and model the median change per scenario (headline / strict), then a
summary of harmful scenarios (median change above +1%) and the mean change over scenarios, headline vs strict.
"""
from __future__ import annotations


import numpy as np

from pano.paths import BENCHMARK_RESULTS
from scripts.analysis.final_summary import EXT, SCEN
from scripts.analysis.policy_e2e_compare import compare, load_rows
RES = BENCHMARK_RESULTS
TS = RES / "threshold_sweep"
MODELS = ("midas", "dap", "da360", "da2")


def summarize(pairs):
    """pairs: [(head cell, alt cell)] over (model, set, scenario) -> dict of harmful counts and mean change for both."""
    out = {}
    for name, idx in (("headline", 0), ("strict", 1)):
        ch = [p[idx]["chg"] for p in pairs if p[0] is not None and p[1] is not None]
        out[name] = {"harmful": int(sum(c > 1.0 for c in ch)), "mean": float(np.mean(ch)) if ch else float("nan"), "n": len(ch)}
    return out


def main():
    fm = lambda c: "n/a" if c is None else f"{c['chg']:+.1f}%"
    rules = sorted(p.name[len("e2e_"):] for p in TS.glob("e2e_*") if p.is_dir())
    L = ["# End-to-end: stricter do-no-harm rules on the external sets", "",
         "Same frames (matched by id), same code; only the policy rule differs. Rule `s<G>w<W>`: a fix needs a median gain of G% and W% of training frames "
         "improved, chosen on the four core sets (Stanford2D3D and NYC never train). Cells: median per-frame change of AbsRel (headline / strict).", ""]
    if not rules:
        L.append("No strict-rule runs found.")
    for rule in rules:
        d = TS / f"e2e_{rule}"
        L += [f"## Rule {rule}", "", "| set | model | frames | policy differs in | " + " | ".join(SCEN[1:]) + " |", "|---|---|---:|---|" + "---|" * (len(SCEN) - 1)]
        pairs = []
        for ds in EXT:
            for m in MODELS:
                head, alt = load_rows(RES / "external" / f"correction_{m}_{ds}.json"), load_rows(d / f"correction_{m}_{ds}.json")
                if head is None or alt is None:
                    continue
                res, ph, pa, n = compare(head, alt)
                diff = ", ".join(f"{k}: {ph.get(k, 'none')}->{pa.get(k, 'none')}" for k in sorted(set(ph) | set(pa)) if ph.get(k) != pa.get(k)) or "-"
                L.append(f"| {ds} | {m} | {n} | {diff} | " + " | ".join(f"{fm(res[s][0])} / {fm(res[s][1])}" for s in SCEN[1:]) + " |")
                pairs += [(res[s][0], res[s][1]) for s in SCEN[1:]]
        s = summarize(pairs)
        L += ["", f"Over {s['headline']['n']} (model, set, scenario) cells: harmful scenarios {s['headline']['harmful']} (headline) vs {s['strict']['harmful']} (strict); "
              f"mean change {s['headline']['mean']:+.2f}% vs {s['strict']['mean']:+.2f}%.", ""]
    TS.mkdir(parents=True, exist_ok=True)
    (TS / "E2E_STRICT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
