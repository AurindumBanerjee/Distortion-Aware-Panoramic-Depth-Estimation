# Experiment 1 — DA360 scale-only evaluation protocol

- Scenes: 200
- Model: da360
- Primary comparison: scale-only disparity fit vs affine disparity fit
- Protocols: align-all, align-equatorial
- Positive bootstrap gain means scale-only has lower AbsRel than affine.

## align-all

| Band | Scale-only median | Affine median | Scale-only vs affine gain (95% CI) |
|---|---:|---:|---:|
| all | 0.0127 | 0.0130 | +0.06% [-0.18%, +1.04%] |
| 45-60 | 0.0100 | 0.0097 | -0.55% [-2.23%, -0.00%] |
| 60-75 | 0.0079 | 0.0076 | -2.10% [-4.98%, -0.14%] |
| 75-90 | 0.0056 | 0.0054 | -0.45% [-6.27%, +1.85%] |

## align-equatorial

| Band | Scale-only median | Affine median | Scale-only vs affine gain (95% CI) |
|---|---:|---:|---:|
| all | 0.0140 | 0.0148 | +2.63% [+0.10%, +5.74%] |
| 45-60 | 0.0112 | 0.0130 | +2.64% [+0.07%, +5.34%] |
| 60-75 | 0.0093 | 0.0112 | +4.51% [+0.02%, +13.14%] |
| 75-90 | 0.0070 | 0.0095 | +5.74% [+0.27%, +17.95%] |

## Interpretation guardrails

DA360 describes its prediction as scale-invariant disparity. The scale-only fit is therefore the
methodologically preferred headline protocol; affine fitting is retained as a sensitivity analysis.
This script does not alter model predictions or fit alignment separately by latitude band.
The same scenes and validity masks are used in paired comparisons.

Raw per-scene metrics are in per_scene.csv; the complete record is summary.json.
