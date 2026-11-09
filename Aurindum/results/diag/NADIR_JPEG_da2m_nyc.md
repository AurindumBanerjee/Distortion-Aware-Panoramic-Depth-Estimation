# Nadir + JPEG diagnosis: da2m_nyc

model `da2` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 45% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +0.61)

## nadir · protocol `align-all` · region AbsRel (raw median 0.1263)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0560 | -54.9% | 82% | [-69.0, -39.2] |
| oracle+1.5:inpaint_erp | 0.0633 | -58.1% | 75% | [-67.9, -31.0] |
| detected:inpaint_erp | 0.0560 | -57.4% | 82% | [-65.6, -42.7] |
| detected+1.5:inpaint_erp | 0.0615 | -60.6% | 80% | [-70.2, -43.2] |
| pipe:inpaint_erp | 0.0560 | -57.4% | 82% | [-65.6, -42.7] |
| oracle:inpaint_tangent | 0.0655 | -39.2% | 62% | [-62.9, +12.5] |
| oracle+1.5:inpaint_tangent | 0.0682 | -36.6% | 57% | [-60.3, +28.6] |
| detected:inpaint_tangent | 0.0658 | -39.2% | 65% | [-60.4, -2.8] |
| detected+1.5:inpaint_tangent | 0.0718 | -40.8% | 60% | [-59.2, +13.7] |
| pipe:inpaint_tangent | 0.0658 | -39.2% | 65% | [-60.4, -2.8] |
| oracle:plane_fill | 0.0708 | -41.7% | 60% | [-60.3, +23.5] |
| oracle+1.5:plane_fill | 0.0793 | -32.7% | 55% | [-61.5, +35.1] |
| detected:plane_fill | 0.0708 | -41.7% | 62% | [-58.7, +10.5] |
| detected+1.5:plane_fill | 0.0793 | -44.5% | 57% | [-61.5, +15.1] |
| pipe:plane_fill | 0.0708 | -41.7% | 62% | [-58.7, +10.5] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.2365)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2384 | +4.2% | 32% | [+0.9, +8.1] |
| oracle+1.5:inpaint_erp | 0.2436 | +5.8% | 30% | [+2.0, +10.8] |
| detected:inpaint_erp | 0.2419 | +6.4% | 30% | [+1.4, +9.7] |
| detected+1.5:inpaint_erp | 0.2364 | +4.8% | 32% | [+1.7, +9.2] |
| pipe:inpaint_erp | 0.2419 | +6.4% | 30% | [+1.4, +9.7] |
| oracle:inpaint_tangent | 0.2485 | +9.7% | 20% | [+6.3, +12.7] |
| oracle+1.5:inpaint_tangent | 0.2477 | +9.0% | 18% | [+6.3, +13.9] |
| detected:inpaint_tangent | 0.2485 | +9.4% | 22% | [+5.3, +12.7] |
| detected+1.5:inpaint_tangent | 0.2447 | +9.0% | 20% | [+5.9, +13.9] |
| pipe:inpaint_tangent | 0.2485 | +9.4% | 22% | [+5.3, +12.7] |
| oracle:plane_fill | 0.2485 | +9.7% | 20% | [+6.3, +12.8] |
| oracle+1.5:plane_fill | 0.2477 | +9.0% | 18% | [+6.3, +13.9] |
| detected:plane_fill | 0.2485 | +9.4% | 22% | [+5.2, +12.8] |
| detected+1.5:plane_fill | 0.2446 | +9.0% | 20% | [+5.9, +13.9] |
| pipe:plane_fill | 0.2485 | +9.4% | 22% | [+5.2, +12.8] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0893)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0530 | -41.8% | 80% | [-64.0, -18.0] |
| oracle+1.5:inpaint_erp | 0.0544 | -42.4% | 78% | [-62.5, -24.7] |
| detected:inpaint_erp | 0.0530 | -45.9% | 80% | [-66.7, -20.0] |
| detected+1.5:inpaint_erp | 0.0544 | -50.4% | 78% | [-66.3, -30.4] |
| pipe:inpaint_erp | 0.0530 | -45.9% | 80% | [-66.7, -20.0] |
| oracle:inpaint_tangent | 0.0505 | -31.5% | 78% | [-59.8, -7.6] |
| oracle+1.5:inpaint_tangent | 0.0599 | -26.4% | 72% | [-60.7, -9.3] |
| detected:inpaint_tangent | 0.0505 | -29.4% | 75% | [-57.8, -9.6] |
| detected+1.5:inpaint_tangent | 0.0585 | -27.7% | 70% | [-64.6, -6.2] |
| pipe:inpaint_tangent | 0.0505 | -29.4% | 75% | [-57.8, -9.6] |
| oracle:plane_fill | 0.0516 | -31.1% | 78% | [-59.8, -7.2] |
| oracle+1.5:plane_fill | 0.0611 | -25.8% | 72% | [-61.1, -6.2] |
| detected:plane_fill | 0.0508 | -28.9% | 75% | [-57.4, -7.2] |
| detected+1.5:plane_fill | 0.0611 | -26.9% | 70% | [-63.9, -6.2] |
| pipe:plane_fill | 0.0508 | -28.9% | 75% | [-57.4, -7.2] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.2189)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2055 | -3.7% | 60% | [-6.0, +2.2] |
| oracle+1.5:inpaint_erp | 0.2116 | -1.7% | 52% | [-6.7, +5.1] |
| detected:inpaint_erp | 0.2073 | -3.1% | 55% | [-6.1, +3.0] |
| detected+1.5:inpaint_erp | 0.2059 | -3.2% | 57% | [-6.8, +2.1] |
| pipe:inpaint_erp | 0.2073 | -3.1% | 55% | [-6.1, +3.0] |
| oracle:inpaint_tangent | 0.2172 | +5.6% | 40% | [-1.1, +11.5] |
| oracle+1.5:inpaint_tangent | 0.2163 | +6.1% | 38% | [-0.6, +13.6] |
| detected:inpaint_tangent | 0.2176 | +4.2% | 40% | [-1.5, +9.4] |
| detected+1.5:inpaint_tangent | 0.2136 | +4.3% | 42% | [-1.6, +12.7] |
| pipe:inpaint_tangent | 0.2176 | +4.2% | 40% | [-1.5, +9.4] |
| oracle:plane_fill | 0.2157 | +5.3% | 38% | [-0.4, +11.2] |
| oracle+1.5:plane_fill | 0.2160 | +5.9% | 38% | [-0.1, +13.6] |
| detected:plane_fill | 0.2165 | +5.1% | 40% | [-0.5, +9.2] |
| detected+1.5:plane_fill | 0.2138 | +4.8% | 40% | [-1.3, +12.5] |
| pipe:plane_fill | 0.2165 | +5.1% | 40% | [-0.5, +9.2] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1621)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1918 | +7.7% | 32% | [+2.0, +19.8] |
| oracle:inpaint_erp | 0.1511 | +5.2% | 48% | [-22.2, +37.6] |
| oracle+1.5:inpaint_erp | 0.1766 | +15.3% | 42% | [-5.3, +52.6] |
| detected:inpaint_erp | 0.1995 | +0.0% | 12% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.2077 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.1732 | +5.7% | 48% | [-21.9, +56.8] |
| pipe_photometric:inpaint_erp | 0.1983 | +8.6% | 30% | [+3.2, +27.3] |
| pipe_cap_first:inpaint_erp | 0.1971 | +8.6% | 30% | [+3.2, +27.3] |
| oracle:inpaint_tangent | 0.1355 | -27.8% | 55% | [-55.9, +28.4] |
| oracle+1.5:inpaint_tangent | 0.1487 | -30.7% | 55% | [-53.7, +19.8] |
| detected:inpaint_tangent | 0.1670 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1630 | +0.0% | 18% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1743 | -29.3% | 55% | [-53.3, +37.7] |
| pipe_photometric:inpaint_tangent | 0.1757 | +8.6% | 32% | [+2.0, +26.4] |
| pipe_cap_first:inpaint_tangent | 0.1868 | +8.6% | 32% | [+2.0, +27.3] |
| oracle:plane_fill | 0.1225 | -32.6% | 57% | [-56.0, +31.5] |
| oracle+1.5:plane_fill | 0.1273 | -32.7% | 60% | [-49.8, +16.5] |
| detected:plane_fill | 0.1681 | +0.0% | 20% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1666 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.1583 | -29.3% | 55% | [-54.4, +23.6] |
| pipe_photometric:plane_fill | 0.1810 | +8.6% | 32% | [+2.0, +24.4] |
| pipe_cap_first:plane_fill | 0.1929 | +8.6% | 32% | [+2.0, +24.4] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.3072)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2910 | -3.6% | 65% | [-5.0, -0.0] |
| oracle:inpaint_erp | 0.3887 | +17.0% | 18% | [+9.5, +23.3] |
| oracle+1.5:inpaint_erp | 0.3959 | +20.5% | 15% | [+14.3, +25.3] |
| detected:inpaint_erp | 0.3901 | +0.0% | 2% | [+0.0, +10.5] |
| detected+1.5:inpaint_erp | 0.3962 | +0.0% | 2% | [+0.0, +12.9] |
| deblock_oracle:inpaint_erp | 0.3669 | +10.6% | 22% | [+3.0, +18.4] |
| pipe_photometric:inpaint_erp | 0.3836 | +2.2% | 38% | [-0.4, +9.5] |
| pipe_cap_first:inpaint_erp | 0.3831 | +2.2% | 40% | [-0.4, +9.6] |
| oracle:inpaint_tangent | 0.3574 | +13.3% | 30% | [+2.2, +18.7] |
| oracle+1.5:inpaint_tangent | 0.3649 | +12.1% | 32% | [+2.1, +19.5] |
| detected:inpaint_tangent | 0.3737 | +0.0% | 2% | [+0.0, +12.7] |
| detected+1.5:inpaint_tangent | 0.3768 | +0.0% | 2% | [+0.0, +12.0] |
| deblock_oracle:inpaint_tangent | 0.3439 | +8.3% | 32% | [+2.8, +13.5] |
| pipe_photometric:inpaint_tangent | 0.3701 | +3.9% | 38% | [-0.4, +9.7] |
| pipe_cap_first:inpaint_tangent | 0.3796 | +4.1% | 38% | [-0.4, +9.7] |
| oracle:plane_fill | 0.3573 | +13.3% | 30% | [+2.2, +18.7] |
| oracle+1.5:plane_fill | 0.3649 | +12.1% | 32% | [+2.1, +19.5] |
| detected:plane_fill | 0.3737 | +0.0% | 2% | [+0.0, +12.7] |
| detected+1.5:plane_fill | 0.3767 | +0.0% | 2% | [+0.0, +12.0] |
| deblock_oracle:plane_fill | 0.3439 | +8.3% | 32% | [+2.8, +13.5] |
| pipe_photometric:plane_fill | 0.3701 | +3.9% | 38% | [-0.4, +9.6] |
| pipe_cap_first:plane_fill | 0.3795 | +4.1% | 38% | [-0.4, +9.7] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.1289)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1271 | -2.1% | 57% | [-7.3, +3.3] |
| oracle:inpaint_erp | 0.1173 | +6.0% | 42% | [-3.9, +44.6] |
| oracle+1.5:inpaint_erp | 0.1344 | +13.4% | 35% | [+0.5, +59.9] |
| detected:inpaint_erp | 0.1372 | +0.0% | 12% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.1589 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.1534 | +14.7% | 42% | [-13.1, +59.5] |
| pipe_photometric:inpaint_erp | 0.1547 | +1.4% | 48% | [-5.8, +16.1] |
| pipe_cap_first:inpaint_erp | 0.1569 | +1.0% | 50% | [-5.8, +16.1] |
| oracle:inpaint_tangent | 0.1213 | -1.9% | 52% | [-25.2, +19.0] |
| oracle+1.5:inpaint_tangent | 0.1207 | -5.9% | 52% | [-32.5, +23.3] |
| detected:inpaint_tangent | 0.1208 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1196 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1209 | -2.2% | 52% | [-31.4, +41.8] |
| pipe_photometric:inpaint_tangent | 0.1230 | -1.1% | 52% | [-7.3, +11.2] |
| pipe_cap_first:inpaint_tangent | 0.1230 | +1.0% | 50% | [-7.3, +11.2] |
| oracle:plane_fill | 0.1213 | -1.1% | 50% | [-25.1, +20.7] |
| oracle+1.5:plane_fill | 0.1210 | -6.2% | 52% | [-32.5, +28.8] |
| detected:plane_fill | 0.1208 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1198 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.1198 | -2.5% | 52% | [-31.4, +41.7] |
| pipe_photometric:plane_fill | 0.1230 | -1.1% | 52% | [-7.3, +11.2] |
| pipe_cap_first:plane_fill | 0.1230 | +1.0% | 50% | [-7.3, +11.2] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.2613)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2615 | -0.3% | 57% | [-3.0, +1.7] |
| oracle:inpaint_erp | 0.3392 | +14.3% | 28% | [+2.9, +25.4] |
| oracle+1.5:inpaint_erp | 0.3443 | +21.2% | 22% | [+11.2, +25.9] |
| detected:inpaint_erp | 0.3392 | +0.0% | 5% | [+0.0, +2.7] |
| detected+1.5:inpaint_erp | 0.3556 | +0.0% | 5% | [+0.0, +1.6] |
| deblock_oracle:inpaint_erp | 0.3172 | +14.0% | 35% | [+0.2, +19.5] |
| pipe_photometric:inpaint_erp | 0.3432 | +4.9% | 32% | [+0.5, +9.0] |
| pipe_cap_first:inpaint_erp | 0.3437 | +4.9% | 35% | [+0.4, +9.3] |
| oracle:inpaint_tangent | 0.3195 | +5.3% | 38% | [-6.3, +20.0] |
| oracle+1.5:inpaint_tangent | 0.3266 | +5.2% | 38% | [-9.1, +20.1] |
| detected:inpaint_tangent | 0.3230 | +0.0% | 5% | [+0.0, +5.3] |
| detected+1.5:inpaint_tangent | 0.3245 | +0.0% | 5% | [+0.0, +6.6] |
| deblock_oracle:inpaint_tangent | 0.3053 | +2.4% | 48% | [-4.2, +13.1] |
| pipe_photometric:inpaint_tangent | 0.3239 | +4.9% | 35% | [+0.3, +9.2] |
| pipe_cap_first:inpaint_tangent | 0.3330 | +4.9% | 35% | [+0.3, +8.9] |
| oracle:plane_fill | 0.3170 | +5.6% | 38% | [-6.4, +19.0] |
| oracle+1.5:plane_fill | 0.3249 | +5.1% | 42% | [-9.5, +19.1] |
| detected:plane_fill | 0.3215 | +0.0% | 8% | [+0.0, +5.2] |
| detected+1.5:plane_fill | 0.3228 | +0.0% | 5% | [+0.0, +5.7] |
| deblock_oracle:plane_fill | 0.3045 | +0.3% | 50% | [-5.9, +11.8] |
| pipe_photometric:plane_fill | 0.3225 | +4.9% | 35% | [+0.3, +8.4] |
| pipe_cap_first:plane_fill | 0.3314 | +4.9% | 35% | [+0.3, +8.2] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 1.054 | 0.964 | 0.982 |
| nadir+jpeg | 0.976 | 0.932 | 0.883 |
