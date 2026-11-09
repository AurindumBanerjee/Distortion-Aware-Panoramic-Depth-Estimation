# Nadir + JPEG diagnosis: dap_stanford

model `dap` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `none`, `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 0% of frames; detected edge minus true edge: median -0.12 deg (p5 -0.12, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 0% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)

## nadir · protocol `none` · region AbsRel (raw median 0.3716)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1446 | -37.6% | 95% | [-51.6, -25.4] |
| oracle+1.5:inpaint_erp | 0.1350 | -39.0% | 95% | [-54.1, -16.7] |
| detected:inpaint_erp | 0.1446 | -37.6% | 95% | [-52.3, -25.4] |
| detected+1.5:inpaint_erp | 0.1350 | -39.0% | 95% | [-52.5, -16.7] |
| pipe:inpaint_erp | 0.1207 | -47.8% | 98% | [-65.3, -31.3] |
| oracle:inpaint_tangent | 0.1921 | -28.1% | 82% | [-39.0, -11.6] |
| oracle+1.5:inpaint_tangent | 0.2752 | -8.0% | 68% | [-15.3, -3.4] |
| detected:inpaint_tangent | 0.1921 | -28.1% | 82% | [-39.2, -11.6] |
| detected+1.5:inpaint_tangent | 0.2781 | -6.5% | 68% | [-11.7, -3.4] |
| pipe:inpaint_tangent | 0.1694 | -39.7% | 95% | [-48.7, -16.5] |
| oracle:plane_fill | 0.0727 | -72.3% | 98% | [-82.0, -50.4] |
| oracle+1.5:plane_fill | 0.0858 | -65.5% | 95% | [-78.2, -24.9] |
| detected:plane_fill | 0.0750 | -70.2% | 98% | [-80.7, -48.6] |
| detected+1.5:plane_fill | 0.0867 | -64.7% | 95% | [-78.1, -21.1] |
| pipe:plane_fill | 0.0697 | -78.9% | 98% | [-84.1, -54.5] |

## nadir · protocol `none` · outside AbsRel (raw median 0.1257)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1216 | -2.4% | 75% | [-4.7, -1.5] |
| oracle+1.5:inpaint_erp | 0.1224 | -2.5% | 72% | [-5.8, -1.1] |
| detected:inpaint_erp | 0.1216 | -2.4% | 75% | [-4.7, -1.5] |
| detected+1.5:inpaint_erp | 0.1224 | -2.5% | 72% | [-5.5, -1.1] |
| pipe:inpaint_erp | 0.0881 | -22.2% | 92% | [-25.5, -15.4] |
| oracle:inpaint_tangent | 0.1235 | -2.5% | 75% | [-3.7, -1.1] |
| oracle+1.5:inpaint_tangent | 0.1253 | -0.9% | 70% | [-2.0, -0.1] |
| detected:inpaint_tangent | 0.1235 | -2.5% | 75% | [-3.7, -1.1] |
| detected+1.5:inpaint_tangent | 0.1253 | -0.9% | 68% | [-1.9, -0.0] |
| pipe:inpaint_tangent | 0.0945 | -14.2% | 90% | [-19.6, -11.8] |
| oracle:plane_fill | 0.1236 | -2.4% | 75% | [-3.6, -0.8] |
| oracle+1.5:plane_fill | 0.1249 | -1.3% | 68% | [-2.2, -0.3] |
| detected:plane_fill | 0.1236 | -2.4% | 75% | [-3.6, -0.8] |
| detected+1.5:plane_fill | 0.1250 | -1.2% | 65% | [-2.2, -0.1] |
| pipe:plane_fill | 0.0881 | -24.7% | 95% | [-30.8, -20.5] |

## nadir · protocol `none` · ring AbsRel (raw median 0.0452)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0455 | +1.3% | 42% | [-4.9, +4.5] |
| oracle+1.5:inpaint_erp | 0.0628 | +26.4% | 22% | [+13.4, +48.3] |
| detected:inpaint_erp | 0.0455 | +2.0% | 40% | [-3.5, +4.5] |
| detected+1.5:inpaint_erp | 0.0645 | +27.9% | 22% | [+13.4, +49.6] |
| pipe:inpaint_erp | 0.0431 | -7.7% | 57% | [-16.5, +9.2] |
| oracle:inpaint_tangent | 0.0453 | -4.0% | 68% | [-5.5, -1.0] |
| oracle+1.5:inpaint_tangent | 0.0671 | +35.8% | 18% | [+23.4, +46.0] |
| detected:inpaint_tangent | 0.0453 | -3.5% | 65% | [-5.5, -0.4] |
| detected+1.5:inpaint_tangent | 0.0688 | +35.8% | 18% | [+23.4, +46.0] |
| pipe:inpaint_tangent | 0.0426 | -10.3% | 68% | [-20.6, -2.5] |
| oracle:plane_fill | 0.0461 | -3.8% | 57% | [-5.6, +1.0] |
| oracle+1.5:plane_fill | 0.0551 | +8.3% | 45% | [-2.5, +33.7] |
| detected:plane_fill | 0.0461 | -3.1% | 57% | [-5.6, +1.0] |
| detected+1.5:plane_fill | 0.0551 | +9.2% | 38% | [-2.1, +34.1] |
| pipe:plane_fill | 0.0430 | -10.5% | 65% | [-20.4, -1.4] |

## nadir · protocol `none` · all AbsRel (raw median 0.1681)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1294 | -14.5% | 92% | [-17.8, -9.9] |
| oracle+1.5:inpaint_erp | 0.1353 | -11.1% | 98% | [-15.4, -8.5] |
| detected:inpaint_erp | 0.1294 | -14.5% | 92% | [-17.8, -9.9] |
| detected+1.5:inpaint_erp | 0.1353 | -11.1% | 98% | [-15.4, -8.5] |
| pipe:inpaint_erp | 0.0965 | -29.7% | 100% | [-33.0, -22.6] |
| oracle:inpaint_tangent | 0.1368 | -9.0% | 92% | [-14.4, -5.3] |
| oracle+1.5:inpaint_tangent | 0.1380 | -2.6% | 75% | [-5.6, -1.6] |
| detected:inpaint_tangent | 0.1368 | -9.0% | 92% | [-14.4, -5.3] |
| detected+1.5:inpaint_tangent | 0.1380 | -2.3% | 75% | [-5.3, -1.4] |
| pipe:inpaint_tangent | 0.1029 | -23.1% | 98% | [-27.2, -17.3] |
| oracle:plane_fill | 0.1293 | -21.7% | 100% | [-25.1, -14.1] |
| oracle+1.5:plane_fill | 0.1381 | -13.5% | 98% | [-24.6, -7.5] |
| detected:plane_fill | 0.1293 | -20.2% | 100% | [-25.0, -12.4] |
| detected+1.5:plane_fill | 0.1382 | -13.2% | 98% | [-24.2, -6.0] |
| pipe:plane_fill | 0.0881 | -35.8% | 100% | [-39.2, -31.6] |

## nadir+jpeg · protocol `none` · region AbsRel (raw median 0.3352)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2450 | -20.1% | 88% | [-33.1, -7.4] |
| oracle:inpaint_erp | 0.1883 | -7.0% | 62% | [-26.5, +0.8] |
| oracle+1.5:inpaint_erp | 0.1942 | -7.8% | 68% | [-22.1, -1.6] |
| detected:inpaint_erp | 0.1931 | -7.0% | 62% | [-26.5, +0.8] |
| detected+1.5:inpaint_erp | 0.1965 | -7.8% | 68% | [-22.1, -1.6] |
| deblock_oracle:inpaint_erp | 0.1203 | -37.2% | 92% | [-50.9, -27.2] |
| pipe_photometric:inpaint_erp | 0.0777 | -63.6% | 90% | [-72.4, -49.0] |
| pipe_cap_first:inpaint_erp | 0.0773 | -64.6% | 90% | [-73.1, -49.9] |
| oracle:inpaint_tangent | 0.1526 | -21.2% | 80% | [-41.1, -8.0] |
| oracle+1.5:inpaint_tangent | 0.1542 | -18.7% | 75% | [-40.0, -5.5] |
| detected:inpaint_tangent | 0.1526 | -18.9% | 80% | [-41.1, -8.0] |
| detected+1.5:inpaint_tangent | 0.1542 | -18.3% | 75% | [-40.0, -5.5] |
| deblock_oracle:inpaint_tangent | 0.0994 | -57.6% | 92% | [-69.4, -38.4] |
| pipe_photometric:inpaint_tangent | 0.0638 | -71.5% | 90% | [-78.3, -60.8] |
| pipe_cap_first:inpaint_tangent | 0.0626 | -73.0% | 90% | [-78.9, -62.5] |
| oracle:plane_fill | 0.1534 | -15.4% | 68% | [-36.8, -2.1] |
| oracle+1.5:plane_fill | 0.1541 | -14.8% | 68% | [-35.8, -1.1] |
| detected:plane_fill | 0.1534 | -14.9% | 68% | [-36.8, -2.1] |
| detected+1.5:plane_fill | 0.1546 | -14.5% | 65% | [-34.3, +1.5] |
| deblock_oracle:plane_fill | 0.0998 | -51.9% | 92% | [-62.9, -33.0] |
| pipe_photometric:plane_fill | 0.0769 | -68.3% | 92% | [-75.9, -57.1] |
| pipe_cap_first:plane_fill | 0.0744 | -69.4% | 92% | [-75.9, -57.7] |

## nadir+jpeg · protocol `none` · outside AbsRel (raw median 0.2151)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1757 | -13.5% | 95% | [-19.5, -12.0] |
| oracle:inpaint_erp | 0.2248 | +0.1% | 48% | [-2.8, +8.6] |
| oracle+1.5:inpaint_erp | 0.2262 | +1.5% | 48% | [-2.6, +6.5] |
| detected:inpaint_erp | 0.2248 | +0.1% | 48% | [-2.7, +8.0] |
| detected+1.5:inpaint_erp | 0.2405 | +1.5% | 48% | [-2.5, +7.0] |
| deblock_oracle:inpaint_erp | 0.1737 | -11.8% | 75% | [-18.7, -5.4] |
| pipe_photometric:inpaint_erp | 0.1324 | -37.1% | 90% | [-43.0, -22.5] |
| pipe_cap_first:inpaint_erp | 0.1324 | -37.0% | 90% | [-43.1, -24.0] |
| oracle:inpaint_tangent | 0.2107 | -5.7% | 75% | [-9.3, -2.5] |
| oracle+1.5:inpaint_tangent | 0.2116 | -5.3% | 78% | [-9.6, -2.6] |
| detected:inpaint_tangent | 0.2115 | -5.7% | 78% | [-9.3, -2.5] |
| detected+1.5:inpaint_tangent | 0.2133 | -5.3% | 75% | [-9.1, -2.5] |
| deblock_oracle:inpaint_tangent | 0.1653 | -23.9% | 95% | [-29.2, -14.8] |
| pipe_photometric:inpaint_tangent | 0.1281 | -44.8% | 95% | [-46.8, -39.9] |
| pipe_cap_first:inpaint_tangent | 0.1277 | -45.0% | 95% | [-48.0, -39.0] |
| oracle:plane_fill | 0.2107 | -5.7% | 75% | [-9.2, -2.5] |
| oracle+1.5:plane_fill | 0.2116 | -5.3% | 78% | [-9.6, -2.6] |
| detected:plane_fill | 0.2115 | -5.7% | 78% | [-9.2, -2.5] |
| detected+1.5:plane_fill | 0.2133 | -5.3% | 75% | [-9.0, -2.5] |
| deblock_oracle:plane_fill | 0.1653 | -23.9% | 95% | [-29.1, -14.8] |
| pipe_photometric:plane_fill | 0.1280 | -44.3% | 95% | [-47.1, -38.6] |
| pipe_cap_first:plane_fill | 0.1277 | -44.6% | 95% | [-48.0, -37.6] |

## nadir+jpeg · protocol `none` · ring AbsRel (raw median 0.1731)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1090 | -28.6% | 95% | [-34.6, -20.0] |
| oracle:inpaint_erp | 0.1972 | +10.6% | 30% | [+2.4, +21.6] |
| oracle+1.5:inpaint_erp | 0.1889 | +9.8% | 32% | [+3.0, +23.0] |
| detected:inpaint_erp | 0.1972 | +10.6% | 28% | [+3.1, +22.0] |
| detected+1.5:inpaint_erp | 0.1889 | +11.0% | 30% | [+4.0, +27.1] |
| deblock_oracle:inpaint_erp | 0.1290 | -14.0% | 62% | [-28.3, +3.6] |
| pipe_photometric:inpaint_erp | 0.1014 | -35.7% | 82% | [-49.1, -15.5] |
| pipe_cap_first:inpaint_erp | 0.1020 | -35.0% | 82% | [-49.3, -16.4] |
| oracle:inpaint_tangent | 0.1645 | -3.7% | 55% | [-9.8, +2.0] |
| oracle+1.5:inpaint_tangent | 0.1615 | -2.5% | 57% | [-10.4, +1.9] |
| detected:inpaint_tangent | 0.1609 | -3.3% | 55% | [-9.4, +2.7] |
| detected+1.5:inpaint_tangent | 0.1626 | -1.6% | 55% | [-10.4, +1.9] |
| deblock_oracle:inpaint_tangent | 0.1074 | -34.5% | 85% | [-44.8, -27.8] |
| pipe_photometric:inpaint_tangent | 0.0995 | -48.0% | 80% | [-55.5, -39.5] |
| pipe_cap_first:inpaint_tangent | 0.0993 | -48.4% | 80% | [-56.3, -38.3] |
| oracle:plane_fill | 0.1645 | -3.1% | 55% | [-9.6, +2.0] |
| oracle+1.5:plane_fill | 0.1615 | -2.1% | 55% | [-9.8, +2.8] |
| detected:plane_fill | 0.1609 | -2.6% | 55% | [-9.2, +2.7] |
| detected+1.5:plane_fill | 0.1629 | -0.3% | 52% | [-8.3, +2.9] |
| deblock_oracle:plane_fill | 0.1073 | -34.6% | 85% | [-44.2, -27.1] |
| pipe_photometric:plane_fill | 0.0994 | -48.0% | 80% | [-55.6, -39.2] |
| pipe_cap_first:plane_fill | 0.0991 | -48.4% | 80% | [-56.3, -38.6] |

## nadir+jpeg · protocol `none` · all AbsRel (raw median 0.2375)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2019 | -13.8% | 98% | [-18.3, -11.5] |
| oracle:inpaint_erp | 0.2206 | +0.3% | 50% | [-4.1, +5.4] |
| oracle+1.5:inpaint_erp | 0.2231 | +1.6% | 48% | [-4.6, +6.3] |
| detected:inpaint_erp | 0.2206 | +0.3% | 50% | [-4.1, +5.4] |
| detected+1.5:inpaint_erp | 0.2272 | +2.6% | 45% | [-4.6, +6.3] |
| deblock_oracle:inpaint_erp | 0.1652 | -16.5% | 88% | [-25.5, -10.0] |
| pipe_photometric:inpaint_erp | 0.1289 | -41.5% | 92% | [-48.0, -33.8] |
| pipe_cap_first:inpaint_erp | 0.1289 | -41.4% | 92% | [-48.1, -36.5] |
| oracle:inpaint_tangent | 0.2062 | -6.5% | 80% | [-15.0, -3.5] |
| oracle+1.5:inpaint_tangent | 0.2076 | -6.7% | 78% | [-17.5, -3.4] |
| detected:inpaint_tangent | 0.2062 | -6.5% | 80% | [-15.0, -3.5] |
| detected+1.5:inpaint_tangent | 0.2076 | -6.7% | 78% | [-17.5, -3.4] |
| deblock_oracle:inpaint_tangent | 0.1523 | -28.8% | 98% | [-36.5, -18.3] |
| pipe_photometric:inpaint_tangent | 0.1223 | -48.9% | 95% | [-51.2, -44.0] |
| pipe_cap_first:inpaint_tangent | 0.1221 | -49.2% | 95% | [-51.5, -44.3] |
| oracle:plane_fill | 0.2069 | -5.3% | 80% | [-14.8, -2.4] |
| oracle+1.5:plane_fill | 0.2082 | -5.5% | 75% | [-16.8, -2.4] |
| detected:plane_fill | 0.2069 | -5.0% | 80% | [-14.8, -2.4] |
| detected+1.5:plane_fill | 0.2082 | -5.4% | 75% | [-16.8, -2.4] |
| deblock_oracle:plane_fill | 0.1527 | -27.3% | 98% | [-36.1, -18.1] |
| pipe_photometric:plane_fill | 0.1222 | -47.3% | 95% | [-49.8, -43.9] |
| pipe_cap_first:plane_fill | 0.1220 | -48.3% | 95% | [-50.2, -43.4] |

## nadir · protocol `align-all` · region AbsRel (raw median 0.2058)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0691 | -49.2% | 95% | [-64.9, -33.7] |
| oracle+1.5:inpaint_erp | 0.0941 | -41.5% | 92% | [-55.6, -30.4] |
| detected:inpaint_erp | 0.0640 | -49.2% | 95% | [-64.9, -33.7] |
| detected+1.5:inpaint_erp | 0.0941 | -41.5% | 92% | [-55.6, -30.4] |
| pipe:inpaint_erp | 0.0666 | -47.3% | 88% | [-60.6, -19.2] |
| oracle:inpaint_tangent | 0.0951 | -41.3% | 82% | [-58.5, -22.1] |
| oracle+1.5:inpaint_tangent | 0.1324 | -13.1% | 68% | [-41.3, -5.3] |
| detected:inpaint_tangent | 0.0889 | -41.3% | 82% | [-60.2, -22.1] |
| detected+1.5:inpaint_tangent | 0.1324 | -12.8% | 68% | [-35.7, -5.3] |
| pipe:inpaint_tangent | 0.0826 | -33.1% | 82% | [-47.7, -12.6] |
| oracle:plane_fill | 0.0666 | -62.0% | 88% | [-76.5, -32.0] |
| oracle+1.5:plane_fill | 0.0729 | -38.7% | 80% | [-72.2, -13.9] |
| detected:plane_fill | 0.0666 | -57.5% | 88% | [-76.0, -32.0] |
| detected+1.5:plane_fill | 0.0744 | -34.3% | 80% | [-72.3, -13.3] |
| pipe:plane_fill | 0.0541 | -72.9% | 92% | [-82.0, -50.6] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.1339)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1272 | -4.2% | 88% | [-4.8, -3.1] |
| oracle+1.5:inpaint_erp | 0.1334 | -1.7% | 68% | [-5.1, -0.2] |
| detected:inpaint_erp | 0.1272 | -4.2% | 88% | [-4.8, -3.1] |
| detected+1.5:inpaint_erp | 0.1334 | -1.5% | 65% | [-5.1, -0.1] |
| pipe:inpaint_erp | 0.0777 | -40.4% | 92% | [-48.8, -18.9] |
| oracle:inpaint_tangent | 0.1295 | -2.5% | 85% | [-4.6, -1.6] |
| oracle+1.5:inpaint_tangent | 0.1369 | +0.1% | 48% | [-2.3, +2.2] |
| detected:inpaint_tangent | 0.1295 | -2.4% | 85% | [-4.6, -1.6] |
| detected+1.5:inpaint_tangent | 0.1369 | +0.1% | 48% | [-2.3, +2.7] |
| pipe:inpaint_tangent | 0.0940 | -20.2% | 82% | [-41.1, -8.5] |
| oracle:plane_fill | 0.1254 | -3.8% | 82% | [-13.7, -1.8] |
| oracle+1.5:plane_fill | 0.1264 | -2.7% | 65% | [-9.4, -0.0] |
| detected:plane_fill | 0.1254 | -3.8% | 82% | [-13.7, -1.8] |
| detected+1.5:plane_fill | 0.1265 | -2.7% | 65% | [-9.3, -0.0] |
| pipe:plane_fill | 0.0694 | -47.3% | 95% | [-54.3, -38.9] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0933)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0786 | -7.6% | 78% | [-12.0, -4.9] |
| oracle+1.5:inpaint_erp | 0.0956 | -6.0% | 60% | [-9.4, +3.8] |
| detected:inpaint_erp | 0.0786 | -7.6% | 78% | [-12.2, -4.9] |
| detected+1.5:inpaint_erp | 0.0956 | -6.0% | 60% | [-9.4, +3.8] |
| pipe:inpaint_erp | 0.0661 | -28.1% | 72% | [-59.5, -9.2] |
| oracle:inpaint_tangent | 0.0778 | -3.6% | 78% | [-9.3, -1.1] |
| oracle+1.5:inpaint_tangent | 0.1039 | +2.9% | 45% | [-5.0, +13.0] |
| detected:inpaint_tangent | 0.0778 | -3.6% | 78% | [-9.3, -1.1] |
| detected+1.5:inpaint_tangent | 0.1039 | +2.9% | 42% | [-3.7, +13.0] |
| pipe:inpaint_tangent | 0.0728 | -12.5% | 57% | [-42.5, +8.2] |
| oracle:plane_fill | 0.0640 | -7.6% | 78% | [-26.8, -2.8] |
| oracle+1.5:plane_fill | 0.0650 | -5.7% | 62% | [-23.3, +2.9] |
| detected:plane_fill | 0.0640 | -7.6% | 80% | [-26.8, -2.8] |
| detected+1.5:plane_fill | 0.0652 | -5.5% | 60% | [-23.0, +2.9] |
| pipe:plane_fill | 0.0597 | -43.0% | 78% | [-67.9, -21.2] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.1569)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1312 | -12.0% | 95% | [-22.9, -7.4] |
| oracle+1.5:inpaint_erp | 0.1324 | -9.3% | 90% | [-16.5, -7.3] |
| detected:inpaint_erp | 0.1312 | -12.0% | 95% | [-22.9, -7.4] |
| detected+1.5:inpaint_erp | 0.1324 | -9.3% | 90% | [-16.5, -7.3] |
| pipe:inpaint_erp | 0.0771 | -43.9% | 95% | [-46.8, -27.7] |
| oracle:inpaint_tangent | 0.1371 | -8.4% | 90% | [-16.2, -3.8] |
| oracle+1.5:inpaint_tangent | 0.1518 | -2.0% | 68% | [-4.6, -0.2] |
| detected:inpaint_tangent | 0.1371 | -8.4% | 90% | [-16.2, -3.8] |
| detected+1.5:inpaint_tangent | 0.1518 | -1.8% | 65% | [-3.6, +0.4] |
| pipe:inpaint_tangent | 0.0923 | -31.2% | 90% | [-39.3, -18.0] |
| oracle:plane_fill | 0.1284 | -23.4% | 92% | [-34.8, -15.6] |
| oracle+1.5:plane_fill | 0.1394 | -15.0% | 88% | [-31.6, -8.3] |
| detected:plane_fill | 0.1284 | -23.4% | 92% | [-34.8, -13.8] |
| detected+1.5:plane_fill | 0.1396 | -15.0% | 85% | [-31.4, -5.3] |
| pipe:plane_fill | 0.0766 | -51.4% | 98% | [-53.0, -45.7] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.0398)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0466 | +2.6% | 45% | [-8.2, +16.8] |
| oracle:inpaint_erp | 0.0456 | -3.8% | 55% | [-10.5, +13.4] |
| oracle+1.5:inpaint_erp | 0.0493 | -3.0% | 55% | [-13.0, +11.2] |
| detected:inpaint_erp | 0.0486 | -3.8% | 55% | [-12.1, +13.4] |
| detected+1.5:inpaint_erp | 0.0526 | -3.0% | 55% | [-14.8, +11.2] |
| deblock_oracle:inpaint_erp | 0.0429 | -11.2% | 55% | [-25.4, +29.4] |
| pipe_photometric:inpaint_erp | 0.0637 | -35.7% | 62% | [-49.3, +13.7] |
| pipe_cap_first:inpaint_erp | 0.0629 | -36.7% | 60% | [-50.6, +13.1] |
| oracle:inpaint_tangent | 0.0552 | +2.7% | 45% | [-9.4, +12.4] |
| oracle+1.5:inpaint_tangent | 0.0533 | +0.1% | 50% | [-15.9, +9.7] |
| detected:inpaint_tangent | 0.0529 | +1.8% | 48% | [-11.2, +12.4] |
| detected+1.5:inpaint_tangent | 0.0522 | +0.1% | 50% | [-15.9, +9.7] |
| deblock_oracle:inpaint_tangent | 0.0453 | -11.2% | 57% | [-27.6, +30.5] |
| pipe_photometric:inpaint_tangent | 0.0371 | -41.5% | 65% | [-67.5, -0.5] |
| pipe_cap_first:inpaint_tangent | 0.0321 | -43.2% | 65% | [-66.3, -1.6] |
| oracle:plane_fill | 0.0511 | +2.0% | 48% | [-17.0, +11.7] |
| oracle+1.5:plane_fill | 0.0464 | +2.9% | 45% | [-11.4, +21.6] |
| detected:plane_fill | 0.0511 | +2.8% | 45% | [-13.2, +18.9] |
| detected+1.5:plane_fill | 0.0458 | +3.5% | 42% | [-9.3, +20.3] |
| deblock_oracle:plane_fill | 0.0454 | -4.4% | 57% | [-32.6, +17.0] |
| pipe_photometric:plane_fill | 0.0357 | -29.2% | 65% | [-47.1, -3.7] |
| pipe_cap_first:plane_fill | 0.0329 | -28.2% | 62% | [-48.2, +5.2] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.1424)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1486 | -1.2% | 57% | [-6.0, +2.8] |
| oracle:inpaint_erp | 0.1481 | -1.0% | 57% | [-4.1, +1.2] |
| oracle+1.5:inpaint_erp | 0.1467 | -0.9% | 55% | [-3.8, +1.5] |
| detected:inpaint_erp | 0.1471 | -1.0% | 57% | [-4.1, +1.2] |
| detected+1.5:inpaint_erp | 0.1510 | -0.9% | 55% | [-3.8, +1.5] |
| deblock_oracle:inpaint_erp | 0.1391 | -3.9% | 65% | [-13.2, +0.1] |
| pipe_photometric:inpaint_erp | 0.1066 | -20.8% | 92% | [-32.7, -11.4] |
| pipe_cap_first:inpaint_erp | 0.1063 | -20.7% | 92% | [-32.7, -11.3] |
| oracle:inpaint_tangent | 0.1478 | -1.6% | 70% | [-5.1, -0.5] |
| oracle+1.5:inpaint_tangent | 0.1461 | -1.0% | 57% | [-3.1, +1.1] |
| detected:inpaint_tangent | 0.1457 | -1.4% | 68% | [-5.0, -0.3] |
| detected+1.5:inpaint_tangent | 0.1464 | -0.9% | 55% | [-3.1, +1.2] |
| deblock_oracle:inpaint_tangent | 0.1393 | -4.7% | 68% | [-11.4, -0.7] |
| pipe_photometric:inpaint_tangent | 0.1051 | -19.6% | 95% | [-30.1, -14.1] |
| pipe_cap_first:inpaint_tangent | 0.1047 | -20.0% | 95% | [-30.4, -13.6] |
| oracle:plane_fill | 0.1477 | -1.3% | 60% | [-4.6, +1.3] |
| oracle+1.5:plane_fill | 0.1454 | -0.9% | 55% | [-3.5, +2.6] |
| detected:plane_fill | 0.1453 | -1.2% | 57% | [-4.6, +1.3] |
| detected+1.5:plane_fill | 0.1470 | -0.6% | 52% | [-3.6, +2.7] |
| deblock_oracle:plane_fill | 0.1393 | -4.3% | 68% | [-10.8, -0.7] |
| pipe_photometric:plane_fill | 0.1065 | -18.4% | 98% | [-29.4, -12.6] |
| pipe_cap_first:plane_fill | 0.1056 | -19.1% | 98% | [-29.5, -12.3] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.0981)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0910 | -9.8% | 70% | [-16.6, -2.8] |
| oracle:inpaint_erp | 0.0995 | -15.0% | 80% | [-27.7, -9.6] |
| oracle+1.5:inpaint_erp | 0.0966 | -14.7% | 78% | [-25.7, -8.2] |
| detected:inpaint_erp | 0.0993 | -15.0% | 80% | [-27.9, -8.1] |
| detected+1.5:inpaint_erp | 0.0966 | -14.7% | 78% | [-25.7, -7.1] |
| deblock_oracle:inpaint_erp | 0.0723 | -24.7% | 82% | [-37.3, -19.2] |
| pipe_photometric:inpaint_erp | 0.0902 | -38.2% | 80% | [-47.3, -22.4] |
| pipe_cap_first:inpaint_erp | 0.0905 | -38.5% | 80% | [-47.8, -21.6] |
| oracle:inpaint_tangent | 0.1054 | -12.9% | 72% | [-26.6, -3.9] |
| oracle+1.5:inpaint_tangent | 0.1048 | -12.5% | 72% | [-22.0, -1.1] |
| detected:inpaint_tangent | 0.1054 | -13.3% | 70% | [-26.6, -2.3] |
| detected+1.5:inpaint_tangent | 0.1057 | -12.5% | 70% | [-22.0, -1.1] |
| deblock_oracle:inpaint_tangent | 0.0778 | -23.5% | 78% | [-33.7, -14.5] |
| pipe_photometric:inpaint_tangent | 0.0978 | -41.4% | 85% | [-53.4, -28.3] |
| pipe_cap_first:inpaint_tangent | 0.0981 | -42.2% | 85% | [-54.0, -27.6] |
| oracle:plane_fill | 0.1054 | -9.9% | 70% | [-24.8, -0.6] |
| oracle+1.5:plane_fill | 0.1046 | -7.2% | 60% | [-20.2, +4.4] |
| detected:plane_fill | 0.1054 | -9.9% | 68% | [-24.8, -0.2] |
| detected+1.5:plane_fill | 0.1057 | -6.3% | 57% | [-20.3, +5.8] |
| deblock_oracle:plane_fill | 0.0778 | -24.6% | 75% | [-33.7, -13.9] |
| pipe_photometric:plane_fill | 0.0950 | -36.6% | 85% | [-46.3, -25.0] |
| pipe_cap_first:plane_fill | 0.0933 | -34.4% | 85% | [-49.3, -25.9] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.1352)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1434 | -1.3% | 55% | [-7.5, +2.3] |
| oracle:inpaint_erp | 0.1328 | -0.8% | 55% | [-5.8, +2.1] |
| oracle+1.5:inpaint_erp | 0.1329 | -0.5% | 52% | [-5.7, +2.9] |
| detected:inpaint_erp | 0.1333 | -0.8% | 55% | [-5.8, +2.1] |
| detected+1.5:inpaint_erp | 0.1329 | -0.5% | 52% | [-5.7, +2.9] |
| deblock_oracle:inpaint_erp | 0.1258 | -6.7% | 62% | [-12.2, +2.1] |
| pipe_photometric:inpaint_erp | 0.0973 | -16.5% | 88% | [-36.1, -11.6] |
| pipe_cap_first:inpaint_erp | 0.0972 | -17.2% | 88% | [-36.0, -11.7] |
| oracle:inpaint_tangent | 0.1328 | -1.3% | 65% | [-7.4, +0.2] |
| oracle+1.5:inpaint_tangent | 0.1333 | -0.9% | 55% | [-7.9, +0.7] |
| detected:inpaint_tangent | 0.1328 | -1.2% | 62% | [-7.4, +0.7] |
| detected+1.5:inpaint_tangent | 0.1333 | -0.9% | 55% | [-7.9, +1.3] |
| deblock_oracle:inpaint_tangent | 0.1262 | -7.5% | 62% | [-15.7, +0.9] |
| pipe_photometric:inpaint_tangent | 0.0951 | -18.5% | 95% | [-34.5, -14.7] |
| pipe_cap_first:inpaint_tangent | 0.0944 | -17.9% | 95% | [-34.9, -14.4] |
| oracle:plane_fill | 0.1328 | -1.4% | 55% | [-6.5, +1.2] |
| oracle+1.5:plane_fill | 0.1332 | -1.4% | 52% | [-6.3, +2.6] |
| detected:plane_fill | 0.1329 | -1.4% | 52% | [-6.5, +1.3] |
| detected+1.5:plane_fill | 0.1331 | -1.4% | 52% | [-6.2, +2.9] |
| deblock_oracle:plane_fill | 0.1259 | -7.4% | 62% | [-15.7, +0.9] |
| pipe_photometric:plane_fill | 0.0966 | -17.1% | 92% | [-30.6, -12.0] |
| pipe_cap_first:plane_fill | 0.0964 | -18.0% | 95% | [-31.8, -12.5] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.625 | 0.952 | 0.855 |
| nadir+jpeg | 0.663 | 0.847 | 0.815 |
