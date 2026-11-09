# Nadir + JPEG diagnosis: da2_s3

model `da2` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -1.57, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 52% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +4.09)

## nadir · protocol `align-all` · region AbsRel (raw median 0.1821)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0563 | -64.7% | 95% | [-74.2, -57.6] |
| oracle+1.5:inpaint_erp | 0.0548 | -61.2% | 95% | [-74.7, -52.1] |
| detected:inpaint_erp | 0.0563 | -64.7% | 95% | [-74.2, -57.6] |
| detected+1.5:inpaint_erp | 0.0570 | -61.2% | 95% | [-74.7, -52.1] |
| pipe:inpaint_erp | 0.0563 | -64.7% | 95% | [-74.2, -57.6] |
| oracle:inpaint_tangent | 0.0524 | -70.7% | 95% | [-74.6, -64.2] |
| oracle+1.5:inpaint_tangent | 0.0557 | -69.6% | 95% | [-79.9, -64.9] |
| detected:inpaint_tangent | 0.0524 | -70.7% | 95% | [-77.1, -64.2] |
| detected+1.5:inpaint_tangent | 0.0557 | -69.6% | 95% | [-81.0, -64.9] |
| pipe:inpaint_tangent | 0.0524 | -70.7% | 95% | [-77.1, -64.2] |
| oracle:plane_fill | 0.0524 | -70.9% | 95% | [-79.9, -64.5] |
| oracle+1.5:plane_fill | 0.0518 | -69.6% | 95% | [-80.2, -65.4] |
| detected:plane_fill | 0.0524 | -70.9% | 95% | [-79.9, -64.5] |
| detected+1.5:plane_fill | 0.0518 | -69.6% | 95% | [-80.9, -65.4] |
| pipe:plane_fill | 0.0524 | -70.9% | 95% | [-79.9, -64.5] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.0916)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0434 | -49.0% | 88% | [-56.1, -39.7] |
| oracle+1.5:inpaint_erp | 0.0451 | -50.3% | 88% | [-55.3, -39.5] |
| detected:inpaint_erp | 0.0434 | -49.0% | 88% | [-56.1, -39.7] |
| detected+1.5:inpaint_erp | 0.0451 | -48.6% | 88% | [-55.3, -39.5] |
| pipe:inpaint_erp | 0.0434 | -49.0% | 88% | [-56.1, -39.7] |
| oracle:inpaint_tangent | 0.0415 | -51.8% | 92% | [-57.0, -40.0] |
| oracle+1.5:inpaint_tangent | 0.0429 | -50.3% | 90% | [-56.7, -39.7] |
| detected:inpaint_tangent | 0.0415 | -51.8% | 92% | [-57.0, -40.0] |
| detected+1.5:inpaint_tangent | 0.0429 | -50.3% | 90% | [-56.7, -39.7] |
| pipe:inpaint_tangent | 0.0415 | -51.8% | 92% | [-57.0, -40.0] |
| oracle:plane_fill | 0.0415 | -51.8% | 92% | [-57.0, -39.4] |
| oracle+1.5:plane_fill | 0.0433 | -50.3% | 90% | [-56.6, -39.6] |
| detected:plane_fill | 0.0415 | -51.8% | 92% | [-57.0, -39.4] |
| detected+1.5:plane_fill | 0.0433 | -50.3% | 90% | [-56.6, -39.5] |
| pipe:plane_fill | 0.0415 | -51.8% | 92% | [-57.0, -39.4] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.1411)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0504 | -64.2% | 95% | [-75.1, -62.8] |
| oracle+1.5:inpaint_erp | 0.0514 | -63.6% | 95% | [-73.2, -58.3] |
| detected:inpaint_erp | 0.0504 | -64.0% | 95% | [-75.1, -61.8] |
| detected+1.5:inpaint_erp | 0.0513 | -63.7% | 95% | [-73.2, -58.3] |
| pipe:inpaint_erp | 0.0504 | -64.0% | 95% | [-75.1, -61.8] |
| oracle:inpaint_tangent | 0.0453 | -67.9% | 95% | [-76.6, -61.0] |
| oracle+1.5:inpaint_tangent | 0.0420 | -70.2% | 95% | [-75.3, -60.1] |
| detected:inpaint_tangent | 0.0453 | -67.9% | 95% | [-76.6, -58.6] |
| detected+1.5:inpaint_tangent | 0.0420 | -70.2% | 95% | [-75.3, -59.5] |
| pipe:inpaint_tangent | 0.0453 | -67.9% | 95% | [-76.6, -58.6] |
| oracle:plane_fill | 0.0458 | -67.9% | 95% | [-75.8, -61.0] |
| oracle+1.5:plane_fill | 0.0451 | -69.7% | 95% | [-75.3, -60.1] |
| detected:plane_fill | 0.0458 | -67.9% | 95% | [-75.8, -58.6] |
| detected+1.5:plane_fill | 0.0451 | -69.7% | 95% | [-75.3, -59.5] |
| pipe:plane_fill | 0.0458 | -67.9% | 95% | [-75.8, -58.6] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.1064)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0444 | -50.8% | 92% | [-59.3, -46.7] |
| oracle+1.5:inpaint_erp | 0.0449 | -51.3% | 92% | [-56.9, -46.0] |
| detected:inpaint_erp | 0.0444 | -50.8% | 92% | [-59.3, -46.3] |
| detected+1.5:inpaint_erp | 0.0449 | -51.3% | 92% | [-56.9, -44.3] |
| pipe:inpaint_erp | 0.0444 | -50.8% | 92% | [-59.3, -46.3] |
| oracle:inpaint_tangent | 0.0437 | -55.6% | 98% | [-60.2, -48.3] |
| oracle+1.5:inpaint_tangent | 0.0454 | -54.1% | 98% | [-60.8, -48.4] |
| detected:inpaint_tangent | 0.0449 | -55.6% | 98% | [-59.7, -48.3] |
| detected+1.5:inpaint_tangent | 0.0458 | -54.1% | 98% | [-60.0, -48.4] |
| pipe:inpaint_tangent | 0.0449 | -55.6% | 98% | [-59.7, -48.3] |
| oracle:plane_fill | 0.0461 | -54.4% | 98% | [-61.4, -48.3] |
| oracle+1.5:plane_fill | 0.0460 | -54.0% | 98% | [-61.1, -47.8] |
| detected:plane_fill | 0.0468 | -54.4% | 98% | [-59.9, -48.3] |
| detected+1.5:plane_fill | 0.0485 | -54.0% | 98% | [-60.3, -47.8] |
| pipe:plane_fill | 0.0468 | -54.4% | 98% | [-59.9, -48.3] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1229)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1429 | +14.4% | 22% | [+5.0, +22.6] |
| oracle:inpaint_erp | 0.1252 | +6.9% | 42% | [-23.9, +45.0] |
| oracle+1.5:inpaint_erp | 0.1342 | +12.1% | 40% | [-13.1, +47.4] |
| detected:inpaint_erp | 0.1322 | +0.0% | 20% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.1269 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.1054 | +4.4% | 48% | [-19.8, +36.7] |
| pipe_photometric:inpaint_erp | 0.1297 | +14.3% | 30% | [+3.6, +28.8] |
| pipe_cap_first:inpaint_erp | 0.1073 | +10.6% | 32% | [+2.7, +28.8] |
| oracle:inpaint_tangent | 0.0999 | -34.0% | 68% | [-46.2, -3.3] |
| oracle+1.5:inpaint_tangent | 0.0909 | -26.0% | 68% | [-48.2, -1.6] |
| detected:inpaint_tangent | 0.1155 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1091 | +0.0% | 32% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0881 | -20.3% | 70% | [-45.8, -7.2] |
| pipe_photometric:inpaint_tangent | 0.1052 | +7.1% | 40% | [-4.7, +15.4] |
| pipe_cap_first:inpaint_tangent | 0.1052 | +7.1% | 40% | [-4.0, +15.4] |
| oracle:plane_fill | 0.0999 | -32.9% | 65% | [-45.6, -3.3] |
| oracle+1.5:plane_fill | 0.0909 | -27.8% | 65% | [-48.2, +0.3] |
| detected:plane_fill | 0.1174 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1130 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.0856 | -22.3% | 72% | [-43.9, -8.8] |
| pipe_photometric:plane_fill | 0.1052 | +7.1% | 40% | [-2.1, +15.4] |
| pipe_cap_first:plane_fill | 0.1052 | +7.1% | 40% | [-2.2, +15.4] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.0882)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0925 | +1.2% | 42% | [-1.7, +5.8] |
| oracle:inpaint_erp | 0.0818 | -13.5% | 62% | [-24.8, +1.9] |
| oracle+1.5:inpaint_erp | 0.0827 | -12.7% | 65% | [-16.3, -0.9] |
| detected:inpaint_erp | 0.0854 | +0.0% | 38% | [-2.7, +0.0] |
| detected+1.5:inpaint_erp | 0.0836 | +0.0% | 32% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.0761 | -13.1% | 62% | [-26.2, +6.6] |
| pipe_photometric:inpaint_erp | 0.0836 | -3.5% | 57% | [-12.0, +5.0] |
| pipe_cap_first:inpaint_erp | 0.0823 | -3.5% | 60% | [-11.3, +5.0] |
| oracle:inpaint_tangent | 0.0764 | -19.2% | 72% | [-28.4, -7.8] |
| oracle+1.5:inpaint_tangent | 0.0793 | -16.6% | 68% | [-31.1, -6.4] |
| detected:inpaint_tangent | 0.0854 | +0.0% | 35% | [-5.6, +0.0] |
| detected+1.5:inpaint_tangent | 0.0844 | +0.0% | 35% | [-5.3, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0728 | -17.7% | 70% | [-27.9, -4.9] |
| pipe_photometric:inpaint_tangent | 0.0889 | -3.5% | 60% | [-11.2, +4.7] |
| pipe_cap_first:inpaint_tangent | 0.0891 | -3.5% | 60% | [-11.3, +4.5] |
| oracle:plane_fill | 0.0764 | -19.2% | 72% | [-28.5, -7.8] |
| oracle+1.5:plane_fill | 0.0793 | -16.6% | 68% | [-31.1, -6.4] |
| detected:plane_fill | 0.0851 | +0.0% | 35% | [-5.6, +0.0] |
| detected+1.5:plane_fill | 0.0849 | +0.0% | 35% | [-5.3, +0.0] |
| deblock_oracle:plane_fill | 0.0728 | -17.7% | 70% | [-27.9, -4.9] |
| pipe_photometric:plane_fill | 0.0889 | -3.5% | 60% | [-11.2, +4.7] |
| pipe_cap_first:plane_fill | 0.0891 | -3.5% | 60% | [-11.3, +4.5] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.1004)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1159 | +7.4% | 25% | [+4.3, +14.8] |
| oracle:inpaint_erp | 0.0859 | -33.1% | 62% | [-40.6, +3.6] |
| oracle+1.5:inpaint_erp | 0.0877 | -21.8% | 55% | [-37.9, +9.2] |
| detected:inpaint_erp | 0.1003 | +0.0% | 35% | [-1.7, +0.0] |
| detected+1.5:inpaint_erp | 0.1002 | +0.0% | 35% | [-3.8, +0.0] |
| deblock_oracle:inpaint_erp | 0.0734 | -18.2% | 60% | [-41.7, +3.3] |
| pipe_photometric:inpaint_erp | 0.1071 | +4.7% | 40% | [-2.3, +13.2] |
| pipe_cap_first:inpaint_erp | 0.1128 | +4.3% | 42% | [-3.0, +14.8] |
| oracle:inpaint_tangent | 0.0780 | -30.5% | 78% | [-42.2, -9.8] |
| oracle+1.5:inpaint_tangent | 0.0800 | -30.7% | 78% | [-41.6, -12.5] |
| detected:inpaint_tangent | 0.0984 | +0.0% | 38% | [-3.9, +0.0] |
| detected+1.5:inpaint_tangent | 0.0992 | +0.0% | 38% | [-5.9, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0735 | -31.5% | 72% | [-46.2, -9.8] |
| pipe_photometric:inpaint_tangent | 0.1045 | +3.5% | 48% | [-6.1, +10.9] |
| pipe_cap_first:inpaint_tangent | 0.1045 | +3.5% | 48% | [-6.1, +10.9] |
| oracle:plane_fill | 0.0783 | -30.5% | 78% | [-42.2, -9.8] |
| oracle+1.5:plane_fill | 0.0800 | -30.7% | 78% | [-38.9, -12.5] |
| detected:plane_fill | 0.0984 | +0.0% | 38% | [-3.9, +0.0] |
| detected+1.5:plane_fill | 0.1004 | +0.0% | 38% | [-5.9, +0.0] |
| deblock_oracle:plane_fill | 0.0735 | -31.5% | 72% | [-46.2, -9.3] |
| pipe_photometric:plane_fill | 0.1045 | +3.5% | 48% | [-6.1, +10.9] |
| pipe_cap_first:plane_fill | 0.1045 | +3.5% | 48% | [-6.1, +10.9] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.0959)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1007 | +4.6% | 42% | [-1.4, +8.8] |
| oracle:inpaint_erp | 0.0960 | -9.2% | 57% | [-17.5, +16.7] |
| oracle+1.5:inpaint_erp | 0.1022 | -5.8% | 52% | [-13.8, +17.0] |
| detected:inpaint_erp | 0.0932 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.0896 | +0.0% | 35% | [-2.5, +0.0] |
| deblock_oracle:inpaint_erp | 0.0874 | -6.9% | 57% | [-14.9, +11.0] |
| pipe_photometric:inpaint_erp | 0.0884 | -1.7% | 55% | [-5.6, +10.1] |
| pipe_cap_first:inpaint_erp | 0.0872 | -1.7% | 57% | [-6.7, +10.1] |
| oracle:inpaint_tangent | 0.0851 | -21.9% | 75% | [-30.7, -5.9] |
| oracle+1.5:inpaint_tangent | 0.0868 | -15.5% | 70% | [-33.2, -7.6] |
| detected:inpaint_tangent | 0.0881 | +0.0% | 38% | [-4.7, +0.0] |
| detected+1.5:inpaint_tangent | 0.0881 | +0.0% | 38% | [-5.3, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0864 | -17.0% | 70% | [-33.1, -4.4] |
| pipe_photometric:inpaint_tangent | 0.0872 | -2.6% | 62% | [-6.8, +5.7] |
| pipe_cap_first:inpaint_tangent | 0.0868 | -2.7% | 62% | [-6.6, +5.7] |
| oracle:plane_fill | 0.0856 | -21.9% | 75% | [-31.0, -5.9] |
| oracle+1.5:plane_fill | 0.0880 | -15.5% | 70% | [-33.2, -7.6] |
| detected:plane_fill | 0.0882 | +0.0% | 38% | [-4.7, +0.0] |
| detected+1.5:plane_fill | 0.0885 | +0.0% | 40% | [-5.3, +0.0] |
| deblock_oracle:plane_fill | 0.0869 | -17.0% | 72% | [-32.3, -4.1] |
| pipe_photometric:plane_fill | 0.0877 | -2.6% | 62% | [-6.8, +5.7] |
| pipe_cap_first:plane_fill | 0.0874 | -2.7% | 62% | [-6.6, +5.7] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 1.156 | 1.009 | 1.026 |
| nadir+jpeg | 1.058 | 0.938 | 0.889 |
