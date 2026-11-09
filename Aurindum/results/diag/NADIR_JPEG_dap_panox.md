# Nadir + JPEG diagnosis: dap_panox

model `dap` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `none`, `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -0.88, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -0.12, p95 -0.12)

## nadir · protocol `none` · region AbsRel (raw median 0.2223)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2369 | -6.8% | 72% | [-19.5, -2.7] |
| oracle+1.5:inpaint_erp | 0.2089 | -2.8% | 60% | [-15.6, +2.7] |
| detected:inpaint_erp | 0.2369 | -6.8% | 72% | [-17.4, -2.7] |
| detected+1.5:inpaint_erp | 0.2089 | -2.8% | 60% | [-18.1, +2.7] |
| pipe:inpaint_erp | 0.2369 | -6.8% | 72% | [-17.4, -2.7] |
| oracle:inpaint_tangent | 0.2229 | -4.0% | 55% | [-15.8, +7.7] |
| oracle+1.5:inpaint_tangent | 0.3849 | +10.0% | 40% | [-3.6, +37.3] |
| detected:inpaint_tangent | 0.2280 | -2.6% | 52% | [-9.7, +7.7] |
| detected+1.5:inpaint_tangent | 0.3713 | +10.0% | 40% | [-3.7, +37.3] |
| pipe:inpaint_tangent | 0.2280 | -2.6% | 52% | [-9.7, +7.7] |
| oracle:plane_fill | 0.1425 | -23.5% | 80% | [-30.8, -7.5] |
| oracle+1.5:plane_fill | 0.1548 | -19.2% | 72% | [-35.0, -6.1] |
| detected:plane_fill | 0.1425 | -23.5% | 80% | [-30.8, -7.5] |
| detected+1.5:plane_fill | 0.1552 | -19.3% | 72% | [-35.0, -6.2] |
| pipe:plane_fill | 0.1425 | -23.5% | 80% | [-30.8, -7.5] |

## nadir · protocol `none` · outside AbsRel (raw median 0.2038)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1999 | -1.1% | 62% | [-2.6, +0.1] |
| oracle+1.5:inpaint_erp | 0.2001 | +0.3% | 48% | [-1.8, +1.6] |
| detected:inpaint_erp | 0.1999 | -1.1% | 62% | [-2.6, +0.1] |
| detected+1.5:inpaint_erp | 0.2001 | +0.3% | 48% | [-1.8, +1.6] |
| pipe:inpaint_erp | 0.1999 | -1.1% | 62% | [-2.6, +0.1] |
| oracle:inpaint_tangent | 0.1978 | -1.1% | 68% | [-2.1, -0.1] |
| oracle+1.5:inpaint_tangent | 0.1979 | -0.3% | 52% | [-1.5, +1.0] |
| detected:inpaint_tangent | 0.1978 | -1.1% | 65% | [-2.1, -0.0] |
| detected+1.5:inpaint_tangent | 0.1979 | -0.3% | 52% | [-1.5, +1.0] |
| pipe:inpaint_tangent | 0.1978 | -1.1% | 65% | [-2.1, -0.0] |
| oracle:plane_fill | 0.1978 | -1.1% | 65% | [-2.2, -0.1] |
| oracle+1.5:plane_fill | 0.1974 | -0.7% | 60% | [-1.7, +0.4] |
| detected:plane_fill | 0.1978 | -1.2% | 65% | [-2.2, -0.1] |
| detected+1.5:plane_fill | 0.1974 | -0.7% | 57% | [-1.7, +0.4] |
| pipe:plane_fill | 0.1978 | -1.2% | 65% | [-2.2, -0.1] |

## nadir · protocol `none` · ring AbsRel (raw median 0.1336)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1270 | +0.8% | 45% | [-1.3, +2.6] |
| oracle+1.5:inpaint_erp | 0.1382 | +4.8% | 32% | [+0.4, +10.8] |
| detected:inpaint_erp | 0.1361 | +0.8% | 45% | [-1.3, +2.6] |
| detected+1.5:inpaint_erp | 0.1469 | +4.8% | 32% | [+0.4, +10.8] |
| pipe:inpaint_erp | 0.1361 | +0.8% | 45% | [-1.3, +2.6] |
| oracle:inpaint_tangent | 0.1256 | -2.2% | 68% | [-4.2, -0.4] |
| oracle+1.5:inpaint_tangent | 0.1438 | +4.4% | 32% | [+0.2, +8.7] |
| detected:inpaint_tangent | 0.1450 | -2.2% | 68% | [-4.2, -0.4] |
| detected+1.5:inpaint_tangent | 0.1624 | +4.4% | 32% | [+0.2, +8.7] |
| pipe:inpaint_tangent | 0.1450 | -2.2% | 68% | [-4.2, -0.4] |
| oracle:plane_fill | 0.1264 | -2.4% | 62% | [-3.6, +0.2] |
| oracle+1.5:plane_fill | 0.1333 | -2.5% | 68% | [-6.0, -0.5] |
| detected:plane_fill | 0.1264 | -2.5% | 65% | [-3.7, -0.4] |
| detected+1.5:plane_fill | 0.1335 | -2.2% | 65% | [-6.0, -0.0] |
| pipe:plane_fill | 0.1264 | -2.5% | 65% | [-3.7, -0.4] |

## nadir · protocol `none` · all AbsRel (raw median 0.2160)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2030 | -2.8% | 75% | [-6.5, -1.7] |
| oracle+1.5:inpaint_erp | 0.2063 | -2.1% | 62% | [-3.9, +0.6] |
| detected:inpaint_erp | 0.2047 | -2.8% | 75% | [-6.5, -1.7] |
| detected+1.5:inpaint_erp | 0.2063 | -2.1% | 62% | [-4.2, +0.6] |
| pipe:inpaint_erp | 0.2047 | -2.8% | 75% | [-6.5, -1.7] |
| oracle:inpaint_tangent | 0.2052 | -2.6% | 57% | [-4.6, +1.2] |
| oracle+1.5:inpaint_tangent | 0.2280 | +2.5% | 40% | [-2.0, +3.9] |
| detected:inpaint_tangent | 0.2139 | -2.0% | 55% | [-3.6, +1.5] |
| detected+1.5:inpaint_tangent | 0.2300 | +2.7% | 40% | [-2.1, +4.0] |
| pipe:inpaint_tangent | 0.2139 | -2.0% | 55% | [-3.6, +1.5] |
| oracle:plane_fill | 0.1981 | -4.2% | 80% | [-9.6, -3.1] |
| oracle+1.5:plane_fill | 0.2113 | -3.9% | 72% | [-7.9, -2.7] |
| detected:plane_fill | 0.1981 | -4.2% | 80% | [-9.6, -3.1] |
| detected+1.5:plane_fill | 0.2114 | -3.9% | 72% | [-7.9, -2.7] |
| pipe:plane_fill | 0.1981 | -4.2% | 80% | [-9.6, -3.1] |

## nadir+jpeg · protocol `none` · region AbsRel (raw median 0.4063)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3778 | -1.6% | 70% | [-4.8, -0.3] |
| oracle:inpaint_erp | 0.2686 | -13.8% | 82% | [-33.8, -5.1] |
| oracle+1.5:inpaint_erp | 0.2748 | -13.4% | 82% | [-34.0, -5.9] |
| detected:inpaint_erp | 0.2705 | -13.8% | 82% | [-33.8, -5.1] |
| detected+1.5:inpaint_erp | 0.2826 | -13.4% | 82% | [-34.0, -5.9] |
| deblock_oracle:inpaint_erp | 0.2603 | -15.3% | 80% | [-28.6, -7.0] |
| pipe_photometric:inpaint_erp | 0.2703 | -15.0% | 78% | [-24.6, -6.9] |
| pipe_cap_first:inpaint_erp | 0.2698 | -15.2% | 78% | [-24.9, -7.0] |
| oracle:inpaint_tangent | 0.2622 | -12.8% | 88% | [-30.5, -6.9] |
| oracle+1.5:inpaint_tangent | 0.2657 | -13.5% | 90% | [-30.3, -5.8] |
| detected:inpaint_tangent | 0.2620 | -12.8% | 88% | [-30.5, -6.9] |
| detected+1.5:inpaint_tangent | 0.2696 | -13.5% | 90% | [-30.3, -5.8] |
| deblock_oracle:inpaint_tangent | 0.2557 | -15.3% | 85% | [-29.3, -9.9] |
| pipe_photometric:inpaint_tangent | 0.2833 | -13.8% | 80% | [-25.3, -8.8] |
| pipe_cap_first:inpaint_tangent | 0.2704 | -13.8% | 80% | [-27.7, -8.8] |
| oracle:plane_fill | 0.2636 | -13.9% | 85% | [-29.8, -5.9] |
| oracle+1.5:plane_fill | 0.2657 | -13.6% | 80% | [-30.6, -3.6] |
| detected:plane_fill | 0.2627 | -13.9% | 85% | [-29.8, -5.9] |
| detected+1.5:plane_fill | 0.2698 | -13.6% | 75% | [-30.4, -3.6] |
| deblock_oracle:plane_fill | 0.2506 | -15.3% | 88% | [-28.1, -11.1] |
| pipe_photometric:plane_fill | 0.2620 | -15.9% | 88% | [-26.8, -9.8] |
| pipe_cap_first:plane_fill | 0.2624 | -15.7% | 88% | [-29.5, -9.5] |

## nadir+jpeg · protocol `none` · outside AbsRel (raw median 0.3584)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3440 | -4.1% | 75% | [-6.4, -2.7] |
| oracle:inpaint_erp | 0.3664 | +0.1% | 48% | [-1.1, +2.4] |
| oracle+1.5:inpaint_erp | 0.3712 | +0.1% | 50% | [-2.2, +1.2] |
| detected:inpaint_erp | 0.3664 | +0.1% | 48% | [-1.1, +2.4] |
| detected+1.5:inpaint_erp | 0.3712 | +0.1% | 50% | [-2.2, +1.2] |
| deblock_oracle:inpaint_erp | 0.3356 | -3.2% | 62% | [-8.8, +2.6] |
| pipe_photometric:inpaint_erp | 0.3367 | -3.4% | 57% | [-8.5, +2.7] |
| pipe_cap_first:inpaint_erp | 0.3369 | -3.5% | 60% | [-8.4, +2.2] |
| oracle:inpaint_tangent | 0.3542 | -1.1% | 72% | [-2.7, -0.3] |
| oracle+1.5:inpaint_tangent | 0.3537 | -1.4% | 72% | [-2.5, -0.6] |
| detected:inpaint_tangent | 0.3542 | -1.1% | 72% | [-2.7, -0.3] |
| detected+1.5:inpaint_tangent | 0.3537 | -1.4% | 72% | [-2.5, -0.6] |
| deblock_oracle:inpaint_tangent | 0.3264 | -7.4% | 70% | [-10.1, -3.5] |
| pipe_photometric:inpaint_tangent | 0.3274 | -6.7% | 68% | [-9.4, -3.2] |
| pipe_cap_first:inpaint_tangent | 0.3265 | -7.0% | 68% | [-10.4, -3.4] |
| oracle:plane_fill | 0.3542 | -1.1% | 72% | [-2.7, -0.3] |
| oracle+1.5:plane_fill | 0.3537 | -1.4% | 70% | [-2.5, -0.6] |
| detected:plane_fill | 0.3542 | -1.1% | 72% | [-2.7, -0.3] |
| detected+1.5:plane_fill | 0.3537 | -1.4% | 70% | [-2.5, -0.6] |
| deblock_oracle:plane_fill | 0.3265 | -7.4% | 70% | [-10.1, -3.5] |
| pipe_photometric:plane_fill | 0.3275 | -6.7% | 68% | [-9.3, -3.2] |
| pipe_cap_first:plane_fill | 0.3266 | -7.0% | 68% | [-10.4, -3.5] |

## nadir+jpeg · protocol `none` · ring AbsRel (raw median 0.2597)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2451 | -2.4% | 68% | [-6.1, -0.3] |
| oracle:inpaint_erp | 0.2531 | +2.2% | 42% | [-1.6, +7.4] |
| oracle+1.5:inpaint_erp | 0.2572 | +1.6% | 42% | [-1.5, +6.7] |
| detected:inpaint_erp | 0.2524 | +2.2% | 42% | [-1.6, +7.4] |
| detected+1.5:inpaint_erp | 0.2625 | +1.6% | 42% | [-1.5, +6.7] |
| deblock_oracle:inpaint_erp | 0.2565 | +5.5% | 40% | [-1.8, +10.7] |
| pipe_photometric:inpaint_erp | 0.2614 | +4.1% | 40% | [-3.0, +9.5] |
| pipe_cap_first:inpaint_erp | 0.2607 | +3.8% | 40% | [-3.4, +9.5] |
| oracle:inpaint_tangent | 0.2500 | -1.7% | 68% | [-5.7, -0.5] |
| oracle+1.5:inpaint_tangent | 0.2539 | -2.3% | 70% | [-6.0, -0.9] |
| detected:inpaint_tangent | 0.2500 | -1.7% | 68% | [-5.7, -0.5] |
| detected+1.5:inpaint_tangent | 0.2539 | -2.3% | 70% | [-6.0, -0.9] |
| deblock_oracle:inpaint_tangent | 0.2368 | -2.2% | 65% | [-10.2, +0.1] |
| pipe_photometric:inpaint_tangent | 0.2502 | -1.9% | 60% | [-9.7, +1.2] |
| pipe_cap_first:inpaint_tangent | 0.2498 | -2.2% | 60% | [-11.0, +1.1] |
| oracle:plane_fill | 0.2498 | -1.7% | 68% | [-5.7, -0.6] |
| oracle+1.5:plane_fill | 0.2535 | -2.3% | 68% | [-5.9, -0.8] |
| detected:plane_fill | 0.2498 | -1.7% | 68% | [-5.7, -0.6] |
| detected+1.5:plane_fill | 0.2535 | -2.3% | 68% | [-5.9, -0.8] |
| deblock_oracle:plane_fill | 0.2369 | -2.2% | 65% | [-10.4, -0.1] |
| pipe_photometric:plane_fill | 0.2503 | -2.2% | 60% | [-9.7, +1.2] |
| pipe_cap_first:plane_fill | 0.2494 | -2.5% | 60% | [-11.2, +1.4] |

## nadir+jpeg · protocol `none` · all AbsRel (raw median 0.3522)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3360 | -4.0% | 72% | [-5.9, -1.9] |
| oracle:inpaint_erp | 0.3377 | -3.2% | 75% | [-5.9, -1.2] |
| oracle+1.5:inpaint_erp | 0.3430 | -3.3% | 80% | [-6.2, -1.3] |
| detected:inpaint_erp | 0.3377 | -3.2% | 75% | [-5.9, -1.2] |
| detected+1.5:inpaint_erp | 0.3430 | -3.3% | 80% | [-6.2, -1.3] |
| deblock_oracle:inpaint_erp | 0.3185 | -7.0% | 70% | [-15.3, -3.5] |
| pipe_photometric:inpaint_erp | 0.3192 | -6.3% | 68% | [-15.2, -3.3] |
| pipe_cap_first:inpaint_erp | 0.3194 | -6.4% | 68% | [-15.4, -3.5] |
| oracle:inpaint_tangent | 0.3407 | -4.2% | 92% | [-6.4, -1.7] |
| oracle+1.5:inpaint_tangent | 0.3431 | -4.3% | 85% | [-6.2, -2.3] |
| detected:inpaint_tangent | 0.3407 | -4.2% | 92% | [-6.4, -1.7] |
| detected+1.5:inpaint_tangent | 0.3431 | -4.3% | 85% | [-6.2, -2.3] |
| deblock_oracle:inpaint_tangent | 0.3081 | -10.1% | 78% | [-16.4, -6.3] |
| pipe_photometric:inpaint_tangent | 0.3100 | -9.8% | 80% | [-15.2, -5.5] |
| pipe_cap_first:inpaint_tangent | 0.3096 | -10.1% | 78% | [-15.5, -6.2] |
| oracle:plane_fill | 0.3423 | -4.2% | 90% | [-6.4, -1.9] |
| oracle+1.5:plane_fill | 0.3437 | -4.4% | 80% | [-6.4, -2.2] |
| detected:plane_fill | 0.3423 | -4.2% | 90% | [-6.4, -1.9] |
| detected+1.5:plane_fill | 0.3438 | -4.4% | 80% | [-6.4, -2.1] |
| deblock_oracle:plane_fill | 0.3082 | -9.5% | 80% | [-16.7, -6.2] |
| pipe_photometric:plane_fill | 0.3100 | -9.6% | 82% | [-15.2, -5.6] |
| pipe_cap_first:plane_fill | 0.3097 | -9.9% | 80% | [-15.5, -6.1] |

## nadir · protocol `align-all` · region AbsRel (raw median 0.1123)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0955 | -12.4% | 70% | [-39.5, -5.1] |
| oracle+1.5:inpaint_erp | 0.0779 | -12.2% | 70% | [-51.1, -1.8] |
| detected:inpaint_erp | 0.0955 | -12.4% | 70% | [-32.1, -5.1] |
| detected+1.5:inpaint_erp | 0.0779 | -12.2% | 70% | [-52.5, -1.8] |
| pipe:inpaint_erp | 0.0955 | -12.4% | 70% | [-32.1, -5.1] |
| oracle:inpaint_tangent | 0.0980 | -7.4% | 57% | [-21.8, +31.8] |
| oracle+1.5:inpaint_tangent | 0.1505 | +21.1% | 40% | [-3.5, +55.0] |
| detected:inpaint_tangent | 0.0980 | -4.2% | 55% | [-17.0, +31.8] |
| detected+1.5:inpaint_tangent | 0.1505 | +21.1% | 40% | [-5.2, +55.0] |
| pipe:inpaint_tangent | 0.0980 | -4.2% | 55% | [-17.0, +31.8] |
| oracle:plane_fill | 0.0485 | -21.7% | 72% | [-51.8, -10.6] |
| oracle+1.5:plane_fill | 0.0521 | -17.4% | 62% | [-49.9, +6.2] |
| detected:plane_fill | 0.0489 | -21.7% | 72% | [-51.8, -10.6] |
| detected+1.5:plane_fill | 0.0519 | -17.6% | 62% | [-50.5, +5.4] |
| pipe:plane_fill | 0.0489 | -21.7% | 72% | [-51.8, -10.6] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.1001)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0993 | +0.7% | 48% | [-0.9, +2.3] |
| oracle+1.5:inpaint_erp | 0.0994 | +1.9% | 35% | [+0.3, +3.0] |
| detected:inpaint_erp | 0.0993 | +1.1% | 45% | [-0.6, +2.7] |
| detected+1.5:inpaint_erp | 0.1001 | +1.9% | 35% | [+0.3, +3.6] |
| pipe:inpaint_erp | 0.0993 | +1.1% | 45% | [-0.6, +2.7] |
| oracle:inpaint_tangent | 0.0983 | +0.6% | 48% | [-1.0, +1.5] |
| oracle+1.5:inpaint_tangent | 0.1015 | +1.9% | 28% | [+0.5, +3.9] |
| detected:inpaint_tangent | 0.0991 | +1.0% | 45% | [-1.0, +2.5] |
| detected+1.5:inpaint_tangent | 0.1031 | +1.9% | 28% | [+0.5, +4.2] |
| pipe:inpaint_tangent | 0.0991 | +1.0% | 45% | [-1.0, +2.5] |
| oracle:plane_fill | 0.0983 | +0.5% | 48% | [-1.0, +1.5] |
| oracle+1.5:plane_fill | 0.0989 | +0.9% | 32% | [+0.2, +2.4] |
| detected:plane_fill | 0.0982 | +0.3% | 50% | [-1.2, +1.5] |
| detected+1.5:plane_fill | 0.0989 | +1.1% | 30% | [+0.2, +2.4] |
| pipe:plane_fill | 0.0982 | +0.3% | 50% | [-1.2, +1.5] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0455)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0444 | +4.6% | 42% | [-2.0, +8.5] |
| oracle+1.5:inpaint_erp | 0.0529 | +16.8% | 25% | [+8.0, +23.4] |
| detected:inpaint_erp | 0.0508 | +6.7% | 38% | [-0.4, +11.2] |
| detected+1.5:inpaint_erp | 0.0571 | +16.8% | 25% | [+8.0, +23.7] |
| pipe:inpaint_erp | 0.0508 | +6.7% | 38% | [-0.4, +11.2] |
| oracle:inpaint_tangent | 0.0466 | +2.2% | 40% | [-1.9, +9.6] |
| oracle+1.5:inpaint_tangent | 0.0633 | +24.5% | 18% | [+12.9, +51.8] |
| detected:inpaint_tangent | 0.0541 | +3.7% | 38% | [-0.9, +13.6] |
| detected+1.5:inpaint_tangent | 0.0665 | +24.5% | 18% | [+12.9, +51.8] |
| pipe:inpaint_tangent | 0.0541 | +3.7% | 38% | [-0.9, +13.6] |
| oracle:plane_fill | 0.0469 | +1.7% | 40% | [-1.3, +7.8] |
| oracle+1.5:plane_fill | 0.0516 | +7.9% | 30% | [+2.1, +14.3] |
| detected:plane_fill | 0.0469 | +1.7% | 40% | [-0.6, +8.1] |
| detected+1.5:plane_fill | 0.0514 | +9.1% | 28% | [+3.2, +15.5] |
| pipe:plane_fill | 0.0469 | +1.7% | 40% | [-0.6, +8.1] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.1144)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1073 | -1.9% | 57% | [-8.7, +3.0] |
| oracle+1.5:inpaint_erp | 0.1112 | -2.2% | 55% | [-5.7, +3.6] |
| detected:inpaint_erp | 0.1073 | -1.9% | 57% | [-8.7, +3.0] |
| detected+1.5:inpaint_erp | 0.1112 | -2.2% | 55% | [-5.7, +3.6] |
| pipe:inpaint_erp | 0.1073 | -1.9% | 57% | [-8.7, +3.0] |
| oracle:inpaint_tangent | 0.1058 | -2.4% | 57% | [-5.5, +3.0] |
| oracle+1.5:inpaint_tangent | 0.1254 | +4.5% | 40% | [-0.4, +15.1] |
| detected:inpaint_tangent | 0.1058 | -1.8% | 55% | [-4.9, +3.1] |
| detected+1.5:inpaint_tangent | 0.1254 | +4.9% | 40% | [-0.4, +15.1] |
| pipe:inpaint_tangent | 0.1058 | -1.8% | 55% | [-4.9, +3.1] |
| oracle:plane_fill | 0.0974 | -5.3% | 70% | [-9.2, -1.1] |
| oracle+1.5:plane_fill | 0.0980 | -2.9% | 57% | [-7.6, +1.5] |
| detected:plane_fill | 0.0971 | -5.3% | 70% | [-9.2, -1.1] |
| detected+1.5:plane_fill | 0.0987 | -3.0% | 57% | [-7.6, +1.4] |
| pipe:plane_fill | 0.0971 | -5.3% | 70% | [-9.2, -1.1] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1732)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1667 | -4.1% | 60% | [-26.6, +2.3] |
| oracle:inpaint_erp | 0.0862 | -25.1% | 62% | [-60.8, +2.2] |
| oracle+1.5:inpaint_erp | 0.0781 | -23.4% | 65% | [-61.1, -1.0] |
| detected:inpaint_erp | 0.0862 | -25.1% | 62% | [-60.8, +2.2] |
| detected+1.5:inpaint_erp | 0.0781 | -23.4% | 65% | [-61.1, -1.0] |
| deblock_oracle:inpaint_erp | 0.0916 | -33.2% | 75% | [-63.1, -23.6] |
| pipe_photometric:inpaint_erp | 0.0937 | -33.1% | 78% | [-65.9, -23.6] |
| pipe_cap_first:inpaint_erp | 0.0939 | -33.4% | 78% | [-66.4, -23.5] |
| oracle:inpaint_tangent | 0.1043 | -28.0% | 62% | [-58.1, +4.1] |
| oracle+1.5:inpaint_tangent | 0.0975 | -26.1% | 62% | [-53.7, +3.9] |
| detected:inpaint_tangent | 0.1043 | -28.0% | 62% | [-58.1, +4.1] |
| detected+1.5:inpaint_tangent | 0.0975 | -26.1% | 62% | [-53.7, +3.9] |
| deblock_oracle:inpaint_tangent | 0.0860 | -30.7% | 75% | [-61.9, -12.6] |
| pipe_photometric:inpaint_tangent | 0.0941 | -27.8% | 70% | [-59.3, -11.9] |
| pipe_cap_first:inpaint_tangent | 0.0852 | -30.2% | 72% | [-59.8, -14.8] |
| oracle:plane_fill | 0.0888 | -29.0% | 70% | [-57.2, -1.6] |
| oracle+1.5:plane_fill | 0.0872 | -29.5% | 75% | [-55.4, -3.0] |
| detected:plane_fill | 0.0888 | -29.0% | 70% | [-57.2, -1.6] |
| detected+1.5:plane_fill | 0.0866 | -29.6% | 75% | [-56.4, -3.1] |
| deblock_oracle:plane_fill | 0.0826 | -32.7% | 75% | [-64.3, -13.6] |
| pipe_photometric:plane_fill | 0.0810 | -30.2% | 78% | [-61.8, -11.6] |
| pipe_cap_first:plane_fill | 0.0807 | -32.1% | 78% | [-63.1, -11.7] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.2069)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1963 | -1.5% | 55% | [-4.2, +1.0] |
| oracle:inpaint_erp | 0.1936 | +0.2% | 48% | [-0.9, +1.9] |
| oracle+1.5:inpaint_erp | 0.1987 | -0.2% | 52% | [-1.5, +1.2] |
| detected:inpaint_erp | 0.1944 | +0.2% | 48% | [-0.9, +1.9] |
| detected+1.5:inpaint_erp | 0.1987 | -0.2% | 52% | [-1.5, +1.2] |
| deblock_oracle:inpaint_erp | 0.1903 | +0.1% | 50% | [-4.2, +4.1] |
| pipe_photometric:inpaint_erp | 0.1926 | -0.5% | 52% | [-4.2, +3.7] |
| pipe_cap_first:inpaint_erp | 0.1923 | -0.5% | 52% | [-4.2, +3.9] |
| oracle:inpaint_tangent | 0.2047 | +0.1% | 50% | [-1.3, +1.6] |
| oracle+1.5:inpaint_tangent | 0.2071 | +0.3% | 45% | [-0.8, +1.5] |
| detected:inpaint_tangent | 0.2047 | +0.1% | 50% | [-1.3, +1.6] |
| detected+1.5:inpaint_tangent | 0.2071 | +0.3% | 45% | [-0.8, +1.5] |
| deblock_oracle:inpaint_tangent | 0.1974 | +0.2% | 45% | [-2.4, +3.3] |
| pipe_photometric:inpaint_tangent | 0.2011 | +0.4% | 45% | [-2.3, +2.8] |
| pipe_cap_first:inpaint_tangent | 0.2009 | +0.3% | 45% | [-2.1, +2.9] |
| oracle:plane_fill | 0.2047 | +0.0% | 50% | [-1.3, +1.5] |
| oracle+1.5:plane_fill | 0.2071 | +0.3% | 48% | [-0.8, +1.5] |
| detected:plane_fill | 0.2047 | +0.0% | 50% | [-1.3, +1.5] |
| detected+1.5:plane_fill | 0.2071 | +0.3% | 48% | [-0.8, +1.5] |
| deblock_oracle:plane_fill | 0.1973 | +0.2% | 45% | [-2.5, +3.3] |
| pipe_photometric:plane_fill | 0.2006 | +0.4% | 45% | [-2.4, +2.8] |
| pipe_cap_first:plane_fill | 0.2005 | +0.3% | 45% | [-2.2, +2.8] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.1129)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0828 | -5.3% | 57% | [-11.7, +1.1] |
| oracle:inpaint_erp | 0.0842 | -0.1% | 50% | [-6.8, +4.5] |
| oracle+1.5:inpaint_erp | 0.0856 | -0.4% | 52% | [-4.9, +5.1] |
| detected:inpaint_erp | 0.0842 | -0.1% | 50% | [-6.8, +4.5] |
| detected+1.5:inpaint_erp | 0.0856 | -0.4% | 52% | [-4.9, +5.1] |
| deblock_oracle:inpaint_erp | 0.0859 | -7.1% | 60% | [-26.4, +4.9] |
| pipe_photometric:inpaint_erp | 0.0877 | -8.1% | 57% | [-23.9, +7.0] |
| pipe_cap_first:inpaint_erp | 0.0882 | -6.6% | 57% | [-23.9, +7.1] |
| oracle:inpaint_tangent | 0.1023 | -0.4% | 52% | [-4.7, +4.8] |
| oracle+1.5:inpaint_tangent | 0.1037 | +2.1% | 45% | [-3.2, +6.1] |
| detected:inpaint_tangent | 0.1023 | -0.4% | 52% | [-4.7, +4.8] |
| detected+1.5:inpaint_tangent | 0.1037 | +2.1% | 45% | [-3.2, +6.1] |
| deblock_oracle:inpaint_tangent | 0.0879 | -7.3% | 62% | [-20.1, +2.5] |
| pipe_photometric:inpaint_tangent | 0.0863 | -5.3% | 57% | [-18.7, +4.4] |
| pipe_cap_first:inpaint_tangent | 0.0875 | -5.8% | 57% | [-19.1, +4.9] |
| oracle:plane_fill | 0.1022 | -0.6% | 52% | [-4.9, +4.7] |
| oracle+1.5:plane_fill | 0.1035 | +2.2% | 45% | [-3.4, +6.6] |
| detected:plane_fill | 0.1022 | -0.6% | 52% | [-4.9, +4.7] |
| detected+1.5:plane_fill | 0.1034 | +2.2% | 45% | [-3.5, +6.5] |
| deblock_oracle:plane_fill | 0.0878 | -7.2% | 62% | [-20.1, +2.5] |
| pipe_photometric:plane_fill | 0.0850 | -5.6% | 62% | [-19.0, +1.5] |
| pipe_cap_first:plane_fill | 0.0868 | -5.5% | 57% | [-19.1, +1.7] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.2236)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2158 | -3.2% | 62% | [-6.6, +0.5] |
| oracle:inpaint_erp | 0.1818 | -3.5% | 60% | [-10.4, +0.6] |
| oracle+1.5:inpaint_erp | 0.1816 | -2.5% | 62% | [-10.1, +0.4] |
| detected:inpaint_erp | 0.1818 | -3.5% | 60% | [-10.4, +0.6] |
| detected+1.5:inpaint_erp | 0.1816 | -2.5% | 62% | [-10.1, +0.4] |
| deblock_oracle:inpaint_erp | 0.1858 | -12.9% | 70% | [-17.8, -2.8] |
| pipe_photometric:inpaint_erp | 0.1848 | -12.4% | 72% | [-16.4, -3.8] |
| pipe_cap_first:inpaint_erp | 0.1849 | -12.3% | 72% | [-15.8, -3.8] |
| oracle:inpaint_tangent | 0.1878 | -2.3% | 62% | [-7.1, +2.3] |
| oracle+1.5:inpaint_tangent | 0.1884 | -1.7% | 60% | [-7.0, +2.3] |
| detected:inpaint_tangent | 0.1878 | -2.3% | 62% | [-7.1, +2.3] |
| detected+1.5:inpaint_tangent | 0.1884 | -1.7% | 60% | [-7.0, +2.3] |
| deblock_oracle:inpaint_tangent | 0.1858 | -8.5% | 78% | [-11.6, -3.2] |
| pipe_photometric:inpaint_tangent | 0.1847 | -7.9% | 75% | [-11.1, -0.9] |
| pipe_cap_first:inpaint_tangent | 0.1856 | -8.1% | 70% | [-11.3, -2.5] |
| oracle:plane_fill | 0.1873 | -2.7% | 62% | [-7.2, +1.2] |
| oracle+1.5:plane_fill | 0.1880 | -2.2% | 60% | [-7.2, +1.1] |
| detected:plane_fill | 0.1873 | -2.7% | 62% | [-7.2, +1.2] |
| detected+1.5:plane_fill | 0.1879 | -2.2% | 60% | [-7.1, +1.0] |
| deblock_oracle:plane_fill | 0.1851 | -8.6% | 78% | [-12.0, -3.3] |
| pipe_photometric:plane_fill | 0.1866 | -8.2% | 72% | [-12.2, -3.1] |
| pipe_cap_first:plane_fill | 0.1862 | -8.3% | 70% | [-12.2, -3.3] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.776 | 0.901 | 0.824 |
| nadir+jpeg | 0.610 | 0.772 | 0.743 |
