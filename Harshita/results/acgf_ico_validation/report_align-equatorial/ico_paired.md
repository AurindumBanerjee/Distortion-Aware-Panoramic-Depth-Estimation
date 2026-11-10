### acgf|ico-affine|polar vs baseline (AbsRel, pixel-weighted; positive = acgf|ico-affine|polar better)

| band   |   baseline |   acgf|ico-affine|polar |   improvement_% |   median_per_image_impr_% |   wilcoxon_p |   images_improved |   n_images |
|:-------|-----------:|------------------------:|----------------:|--------------------------:|-------------:|------------------:|-----------:|
| all    |     0.3188 |                  0.2641 |         17.1601 |                   16.8853 |       0.0000 |                38 |         41 |
| 0-15   |     0.2665 |                  0.2665 |          0.0000 |                    0.0000 |     nan      |                 0 |         41 |
| 60-75  |     0.4068 |                  0.2983 |         26.6625 |                   26.6937 |       0.0000 |                38 |         41 |
| 75-90  |     0.4726 |                  0.3169 |         32.9413 |                   35.4116 |       0.0000 |                38 |         41 |

### acgf|ico-affine|polar vs mono360 (AbsRel, pixel-weighted; positive = acgf|ico-affine|polar better)

| band   |   mono360 |   acgf|ico-affine|polar |   improvement_% |   median_per_image_impr_% |   wilcoxon_p |   images_improved |   n_images |
|:-------|----------:|------------------------:|----------------:|--------------------------:|-------------:|------------------:|-----------:|
| all    |    0.1685 |                  0.2641 |        -56.7701 |                  -56.9517 |       0.0000 |                 7 |         41 |
| 0-15   |    0.1978 |                  0.2665 |        -34.6899 |                  -31.8960 |       0.0000 |                 9 |         41 |
| 60-75  |    0.1762 |                  0.2983 |        -69.3523 |                  -85.2706 |       0.0000 |                 7 |         41 |
| 75-90  |    0.1861 |                  0.3169 |        -70.2614 |                 -103.5210 |       0.0001 |                 9 |         41 |

### acgf|ico-affine|polar vs acgf (AbsRel, pixel-weighted; positive = acgf|ico-affine|polar better)

| band   |   acgf |   acgf|ico-affine|polar |   improvement_% |   median_per_image_impr_% |   wilcoxon_p |   images_improved |   n_images |
|:-------|-------:|------------------------:|----------------:|--------------------------:|-------------:|------------------:|-----------:|
| all    | 0.2736 |                  0.2641 |          3.4883 |                    2.5276 |       0.0100 |                31 |         41 |
| 0-15   | 0.2665 |                  0.2665 |          0.0000 |                    0.0000 |     nan      |                 0 |         41 |
| 60-75  | 0.3167 |                  0.2983 |          5.7945 |                    3.1970 |       0.0113 |                29 |         41 |
| 75-90  | 0.3317 |                  0.3169 |          4.4497 |                    1.0108 |       0.7100 |                23 |         41 |

