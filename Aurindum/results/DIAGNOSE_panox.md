# Re-anchor diagnostic: panox

68 rotated passes from 40 frames. Gains are relative AbsRel reductions on the polar cap (|lat| > 60 deg of the pole the pass targets); positive is better than the identity view.

| quantity | median |
|---|---:|
| intrinsic gain (oracle polar fit of both views) | -72.0% |
| realised gain (label-free re-anchor, global GT fit of identity) | -521.8% |
| anchor loss (realised error vs oracle error of the rotated view) | +2106.8% |
| anchor fit residual (fit_quality; 0 = perfect) | 0.75 |
| anchor re-scale a | 0.81 |
| anchor pixels | 15520 |
| far-field fraction on anchor (> 0.8 max depth) | 0.00 |
| depth spread on anchor (std/mean) | 0.88 |
| passes with realised gain < 0 | 79% |
| passes with intrinsic gain < 0 | 76% |

## What predicts harm? (AUC: probability that a harmful pass scores higher than a harmless one; 0.5 = no information)

| signal | AUC for 'realised gain < 0' |
|---|---:|
| fit_res | 0.61 |
| far_frac | 0.47 |
| gt_cv | 0.42 |
| n_anchor | 0.50 |
| |log a| | 0.58 |

## Reading it
- intrinsic gain > 0 but realised gain < 0 -> the rotated view is better; the label-free re-anchor ruins it (fix the anchoring).
- intrinsic gain < 0 -> the rotated view itself is worse at the pole on this data (the model does not like rotated content); no anchoring fixes that.
- fit_res AUC well above 0.5 -> `fit_guard` can detect these cases without labels; around 0.5 -> it cannot, drop it.
