
#!/usr/bin/env python3
"""Direct paired statistical comparison of Experiment 04 methods; no GPU required."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_INPUT = (
    ROOT / "followup_experiments/04_mono360_20view/outputs/"
    "run_20261105_195950/per_scene.csv"
)


def paired_cluster_bootstrap_gain(
    reference: dict[str, float],
    candidate: dict[str, float],
    groups: dict[str, str],
    *,
    n_boot: int = 10000,
    seed: int = 0,
) -> dict:
    """Equal-weight bootstrap of environment-level means; positive = candidate better."""
    ids = sorted(set(reference) & set(candidate))
    by_group: dict[str, list[float]] = {}
    for sid in ids:
        ref, cand = reference[sid], candidate[sid]
        if np.isfinite(ref) and np.isfinite(cand) and ref > 0:
            by_group.setdefault(groups[sid], []).append((ref - cand) / ref)
    if len(by_group) < 4:
        raise RuntimeError(f"Expected at least 4 environments; found {len(by_group)}.")
    cluster_effects = np.asarray(
        [np.mean(v) for _, v in sorted(by_group.items())], dtype=np.float64
    )
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(cluster_effects), size=(n_boot, len(cluster_effects)))
    boot = np.median(cluster_effects[draw], axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {
        "n_scenes": len(ids),
        "n_environments": len(cluster_effects),
        "median_environment_gain": float(np.median(cluster_effects)),
        "ci95": [float(lo), float(hi)],
        "ci_excludes_zero": bool(lo > 0 or hi < 0),
        "interpretation": "positive = candidate reduces AbsRel vs reference",
        "bootstrap_replicates": n_boot,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output-dir", type=Path, default=HERE / "outputs")
    ap.add_argument("--bootstrap", type=int, default=10000)
    args = ap.parse_args()

    source = args.input if args.input.is_absolute() else ROOT / args.input
    if not source.is_file():
        raise SystemExit(f"Experiment 04 per_scene.csv not found: {source}")

    values: dict[tuple[str, str, str], float] = {}
    groups: dict[str, str] = {}
    with source.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["band"] != "75-90":
                continue
            sid, protocol, method = row["scene"], row["protocol"], row["method"]
            key = (protocol, method, sid)
            if key in values:
                raise RuntimeError(f"Duplicate result row: {key}")
            values[key] = float(row["abs_rel"])
            group = row["environment"]
            if sid in groups and groups[sid] != group:
                raise RuntimeError(f"Scene {sid} assigned to multiple environments.")
            groups[sid] = group

    methods = ("baseline", "two_pole_tangent", "mono360_20view")
    protocols = ("align-all", "align-equatorial")
    expected_scenes = 200
    expected_environments = 8
    summary: dict = {}
    report_rows: list[dict] = []

    for p_idx, protocol in enumerate(protocols):
        maps = {
            method: {
                sid: value
                for (p, m, sid), value in values.items()
                if p == protocol and m == method
            }
            for method in methods
        }
        sizes = {method: len(mapping) for method, mapping in maps.items()}
        if any(n != expected_scenes for n in sizes.values()):
            raise RuntimeError(
                f"{protocol}: expected {expected_scenes} paired scenes per method; got {sizes}. "
                "Do not silently compare unmatched scene sets."
            )
        scene_sets = [set(maps[method]) for method in methods]
        if not (scene_sets[0] == scene_sets[1] == scene_sets[2]):
            raise RuntimeError(f"{protocol}: scene IDs differ across methods.")
        active_groups = {sid: groups[sid] for sid in scene_sets[0]}
        n_groups = len(set(active_groups.values()))
        if n_groups != expected_environments:
            raise RuntimeError(
                f"{protocol}: expected {expected_environments} PanoX environments; got {n_groups}."
            )

        paired = {
            "two_pole_vs_baseline": paired_cluster_bootstrap_gain(
                maps["baseline"], maps["two_pole_tangent"], active_groups,
                n_boot=args.bootstrap, seed=101 + p_idx,
            ),
            "20_view_vs_baseline": paired_cluster_bootstrap_gain(
                maps["baseline"], maps["mono360_20view"], active_groups,
                n_boot=args.bootstrap, seed=201 + p_idx,
            ),
            "20_view_vs_two_pole": paired_cluster_bootstrap_gain(
                maps["two_pole_tangent"], maps["mono360_20view"], active_groups,
                n_boot=args.bootstrap, seed=301 + p_idx,
            ),
        }
        summary[protocol] = {
            "n_scenes": expected_scenes,
            "n_environments": expected_environments,
            "median_abs_rel": {
                method: float(np.median(list(maps[method].values())))
                for method in methods
            },
            "paired_cluster_bootstrap_gain": paired,
        }
        for comparison, result in paired.items():
            report_rows.append({
                "protocol": protocol,
                "comparison": comparison,
                "n_scenes": result["n_scenes"],
                "n_environments": result["n_environments"],
                "median_environment_gain_pct": 100 * result["median_environment_gain"],
                "ci95_low_pct": 100 * result["ci95"][0],
                "ci95_high_pct": 100 * result["ci95"][1],
                "ci_excludes_zero": result["ci_excludes_zero"],
            })

    try:
        source_label = source.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        source_label = source.name

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_base = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out = output_base / f"run_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    (out / "summary.json").write_text(json.dumps({
        "experiment": "08_paired_panox_analysis",
        "source_csv": source_label,
        "source_run": "Experiment 04 run_20261105_195950",
        "summary": summary,
        "note": "Reanalysis only; no new model inference. PanoX environment is the bootstrap unit."
    }, indent=2), encoding="utf-8")
    with (out / "pairwise.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(report_rows[0]))
        writer.writeheader()
        writer.writerows(report_rows)

    lines = [
        "# Experiment 08 — Direct paired PanoX significance audit",
        "",
        "- Source: saved Experiment 04 per-scene results; no GPU inference is run.",
        "- Methods: baseline, two-pole tangent, and 20-view icosahedral inference.",
        "- Primary endpoint: 75–90° AbsRel; identical 200 scenes for each method.",
        "- Bootstrap unit: PanoX environment (8 clusters), not individual panoramas.",
        "- Positive gain means the candidate has lower AbsRel than its reference.",
        "",
        "| Protocol | Comparison | Median environment gain | 95% CI |",
        "|---|---|---:|---:|",
    ]
    for row in report_rows:
        lines.append(
            f"| {row['protocol']} | {row['comparison'].replace('_', ' ')} | "
            f"{row['median_environment_gain_pct']:+.2f}% | "
            f"[{row['ci95_low_pct']:+.2f}%, {row['ci95_high_pct']:+.2f}%] |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "A 20-view advantage over two-pole tangent is supported only if the direct "
        "20-view-vs-two-pole interval excludes zero. Showing that both beat baseline "
        "does not establish which correction is better.",
        "",
        "Only eight environment clusters are available. Treat this interval as uncertainty "
        "over these PanoX environments, not as a universal population guarantee.",
        "",
    ]
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out}")
    print(f"Report: {out / 'REPORT.md'}")


if __name__ == "__main__":
    main()