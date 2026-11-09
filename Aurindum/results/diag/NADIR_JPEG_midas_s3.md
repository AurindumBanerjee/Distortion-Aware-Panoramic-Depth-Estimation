# Nadir + JPEG diagnosis: midas_s3

model `midas_dpt_hybrid_384` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -1.57, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 52% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +4.09)

## nadir · protocol `align-all` · region AbsRel (raw median 0.2476)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2388 | -5.8% | 72% | [-11.4, -2.2] |
| oracle+1.5:inpaint_erp | 0.2402 | -4.7% | 65% | [-8.9, -0.3] |
| detected:inpaint_erp | 0.2388 | -5.3% | 70% | [-9.7, -1.2] |
| detected+1.5:inpaint_erp | 0.2398 | -5.2% | 68% | [-8.9, -1.5] |
| pipe:inpaint_erp | 0.2388 | -5.3% | 70% | [-9.7, -1.2] |
| oracle:inpaint_tangent | 0.2173 | -10.5% | 80% | [-18.3, -5.9] |
| oracle+1.5:inpaint_tangent | 0.2351 | -4.5% | 70% | [-7.8, -0.6] |
| detected:inpaint_tangent | 0.2235 | -10.5% | 80% | [-16.8, -5.9] |
| detected+1.5:inpaint_tangent | 0.2285 | -4.0% | 70% | [-7.2, -0.6] |
| pipe:inpaint_tangent | 0.2235 | -10.5% | 80% | [-16.8, -5.9] |
| oracle:plane_fill | 0.2173 | -11.3% | 75% | [-19.9, -5.5] |
| oracle+1.5:plane_fill | 0.2351 | -4.5% | 70% | [-7.8, -0.6] |
| detected:plane_fill | 0.2235 | -11.3% | 78% | [-18.0, -5.7] |
| detected+1.5:plane_fill | 0.2285 | -4.0% | 70% | [-7.2, -0.6] |
| pipe:plane_fill | 0.2235 | -11.3% | 78% | [-18.0, -5.7] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.2214)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2505 | +11.4% | 10% | [+5.7, +18.6] |
| oracle+1.5:inpaint_erp | 0.2487 | +8.8% | 22% | [+6.1, +17.5] |
| detected:inpaint_erp | 0.2505 | +11.4% | 10% | [+5.3, +18.6] |
| detected+1.5:inpaint_erp | 0.2487 | +8.8% | 22% | [+6.1, +17.5] |
| pipe:inpaint_erp | 0.2505 | +11.4% | 10% | [+5.3, +18.6] |
| oracle:inpaint_tangent | 0.2525 | +17.6% | 8% | [+7.3, +24.6] |
| oracle+1.5:inpaint_tangent | 0.2481 | +9.1% | 20% | [+4.8, +15.1] |
| detected:inpaint_tangent | 0.2544 | +17.6% | 8% | [+6.9, +24.6] |
| detected+1.5:inpaint_tangent | 0.2481 | +9.1% | 20% | [+4.5, +15.1] |
| pipe:inpaint_tangent | 0.2544 | +17.6% | 8% | [+6.9, +24.6] |
| oracle:plane_fill | 0.2501 | +12.0% | 12% | [+4.5, +22.3] |
| oracle+1.5:plane_fill | 0.2481 | +9.1% | 22% | [+4.5, +15.1] |
| detected:plane_fill | 0.2525 | +14.0% | 10% | [+5.7, +23.6] |
| detected+1.5:plane_fill | 0.2481 | +9.1% | 22% | [+3.0, +15.1] |
| pipe:plane_fill | 0.2525 | +14.0% | 10% | [+5.7, +23.6] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.2158)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2297 | +3.3% | 30% | [+0.6, +7.2] |
| oracle+1.5:inpaint_erp | 0.2374 | +7.6% | 25% | [+3.0, +10.8] |
| detected:inpaint_erp | 0.2297 | +2.9% | 30% | [+0.6, +7.2] |
| detected+1.5:inpaint_erp | 0.2374 | +7.6% | 25% | [+3.1, +10.8] |
| pipe:inpaint_erp | 0.2297 | +2.9% | 30% | [+0.6, +7.2] |
| oracle:inpaint_tangent | 0.2272 | +2.9% | 42% | [-0.8, +7.2] |
| oracle+1.5:inpaint_tangent | 0.2311 | +6.2% | 40% | [-0.5, +9.6] |
| detected:inpaint_tangent | 0.2272 | +2.9% | 42% | [-2.1, +7.2] |
| detected+1.5:inpaint_tangent | 0.2311 | +6.2% | 40% | [-0.5, +9.6] |
| pipe:inpaint_tangent | 0.2272 | +2.9% | 42% | [-2.1, +7.2] |
| oracle:plane_fill | 0.2272 | +4.3% | 40% | [-0.6, +7.2] |
| oracle+1.5:plane_fill | 0.2311 | +6.2% | 38% | [-0.3, +9.6] |
| detected:plane_fill | 0.2272 | +4.2% | 40% | [-0.7, +9.4] |
| detected+1.5:plane_fill | 0.2311 | +6.2% | 38% | [-0.3, +9.6] |
| pipe:plane_fill | 0.2272 | +4.2% | 40% | [-0.7, +9.4] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.2227)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.2453 | +8.8% | 15% | [+2.9, +13.2] |
| oracle+1.5:inpaint_erp | 0.2422 | +7.2% | 18% | [+2.9, +11.9] |
| detected:inpaint_erp | 0.2453 | +8.8% | 12% | [+2.8, +13.2] |
| detected+1.5:inpaint_erp | 0.2422 | +7.2% | 22% | [+2.9, +11.9] |
| pipe:inpaint_erp | 0.2453 | +8.8% | 12% | [+2.8, +13.2] |
| oracle:inpaint_tangent | 0.2439 | +11.0% | 15% | [+6.6, +17.4] |
| oracle+1.5:inpaint_tangent | 0.2478 | +7.5% | 18% | [+3.1, +11.1] |
| detected:inpaint_tangent | 0.2500 | +11.0% | 12% | [+6.6, +17.4] |
| detected+1.5:inpaint_tangent | 0.2478 | +7.5% | 20% | [+2.7, +11.1] |
| pipe:inpaint_tangent | 0.2500 | +11.0% | 12% | [+6.6, +17.4] |
| oracle:plane_fill | 0.2437 | +9.4% | 20% | [+2.5, +14.6] |
| oracle+1.5:plane_fill | 0.2478 | +7.5% | 20% | [+2.4, +11.1] |
| detected:plane_fill | 0.2500 | +10.1% | 15% | [+3.1, +15.5] |
| detected+1.5:plane_fill | 0.2478 | +7.5% | 22% | [+1.5, +11.1] |
| pipe:plane_fill | 0.2500 | +10.1% | 15% | [+3.1, +15.5] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1718)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1838 | +0.6% | 50% | [-5.0, +11.6] |
| oracle:inpaint_erp | 0.1776 | +7.5% | 38% | [-2.0, +16.5] |
| oracle+1.5:inpaint_erp | 0.1854 | +1.8% | 48% | [-5.0, +12.5] |
| detected:inpaint_erp | 0.1882 | +0.0% | 15% | [+0.0, +1.4] |
| detected+1.5:inpaint_erp | 0.1882 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.2032 | +4.0% | 48% | [-11.3, +10.2] |
| pipe_photometric:inpaint_erp | 0.2046 | +1.8% | 48% | [-2.4, +15.7] |
| pipe_cap_first:inpaint_erp | 0.2043 | +1.8% | 48% | [-4.3, +15.4] |
| oracle:inpaint_tangent | 0.1772 | +6.1% | 32% | [+2.0, +18.4] |
| oracle+1.5:inpaint_tangent | 0.1790 | +5.7% | 30% | [+1.1, +16.3] |
| detected:inpaint_tangent | 0.1871 | +0.0% | 12% | [+0.0, +4.2] |
| detected+1.5:inpaint_tangent | 0.1837 | +0.0% | 8% | [+0.0, +1.6] |
| deblock_oracle:inpaint_tangent | 0.1740 | -0.3% | 50% | [-13.3, +8.1] |
| pipe_photometric:inpaint_tangent | 0.1779 | +2.1% | 45% | [-2.6, +14.7] |
| pipe_cap_first:inpaint_tangent | 0.1779 | +2.2% | 45% | [-2.9, +13.7] |
| oracle:plane_fill | 0.1772 | +3.2% | 38% | [-1.8, +16.6] |
| oracle+1.5:plane_fill | 0.1790 | +3.3% | 35% | [+0.0, +11.2] |
| detected:plane_fill | 0.1871 | +0.0% | 18% | [+0.0, +0.9] |
| detected+1.5:plane_fill | 0.1837 | +0.0% | 12% | [+0.0, +1.1] |
| deblock_oracle:plane_fill | 0.1812 | -4.6% | 52% | [-15.9, +6.3] |
| pipe_photometric:plane_fill | 0.1843 | +2.1% | 45% | [-2.6, +14.7] |
| pipe_cap_first:plane_fill | 0.1815 | +2.2% | 45% | [-2.9, +13.7] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.2509)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2465 | -1.3% | 62% | [-2.3, +0.4] |
| oracle:inpaint_erp | 0.2464 | -0.9% | 57% | [-3.1, +0.4] |
| oracle+1.5:inpaint_erp | 0.2469 | -0.7% | 55% | [-2.3, +0.9] |
| detected:inpaint_erp | 0.2458 | +0.0% | 28% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.2440 | +0.0% | 28% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.2574 | -1.0% | 55% | [-3.8, +0.5] |
| pipe_photometric:inpaint_erp | 0.2488 | -1.3% | 65% | [-2.6, +0.1] |
| pipe_cap_first:inpaint_erp | 0.2477 | -1.3% | 62% | [-2.3, +0.5] |
| oracle:inpaint_tangent | 0.2564 | +0.2% | 45% | [-1.9, +1.0] |
| oracle+1.5:inpaint_tangent | 0.2576 | -0.1% | 55% | [-1.7, +1.5] |
| detected:inpaint_tangent | 0.2508 | +0.0% | 28% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.2517 | +0.0% | 28% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.2507 | -0.9% | 65% | [-3.5, -0.1] |
| pipe_photometric:inpaint_tangent | 0.2419 | -1.0% | 57% | [-2.5, +0.3] |
| pipe_cap_first:inpaint_tangent | 0.2420 | -1.0% | 62% | [-2.5, +0.2] |
| oracle:plane_fill | 0.2564 | +0.2% | 48% | [-2.2, +0.9] |
| oracle+1.5:plane_fill | 0.2539 | -0.1% | 55% | [-2.1, +1.0] |
| detected:plane_fill | 0.2508 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.2465 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.2514 | -0.9% | 65% | [-3.7, +0.0] |
| pipe_photometric:plane_fill | 0.2419 | -1.0% | 57% | [-3.0, +0.3] |
| pipe_cap_first:plane_fill | 0.2420 | -1.0% | 62% | [-2.5, +0.2] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.2115)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2223 | -0.8% | 55% | [-3.5, +1.1] |
| oracle:inpaint_erp | 0.1990 | -2.7% | 65% | [-6.1, +0.0] |
| oracle+1.5:inpaint_erp | 0.2036 | -2.3% | 65% | [-6.4, +0.1] |
| detected:inpaint_erp | 0.2083 | +0.0% | 35% | [-0.3, +0.0] |
| detected+1.5:inpaint_erp | 0.2083 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.2017 | -3.6% | 62% | [-8.7, +0.5] |
| pipe_photometric:inpaint_erp | 0.2111 | -1.4% | 57% | [-5.0, +1.7] |
| pipe_cap_first:inpaint_erp | 0.2111 | -1.4% | 57% | [-4.9, +1.7] |
| oracle:inpaint_tangent | 0.2173 | -1.5% | 60% | [-3.9, +1.0] |
| oracle+1.5:inpaint_tangent | 0.2203 | +0.5% | 45% | [-3.6, +3.1] |
| detected:inpaint_tangent | 0.2111 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.2111 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.2231 | -0.4% | 55% | [-6.1, +1.2] |
| pipe_photometric:inpaint_tangent | 0.2111 | -2.7% | 65% | [-5.2, +0.3] |
| pipe_cap_first:inpaint_tangent | 0.2111 | -2.7% | 62% | [-5.2, +0.8] |
| oracle:plane_fill | 0.2173 | -2.0% | 60% | [-6.3, +1.0] |
| oracle+1.5:plane_fill | 0.2203 | +0.5% | 45% | [-3.9, +3.1] |
| detected:plane_fill | 0.2111 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.2111 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.2231 | -1.1% | 57% | [-6.1, +1.2] |
| pipe_photometric:plane_fill | 0.2111 | -2.7% | 70% | [-5.2, -0.4] |
| pipe_cap_first:plane_fill | 0.2111 | -2.7% | 68% | [-5.2, -0.2] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.2465)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2385 | -0.5% | 55% | [-1.7, +0.5] |
| oracle:inpaint_erp | 0.2413 | -0.2% | 52% | [-1.7, +1.7] |
| oracle+1.5:inpaint_erp | 0.2438 | -0.1% | 55% | [-2.4, +1.5] |
| detected:inpaint_erp | 0.2401 | +0.0% | 25% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.2389 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.2432 | -1.0% | 55% | [-3.4, +1.0] |
| pipe_photometric:inpaint_erp | 0.2430 | -0.1% | 50% | [-1.4, +1.0] |
| pipe_cap_first:inpaint_erp | 0.2467 | +0.2% | 48% | [-1.4, +1.0] |
| oracle:inpaint_tangent | 0.2522 | +0.4% | 42% | [-1.5, +1.4] |
| oracle+1.5:inpaint_tangent | 0.2535 | +0.4% | 45% | [-1.4, +2.1] |
| detected:inpaint_tangent | 0.2504 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.2474 | +0.0% | 22% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.2321 | -1.2% | 57% | [-2.5, +0.4] |
| pipe_photometric:inpaint_tangent | 0.2266 | -0.4% | 52% | [-1.5, +0.6] |
| pipe_cap_first:inpaint_tangent | 0.2275 | -0.4% | 52% | [-1.5, +0.6] |
| oracle:plane_fill | 0.2504 | +0.3% | 42% | [-1.6, +1.3] |
| oracle+1.5:plane_fill | 0.2434 | +0.2% | 48% | [-1.4, +1.9] |
| detected:plane_fill | 0.2478 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.2430 | +0.0% | 25% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.2348 | -1.6% | 60% | [-3.4, +0.3] |
| pipe_photometric:plane_fill | 0.2266 | -0.5% | 55% | [-1.8, +0.5] |
| pipe_cap_first:plane_fill | 0.2275 | -0.5% | 55% | [-1.6, +0.5] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.737 | 0.767 | 0.755 |
| nadir+jpeg | 0.890 | 0.828 | 0.859 |
