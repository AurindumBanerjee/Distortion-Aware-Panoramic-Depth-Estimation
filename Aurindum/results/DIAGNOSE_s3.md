# Re-anchor diagnostic: s3

80 rotated passes from 40 frames. Gains are relative AbsRel reductions on the polar cap (|lat| > 60 deg of the pole the pass targets); positive is better than the identity view.

| quantity | median |
|---|---:|
| intrinsic gain (oracle polar fit of both views) | -23.4% |
| realised gain (label-free re-anchor, global GT fit of identity) | -19.5% |
| anchor loss (realised error vs oracle error of the rotated view) | +477.6% |
| anchor fit residual (fit_quality; 0 = perfect) | 0.53 |
| anchor re-scale a | 0.94 |
| anchor pixels | 15520 |
| far-field fraction on anchor (> 0.8 max depth) | 0.00 |
| depth spread on anchor (std/mean) | 0.28 |
| passes with realised gain < 0 | 62% |
| passes with intrinsic gain < 0 | 64% |

## What predicts harm? (AUC: probability that a harmful pass scores higher than a harmless one; 0.5 = no information)

| signal | AUC for 'realised gain < 0' |
|---|---:|
| fit_res | 0.65 |
| far_frac | 0.49 |
| gt_cv | 0.35 |
| n_anchor | 0.50 |
| |log a| | 0.59 |

## Reading it
- intrinsic gain > 0 but realised gain < 0 -> the rotated view is better; the label-free re-anchor ruins it (fix the anchoring).
- intrinsic gain < 0 -> the rotated view itself is worse at the pole on this data (the model does not like rotated content); no anchoring fixes that.
- fit_res AUC well above 0.5 -> `fit_guard` can detect these cases without labels; around 0.5 -> it cannot, drop it.
