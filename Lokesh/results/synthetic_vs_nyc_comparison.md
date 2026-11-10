# Synthetic vs NYC real-world comparison

**Model:** MiDaS DPT-Hybrid 384 (CPU)
**Alignment:** affine in disparity, reported as `align-all` and `align-equatorial`
**Samples:** 24 synthetic indoor panoramas; 75 NYC street panoramas from the DAP dataset.

This is a comparison of the same perspective relative-depth model across two different data domains. It is **not** a DAP-model evaluation. Depth ranges differ substantially, so cross-dataset comparisons focus on AbsRel and threshold metrics; SqRel, RMSE and MAE are not directly comparable in metres.

## Global AbsRel ? align-all

| Method | Synthetic | NYC |
|---|---:|---:|
| Baseline | 0.1630 | 0.3497 |
| Tangent | 0.1533 | 0.3393 |
| Rotation | 0.2031 | 0.3875 |
| Hybrid | **0.1512** | 0.3606 |

## Polar AbsRel (|latitude| ? 60?)

| Method | Synthetic align-all | NYC align-all | Synthetic align-equatorial | NYC align-equatorial |
|---|---:|---:|---:|---:|
| Baseline | 0.136 | 0.426 | 0.402 | 0.529 |
| Tangent | 0.129 | **0.407** | 0.356 | **0.482** |
| Rotation | 0.222 | 0.497 | 0.419 | 0.651 |
| Hybrid | **0.130** | 0.413 | **0.259** | **0.482** |

## Interpretation

- The synthetic hybrid result is strong under equatorial alignment, but its gains shrink on NYC. Under `align-all`, hybrid improves the synthetic global result but makes the NYC global result worse than baseline.
- Tangent inference is the safer modest improvement on NYC: its polar AbsRel is 0.407 vs 0.426 under `align-all`, and 0.482 vs 0.529 under `align-equatorial`.
- Rotation alone is harmful on the polar bands in both domains.
- The extreme 75?90? NYC band improves under the hybrid, but the benefit does not extend to the whole panorama under `align-all`.
- Alignment protocol changes the apparent size of the correction. Both should remain reported; do not present only the more favourable protocol.

## Source artifacts

- Synthetic run: `results/midas_dpt_hybrid_synthetic/`
- NYC run: `results/midas_dpt_hybrid_nyc/`
- Regenerated aggregate tables: `results/RESULT_TABLES.md`
- Core research narrative: `RESULTS.md`
