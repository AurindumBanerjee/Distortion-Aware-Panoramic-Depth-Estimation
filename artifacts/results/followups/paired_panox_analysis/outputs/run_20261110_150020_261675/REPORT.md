# Experiment 08 — Direct paired PanoX significance audit

- Source: saved Experiment 04 per-scene results; no GPU inference is run.
- Methods: baseline, two-pole tangent, and 20-view icosahedral inference.
- Primary endpoint: 75–90° AbsRel; identical 200 scenes for each method.
- Bootstrap unit: PanoX environment (8 clusters), not individual panoramas.
- Positive gain means the candidate has lower AbsRel than its reference.

| Protocol | Comparison | Median environment gain | 95% CI |
|---|---|---:|---:|
| align-all | two pole vs baseline | +46.29% | [+12.06%, +53.80%] |
| align-all | 20 view vs baseline | +56.81% | [+25.92%, +62.99%] |
| align-all | 20 view vs two pole | +15.55% | [-84.48%, +34.05%] |
| align-equatorial | two pole vs baseline | +41.12% | [+22.17%, +55.24%] |
| align-equatorial | 20 view vs baseline | +51.77% | [+12.49%, +54.53%] |
| align-equatorial | 20 view vs two pole | -13.37% | [-69.33%, +18.00%] |

## Interpretation

A 20-view advantage over two-pole tangent is supported only if the direct 20-view-vs-two-pole interval excludes zero. Showing that both beat baseline does not establish which correction is better.

Only eight environment clusters are available. Treat this interval as uncertainty over these PanoX environments, not as a universal population guarantee.
