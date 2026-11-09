# Nadir + JPEG diagnosis: dap_nyc

model `dap` · 147 frames · nadir cap below -62 deg · JPEG q8. Protocols: `none`, `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.83 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 88% of frames; detected edge minus true edge: median -0.83 deg (p5 -2.23, p95 -0.12)

## nadir · protocol `none` · region AbsRel (raw median 0.5238)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1902 | -49.0% | 87% | [-61.7, -35.2] |
| oracle+1.5:inpaint_erp | 0.2361 | -51.6% | 85% | [-55.1, -32.8] |
| detected:inpaint_erp | 0.1733 | -50.5% | 82% | [-65.5, -35.2] |
| detected+1.5:inpaint_erp | 0.1953 | -52.3% | 83% | [-63.7, -40.6] |
| pipe:inpaint_erp | 0.1733 | -50.5% | 82% | [-65.5, -35.2] |
| oracle:inpaint_tangent | 0.2923 | -36.3% | 82% | [-45.5, -25.4] |
| oracle+1.5:inpaint_tangent | 0.4683 | -7.2% | 63% | [-11.3, -2.8] |
| detected:inpaint_tangent | 0.4040 | -15.7% | 67% | [-27.8, -5.8] |
| detected+1.5:inpaint_tangent | 0.4630 | -5.0% | 57% | [-11.5, +0.2] |
| pipe:inpaint_tangent | 0.4040 | -15.7% | 67% | [-27.8, -5.8] |
| oracle:plane_fill | 0.0417 | -89.6% | 93% | [-91.3, -82.1] |
| oracle+1.5:plane_fill | 0.0494 | -86.6% | 81% | [-90.8, -78.0] |
| detected:plane_fill | 0.0426 | -89.3% | 79% | [-91.4, -80.4] |
| detected+1.5:plane_fill | 0.0455 | -86.2% | 73% | [-91.3, -78.2] |
| pipe:plane_fill | 0.0426 | -89.3% | 79% | [-91.4, -80.4] |

## nadir · protocol `none` · outside AbsRel (raw median 0.0432)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0436 | -0.1% | 51% | [-1.2, +0.8] |
| oracle+1.5:inpaint_erp | 0.0464 | +4.4% | 31% | [+1.8, +6.3] |
| detected:inpaint_erp | 0.0471 | +1.6% | 42% | [-0.0, +3.4] |
| detected+1.5:inpaint_erp | 0.0483 | +6.0% | 27% | [+4.1, +7.7] |
| pipe:inpaint_erp | 0.0471 | +1.6% | 42% | [-0.0, +3.4] |
| oracle:inpaint_tangent | 0.0432 | -0.7% | 54% | [-1.9, +0.7] |
| oracle+1.5:inpaint_tangent | 0.0481 | +6.7% | 21% | [+5.3, +10.1] |
| detected:inpaint_tangent | 0.0472 | +2.4% | 41% | [+0.2, +4.6] |
| detected+1.5:inpaint_tangent | 0.0506 | +12.1% | 16% | [+7.7, +14.9] |
| pipe:inpaint_tangent | 0.0472 | +2.4% | 41% | [+0.2, +4.6] |
| oracle:plane_fill | 0.0430 | -0.8% | 54% | [-1.8, +0.1] |
| oracle+1.5:plane_fill | 0.0451 | +1.3% | 44% | [-0.2, +3.4] |
| detected:plane_fill | 0.0460 | +0.4% | 48% | [-1.7, +1.8] |
| detected+1.5:plane_fill | 0.0476 | +4.2% | 38% | [+1.3, +6.0] |
| pipe:plane_fill | 0.0460 | +0.4% | 48% | [-1.7, +1.8] |

## nadir · protocol `none` · ring AbsRel (raw median 0.0364)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0324 | -7.7% | 60% | [-12.5, -2.6] |
| oracle+1.5:inpaint_erp | 0.0443 | +47.3% | 27% | [+27.6, +60.7] |
| detected:inpaint_erp | 0.0368 | +16.0% | 43% | [-1.6, +26.8] |
| detected+1.5:inpaint_erp | 0.0471 | +67.7% | 22% | [+50.6, +100.8] |
| pipe:inpaint_erp | 0.0368 | +16.0% | 43% | [-1.6, +26.8] |
| oracle:inpaint_tangent | 0.0304 | -13.7% | 67% | [-18.3, -8.7] |
| oracle+1.5:inpaint_tangent | 0.0649 | +97.4% | 10% | [+72.6, +114.4] |
| detected:inpaint_tangent | 0.0388 | +30.9% | 39% | [+5.4, +55.2] |
| detected+1.5:inpaint_tangent | 0.0741 | +135.6% | 9% | [+121.1, +168.6] |
| pipe:inpaint_tangent | 0.0388 | +30.9% | 39% | [+5.4, +55.2] |
| oracle:plane_fill | 0.0307 | -14.7% | 70% | [-18.9, -10.5] |
| oracle+1.5:plane_fill | 0.0372 | +15.2% | 44% | [-1.0, +27.4] |
| detected:plane_fill | 0.0311 | -6.6% | 53% | [-14.7, +4.7] |
| detected+1.5:plane_fill | 0.0369 | +34.4% | 37% | [+18.3, +51.9] |
| pipe:plane_fill | 0.0311 | -6.6% | 53% | [-14.7, +4.7] |

## nadir · protocol `none` · all AbsRel (raw median 0.1372)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0729 | -34.2% | 86% | [-45.7, -21.5] |
| oracle+1.5:inpaint_erp | 0.0781 | -35.1% | 76% | [-39.3, -20.3] |
| detected:inpaint_erp | 0.0726 | -33.4% | 75% | [-47.4, -19.5] |
| detected+1.5:inpaint_erp | 0.0721 | -35.5% | 71% | [-41.9, -21.5] |
| pipe:inpaint_erp | 0.0726 | -33.4% | 75% | [-47.4, -19.5] |
| oracle:inpaint_tangent | 0.0981 | -25.8% | 82% | [-35.9, -17.2] |
| oracle+1.5:inpaint_tangent | 0.1280 | -1.9% | 54% | [-5.5, +1.5] |
| detected:inpaint_tangent | 0.1113 | -8.7% | 65% | [-18.5, -2.6] |
| detected+1.5:inpaint_tangent | 0.1286 | +0.2% | 50% | [-5.5, +6.0] |
| pipe:inpaint_tangent | 0.1113 | -8.7% | 65% | [-18.5, -2.6] |
| oracle:plane_fill | 0.0470 | -61.4% | 93% | [-65.4, -51.8] |
| oracle+1.5:plane_fill | 0.0499 | -58.0% | 76% | [-63.4, -41.0] |
| detected:plane_fill | 0.0473 | -59.7% | 79% | [-64.8, -47.6] |
| detected+1.5:plane_fill | 0.0500 | -57.9% | 71% | [-63.3, -37.1] |
| pipe:plane_fill | 0.0473 | -59.7% | 79% | [-64.8, -47.6] |

## nadir+jpeg · protocol `none` · region AbsRel (raw median 0.3219)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3316 | +0.3% | 47% | [-1.0, +2.8] |
| oracle:inpaint_erp | 0.2581 | -8.2% | 68% | [-14.3, -2.3] |
| oracle+1.5:inpaint_erp | 0.2811 | -4.1% | 67% | [-10.8, -2.0] |
| detected:inpaint_erp | 0.2802 | -2.1% | 59% | [-6.7, -0.2] |
| detected+1.5:inpaint_erp | 0.2853 | -4.1% | 62% | [-10.6, -1.2] |
| deblock_oracle:inpaint_erp | 0.2430 | -11.2% | 71% | [-16.5, -5.2] |
| pipe_photometric:inpaint_erp | 0.2781 | -6.1% | 66% | [-9.8, -3.2] |
| pipe_cap_first:inpaint_erp | 0.2776 | -6.3% | 65% | [-9.8, -3.3] |
| oracle:inpaint_tangent | 0.2673 | -3.2% | 63% | [-8.4, -1.0] |
| oracle+1.5:inpaint_tangent | 0.2831 | +0.7% | 46% | [-1.3, +1.7] |
| detected:inpaint_tangent | 0.2801 | +0.0% | 40% | [+0.0, +0.8] |
| detected+1.5:inpaint_tangent | 0.2839 | +0.2% | 35% | [+0.0, +1.8] |
| deblock_oracle:inpaint_tangent | 0.2487 | -6.7% | 66% | [-10.3, -3.3] |
| pipe_photometric:inpaint_tangent | 0.2785 | +2.8% | 41% | [+0.2, +4.6] |
| pipe_cap_first:inpaint_tangent | 0.2719 | +2.5% | 45% | [-1.1, +3.7] |
| oracle:plane_fill | 0.2664 | -3.0% | 62% | [-8.1, -1.3] |
| oracle+1.5:plane_fill | 0.2753 | -0.7% | 52% | [-2.2, +1.2] |
| detected:plane_fill | 0.2761 | +0.0% | 43% | [-0.3, +0.6] |
| detected+1.5:plane_fill | 0.2786 | +0.0% | 40% | [+0.0, +1.2] |
| deblock_oracle:plane_fill | 0.2504 | -5.9% | 71% | [-10.9, -4.3] |
| pipe_photometric:plane_fill | 0.2688 | +1.3% | 47% | [-2.7, +3.5] |
| pipe_cap_first:plane_fill | 0.2680 | +0.5% | 50% | [-2.5, +2.5] |

## nadir+jpeg · protocol `none` · outside AbsRel (raw median 0.1675)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1600 | -7.3% | 86% | [-8.6, -6.2] |
| oracle:inpaint_erp | 0.1868 | +7.8% | 10% | [+6.5, +9.7] |
| oracle+1.5:inpaint_erp | 0.1870 | +7.3% | 8% | [+5.9, +9.6] |
| detected:inpaint_erp | 0.1869 | +6.3% | 7% | [+4.3, +7.8] |
| detected+1.5:inpaint_erp | 0.1913 | +6.0% | 8% | [+4.6, +8.5] |
| deblock_oracle:inpaint_erp | 0.1763 | +3.0% | 41% | [+0.5, +4.2] |
| pipe_photometric:inpaint_erp | 0.1764 | +2.1% | 44% | [-0.3, +5.6] |
| pipe_cap_first:inpaint_erp | 0.1763 | +2.2% | 44% | [-0.2, +5.5] |
| oracle:inpaint_tangent | 0.1809 | +5.2% | 12% | [+4.0, +6.0] |
| oracle+1.5:inpaint_tangent | 0.1806 | +5.5% | 10% | [+4.4, +6.5] |
| detected:inpaint_tangent | 0.1774 | +4.7% | 12% | [+3.3, +5.7] |
| detected+1.5:inpaint_tangent | 0.1780 | +4.8% | 11% | [+4.2, +6.4] |
| deblock_oracle:inpaint_tangent | 0.1695 | -1.7% | 56% | [-4.1, +0.3] |
| pipe_photometric:inpaint_tangent | 0.1753 | -0.1% | 52% | [-2.0, +2.1] |
| pipe_cap_first:inpaint_tangent | 0.1715 | -0.1% | 51% | [-2.0, +2.3] |
| oracle:plane_fill | 0.1809 | +5.2% | 11% | [+4.0, +6.0] |
| oracle+1.5:plane_fill | 0.1806 | +5.5% | 10% | [+4.4, +6.5] |
| detected:plane_fill | 0.1774 | +4.7% | 11% | [+3.3, +5.7] |
| detected+1.5:plane_fill | 0.1780 | +5.0% | 11% | [+4.2, +6.4] |
| deblock_oracle:plane_fill | 0.1695 | -1.6% | 56% | [-4.1, +0.3] |
| pipe_photometric:plane_fill | 0.1727 | -0.1% | 52% | [-2.0, +2.1] |
| pipe_cap_first:plane_fill | 0.1717 | -0.0% | 51% | [-2.3, +2.1] |

## nadir+jpeg · protocol `none` · ring AbsRel (raw median 0.1628)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1600 | -6.2% | 69% | [-8.2, -3.6] |
| oracle:inpaint_erp | 0.2246 | +18.8% | 6% | [+15.5, +23.1] |
| oracle+1.5:inpaint_erp | 0.2257 | +18.4% | 9% | [+14.6, +24.1] |
| detected:inpaint_erp | 0.2247 | +15.2% | 6% | [+10.0, +21.3] |
| detected+1.5:inpaint_erp | 0.2415 | +16.6% | 8% | [+11.6, +24.1] |
| deblock_oracle:inpaint_erp | 0.2139 | +17.3% | 17% | [+12.0, +23.6] |
| pipe_photometric:inpaint_erp | 0.2238 | +21.3% | 24% | [+10.8, +29.4] |
| pipe_cap_first:inpaint_erp | 0.2238 | +19.9% | 24% | [+10.7, +29.7] |
| oracle:inpaint_tangent | 0.2058 | +13.5% | 5% | [+10.1, +16.2] |
| oracle+1.5:inpaint_tangent | 0.2150 | +13.3% | 6% | [+10.7, +16.9] |
| detected:inpaint_tangent | 0.2228 | +12.1% | 6% | [+8.3, +16.2] |
| detected+1.5:inpaint_tangent | 0.2431 | +13.1% | 5% | [+10.0, +18.3] |
| deblock_oracle:inpaint_tangent | 0.2009 | +11.9% | 24% | [+6.7, +17.3] |
| pipe_photometric:inpaint_tangent | 0.2238 | +15.4% | 26% | [+9.3, +26.8] |
| pipe_cap_first:inpaint_tangent | 0.2238 | +15.6% | 25% | [+9.1, +27.8] |
| oracle:plane_fill | 0.2060 | +13.3% | 5% | [+10.0, +16.5] |
| oracle+1.5:plane_fill | 0.2160 | +13.0% | 7% | [+10.5, +16.9] |
| detected:plane_fill | 0.2233 | +12.0% | 6% | [+8.5, +16.5] |
| detected+1.5:plane_fill | 0.2371 | +12.8% | 5% | [+9.6, +18.3] |
| deblock_oracle:plane_fill | 0.2009 | +11.7% | 24% | [+6.7, +17.8] |
| pipe_photometric:plane_fill | 0.2233 | +15.4% | 26% | [+9.3, +26.2] |
| pipe_cap_first:plane_fill | 0.2213 | +15.7% | 25% | [+9.6, +27.2] |

## nadir+jpeg · protocol `none` · all AbsRel (raw median 0.2246)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2135 | -5.1% | 75% | [-6.6, -4.4] |
| oracle:inpaint_erp | 0.2080 | +1.3% | 44% | [-0.3, +2.4] |
| oracle+1.5:inpaint_erp | 0.2102 | +1.9% | 40% | [+0.8, +2.6] |
| detected:inpaint_erp | 0.2093 | +0.7% | 37% | [+0.0, +2.3] |
| detected+1.5:inpaint_erp | 0.2140 | +0.9% | 34% | [+0.0, +2.5] |
| deblock_oracle:inpaint_erp | 0.1954 | -5.7% | 70% | [-7.8, -2.3] |
| pipe_photometric:inpaint_erp | 0.2045 | -1.9% | 60% | [-5.4, -0.5] |
| pipe_cap_first:inpaint_erp | 0.2034 | -2.3% | 59% | [-5.3, -0.1] |
| oracle:inpaint_tangent | 0.2020 | +1.7% | 39% | [+0.4, +2.6] |
| oracle+1.5:inpaint_tangent | 0.2164 | +3.2% | 29% | [+1.9, +3.9] |
| detected:inpaint_tangent | 0.2161 | +2.2% | 26% | [+0.4, +3.7] |
| detected+1.5:inpaint_tangent | 0.2192 | +3.1% | 24% | [+1.2, +4.2] |
| deblock_oracle:inpaint_tangent | 0.1889 | -5.9% | 71% | [-8.0, -3.1] |
| pipe_photometric:inpaint_tangent | 0.2087 | +0.2% | 49% | [-1.7, +3.0] |
| pipe_cap_first:inpaint_tangent | 0.2037 | +0.3% | 49% | [-2.8, +2.3] |
| oracle:plane_fill | 0.2027 | +1.6% | 41% | [+0.2, +2.9] |
| oracle+1.5:plane_fill | 0.2121 | +3.1% | 31% | [+1.8, +3.6] |
| detected:plane_fill | 0.2197 | +1.9% | 28% | [+0.5, +3.4] |
| detected+1.5:plane_fill | 0.2192 | +2.5% | 25% | [+1.0, +4.0] |
| deblock_oracle:plane_fill | 0.1895 | -5.6% | 71% | [-8.0, -3.6] |
| pipe_photometric:plane_fill | 0.2011 | -0.7% | 52% | [-2.4, +2.1] |
| pipe_cap_first:plane_fill | 0.2011 | -0.5% | 52% | [-3.4, +2.1] |

## nadir · protocol `align-all` · region AbsRel (raw median 0.5051)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1852 | -52.0% | 88% | [-66.0, -46.0] |
| oracle+1.5:inpaint_erp | 0.2073 | -53.0% | 88% | [-63.2, -42.9] |
| detected:inpaint_erp | 0.1740 | -59.6% | 85% | [-67.8, -43.4] |
| detected+1.5:inpaint_erp | 0.1591 | -53.1% | 88% | [-73.6, -42.9] |
| pipe:inpaint_erp | 0.1740 | -59.6% | 85% | [-67.8, -43.4] |
| oracle:inpaint_tangent | 0.2662 | -43.4% | 83% | [-53.0, -31.6] |
| oracle+1.5:inpaint_tangent | 0.4442 | -9.0% | 66% | [-13.6, -6.1] |
| detected:inpaint_tangent | 0.3864 | -17.2% | 69% | [-29.0, -11.6] |
| detected+1.5:inpaint_tangent | 0.4439 | -8.7% | 62% | [-13.3, -4.4] |
| pipe:inpaint_tangent | 0.3864 | -17.2% | 69% | [-29.0, -11.6] |
| oracle:plane_fill | 0.0377 | -88.8% | 95% | [-92.4, -85.9] |
| oracle+1.5:plane_fill | 0.0453 | -88.3% | 84% | [-91.8, -80.8] |
| detected:plane_fill | 0.0401 | -88.7% | 82% | [-92.0, -84.1] |
| detected+1.5:plane_fill | 0.0509 | -88.3% | 78% | [-91.2, -80.4] |
| pipe:plane_fill | 0.0401 | -88.7% | 82% | [-92.0, -84.1] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.0495)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0480 | -0.5% | 59% | [-1.1, -0.1] |
| oracle+1.5:inpaint_erp | 0.0512 | +3.3% | 28% | [+2.5, +4.3] |
| detected:inpaint_erp | 0.0504 | +1.7% | 38% | [+0.5, +3.0] |
| detected+1.5:inpaint_erp | 0.0523 | +5.8% | 22% | [+4.5, +7.2] |
| pipe:inpaint_erp | 0.0504 | +1.7% | 38% | [+0.5, +3.0] |
| oracle:inpaint_tangent | 0.0490 | -1.3% | 67% | [-1.9, -0.7] |
| oracle+1.5:inpaint_tangent | 0.0529 | +6.1% | 9% | [+5.4, +7.4] |
| detected:inpaint_tangent | 0.0517 | +2.1% | 38% | [+0.4, +4.4] |
| detected+1.5:inpaint_tangent | 0.0550 | +9.5% | 10% | [+8.2, +12.2] |
| pipe:inpaint_tangent | 0.0517 | +2.1% | 38% | [+0.4, +4.4] |
| oracle:plane_fill | 0.0479 | -1.4% | 70% | [-2.0, -1.1] |
| oracle+1.5:plane_fill | 0.0483 | +1.3% | 41% | [+0.2, +2.5] |
| detected:plane_fill | 0.0489 | +0.0% | 49% | [-0.7, +0.9] |
| detected+1.5:plane_fill | 0.0502 | +3.6% | 35% | [+1.4, +4.8] |
| pipe:plane_fill | 0.0489 | +0.0% | 49% | [-0.7, +0.9] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0328)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0342 | -8.7% | 71% | [-10.0, -6.5] |
| oracle+1.5:inpaint_erp | 0.0481 | +5.4% | 47% | [-2.5, +27.4] |
| detected:inpaint_erp | 0.0389 | -2.1% | 52% | [-6.1, +2.0] |
| detected+1.5:inpaint_erp | 0.0523 | +19.5% | 35% | [+7.2, +40.8] |
| pipe:inpaint_erp | 0.0389 | -2.1% | 52% | [-6.1, +2.0] |
| oracle:inpaint_tangent | 0.0303 | -6.9% | 75% | [-10.1, -4.8] |
| oracle+1.5:inpaint_tangent | 0.0667 | +60.9% | 16% | [+33.2, +95.0] |
| detected:inpaint_tangent | 0.0416 | +3.3% | 42% | [+0.1, +6.2] |
| detected+1.5:inpaint_tangent | 0.0761 | +76.2% | 14% | [+48.0, +119.7] |
| pipe:inpaint_tangent | 0.0416 | +3.3% | 42% | [+0.1, +6.2] |
| oracle:plane_fill | 0.0296 | -12.5% | 80% | [-16.2, -7.1] |
| oracle+1.5:plane_fill | 0.0345 | -1.7% | 55% | [-5.7, +0.6] |
| detected:plane_fill | 0.0306 | -4.1% | 60% | [-10.8, -0.9] |
| detected+1.5:plane_fill | 0.0359 | +4.8% | 43% | [-0.5, +12.1] |
| pipe:plane_fill | 0.0306 | -4.1% | 60% | [-10.8, -0.9] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.1397)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0728 | -34.0% | 88% | [-46.7, -17.8] |
| oracle+1.5:inpaint_erp | 0.0801 | -29.9% | 79% | [-40.4, -19.0] |
| detected:inpaint_erp | 0.0753 | -28.8% | 76% | [-46.7, -18.3] |
| detected+1.5:inpaint_erp | 0.0754 | -33.0% | 69% | [-42.6, -21.6] |
| pipe:inpaint_erp | 0.0753 | -28.8% | 76% | [-46.7, -18.3] |
| oracle:inpaint_tangent | 0.1009 | -23.7% | 82% | [-30.2, -15.1] |
| oracle+1.5:inpaint_tangent | 0.1312 | -2.1% | 54% | [-4.9, +1.2] |
| detected:inpaint_tangent | 0.1166 | -9.9% | 63% | [-14.7, -3.0] |
| detected+1.5:inpaint_tangent | 0.1313 | -0.5% | 52% | [-6.2, +8.0] |
| pipe:inpaint_tangent | 0.1166 | -9.9% | 63% | [-14.7, -3.0] |
| oracle:plane_fill | 0.0485 | -62.4% | 93% | [-66.3, -51.6] |
| oracle+1.5:plane_fill | 0.0515 | -58.2% | 73% | [-63.9, -37.6] |
| detected:plane_fill | 0.0487 | -61.7% | 76% | [-64.3, -46.7] |
| detected+1.5:plane_fill | 0.0532 | -57.5% | 71% | [-62.0, -34.4] |
| pipe:plane_fill | 0.0487 | -61.7% | 76% | [-64.3, -46.7] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1575)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1794 | +1.9% | 46% | [-2.1, +5.6] |
| oracle:inpaint_erp | 0.0834 | -29.8% | 83% | [-40.4, -20.4] |
| oracle+1.5:inpaint_erp | 0.0885 | -24.6% | 82% | [-30.9, -17.0] |
| detected:inpaint_erp | 0.0954 | -19.4% | 71% | [-25.2, -11.6] |
| detected+1.5:inpaint_erp | 0.0935 | -21.0% | 74% | [-34.1, -15.6] |
| deblock_oracle:inpaint_erp | 0.0814 | -33.1% | 86% | [-44.2, -26.4] |
| pipe_photometric:inpaint_erp | 0.0997 | -20.9% | 78% | [-29.2, -15.4] |
| pipe_cap_first:inpaint_erp | 0.0983 | -20.9% | 78% | [-29.6, -15.3] |
| oracle:inpaint_tangent | 0.0932 | -16.1% | 82% | [-24.1, -10.6] |
| oracle+1.5:inpaint_tangent | 0.1019 | -9.0% | 70% | [-13.4, -5.5] |
| detected:inpaint_tangent | 0.1135 | -4.4% | 60% | [-9.1, -2.3] |
| detected+1.5:inpaint_tangent | 0.1156 | -4.2% | 54% | [-7.1, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0900 | -21.3% | 82% | [-26.6, -15.7] |
| pipe_photometric:inpaint_tangent | 0.1306 | -0.4% | 50% | [-6.5, +4.6] |
| pipe_cap_first:inpaint_tangent | 0.1234 | -3.0% | 55% | [-9.3, +1.6] |
| oracle:plane_fill | 0.0941 | -18.6% | 80% | [-26.3, -11.5] |
| oracle+1.5:plane_fill | 0.0955 | -13.0% | 70% | [-19.4, -7.5] |
| detected:plane_fill | 0.1033 | -6.4% | 61% | [-10.3, -3.3] |
| detected+1.5:plane_fill | 0.1084 | -4.8% | 56% | [-8.6, +0.0] |
| deblock_oracle:plane_fill | 0.0906 | -21.9% | 83% | [-30.5, -18.4] |
| pipe_photometric:plane_fill | 0.1103 | -4.5% | 55% | [-13.1, +1.1] |
| pipe_cap_first:plane_fill | 0.1104 | -5.7% | 59% | [-14.4, -0.5] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.1525)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1450 | -4.2% | 84% | [-5.8, -2.8] |
| oracle:inpaint_erp | 0.1561 | +0.9% | 40% | [+0.1, +2.4] |
| oracle+1.5:inpaint_erp | 0.1578 | +1.7% | 36% | [+0.5, +2.5] |
| detected:inpaint_erp | 0.1525 | +0.6% | 33% | [+0.0, +2.4] |
| detected+1.5:inpaint_erp | 0.1540 | +0.9% | 33% | [+0.0, +2.3] |
| deblock_oracle:inpaint_erp | 0.1457 | -5.2% | 76% | [-6.8, -3.6] |
| pipe_photometric:inpaint_erp | 0.1459 | -2.9% | 65% | [-4.8, -1.9] |
| pipe_cap_first:inpaint_erp | 0.1461 | -2.9% | 65% | [-4.2, -1.9] |
| oracle:inpaint_tangent | 0.1552 | +0.6% | 38% | [+0.1, +1.3] |
| oracle+1.5:inpaint_tangent | 0.1570 | +2.2% | 25% | [+1.5, +2.7] |
| detected:inpaint_tangent | 0.1525 | +1.5% | 24% | [+0.7, +2.4] |
| detected+1.5:inpaint_tangent | 0.1560 | +2.0% | 20% | [+1.2, +3.0] |
| deblock_oracle:inpaint_tangent | 0.1439 | -4.3% | 80% | [-5.9, -3.3] |
| pipe_photometric:inpaint_tangent | 0.1439 | -2.5% | 61% | [-3.9, -0.2] |
| pipe_cap_first:inpaint_tangent | 0.1440 | -2.4% | 61% | [-3.9, -0.4] |
| oracle:plane_fill | 0.1552 | +0.7% | 38% | [+0.1, +1.3] |
| oracle+1.5:plane_fill | 0.1571 | +2.1% | 25% | [+1.5, +2.6] |
| detected:plane_fill | 0.1525 | +1.6% | 23% | [+0.7, +2.4] |
| detected+1.5:plane_fill | 0.1560 | +1.9% | 20% | [+1.2, +3.0] |
| deblock_oracle:plane_fill | 0.1439 | -4.4% | 80% | [-5.9, -3.2] |
| pipe_photometric:plane_fill | 0.1439 | -2.5% | 61% | [-4.0, -0.4] |
| pipe_cap_first:plane_fill | 0.1440 | -2.5% | 61% | [-3.9, -0.4] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.0996)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1050 | -3.7% | 69% | [-4.9, -2.3] |
| oracle:inpaint_erp | 0.1032 | -4.5% | 60% | [-10.7, -0.4] |
| oracle+1.5:inpaint_erp | 0.1034 | -3.9% | 59% | [-7.5, -0.6] |
| detected:inpaint_erp | 0.1032 | -2.2% | 55% | [-5.1, +0.0] |
| detected+1.5:inpaint_erp | 0.1027 | -1.9% | 55% | [-5.6, +0.0] |
| deblock_oracle:inpaint_erp | 0.1006 | -13.3% | 63% | [-18.7, -4.8] |
| pipe_photometric:inpaint_erp | 0.1054 | -7.7% | 62% | [-13.2, -2.6] |
| pipe_cap_first:inpaint_erp | 0.1056 | -7.7% | 61% | [-12.9, -2.3] |
| oracle:inpaint_tangent | 0.1041 | -2.6% | 59% | [-5.9, -0.2] |
| oracle+1.5:inpaint_tangent | 0.1050 | -0.7% | 52% | [-2.3, +1.7] |
| detected:inpaint_tangent | 0.1046 | +0.0% | 46% | [-0.7, +0.2] |
| detected+1.5:inpaint_tangent | 0.1050 | +0.0% | 37% | [+0.0, +2.8] |
| deblock_oracle:inpaint_tangent | 0.1047 | -6.0% | 66% | [-12.4, -2.6] |
| pipe_photometric:inpaint_tangent | 0.1046 | +0.3% | 48% | [-3.6, +7.5] |
| pipe_cap_first:inpaint_tangent | 0.1052 | +0.3% | 49% | [-3.5, +6.1] |
| oracle:plane_fill | 0.1029 | -2.7% | 59% | [-5.9, -0.3] |
| oracle+1.5:plane_fill | 0.1030 | -0.6% | 52% | [-2.1, +1.7] |
| detected:plane_fill | 0.1034 | +0.0% | 45% | [-0.3, +0.6] |
| detected+1.5:plane_fill | 0.1041 | +0.8% | 37% | [+0.0, +2.6] |
| deblock_oracle:plane_fill | 0.1046 | -6.0% | 67% | [-12.3, -2.6] |
| pipe_photometric:plane_fill | 0.1048 | +0.3% | 48% | [-3.8, +7.3] |
| pipe_cap_first:plane_fill | 0.1052 | +0.2% | 49% | [-4.0, +6.1] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.1554)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1512 | -2.9% | 73% | [-3.9, -2.0] |
| oracle:inpaint_erp | 0.1424 | -2.6% | 69% | [-4.4, -2.0] |
| oracle+1.5:inpaint_erp | 0.1470 | -2.0% | 69% | [-3.0, -0.9] |
| detected:inpaint_erp | 0.1498 | -1.4% | 62% | [-2.5, -0.3] |
| detected+1.5:inpaint_erp | 0.1510 | -1.1% | 59% | [-2.7, -0.0] |
| deblock_oracle:inpaint_erp | 0.1341 | -10.7% | 89% | [-13.3, -8.4] |
| pipe_photometric:inpaint_erp | 0.1403 | -6.9% | 79% | [-9.7, -5.2] |
| pipe_cap_first:inpaint_erp | 0.1400 | -6.9% | 78% | [-9.2, -5.1] |
| oracle:inpaint_tangent | 0.1440 | -2.1% | 70% | [-3.3, -1.1] |
| oracle+1.5:inpaint_tangent | 0.1479 | -0.2% | 53% | [-1.1, +0.6] |
| detected:inpaint_tangent | 0.1469 | +0.0% | 48% | [-0.6, +0.0] |
| detected+1.5:inpaint_tangent | 0.1502 | +0.0% | 41% | [+0.0, +0.8] |
| deblock_oracle:inpaint_tangent | 0.1332 | -8.6% | 90% | [-10.5, -6.6] |
| pipe_photometric:inpaint_tangent | 0.1381 | -3.8% | 64% | [-5.0, -2.6] |
| pipe_cap_first:inpaint_tangent | 0.1378 | -4.3% | 65% | [-5.9, -3.0] |
| oracle:plane_fill | 0.1440 | -2.5% | 70% | [-3.6, -1.3] |
| oracle+1.5:plane_fill | 0.1468 | -0.4% | 58% | [-1.4, +0.1] |
| detected:plane_fill | 0.1469 | -0.1% | 51% | [-0.6, +0.0] |
| detected+1.5:plane_fill | 0.1492 | +0.0% | 42% | [-0.0, +0.4] |
| deblock_oracle:plane_fill | 0.1324 | -8.5% | 90% | [-10.8, -7.0] |
| pipe_photometric:plane_fill | 0.1371 | -4.5% | 67% | [-6.1, -3.3] |
| pipe_cap_first:plane_fill | 0.1371 | -5.1% | 67% | [-6.5, -3.3] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.470 | 0.983 | 0.812 |
| nadir+jpeg | 0.679 | 0.725 | 0.729 |
