# Re-anchor diagnostic: holo12

160 rotated passes from 80 frames. Gains are relative AbsRel reductions on the polar cap (|lat| > 60 deg of the pole the pass targets); positive is better than the identity view.

| quantity | median |
|---|---:|
| intrinsic gain (oracle polar fit of both views) | +1.4% |
| realised gain (label-free re-anchor, global GT fit of identity) | -30.0% |
| anchor loss (realised error vs oracle error of the rotated view) | +427.3% |
| anchor fit residual (fit_quality; 0 = perfect) | 0.81 |
| anchor re-scale a | 0.49 |
| anchor pixels | 15520 |
| far-field fraction on anchor (> 0.8 max depth) | 0.00 |
| depth spread on anchor (std/mean) | 0.51 |
| passes with realised gain < 0 | 57% |
| passes with intrinsic gain < 0 | 43% |

## What predicts harm? (AUC: probability that a harmful pass scores higher than a harmless one; 0.5 = no information)

| signal | AUC for 'realised gain < 0' |
|---|---:|
| fit_res | 0.52 |
| far_frac | 0.63 |
| gt_cv | 0.54 |
| n_anchor | 0.50 |
| |log a| | 0.54 |

## Reading it
- intrinsic gain > 0 but realised gain < 0 -> the rotated view is better; the label-free re-anchor ruins it (fix the anchoring).
- intrinsic gain < 0 -> the rotated view itself is worse at the pole on this data (the model does not like rotated content); no anchoring fixes that.
- fit_res AUC well above 0.5 -> `fit_guard` can detect these cases without labels; around 0.5 -> it cannot, drop it.
