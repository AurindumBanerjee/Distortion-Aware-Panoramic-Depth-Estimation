# Experiment 08 — Direct paired PanoX significance audit

## Purpose

Experiment 04 showed that the 20-view method had a lower median 75–90 degree AbsRel than two-pole tangent on PanoX, but its saved confidence intervals compared each method with baseline. They did not test the direct 20-view-vs-two-pole difference.

This script closes that reporting gap using the saved Experiment 04 per-scene metrics. It does not run a model, need a GPU, modify the source results, or tune any method.

## Run

From the Lokesh/ directory:

    python followup_experiments/08_paired_panox_analysis/analyze_panox.py

The default input is the selected Experiment 04 run:

    followup_experiments/04_mono360_20view/outputs/run_20261105_195950/per_scene.csv

To analyze a different compatible per-scene CSV:

    python followup_experiments/08_paired_panox_analysis/analyze_panox.py --input path/to/per_scene.csv

The script fails if it does not find the same 200 scene IDs for all three methods or the eight expected PanoX environment clusters.

## Statistics

Primary endpoint: 75–90 degree AbsRel. Both align-all and align-equatorial are analyzed.

For each comparison, frame-level relative gains are paired by scene, averaged within each PanoX environment, and the eight environment effects are resampled as clusters. The reported point estimate is the median environment effect; the interval is a 10,000-replicate percentile cluster bootstrap interval.

Positive gain means the candidate has lower error than its reference. The key comparison is 20_view_vs_two_pole.

Only eight environments are available, so this is an uncertainty estimate over the eight observed PanoX groups, not a universal guarantee. A confidence interval that includes zero means the direct comparison is inconclusive, even if both methods individually improve on baseline.

## Outputs

A fresh timestamped folder is created under outputs/ with:

- REPORT.md: direct paired comparisons and intervals.
- pairwise.csv: machine-readable rows.
- summary.json: source identity and full bootstrap results.

This is an analysis-only audit. It is not new inference evidence and must be described as a reanalysis of Experiment 04.
