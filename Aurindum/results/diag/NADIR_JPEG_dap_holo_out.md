# Nadir + JPEG diagnosis: dap_holo_out

model `dap` · 71 frames · nadir cap below -62 deg · JPEG q8. Protocols: `none`, `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 96% of frames; detected edge minus true edge: median -0.65 deg (p5 -2.23, p95 -0.12)

## nadir · protocol `none` · region AbsRel (raw median 0.6445)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.5211 | -22.6% | 99% | [-27.6, -19.0] |
| oracle+1.5:inpaint_erp | 0.5078 | -26.8% | 99% | [-29.9, -21.8] |
| detected:inpaint_erp | 0.5211 | -23.0% | 99% | [-27.6, -19.9] |
| detected+1.5:inpaint_erp | 0.4741 | -28.6% | 99% | [-35.8, -23.9] |
| pipe:inpaint_erp | 0.5211 | -23.0% | 99% | [-27.6, -19.9] |
| oracle:inpaint_tangent | 0.5267 | -23.0% | 97% | [-28.2, -19.6] |
| oracle+1.5:inpaint_tangent | 0.5595 | -15.9% | 92% | [-20.3, -9.7] |
| detected:inpaint_tangent | 0.5331 | -21.6% | 94% | [-25.8, -17.1] |
| detected+1.5:inpaint_tangent | 0.5492 | -17.0% | 90% | [-23.0, -12.1] |
| pipe:inpaint_tangent | 0.5331 | -21.6% | 94% | [-25.8, -17.1] |
| oracle:plane_fill | 0.1480 | -69.6% | 100% | [-80.2, -57.0] |
| oracle+1.5:plane_fill | 0.1509 | -70.5% | 99% | [-79.7, -56.8] |
| detected:plane_fill | 0.1505 | -70.0% | 100% | [-79.5, -59.9] |
| detected+1.5:plane_fill | 0.1493 | -71.1% | 99% | [-78.8, -58.2] |
| pipe:plane_fill | 0.1505 | -70.0% | 100% | [-79.5, -59.9] |

## nadir · protocol `none` · outside AbsRel (raw median 0.3259)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.3169 | -1.1% | 65% | [-1.8, -0.4] |
| oracle+1.5:inpaint_erp | 0.3147 | -1.2% | 65% | [-2.4, -0.3] |
| detected:inpaint_erp | 0.3175 | -1.1% | 66% | [-2.1, -0.4] |
| detected+1.5:inpaint_erp | 0.3130 | -1.2% | 61% | [-2.5, +0.0] |
| pipe:inpaint_erp | 0.3175 | -1.1% | 66% | [-2.1, -0.4] |
| oracle:inpaint_tangent | 0.3173 | -0.6% | 65% | [-1.5, -0.2] |
| oracle+1.5:inpaint_tangent | 0.3164 | -0.7% | 62% | [-2.3, -0.1] |
| detected:inpaint_tangent | 0.3177 | -0.7% | 61% | [-1.5, +0.0] |
| detected+1.5:inpaint_tangent | 0.3128 | -0.8% | 59% | [-2.3, +0.2] |
| pipe:inpaint_tangent | 0.3177 | -0.7% | 61% | [-1.5, +0.0] |
| oracle:plane_fill | 0.3171 | -0.6% | 65% | [-1.5, -0.2] |
| oracle+1.5:plane_fill | 0.3135 | -0.9% | 69% | [-3.2, -0.5] |
| detected:plane_fill | 0.3152 | -0.9% | 63% | [-1.6, -0.2] |
| detected+1.5:plane_fill | 0.3134 | -1.0% | 68% | [-3.3, -0.4] |
| pipe:plane_fill | 0.3152 | -0.9% | 63% | [-1.6, -0.2] |

## nadir · protocol `none` · ring AbsRel (raw median 0.1522)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1274 | -4.9% | 58% | [-10.4, +0.3] |
| oracle+1.5:inpaint_erp | 0.1370 | -0.3% | 51% | [-7.9, +19.4] |
| detected:inpaint_erp | 0.1299 | -3.8% | 56% | [-9.1, +0.6] |
| detected+1.5:inpaint_erp | 0.1507 | +1.3% | 49% | [-9.4, +23.2] |
| pipe:inpaint_erp | 0.1299 | -3.8% | 56% | [-9.1, +0.6] |
| oracle:inpaint_tangent | 0.1330 | -2.4% | 59% | [-8.5, +0.8] |
| oracle+1.5:inpaint_tangent | 0.1409 | +4.8% | 42% | [-3.2, +17.4] |
| detected:inpaint_tangent | 0.1319 | +0.7% | 49% | [-5.7, +2.5] |
| detected+1.5:inpaint_tangent | 0.1564 | +6.9% | 38% | [+0.4, +25.2] |
| pipe:inpaint_tangent | 0.1319 | +0.7% | 49% | [-5.7, +2.5] |
| oracle:plane_fill | 0.1305 | -2.9% | 61% | [-8.1, +0.3] |
| oracle+1.5:plane_fill | 0.1377 | -3.1% | 55% | [-11.3, +3.1] |
| detected:plane_fill | 0.1305 | -1.6% | 54% | [-9.2, +1.7] |
| detected+1.5:plane_fill | 0.1335 | -2.6% | 55% | [-12.7, +4.8] |
| pipe:plane_fill | 0.1305 | -1.6% | 54% | [-9.2, +1.7] |

## nadir · protocol `none` · all AbsRel (raw median 0.3472)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.3228 | -4.0% | 94% | [-5.4, -2.8] |
| oracle+1.5:inpaint_erp | 0.3167 | -3.8% | 87% | [-5.4, -2.4] |
| detected:inpaint_erp | 0.3181 | -3.6% | 93% | [-4.6, -2.5] |
| detected+1.5:inpaint_erp | 0.3179 | -4.2% | 86% | [-5.9, -2.3] |
| pipe:inpaint_erp | 0.3181 | -3.6% | 93% | [-4.6, -2.5] |
| oracle:inpaint_tangent | 0.3183 | -3.5% | 96% | [-5.4, -2.7] |
| oracle+1.5:inpaint_tangent | 0.3301 | -2.2% | 83% | [-3.3, -1.4] |
| detected:inpaint_tangent | 0.3236 | -3.2% | 90% | [-4.5, -2.0] |
| detected+1.5:inpaint_tangent | 0.3243 | -2.0% | 80% | [-3.3, -1.2] |
| pipe:inpaint_tangent | 0.3236 | -3.2% | 90% | [-4.5, -2.0] |
| oracle:plane_fill | 0.3174 | -10.1% | 100% | [-13.3, -6.3] |
| oracle+1.5:plane_fill | 0.3173 | -10.3% | 94% | [-12.9, -5.9] |
| detected:plane_fill | 0.3183 | -10.1% | 99% | [-13.1, -6.2] |
| detected+1.5:plane_fill | 0.3194 | -9.7% | 93% | [-13.2, -5.9] |
| pipe:plane_fill | 0.3183 | -10.1% | 99% | [-13.1, -6.2] |

## nadir+jpeg · protocol `none` · region AbsRel (raw median 0.3280)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3936 | +5.0% | 34% | [+1.5, +12.3] |
| oracle:inpaint_erp | 0.2480 | -11.3% | 69% | [-18.4, -2.6] |
| oracle+1.5:inpaint_erp | 0.2515 | -9.7% | 68% | [-16.4, -1.9] |
| detected:inpaint_erp | 0.2548 | -9.4% | 66% | [-18.4, -2.4] |
| detected+1.5:inpaint_erp | 0.2515 | -8.9% | 65% | [-14.3, -1.2] |
| deblock_oracle:inpaint_erp | 0.1945 | -31.4% | 87% | [-37.4, -24.9] |
| pipe_photometric:inpaint_erp | 0.2024 | -29.7% | 85% | [-36.3, -18.9] |
| pipe_cap_first:inpaint_erp | 0.1972 | -30.1% | 85% | [-36.2, -18.8] |
| oracle:inpaint_tangent | 0.2462 | -15.4% | 77% | [-24.3, -11.7] |
| oracle+1.5:inpaint_tangent | 0.2474 | -15.4% | 79% | [-20.9, -7.0] |
| detected:inpaint_tangent | 0.2462 | -14.5% | 73% | [-19.5, -6.9] |
| detected+1.5:inpaint_tangent | 0.2474 | -13.6% | 75% | [-25.1, -5.0] |
| deblock_oracle:inpaint_tangent | 0.1785 | -37.5% | 89% | [-41.9, -29.9] |
| pipe_photometric:inpaint_tangent | 0.1771 | -32.4% | 89% | [-38.4, -23.4] |
| pipe_cap_first:inpaint_tangent | 0.1702 | -35.2% | 89% | [-39.7, -28.3] |
| oracle:plane_fill | 0.2466 | -14.5% | 77% | [-27.4, -10.2] |
| oracle+1.5:plane_fill | 0.2404 | -15.4% | 77% | [-26.2, -7.8] |
| detected:plane_fill | 0.2355 | -14.2% | 73% | [-27.4, -7.3] |
| detected+1.5:plane_fill | 0.2450 | -13.0% | 73% | [-26.1, -4.7] |
| deblock_oracle:plane_fill | 0.1500 | -40.6% | 89% | [-46.9, -32.0] |
| pipe_photometric:plane_fill | 0.1506 | -39.2% | 89% | [-44.0, -29.0] |
| pipe_cap_first:plane_fill | 0.1510 | -39.3% | 87% | [-44.1, -29.4] |

## nadir+jpeg · protocol `none` · outside AbsRel (raw median 0.4731)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.4148 | -10.3% | 76% | [-13.8, -6.8] |
| oracle:inpaint_erp | 0.4969 | +4.1% | 31% | [+0.8, +5.7] |
| oracle+1.5:inpaint_erp | 0.4926 | +3.5% | 30% | [+1.0, +6.4] |
| detected:inpaint_erp | 0.4969 | +3.2% | 30% | [+0.8, +5.7] |
| detected+1.5:inpaint_erp | 0.4994 | +3.3% | 28% | [+0.8, +6.4] |
| deblock_oracle:inpaint_erp | 0.4351 | -8.3% | 77% | [-10.9, -4.1] |
| pipe_photometric:inpaint_erp | 0.4508 | -7.8% | 75% | [-10.9, -3.3] |
| pipe_cap_first:inpaint_erp | 0.4511 | -8.5% | 75% | [-10.8, -3.3] |
| oracle:inpaint_tangent | 0.4998 | +1.5% | 37% | [+0.3, +2.3] |
| oracle+1.5:inpaint_tangent | 0.5006 | +1.6% | 37% | [+0.1, +3.0] |
| detected:inpaint_tangent | 0.5006 | +1.4% | 32% | [+0.3, +2.4] |
| detected+1.5:inpaint_tangent | 0.5007 | +1.5% | 34% | [+0.0, +3.4] |
| deblock_oracle:inpaint_tangent | 0.4351 | -9.1% | 83% | [-11.1, -6.7] |
| pipe_photometric:inpaint_tangent | 0.4350 | -9.7% | 82% | [-11.3, -7.1] |
| pipe_cap_first:inpaint_tangent | 0.4349 | -9.2% | 80% | [-10.9, -6.2] |
| oracle:plane_fill | 0.4998 | +1.5% | 37% | [+0.3, +2.4] |
| oracle+1.5:plane_fill | 0.5006 | +1.6% | 37% | [+0.2, +3.0] |
| detected:plane_fill | 0.5004 | +1.4% | 32% | [+0.3, +2.4] |
| detected+1.5:plane_fill | 0.5009 | +1.6% | 34% | [+0.1, +3.4] |
| deblock_oracle:plane_fill | 0.4351 | -9.1% | 83% | [-11.1, -6.7] |
| pipe_photometric:plane_fill | 0.4350 | -9.7% | 82% | [-11.1, -7.1] |
| pipe_cap_first:plane_fill | 0.4349 | -9.1% | 80% | [-10.8, -6.2] |

## nadir+jpeg · protocol `none` · ring AbsRel (raw median 0.2332)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1828 | -18.0% | 72% | [-27.3, -6.6] |
| oracle:inpaint_erp | 0.2532 | +11.7% | 27% | [+4.2, +17.0] |
| oracle+1.5:inpaint_erp | 0.2500 | +10.5% | 24% | [+3.7, +17.8] |
| detected:inpaint_erp | 0.2606 | +11.8% | 24% | [+3.2, +17.3] |
| detected+1.5:inpaint_erp | 0.2540 | +10.9% | 24% | [+5.1, +19.2] |
| deblock_oracle:inpaint_erp | 0.1635 | -10.2% | 68% | [-16.7, -2.0] |
| pipe_photometric:inpaint_erp | 0.1704 | -5.4% | 55% | [-17.6, +2.2] |
| pipe_cap_first:inpaint_erp | 0.1704 | -5.5% | 56% | [-17.6, +2.1] |
| oracle:inpaint_tangent | 0.2387 | +4.2% | 34% | [+1.8, +8.8] |
| oracle+1.5:inpaint_tangent | 0.2385 | +5.7% | 31% | [+1.3, +10.4] |
| detected:inpaint_tangent | 0.2336 | +4.7% | 30% | [+1.2, +9.8] |
| detected+1.5:inpaint_tangent | 0.2461 | +6.3% | 28% | [+1.5, +12.1] |
| deblock_oracle:inpaint_tangent | 0.1560 | -22.1% | 82% | [-28.6, -9.9] |
| pipe_photometric:inpaint_tangent | 0.1470 | -20.1% | 76% | [-28.9, -6.5] |
| pipe_cap_first:inpaint_tangent | 0.1530 | -17.0% | 75% | [-28.9, -6.1] |
| oracle:plane_fill | 0.2386 | +4.9% | 34% | [+1.8, +8.8] |
| oracle+1.5:plane_fill | 0.2379 | +5.8% | 31% | [+1.7, +10.4] |
| detected:plane_fill | 0.2362 | +5.7% | 30% | [+1.2, +9.3] |
| detected+1.5:plane_fill | 0.2438 | +6.9% | 28% | [+1.7, +12.2] |
| deblock_oracle:plane_fill | 0.1559 | -22.0% | 83% | [-29.0, -9.9] |
| pipe_photometric:plane_fill | 0.1449 | -20.6% | 77% | [-30.5, -7.5] |
| pipe_cap_first:plane_fill | 0.1453 | -20.5% | 75% | [-28.7, -7.1] |

## nadir+jpeg · protocol `none` · all AbsRel (raw median 0.4736)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.4200 | -7.9% | 72% | [-11.5, -5.5] |
| oracle:inpaint_erp | 0.4703 | +3.5% | 32% | [+0.8, +4.9] |
| oracle+1.5:inpaint_erp | 0.4785 | +3.5% | 32% | [+0.5, +4.7] |
| detected:inpaint_erp | 0.4803 | +3.5% | 32% | [+0.6, +4.9] |
| detected+1.5:inpaint_erp | 0.4965 | +3.1% | 31% | [+0.2, +4.7] |
| deblock_oracle:inpaint_erp | 0.4245 | -8.8% | 80% | [-12.1, -5.3] |
| pipe_photometric:inpaint_erp | 0.4350 | -8.7% | 77% | [-12.3, -4.5] |
| pipe_cap_first:inpaint_erp | 0.4346 | -9.4% | 77% | [-12.4, -4.5] |
| oracle:inpaint_tangent | 0.4700 | +0.4% | 41% | [-0.2, +1.3] |
| oracle+1.5:inpaint_tangent | 0.4657 | +0.8% | 39% | [-0.0, +2.1] |
| detected:inpaint_tangent | 0.4700 | +0.8% | 37% | [+0.0, +1.5] |
| detected+1.5:inpaint_tangent | 0.4709 | +1.1% | 38% | [+0.0, +2.4] |
| deblock_oracle:inpaint_tangent | 0.4141 | -10.6% | 89% | [-12.6, -9.0] |
| pipe_photometric:inpaint_tangent | 0.4179 | -10.3% | 86% | [-12.6, -7.6] |
| pipe_cap_first:inpaint_tangent | 0.4182 | -10.3% | 86% | [-13.1, -7.8] |
| oracle:plane_fill | 0.4720 | +0.7% | 41% | [-0.2, +1.3] |
| oracle+1.5:plane_fill | 0.4679 | +0.8% | 39% | [-0.4, +1.9] |
| detected:plane_fill | 0.4720 | +0.9% | 38% | [+0.0, +1.2] |
| detected+1.5:plane_fill | 0.4709 | +1.6% | 37% | [+0.0, +2.4] |
| deblock_oracle:plane_fill | 0.4141 | -10.6% | 90% | [-12.7, -9.0] |
| pipe_photometric:plane_fill | 0.4145 | -10.3% | 86% | [-12.9, -8.2] |
| pipe_cap_first:plane_fill | 0.4161 | -10.1% | 86% | [-13.5, -8.5] |

## nadir · protocol `align-all` · region AbsRel (raw median 0.6665)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.5048 | -21.3% | 99% | [-28.7, -19.4] |
| oracle+1.5:inpaint_erp | 0.4838 | -23.5% | 99% | [-42.9, -19.0] |
| detected:inpaint_erp | 0.5039 | -23.4% | 99% | [-28.7, -19.4] |
| detected+1.5:inpaint_erp | 0.4642 | -32.9% | 99% | [-50.0, -21.1] |
| pipe:inpaint_erp | 0.5039 | -23.4% | 99% | [-28.7, -19.4] |
| oracle:inpaint_tangent | 0.4937 | -22.3% | 99% | [-29.5, -18.7] |
| oracle+1.5:inpaint_tangent | 0.5633 | -16.3% | 93% | [-22.3, -9.2] |
| detected:inpaint_tangent | 0.5176 | -20.4% | 96% | [-29.1, -15.2] |
| detected+1.5:inpaint_tangent | 0.5576 | -19.9% | 92% | [-32.9, -10.3] |
| pipe:inpaint_tangent | 0.5176 | -20.4% | 96% | [-29.1, -15.2] |
| oracle:plane_fill | 0.1528 | -78.6% | 100% | [-87.0, -71.4] |
| oracle+1.5:plane_fill | 0.1518 | -79.2% | 99% | [-87.1, -72.0] |
| detected:plane_fill | 0.1527 | -78.5% | 100% | [-87.6, -75.1] |
| detected+1.5:plane_fill | 0.1259 | -80.3% | 99% | [-88.4, -73.0] |
| pipe:plane_fill | 0.1527 | -78.5% | 100% | [-87.6, -75.1] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.1991)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1976 | -0.4% | 75% | [-0.6, -0.2] |
| oracle+1.5:inpaint_erp | 0.2000 | -0.2% | 51% | [-0.5, +0.3] |
| detected:inpaint_erp | 0.1980 | -0.3% | 69% | [-0.5, -0.1] |
| detected+1.5:inpaint_erp | 0.2019 | +0.1% | 49% | [-0.4, +0.6] |
| pipe:inpaint_erp | 0.1980 | -0.3% | 69% | [-0.5, -0.1] |
| oracle:inpaint_tangent | 0.1982 | -0.3% | 73% | [-0.4, -0.2] |
| oracle+1.5:inpaint_tangent | 0.2003 | +0.2% | 45% | [-0.1, +0.6] |
| detected:inpaint_tangent | 0.1982 | -0.2% | 66% | [-0.3, -0.1] |
| detected+1.5:inpaint_tangent | 0.2017 | +0.3% | 41% | [-0.0, +0.8] |
| pipe:inpaint_tangent | 0.1982 | -0.2% | 66% | [-0.3, -0.1] |
| oracle:plane_fill | 0.1981 | -0.3% | 69% | [-0.4, -0.1] |
| oracle+1.5:plane_fill | 0.1978 | -0.2% | 69% | [-0.6, -0.1] |
| detected:plane_fill | 0.1981 | -0.3% | 75% | [-0.5, -0.2] |
| detected+1.5:plane_fill | 0.1978 | -0.3% | 65% | [-0.6, -0.0] |
| pipe:plane_fill | 0.1981 | -0.3% | 75% | [-0.5, -0.2] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0632)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0606 | +3.1% | 32% | [+0.9, +5.6] |
| oracle+1.5:inpaint_erp | 0.0810 | +34.1% | 13% | [+22.2, +48.0] |
| detected:inpaint_erp | 0.0694 | +10.6% | 23% | [+3.9, +16.5] |
| detected+1.5:inpaint_erp | 0.0905 | +34.2% | 13% | [+24.8, +60.9] |
| pipe:inpaint_erp | 0.0694 | +10.6% | 23% | [+3.9, +16.5] |
| oracle:inpaint_tangent | 0.0597 | -0.5% | 54% | [-2.1, +2.9] |
| oracle+1.5:inpaint_tangent | 0.0824 | +34.1% | 8% | [+23.4, +45.6] |
| detected:inpaint_tangent | 0.0712 | +6.3% | 38% | [+0.0, +11.8] |
| detected+1.5:inpaint_tangent | 0.0967 | +37.5% | 8% | [+28.4, +63.4] |
| pipe:inpaint_tangent | 0.0712 | +6.3% | 38% | [+0.0, +11.8] |
| oracle:plane_fill | 0.0599 | +2.1% | 42% | [-1.0, +5.4] |
| oracle+1.5:plane_fill | 0.0671 | +6.5% | 28% | [+3.0, +13.5] |
| detected:plane_fill | 0.0588 | +1.1% | 44% | [-1.3, +5.9] |
| detected+1.5:plane_fill | 0.0696 | +7.6% | 27% | [+3.5, +15.2] |
| pipe:plane_fill | 0.0588 | +1.1% | 44% | [-1.3, +5.9] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.2385)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2278 | -5.9% | 99% | [-7.1, -3.3] |
| oracle+1.5:inpaint_erp | 0.2281 | -6.1% | 96% | [-11.8, -2.8] |
| detected:inpaint_erp | 0.2278 | -5.6% | 96% | [-7.1, -3.7] |
| detected+1.5:inpaint_erp | 0.2281 | -6.1% | 93% | [-12.2, -2.8] |
| pipe:inpaint_erp | 0.2278 | -5.6% | 96% | [-7.1, -3.7] |
| oracle:inpaint_tangent | 0.2256 | -6.0% | 99% | [-7.6, -3.6] |
| oracle+1.5:inpaint_tangent | 0.2346 | -3.5% | 87% | [-6.5, -1.1] |
| detected:inpaint_tangent | 0.2256 | -5.3% | 94% | [-7.6, -2.1] |
| detected+1.5:inpaint_tangent | 0.2346 | -3.5% | 83% | [-6.8, -1.0] |
| pipe:inpaint_tangent | 0.2256 | -5.3% | 94% | [-7.6, -2.1] |
| oracle:plane_fill | 0.2108 | -12.0% | 100% | [-16.3, -9.5] |
| oracle+1.5:plane_fill | 0.2101 | -11.7% | 99% | [-16.4, -10.2] |
| detected:plane_fill | 0.2108 | -12.1% | 99% | [-16.4, -9.6] |
| detected+1.5:plane_fill | 0.2101 | -13.0% | 97% | [-16.1, -10.3] |
| pipe:plane_fill | 0.2108 | -12.1% | 99% | [-16.4, -9.6] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1777)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3582 | +45.2% | 17% | [+22.6, +117.1] |
| oracle:inpaint_erp | 0.1313 | -23.1% | 70% | [-38.0, -4.9] |
| oracle+1.5:inpaint_erp | 0.1417 | -24.5% | 66% | [-34.3, -4.0] |
| detected:inpaint_erp | 0.1436 | -21.9% | 66% | [-35.3, -3.8] |
| detected+1.5:inpaint_erp | 0.1440 | -20.9% | 66% | [-32.4, -4.0] |
| deblock_oracle:inpaint_erp | 0.1277 | -32.9% | 75% | [-36.9, -20.1] |
| pipe_photometric:inpaint_erp | 0.1328 | -32.4% | 70% | [-38.4, -17.0] |
| pipe_cap_first:inpaint_erp | 0.1277 | -33.5% | 70% | [-39.2, -16.2] |
| oracle:inpaint_tangent | 0.1376 | -27.5% | 66% | [-40.4, -4.6] |
| oracle+1.5:inpaint_tangent | 0.1406 | -24.0% | 69% | [-39.4, -8.9] |
| detected:inpaint_tangent | 0.1403 | -21.1% | 69% | [-33.7, -6.2] |
| detected+1.5:inpaint_tangent | 0.1381 | -24.8% | 70% | [-39.6, -10.8] |
| deblock_oracle:inpaint_tangent | 0.1282 | -29.5% | 76% | [-38.5, -16.0] |
| pipe_photometric:inpaint_tangent | 0.1433 | -21.8% | 69% | [-35.3, -6.5] |
| pipe_cap_first:inpaint_tangent | 0.1411 | -23.1% | 73% | [-39.0, -11.0] |
| oracle:plane_fill | 0.1254 | -21.8% | 66% | [-42.7, -3.2] |
| oracle+1.5:plane_fill | 0.1188 | -21.7% | 69% | [-41.0, -5.9] |
| detected:plane_fill | 0.1184 | -21.5% | 73% | [-40.4, -6.4] |
| detected+1.5:plane_fill | 0.1292 | -22.8% | 72% | [-38.3, -10.2] |
| deblock_oracle:plane_fill | 0.1146 | -35.7% | 76% | [-53.2, -22.0] |
| pipe_photometric:plane_fill | 0.1266 | -35.4% | 72% | [-50.4, -21.8] |
| pipe_cap_first:plane_fill | 0.1211 | -35.6% | 73% | [-50.5, -22.4] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.2525)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2421 | -2.0% | 62% | [-3.0, -0.2] |
| oracle:inpaint_erp | 0.2556 | -0.5% | 63% | [-1.4, -0.0] |
| oracle+1.5:inpaint_erp | 0.2571 | -0.6% | 65% | [-1.5, -0.1] |
| detected:inpaint_erp | 0.2572 | -0.5% | 59% | [-1.4, +0.0] |
| detected+1.5:inpaint_erp | 0.2590 | -0.4% | 56% | [-1.3, +0.0] |
| deblock_oracle:inpaint_erp | 0.2361 | -3.4% | 68% | [-5.8, -1.7] |
| pipe_photometric:inpaint_erp | 0.2374 | -3.6% | 69% | [-6.4, -1.7] |
| pipe_cap_first:inpaint_erp | 0.2380 | -3.3% | 70% | [-6.5, -1.7] |
| oracle:inpaint_tangent | 0.2512 | -0.3% | 58% | [-1.1, +0.0] |
| oracle+1.5:inpaint_tangent | 0.2521 | -0.4% | 65% | [-1.0, -0.1] |
| detected:inpaint_tangent | 0.2522 | -0.4% | 59% | [-0.8, +0.0] |
| detected+1.5:inpaint_tangent | 0.2536 | -0.4% | 63% | [-1.1, -0.0] |
| deblock_oracle:inpaint_tangent | 0.2445 | -2.3% | 70% | [-4.1, -1.5] |
| pipe_photometric:inpaint_tangent | 0.2424 | -2.4% | 70% | [-4.6, -1.6] |
| pipe_cap_first:inpaint_tangent | 0.2397 | -3.1% | 70% | [-4.7, -1.7] |
| oracle:plane_fill | 0.2512 | -0.3% | 56% | [-1.1, +0.0] |
| oracle+1.5:plane_fill | 0.2521 | -0.5% | 66% | [-1.0, -0.1] |
| detected:plane_fill | 0.2522 | -0.3% | 58% | [-1.1, +0.0] |
| detected+1.5:plane_fill | 0.2536 | -0.4% | 63% | [-1.2, -0.0] |
| deblock_oracle:plane_fill | 0.2446 | -2.4% | 70% | [-4.1, -1.5] |
| pipe_photometric:plane_fill | 0.2424 | -2.5% | 72% | [-4.6, -1.6] |
| pipe_cap_first:plane_fill | 0.2397 | -3.0% | 72% | [-4.7, -1.7] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.0974)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0818 | -5.4% | 66% | [-10.3, -2.1] |
| oracle:inpaint_erp | 0.1142 | +4.0% | 42% | [-1.1, +13.9] |
| oracle+1.5:inpaint_erp | 0.1177 | +4.2% | 39% | [-0.3, +14.3] |
| detected:inpaint_erp | 0.1196 | +4.6% | 37% | [+0.0, +12.2] |
| detected+1.5:inpaint_erp | 0.1207 | +4.2% | 35% | [+0.0, +13.0] |
| deblock_oracle:inpaint_erp | 0.1043 | +1.0% | 48% | [-12.1, +8.0] |
| pipe_photometric:inpaint_erp | 0.1110 | +3.2% | 44% | [-5.9, +9.5] |
| pipe_cap_first:inpaint_erp | 0.1110 | +2.6% | 44% | [-5.9, +8.8] |
| oracle:inpaint_tangent | 0.1067 | +2.5% | 45% | [-2.0, +5.0] |
| oracle+1.5:inpaint_tangent | 0.1135 | +1.6% | 44% | [-1.5, +6.0] |
| detected:inpaint_tangent | 0.1143 | +0.5% | 44% | [-1.4, +5.2] |
| detected+1.5:inpaint_tangent | 0.1162 | +0.4% | 45% | [-3.4, +7.2] |
| deblock_oracle:inpaint_tangent | 0.0975 | -4.9% | 59% | [-8.5, +0.2] |
| pipe_photometric:inpaint_tangent | 0.1144 | +1.0% | 48% | [-5.7, +4.3] |
| pipe_cap_first:inpaint_tangent | 0.1144 | +1.3% | 46% | [-6.0, +4.4] |
| oracle:plane_fill | 0.1075 | +3.1% | 42% | [-1.2, +5.2] |
| oracle+1.5:plane_fill | 0.1135 | +2.5% | 45% | [-1.4, +5.7] |
| detected:plane_fill | 0.1149 | +0.5% | 45% | [-1.2, +4.2] |
| detected+1.5:plane_fill | 0.1149 | +0.6% | 45% | [-4.2, +6.0] |
| deblock_oracle:plane_fill | 0.0992 | -4.6% | 61% | [-7.9, +0.4] |
| pipe_photometric:plane_fill | 0.1030 | -0.8% | 52% | [-7.1, +2.8] |
| pipe_cap_first:plane_fill | 0.1065 | +0.3% | 49% | [-6.2, +3.3] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.2492)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2568 | +3.2% | 39% | [-0.5, +4.6] |
| oracle:inpaint_erp | 0.2508 | -2.1% | 68% | [-2.7, -0.9] |
| oracle+1.5:inpaint_erp | 0.2521 | -1.8% | 66% | [-2.6, -1.3] |
| detected:inpaint_erp | 0.2508 | -1.8% | 68% | [-2.6, -0.8] |
| detected+1.5:inpaint_erp | 0.2521 | -1.6% | 65% | [-3.0, -0.7] |
| deblock_oracle:inpaint_erp | 0.2207 | -4.5% | 76% | [-7.6, -3.3] |
| pipe_photometric:inpaint_erp | 0.2209 | -4.8% | 75% | [-8.1, -3.8] |
| pipe_cap_first:inpaint_erp | 0.2210 | -5.0% | 75% | [-8.0, -3.7] |
| oracle:inpaint_tangent | 0.2389 | -1.6% | 79% | [-2.2, -0.9] |
| oracle+1.5:inpaint_tangent | 0.2407 | -1.7% | 80% | [-2.4, -1.2] |
| detected:inpaint_tangent | 0.2427 | -1.6% | 76% | [-2.1, -0.9] |
| detected+1.5:inpaint_tangent | 0.2473 | -1.8% | 77% | [-2.6, -1.0] |
| deblock_oracle:inpaint_tangent | 0.2216 | -4.3% | 76% | [-6.5, -2.3] |
| pipe_photometric:inpaint_tangent | 0.2220 | -4.6% | 77% | [-6.0, -2.1] |
| pipe_cap_first:inpaint_tangent | 0.2219 | -4.6% | 77% | [-6.9, -1.8] |
| oracle:plane_fill | 0.2394 | -1.6% | 79% | [-2.3, -0.8] |
| oracle+1.5:plane_fill | 0.2412 | -1.8% | 80% | [-2.8, -1.2] |
| detected:plane_fill | 0.2431 | -1.7% | 80% | [-2.4, -0.9] |
| detected+1.5:plane_fill | 0.2473 | -1.8% | 77% | [-3.0, -1.1] |
| deblock_oracle:plane_fill | 0.2211 | -4.5% | 79% | [-6.2, -3.4] |
| pipe_photometric:plane_fill | 0.2214 | -4.7% | 80% | [-5.9, -3.6] |
| pipe_cap_first:plane_fill | 0.2213 | -4.6% | 80% | [-7.0, -3.7] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.335 | 1.002 | 0.475 |
| nadir+jpeg | 0.659 | 0.758 | 0.757 |
