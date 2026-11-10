# Follow-up Experiments 07–08: Results and Interpretation Draft

**Status:** Research draft for review. This does not modify the main LaTeX report or compiled PDF.

## Experiment 07 — Real NYC 20-view evaluation

### Protocol and coverage

The run evaluated 182 NYC panorama scenes using frozen MiDaS DPT-Hybrid 384 inference on a 512 × 1024 evaluation grid. It compared baseline, two-pole tangent, and 20-view protocols under align-all and align-equatorial evaluation. All 182/182 scenes completed. The output contains 7,644 per-scene records (182 scenes × 2 protocols × 3 methods × 7 bands), with 10,000 bootstrap replicates.

Sampling used 91 assumed 20-ID clusters, with two panorama IDs per block (offsets 4 and 14). These groupings are an analysis assumption, not verified route/session clusters unless source metadata confirms that interpretation.

### Main results

Median AbsRel:

| Evaluation | Band | Baseline | Two-pole | 20-view |
|---|---|---:|---:|---:|
| Align-all | All | 0.3700 | 0.3741 | 0.3037 |
| Align-all | 75–90° | 0.5113 | 0.4720 | 0.2832 |
| Align-equatorial | All | 0.3955 | 0.3957 | 0.3485 |
| Align-equatorial | 75–90° | 0.6106 | 0.5589 | 0.3594 |

Paired cluster-bootstrap relative AbsRel reduction for 20-view over two-pole (positive favours 20-view):

| Evaluation | Region | Reduction | 95% interval |
|---|---|---:|---:|
| Align-all | All | 28.48% | [15.62%, 32.47%] |
| Align-all | 60–75° | 27.65% | [21.76%, 36.17%] |
| Align-all | 75–90° | 38.85% | [33.56%, 40.86%] |
| Align-equatorial | All | 12.51% | [3.47%, 22.11%] |
| Align-equatorial | 60–75° | 29.96% | [17.29%, 35.45%] |
| Align-equatorial | 75–90° | 35.46% | [31.44%, 40.81%] |

Polar-band scene win rates for 20-view versus two-pole were 89.6% (align-all) and 82.4% (align-equatorial). At the assumed cluster level, 79/91 and 75/91 clusters respectively had positive differences.

### Overlap sensitivity

Fifteen sampled panorama IDs overlap with the 147-frame NYC set used in Aurindum's results. A post-hoc sensitivity analysis excluding these frames left 167 frames across 90 assumed clusters. Results remained positive:

| Evaluation | Region | Reduction | 95% interval |
|---|---|---:|---:|
| Align-all | All | 28.36% | [16.17%, 32.64%] |
| Align-all | 75–90° | 38.78% | [32.48%, 41.34%] |
| Align-equatorial | All | 12.01% | [3.65%, 22.28%] |
| Align-equatorial | 75–90° | 35.42% | [31.44%, 41.66%] |

This suggests the NYC effect is not driven solely by the identified overlapping frames. It remains a post-hoc analysis on the same NYC collection and is not independent dataset, route, or session replication.

### Computational cost

Median per-image runtime was approximately 0.31 s for baseline, 0.46 s for two-pole tangent, and 7.20 s for 20-view. Thus, 20-view was approximately 15.5× slower than two-pole. Accuracy gains should be discussed alongside this substantial inference-time cost.

### Interpretation

On this NYC subset, 20-view correction reduced median AbsRel relative to two-pole tangent, with paired bootstrap intervals above zero for the reported aggregate and polar-band comparisons. The effect was strongest in the 75–90° polar band. The overlap sensitivity analysis preserved the direction and magnitude of the result.

Present this as evidence on the evaluated NYC collection, not proof of generalization to unseen cities, routes, or sessions. The assumed 20-ID cluster definition needs metadata validation before being described as a true sampling cluster.

## Experiment 08 — Paired PanoX statistical audit

Experiment 08 compared 20-view against two-pole on eight PanoX environments. The direct intervals include zero:

| Evaluation | Relative reduction | 95% interval |
|---|---:|---:|
| Align-all | 15.55% | [−84.48%, 34.05%] |
| Align-equatorial | −13.37% | [−69.33%, 18.00%] |

With only eight environment clusters, intervals are very wide. This audit does not establish a direct 20-view advantage on PanoX. The negative align-equatorial point estimate is too uncertain to support a reliable claim that 20-view is worse.

## Joint interpretation and reporting recommendations

1. Present Experiment 07 as a promising, statistically supported result on the evaluated NYC subset, with explicit qualifications about collection-level generalization and assumed cluster structure.
2. Present Experiment 08 as an inconclusive cross-dataset audit, not confirmation of the NYC result.
3. Report runtime alongside accuracy.
4. Label the overlap analysis as post hoc.
5. Do not pool NYC and PanoX into one headline estimate; their sampling structures and uncertainty differ.
6. Stronger generalization claims require a larger independent dataset and verified route/session grouping.

## Reproducibility record

- Experiment 07 run: `run_20261110_102032_346055`
- Experiment 07 log: `run_20261110_101926.log`
- Experiment 08 latest run: `run_20261110_150020_261675`
- Experiment 07 outputs: `artifacts/results/followups/real_nyc_20view/outputs/`
- Experiment 08 outputs: `artifacts/results/followups/paired_panox_analysis/outputs/`

This synthesis is based on recorded run summaries and analyses. Before publication, reconcile all values against the machine-readable summaries and verify cluster construction from source metadata.
