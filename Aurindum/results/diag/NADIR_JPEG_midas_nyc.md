# Nadir + JPEG diagnosis: midas_nyc

model `midas_dpt_hybrid_384` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 45% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +0.61)

## nadir · protocol `align-all` · region AbsRel (raw median 0.0614)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0609 | +4.1% | 45% | [-2.8, +27.9] |
| oracle+1.5:inpaint_erp | 0.0647 | +3.4% | 45% | [-2.0, +22.0] |
| detected:inpaint_erp | 0.0678 | +3.5% | 42% | [-2.7, +27.9] |
| detected+1.5:inpaint_erp | 0.0655 | +1.6% | 48% | [-3.1, +25.2] |
| pipe:inpaint_erp | 0.0678 | +3.5% | 42% | [-2.7, +27.9] |
| oracle:inpaint_tangent | 0.0886 | +11.5% | 38% | [-3.5, +44.2] |
| oracle+1.5:inpaint_tangent | 0.0780 | +11.3% | 32% | [+1.6, +38.9] |
| detected:inpaint_tangent | 0.0850 | +6.3% | 38% | [-2.8, +43.8] |
| detected+1.5:inpaint_tangent | 0.0784 | +13.3% | 35% | [+1.6, +38.9] |
| pipe:inpaint_tangent | 0.0850 | +6.3% | 38% | [-2.8, +43.8] |
| oracle:plane_fill | 0.0741 | -11.2% | 78% | [-17.3, -4.8] |
| oracle+1.5:plane_fill | 0.0742 | -11.3% | 70% | [-25.7, -4.9] |
| detected:plane_fill | 0.0760 | -10.3% | 72% | [-16.9, -4.2] |
| detected+1.5:plane_fill | 0.0784 | -15.2% | 72% | [-27.2, -5.5] |
| pipe:plane_fill | 0.0760 | -10.3% | 72% | [-16.9, -4.2] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.2468)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2548 | +2.1% | 42% | [-0.8, +5.4] |
| oracle+1.5:inpaint_erp | 0.2420 | -0.5% | 50% | [-3.8, +1.5] |
| detected:inpaint_erp | 0.2550 | +0.9% | 50% | [-1.7, +4.6] |
| detected+1.5:inpaint_erp | 0.2399 | +0.2% | 50% | [-3.2, +2.7] |
| pipe:inpaint_erp | 0.2550 | +0.9% | 50% | [-1.7, +4.6] |
| oracle:inpaint_tangent | 0.2828 | +7.4% | 22% | [+1.8, +10.9] |
| oracle+1.5:inpaint_tangent | 0.2631 | +4.2% | 28% | [+0.6, +7.1] |
| detected:inpaint_tangent | 0.2828 | +5.8% | 25% | [+1.3, +7.9] |
| detected+1.5:inpaint_tangent | 0.2631 | +4.2% | 25% | [+0.6, +8.7] |
| pipe:inpaint_tangent | 0.2828 | +5.8% | 25% | [+1.3, +7.9] |
| oracle:plane_fill | 0.2561 | +2.8% | 30% | [+1.1, +5.2] |
| oracle+1.5:plane_fill | 0.2482 | +1.6% | 42% | [-1.2, +4.7] |
| detected:plane_fill | 0.2561 | +1.5% | 35% | [+0.0, +4.5] |
| detected+1.5:plane_fill | 0.2482 | +1.6% | 40% | [-0.6, +5.2] |
| pipe:plane_fill | 0.2561 | +1.5% | 35% | [+0.0, +4.5] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0931)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0718 | +10.3% | 38% | [-3.6, +19.2] |
| oracle+1.5:inpaint_erp | 0.0643 | +6.8% | 45% | [-3.9, +18.1] |
| detected:inpaint_erp | 0.0711 | +10.0% | 40% | [-2.0, +14.1] |
| detected+1.5:inpaint_erp | 0.0547 | +9.4% | 42% | [-5.4, +18.8] |
| pipe:inpaint_erp | 0.0711 | +10.0% | 40% | [-2.0, +14.1] |
| oracle:inpaint_tangent | 0.1530 | +11.6% | 20% | [+6.4, +36.6] |
| oracle+1.5:inpaint_tangent | 0.0941 | +10.1% | 30% | [+4.2, +18.9] |
| detected:inpaint_tangent | 0.1452 | +10.9% | 22% | [+8.7, +40.0] |
| detected+1.5:inpaint_tangent | 0.0977 | +11.8% | 28% | [+4.2, +20.6] |
| pipe:inpaint_tangent | 0.1452 | +10.9% | 22% | [+8.7, +40.0] |
| oracle:plane_fill | 0.0818 | +0.3% | 50% | [-15.2, +5.2] |
| oracle+1.5:plane_fill | 0.0841 | -3.5% | 55% | [-25.0, +7.0] |
| detected:plane_fill | 0.0874 | +0.3% | 50% | [-17.8, +7.2] |
| detected+1.5:plane_fill | 0.0877 | -3.5% | 52% | [-27.7, +7.0] |
| pipe:plane_fill | 0.0874 | +0.3% | 50% | [-17.8, +7.2] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.2093)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2198 | +3.3% | 38% | [-0.6, +6.4] |
| oracle+1.5:inpaint_erp | 0.2046 | -0.7% | 52% | [-2.2, +4.1] |
| detected:inpaint_erp | 0.2160 | +2.8% | 45% | [-2.0, +5.6] |
| detected+1.5:inpaint_erp | 0.2032 | +0.2% | 50% | [-1.8, +4.2] |
| pipe:inpaint_erp | 0.2160 | +2.8% | 45% | [-2.0, +5.6] |
| oracle:inpaint_tangent | 0.2465 | +5.4% | 25% | [+1.2, +11.3] |
| oracle+1.5:inpaint_tangent | 0.2267 | +3.5% | 32% | [+0.9, +6.4] |
| detected:inpaint_tangent | 0.2434 | +4.3% | 30% | [+0.4, +8.7] |
| detected+1.5:inpaint_tangent | 0.2261 | +3.9% | 32% | [+0.8, +7.5] |
| pipe:inpaint_tangent | 0.2434 | +4.3% | 30% | [+0.4, +8.7] |
| oracle:plane_fill | 0.2185 | +1.2% | 35% | [-0.1, +3.6] |
| oracle+1.5:plane_fill | 0.2145 | +1.6% | 48% | [-2.0, +3.6] |
| detected:plane_fill | 0.2161 | +0.5% | 42% | [-1.0, +3.6] |
| detected+1.5:plane_fill | 0.2141 | +1.7% | 45% | [-2.0, +4.0] |
| pipe:plane_fill | 0.2161 | +0.5% | 42% | [-1.0, +3.6] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1140)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2243 | +50.1% | 20% | [+12.2, +150.0] |
| oracle:inpaint_erp | 0.2133 | +37.8% | 20% | [+22.1, +116.3] |
| oracle+1.5:inpaint_erp | 0.2087 | +46.6% | 20% | [+17.3, +143.6] |
| detected:inpaint_erp | 0.1228 | +0.0% | 15% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.1368 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.2691 | +104.8% | 18% | [+29.2, +242.0] |
| pipe_photometric:inpaint_erp | 0.2239 | +50.1% | 28% | [+3.9, +137.3] |
| pipe_cap_first:inpaint_erp | 0.2268 | +50.1% | 28% | [+3.9, +137.3] |
| oracle:inpaint_tangent | 0.1095 | +2.1% | 42% | [-6.7, +19.5] |
| oracle+1.5:inpaint_tangent | 0.1057 | +2.6% | 45% | [-6.2, +18.1] |
| detected:inpaint_tangent | 0.1080 | +0.0% | 20% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1039 | +0.0% | 22% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1542 | +25.9% | 35% | [+2.5, +80.9] |
| pipe_photometric:inpaint_tangent | 0.1882 | +48.8% | 28% | [+3.9, +99.1] |
| pipe_cap_first:inpaint_tangent | 0.1882 | +46.7% | 28% | [+3.9, +100.3] |
| oracle:plane_fill | 0.1019 | -3.7% | 52% | [-17.3, +12.8] |
| oracle+1.5:plane_fill | 0.0972 | -1.5% | 55% | [-15.7, +14.3] |
| detected:plane_fill | 0.1015 | +0.0% | 28% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1066 | +0.0% | 28% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.1583 | +21.1% | 38% | [-1.9, +68.4] |
| pipe_photometric:plane_fill | 0.1882 | +23.2% | 28% | [+3.0, +81.4] |
| pipe_cap_first:plane_fill | 0.1882 | +21.4% | 28% | [+3.0, +82.6] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.3966)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.4285 | +1.3% | 40% | [-0.2, +8.8] |
| oracle:inpaint_erp | 0.3785 | -0.7% | 50% | [-3.6, +2.1] |
| oracle+1.5:inpaint_erp | 0.3826 | -0.8% | 60% | [-4.2, +2.1] |
| detected:inpaint_erp | 0.3852 | +0.0% | 25% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.3850 | +0.0% | 28% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.4057 | +1.2% | 42% | [-1.1, +3.9] |
| pipe_photometric:inpaint_erp | 0.4112 | +0.3% | 48% | [-1.1, +6.1] |
| pipe_cap_first:inpaint_erp | 0.4109 | +0.4% | 48% | [-1.1, +6.0] |
| oracle:inpaint_tangent | 0.4024 | +0.6% | 38% | [-0.1, +5.0] |
| oracle+1.5:inpaint_tangent | 0.3994 | +0.5% | 42% | [-0.4, +4.3] |
| detected:inpaint_tangent | 0.3952 | +0.0% | 20% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.3953 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.4198 | +4.1% | 35% | [+0.1, +7.0] |
| pipe_photometric:inpaint_tangent | 0.4253 | +3.0% | 35% | [+0.0, +8.8] |
| pipe_cap_first:inpaint_tangent | 0.4241 | +3.1% | 35% | [+0.0, +8.8] |
| oracle:plane_fill | 0.4021 | +0.6% | 40% | [-0.2, +4.7] |
| oracle+1.5:plane_fill | 0.3990 | +0.9% | 48% | [-0.5, +4.2] |
| detected:plane_fill | 0.3952 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.3953 | +0.0% | 22% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.4190 | +4.1% | 32% | [+0.1, +6.9] |
| pipe_photometric:plane_fill | 0.4248 | +2.2% | 35% | [+0.0, +8.8] |
| pipe_cap_first:plane_fill | 0.4239 | +2.3% | 35% | [+0.0, +8.8] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.1534)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1625 | -0.7% | 55% | [-4.4, +5.2] |
| oracle:inpaint_erp | 0.1364 | +0.7% | 48% | [-6.5, +6.7] |
| oracle+1.5:inpaint_erp | 0.1446 | +0.8% | 50% | [-6.3, +12.1] |
| detected:inpaint_erp | 0.1533 | +0.0% | 20% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.1597 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.1722 | +0.0% | 50% | [-4.6, +13.6] |
| pipe_photometric:inpaint_erp | 0.1634 | -0.7% | 55% | [-6.9, +13.0] |
| pipe_cap_first:inpaint_erp | 0.1634 | -0.7% | 55% | [-6.9, +13.0] |
| oracle:inpaint_tangent | 0.1452 | -3.9% | 60% | [-12.5, +0.8] |
| oracle+1.5:inpaint_tangent | 0.1384 | -6.0% | 70% | [-19.5, -1.3] |
| detected:inpaint_tangent | 0.1532 | +0.0% | 28% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1513 | +0.0% | 25% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1668 | +0.8% | 48% | [-10.2, +10.9] |
| pipe_photometric:inpaint_tangent | 0.1562 | -1.5% | 57% | [-7.4, +5.5] |
| pipe_cap_first:inpaint_tangent | 0.1562 | -1.5% | 57% | [-7.4, +4.9] |
| oracle:plane_fill | 0.1385 | -4.0% | 62% | [-17.0, +0.3] |
| oracle+1.5:plane_fill | 0.1335 | -8.5% | 72% | [-22.4, -2.1] |
| detected:plane_fill | 0.1532 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1508 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.1647 | +0.8% | 48% | [-10.3, +10.9] |
| pipe_photometric:plane_fill | 0.1562 | -1.5% | 57% | [-7.4, +5.5] |
| pipe_cap_first:plane_fill | 0.1562 | -1.5% | 57% | [-7.4, +4.9] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.3487)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3890 | +8.7% | 30% | [+1.5, +17.7] |
| oracle:inpaint_erp | 0.3434 | +2.6% | 38% | [-1.7, +7.6] |
| oracle+1.5:inpaint_erp | 0.3495 | +2.5% | 35% | [-0.8, +7.8] |
| detected:inpaint_erp | 0.3474 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.3460 | +0.0% | 18% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.3768 | +7.8% | 28% | [+4.1, +14.6] |
| pipe_photometric:inpaint_erp | 0.3778 | +4.2% | 38% | [-0.4, +10.8] |
| pipe_cap_first:inpaint_erp | 0.3778 | +2.9% | 38% | [-0.4, +10.9] |
| oracle:inpaint_tangent | 0.3404 | +1.4% | 42% | [-0.8, +4.2] |
| oracle+1.5:inpaint_tangent | 0.3461 | +1.3% | 42% | [-1.2, +4.1] |
| detected:inpaint_tangent | 0.3406 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.3411 | +0.0% | 22% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.3652 | +5.5% | 28% | [+1.3, +14.0] |
| pipe_photometric:inpaint_tangent | 0.3778 | +6.3% | 35% | [+0.2, +11.0] |
| pipe_cap_first:inpaint_tangent | 0.3778 | +6.5% | 35% | [+0.1, +11.0] |
| oracle:plane_fill | 0.3392 | +1.5% | 45% | [-0.9, +4.2] |
| oracle+1.5:plane_fill | 0.3461 | +1.4% | 42% | [-1.2, +4.2] |
| detected:plane_fill | 0.3406 | +0.0% | 25% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.3411 | +0.0% | 22% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.3623 | +4.6% | 32% | [+1.0, +14.8] |
| pipe_photometric:plane_fill | 0.3742 | +4.4% | 35% | [+0.0, +11.0] |
| pipe_cap_first:plane_fill | 0.3740 | +4.5% | 35% | [+0.0, +11.0] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.956 | 0.953 | 0.960 |
| nadir+jpeg | 1.042 | 1.001 | 1.066 |
