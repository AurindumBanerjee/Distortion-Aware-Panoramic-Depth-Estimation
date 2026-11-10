# Experiment 07 — Real NYC transfer: two-pole vs 20-view inference

- Scenes: **182**; assumed 20-ID clusters: **91**.
- Model: frozen **midas_dpt_hybrid_384**; evaluation grid: 512 x 1024.
- GT range: 0.5–1000 m; both alignment protocols reported.
- Pilot only: **False**. Pilot intervals must not be treated as evaluation evidence.
- IDs 0–74 are excluded because they were used in Lokesh's earlier NYC run.
- The 20-ID cluster is an assumed grouping, not a verified route/session identifier.

Positive bootstrap gain means the candidate has lower AbsRel than its reference.
The direct 20-view vs two-pole comparison is paired by scene and bootstrapped by 20-ID cluster.

## align-all

| Method | All median AbsRel | 60–75° median | 75–90° median | Views / image |
|---|---:|---:|---:|---:|
| baseline | 0.3700 | 0.3986 | 0.5113 | 1 |
| two_pole_tangent | 0.3741 | 0.3923 | 0.4720 | 3 |
| mono360_20view | 0.3037 | 0.2863 | 0.2832 | 20 |

### Paired cluster-bootstrap gains

| Band | Comparison | Median gain | 95% CI |
|---|---|---:|---:|
| all | two pole vs baseline | +3.39% | [+0.68%, +4.28%] |
| all | 20 view vs baseline | +30.38% | [+22.05%, +34.98%] |
| all | 20 view vs two pole | +28.48% | [+15.62%, +32.47%] |
| 60-75 | two pole vs baseline | +0.51% | [-1.06%, +1.89%] |
| 60-75 | 20 view vs baseline | +33.08% | [+22.15%, +41.01%] |
| 60-75 | 20 view vs two pole | +27.65% | [+21.76%, +36.17%] |
| 75-90 | two pole vs baseline | +7.57% | [+6.71%, +9.23%] |
| 75-90 | 20 view vs baseline | +44.91% | [+41.43%, +47.26%] |
| 75-90 | 20 view vs two pole | +38.85% | [+33.56%, +40.86%] |

## align-equatorial

| Method | All median AbsRel | 60–75° median | 75–90° median | Views / image |
|---|---:|---:|---:|---:|
| baseline | 0.3955 | 0.5161 | 0.6106 | 1 |
| two_pole_tangent | 0.3957 | 0.4860 | 0.5589 | 3 |
| mono360_20view | 0.3485 | 0.3673 | 0.3594 | 20 |

### Paired cluster-bootstrap gains

| Band | Comparison | Median gain | 95% CI |
|---|---|---:|---:|
| all | two pole vs baseline | +2.50% | [+1.17%, +3.59%] |
| all | 20 view vs baseline | +16.89% | [+8.28%, +23.95%] |
| all | 20 view vs two pole | +12.51% | [+3.47%, +22.11%] |
| 60-75 | two pole vs baseline | +4.04% | [-0.52%, +5.86%] |
| 60-75 | 20 view vs baseline | +31.82% | [+19.29%, +36.32%] |
| 60-75 | 20 view vs two pole | +29.96% | [+17.29%, +35.45%] |
| 75-90 | two pole vs baseline | +8.26% | [+6.95%, +9.77%] |
| 75-90 | 20 view vs baseline | +41.25% | [+35.99%, +44.49%] |
| 75-90 | 20 view vs two pole | +35.46% | [+31.44%, +40.81%] |

## Runtime

| Method | Median seconds / panorama |
|---|---:|
| Baseline | 0.31 |
| Two-pole tangent | 0.46 |
| 20-view | 7.20 |

## Interpretation guardrails

- Do not tune FOV, padding, alignment or fusion on this evaluation subset.
- A 20-view win is supported only when the direct paired 20-view-vs-two-pole interval excludes zero.
- If the interval includes zero, prefer the lower-call method unless another prespecified metric supports the cost.
- Do not interpret the 20-ID blocks as verified routes; they are an assumed grouping.
- This is a held-out frame subset relative to Lokesh's previous 75-frame run, not a new dataset release.
