# Experiment 1 — DA360 scale-only evaluation protocol

- Scenes: 16
- Model: da360
- Primary comparison: scale-only disparity fit vs affine disparity fit
- Protocols: align-all, align-equatorial
- Positive bootstrap gain means scale-only has lower AbsRel than affine.

## align-all

| Band | Scale-only median | Affine median | Scale-only vs affine gain (95% CI) |
|---|---:|---:|---:|
| all | 0.0150 | 0.0149 | -0.44% [-2.25%, +2.69%] |
| 45-60 | 0.0118 | 0.0106 | -5.56% [-10.30%, +0.45%] |
| 60-75 | 0.0113 | 0.0101 | -6.20% [-23.88%, -0.93%] |
| 75-90 | 0.0077 | 0.0068 | -12.58% [-36.19%, -0.00%] |

## align-equatorial

| Band | Scale-only median | Affine median | Scale-only vs affine gain (95% CI) |
|---|---:|---:|---:|
| all | 0.0153 | 0.0175 | +1.37% [-13.49%, +17.95%] |
| 45-60 | 0.0140 | 0.0158 | +2.72% [-19.16%, +30.63%] |
| 60-75 | 0.0152 | 0.0161 | +2.63% [-27.34%, +32.83%] |
| 75-90 | 0.0099 | 0.0143 | -5.60% [-47.52%, +41.35%] |

## Interpretation guardrails

DA360 describes its prediction as scale-invariant disparity. The scale-only fit is therefore the
methodologically preferred headline protocol; affine fitting is retained as a sensitivity analysis.
This script does not alter model predictions or fit alignment separately by latitude band.
The same scenes and validity masks are used in paired comparisons.

Raw per-scene metrics are in per_scene.csv; the complete record is summary.json.
