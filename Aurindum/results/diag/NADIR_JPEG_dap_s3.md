# Nadir + JPEG diagnosis: dap_s3

model `dap` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `none`, `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -0.88, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 98% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)

## nadir · protocol `none` · region AbsRel (raw median 0.3721)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.3589 | +2.4% | 48% | [-4.8, +12.5] |
| oracle+1.5:inpaint_erp | 0.3965 | +3.6% | 42% | [-3.3, +12.5] |
| detected:inpaint_erp | 0.3589 | +4.5% | 45% | [-2.6, +12.5] |
| detected+1.5:inpaint_erp | 0.3965 | +4.3% | 42% | [-3.3, +14.2] |
| pipe:inpaint_erp | 0.3589 | +4.5% | 45% | [-2.6, +12.5] |
| oracle:inpaint_tangent | 0.3491 | -0.5% | 55% | [-5.6, +10.3] |
| oracle+1.5:inpaint_tangent | 0.3810 | +8.1% | 32% | [+1.8, +19.2] |
| detected:inpaint_tangent | 0.3491 | +0.5% | 50% | [-5.3, +10.3] |
| detected+1.5:inpaint_tangent | 0.3810 | +9.7% | 30% | [+2.4, +20.9] |
| pipe:inpaint_tangent | 0.3491 | +0.5% | 50% | [-5.3, +10.3] |
| oracle:plane_fill | 0.3064 | -5.3% | 68% | [-10.0, -0.1] |
| oracle+1.5:plane_fill | 0.3640 | +3.3% | 45% | [-3.2, +12.2] |
| detected:plane_fill | 0.3064 | -4.4% | 62% | [-8.5, +1.8] |
| detected+1.5:plane_fill | 0.3640 | +4.4% | 42% | [-3.6, +15.1] |
| pipe:plane_fill | 0.3064 | -4.4% | 62% | [-8.5, +1.8] |

## nadir · protocol `none` · outside AbsRel (raw median 0.0334)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0378 | +17.1% | 42% | [-4.2, +29.0] |
| oracle+1.5:inpaint_erp | 0.0409 | +18.0% | 28% | [+4.5, +32.0] |
| detected:inpaint_erp | 0.0381 | +10.2% | 42% | [-4.2, +27.6] |
| detected+1.5:inpaint_erp | 0.0412 | +18.5% | 28% | [+4.5, +32.0] |
| pipe:inpaint_erp | 0.0381 | +10.2% | 42% | [-4.2, +27.6] |
| oracle:inpaint_tangent | 0.0330 | -2.0% | 55% | [-6.2, +5.4] |
| oracle+1.5:inpaint_tangent | 0.0372 | +7.1% | 25% | [+3.9, +11.7] |
| detected:inpaint_tangent | 0.0330 | -2.1% | 57% | [-7.2, +3.9] |
| detected+1.5:inpaint_tangent | 0.0372 | +8.3% | 22% | [+5.0, +12.8] |
| pipe:inpaint_tangent | 0.0330 | -2.1% | 57% | [-7.2, +3.9] |
| oracle:plane_fill | 0.0330 | -1.9% | 55% | [-6.2, +5.4] |
| oracle+1.5:plane_fill | 0.0371 | +5.0% | 28% | [+2.3, +9.1] |
| detected:plane_fill | 0.0330 | -2.1% | 57% | [-7.2, +3.9] |
| detected+1.5:plane_fill | 0.0372 | +6.2% | 25% | [+3.5, +10.9] |
| pipe:plane_fill | 0.0330 | -2.1% | 57% | [-7.2, +3.9] |

## nadir · protocol `none` · ring AbsRel (raw median 0.0345)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0432 | +28.8% | 22% | [+18.9, +51.5] |
| oracle+1.5:inpaint_erp | 0.0728 | +95.3% | 10% | [+68.6, +137.3] |
| detected:inpaint_erp | 0.0469 | +44.0% | 22% | [+19.9, +61.4] |
| detected+1.5:inpaint_erp | 0.0728 | +100.8% | 10% | [+74.6, +141.0] |
| pipe:inpaint_erp | 0.0469 | +44.0% | 22% | [+19.9, +61.4] |
| oracle:inpaint_tangent | 0.0384 | +7.5% | 38% | [-3.2, +17.2] |
| oracle+1.5:inpaint_tangent | 0.0648 | +84.5% | 2% | [+62.1, +124.4] |
| detected:inpaint_tangent | 0.0391 | +14.5% | 32% | [+1.2, +24.7] |
| detected+1.5:inpaint_tangent | 0.0670 | +89.3% | 2% | [+62.7, +127.7] |
| pipe:inpaint_tangent | 0.0391 | +14.5% | 32% | [+1.2, +24.7] |
| oracle:plane_fill | 0.0384 | +8.4% | 40% | [-3.9, +19.4] |
| oracle+1.5:plane_fill | 0.0648 | +62.5% | 8% | [+52.6, +87.0] |
| detected:plane_fill | 0.0391 | +12.2% | 35% | [-1.1, +26.4] |
| detected+1.5:plane_fill | 0.0670 | +65.3% | 8% | [+55.2, +89.3] |
| pipe:plane_fill | 0.0391 | +12.2% | 35% | [-1.1, +26.4] |

## nadir · protocol `none` · all AbsRel (raw median 0.0868)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0875 | +9.0% | 30% | [+2.4, +19.2] |
| oracle+1.5:inpaint_erp | 0.0905 | +10.9% | 22% | [+5.9, +19.4] |
| detected:inpaint_erp | 0.0875 | +9.1% | 28% | [+3.8, +19.2] |
| detected+1.5:inpaint_erp | 0.0905 | +13.1% | 22% | [+5.9, +20.7] |
| pipe:inpaint_erp | 0.0875 | +9.1% | 28% | [+3.8, +19.2] |
| oracle:inpaint_tangent | 0.0849 | +3.8% | 38% | [-1.6, +12.6] |
| oracle+1.5:inpaint_tangent | 0.0918 | +7.7% | 20% | [+5.2, +15.0] |
| detected:inpaint_tangent | 0.0849 | +3.8% | 32% | [+0.3, +12.6] |
| detected+1.5:inpaint_tangent | 0.0918 | +8.5% | 15% | [+5.3, +17.9] |
| pipe:inpaint_tangent | 0.0849 | +3.8% | 32% | [+0.3, +12.6] |
| oracle:plane_fill | 0.0801 | +0.9% | 48% | [-4.8, +6.9] |
| oracle+1.5:plane_fill | 0.0868 | +6.1% | 32% | [+0.6, +9.7] |
| detected:plane_fill | 0.0801 | +1.4% | 42% | [-4.8, +6.9] |
| detected+1.5:plane_fill | 0.0868 | +6.8% | 28% | [+1.3, +10.8] |
| pipe:plane_fill | 0.0801 | +1.4% | 42% | [-4.8, +6.9] |

## nadir+jpeg · protocol `none` · region AbsRel (raw median 0.2586)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2443 | -14.5% | 75% | [-20.6, -4.0] |
| oracle:inpaint_erp | 0.1130 | -52.2% | 80% | [-60.7, -23.5] |
| oracle+1.5:inpaint_erp | 0.1232 | -51.6% | 80% | [-60.2, -24.3] |
| detected:inpaint_erp | 0.1220 | -53.0% | 80% | [-60.4, -23.5] |
| detected+1.5:inpaint_erp | 0.1232 | -51.3% | 80% | [-60.2, -24.3] |
| deblock_oracle:inpaint_erp | 0.0757 | -49.1% | 82% | [-70.2, -33.9] |
| pipe_photometric:inpaint_erp | 0.0840 | -47.8% | 80% | [-68.8, -29.6] |
| pipe_cap_first:inpaint_erp | 0.0840 | -47.4% | 80% | [-68.8, -29.3] |
| oracle:inpaint_tangent | 0.1027 | -53.7% | 82% | [-67.2, -23.7] |
| oracle+1.5:inpaint_tangent | 0.1190 | -52.5% | 82% | [-60.7, -18.0] |
| detected:inpaint_tangent | 0.1028 | -50.6% | 82% | [-61.6, -18.4] |
| detected+1.5:inpaint_tangent | 0.1225 | -48.9% | 80% | [-60.1, -12.5] |
| deblock_oracle:inpaint_tangent | 0.0732 | -54.0% | 88% | [-72.5, -36.4] |
| pipe_photometric:inpaint_tangent | 0.0990 | -44.2% | 82% | [-61.2, -25.3] |
| pipe_cap_first:inpaint_tangent | 0.0889 | -44.9% | 85% | [-65.2, -25.3] |
| oracle:plane_fill | 0.1028 | -53.7% | 85% | [-67.2, -23.7] |
| oracle+1.5:plane_fill | 0.1186 | -52.5% | 82% | [-62.2, -18.0] |
| detected:plane_fill | 0.1028 | -50.6% | 85% | [-61.7, -22.2] |
| detected+1.5:plane_fill | 0.1225 | -48.9% | 80% | [-61.3, -12.5] |
| deblock_oracle:plane_fill | 0.0732 | -54.0% | 88% | [-72.2, -36.4] |
| pipe_photometric:plane_fill | 0.0897 | -46.3% | 82% | [-64.8, -25.3] |
| pipe_cap_first:plane_fill | 0.0885 | -46.9% | 85% | [-65.2, -25.3] |

## nadir+jpeg · protocol `none` · outside AbsRel (raw median 0.0906)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0723 | -17.9% | 85% | [-21.4, -10.8] |
| oracle:inpaint_erp | 0.1013 | +6.2% | 38% | [-0.0, +15.7] |
| oracle+1.5:inpaint_erp | 0.1042 | +7.7% | 28% | [+1.8, +17.3] |
| detected:inpaint_erp | 0.1032 | +6.8% | 35% | [+1.1, +15.7] |
| detected+1.5:inpaint_erp | 0.1053 | +7.7% | 28% | [+2.1, +17.8] |
| deblock_oracle:inpaint_erp | 0.0801 | -3.9% | 62% | [-12.1, +3.4] |
| pipe_photometric:inpaint_erp | 0.0860 | -5.2% | 57% | [-15.2, +6.2] |
| pipe_cap_first:inpaint_erp | 0.0828 | -5.4% | 57% | [-16.6, +4.6] |
| oracle:inpaint_tangent | 0.0994 | +1.0% | 42% | [-1.6, +6.8] |
| oracle+1.5:inpaint_tangent | 0.1049 | +5.1% | 28% | [+1.1, +11.3] |
| detected:inpaint_tangent | 0.1028 | +1.9% | 38% | [-1.1, +7.8] |
| detected+1.5:inpaint_tangent | 0.1062 | +5.8% | 28% | [+1.1, +11.3] |
| deblock_oracle:inpaint_tangent | 0.0797 | -6.1% | 57% | [-14.0, +1.7] |
| pipe_photometric:inpaint_tangent | 0.0932 | +1.1% | 48% | [-9.0, +7.1] |
| pipe_cap_first:inpaint_tangent | 0.0918 | +1.9% | 48% | [-9.6, +6.7] |
| oracle:plane_fill | 0.0994 | +1.0% | 42% | [-1.7, +6.8] |
| oracle+1.5:plane_fill | 0.1049 | +5.1% | 28% | [+1.0, +11.3] |
| detected:plane_fill | 0.1028 | +1.9% | 38% | [-1.2, +7.8] |
| detected+1.5:plane_fill | 0.1062 | +5.8% | 28% | [+1.0, +11.3] |
| deblock_oracle:plane_fill | 0.0798 | -6.1% | 57% | [-14.0, +1.7] |
| pipe_photometric:plane_fill | 0.0932 | +1.1% | 48% | [-9.0, +7.5] |
| pipe_cap_first:plane_fill | 0.0919 | +1.9% | 48% | [-9.6, +6.7] |

## nadir+jpeg · protocol `none` · ring AbsRel (raw median 0.1024)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0836 | -13.3% | 78% | [-20.0, -4.9] |
| oracle:inpaint_erp | 0.1145 | +3.8% | 45% | [-3.7, +20.5] |
| oracle+1.5:inpaint_erp | 0.1288 | +8.9% | 32% | [+0.4, +22.8] |
| detected:inpaint_erp | 0.1163 | +5.3% | 40% | [-1.4, +20.5] |
| detected+1.5:inpaint_erp | 0.1331 | +8.8% | 30% | [+1.9, +22.8] |
| deblock_oracle:inpaint_erp | 0.1036 | -0.1% | 50% | [-6.9, +14.8] |
| pipe_photometric:inpaint_erp | 0.1038 | +1.9% | 45% | [-5.2, +19.3] |
| pipe_cap_first:inpaint_erp | 0.1044 | +2.8% | 45% | [-6.4, +19.9] |
| oracle:inpaint_tangent | 0.1209 | +6.8% | 32% | [+2.0, +13.7] |
| oracle+1.5:inpaint_tangent | 0.1250 | +15.0% | 22% | [+9.8, +23.7] |
| detected:inpaint_tangent | 0.1171 | +11.0% | 28% | [+4.6, +14.7] |
| detected+1.5:inpaint_tangent | 0.1321 | +17.8% | 22% | [+9.4, +26.8] |
| deblock_oracle:inpaint_tangent | 0.1085 | +1.0% | 48% | [-6.8, +7.7] |
| pipe_photometric:inpaint_tangent | 0.1157 | +14.1% | 32% | [+2.1, +26.2] |
| pipe_cap_first:inpaint_tangent | 0.1167 | +13.8% | 32% | [+2.9, +24.6] |
| oracle:plane_fill | 0.1209 | +6.2% | 35% | [+1.2, +13.4] |
| oracle+1.5:plane_fill | 0.1250 | +14.5% | 22% | [+9.4, +21.7] |
| detected:plane_fill | 0.1171 | +11.0% | 30% | [+4.4, +13.9] |
| detected+1.5:plane_fill | 0.1321 | +17.3% | 22% | [+9.4, +26.8] |
| deblock_oracle:plane_fill | 0.1085 | +1.0% | 48% | [-6.8, +7.7] |
| pipe_photometric:plane_fill | 0.1157 | +14.1% | 35% | [-0.5, +25.3] |
| pipe_cap_first:plane_fill | 0.1167 | +13.8% | 35% | [+0.2, +24.6] |

## nadir+jpeg · protocol `none` · all AbsRel (raw median 0.1174)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1099 | -16.2% | 90% | [-20.9, -8.8] |
| oracle:inpaint_erp | 0.1110 | -6.7% | 68% | [-18.7, -1.8] |
| oracle+1.5:inpaint_erp | 0.1130 | -9.2% | 68% | [-17.9, -2.6] |
| detected:inpaint_erp | 0.1116 | -6.7% | 68% | [-18.7, -0.4] |
| detected+1.5:inpaint_erp | 0.1143 | -9.2% | 68% | [-17.9, -2.9] |
| deblock_oracle:inpaint_erp | 0.0867 | -19.1% | 80% | [-31.1, -10.0] |
| pipe_photometric:inpaint_erp | 0.0898 | -19.5% | 78% | [-30.5, -7.0] |
| pipe_cap_first:inpaint_erp | 0.0902 | -19.7% | 78% | [-30.0, -6.8] |
| oracle:inpaint_tangent | 0.1043 | -11.3% | 70% | [-25.1, -2.8] |
| oracle+1.5:inpaint_tangent | 0.1066 | -10.6% | 65% | [-22.0, -0.7] |
| detected:inpaint_tangent | 0.1043 | -12.0% | 68% | [-23.8, -2.6] |
| detected+1.5:inpaint_tangent | 0.1066 | -9.5% | 65% | [-21.4, -0.7] |
| deblock_oracle:inpaint_tangent | 0.0858 | -21.7% | 82% | [-35.0, -8.2] |
| pipe_photometric:inpaint_tangent | 0.0987 | -17.7% | 78% | [-28.4, -6.0] |
| pipe_cap_first:inpaint_tangent | 0.0947 | -17.9% | 78% | [-28.6, -6.1] |
| oracle:plane_fill | 0.1055 | -12.2% | 70% | [-25.1, -2.8] |
| oracle+1.5:plane_fill | 0.1087 | -11.1% | 65% | [-22.0, -0.8] |
| detected:plane_fill | 0.1055 | -12.8% | 68% | [-23.8, -2.6] |
| detected+1.5:plane_fill | 0.1089 | -10.6% | 65% | [-20.5, -0.8] |
| deblock_oracle:plane_fill | 0.0858 | -21.7% | 82% | [-35.0, -9.0] |
| pipe_photometric:plane_fill | 0.0974 | -17.7% | 78% | [-27.6, -6.4] |
| pipe_cap_first:plane_fill | 0.0942 | -17.9% | 78% | [-28.2, -6.2] |

## nadir · protocol `align-all` · region AbsRel (raw median 0.2899)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.3031 | +5.7% | 42% | [-4.1, +23.6] |
| oracle+1.5:inpaint_erp | 0.3144 | +6.9% | 42% | [-2.0, +20.3] |
| detected:inpaint_erp | 0.3031 | +7.7% | 38% | [-0.8, +23.6] |
| detected+1.5:inpaint_erp | 0.3144 | +8.3% | 42% | [-2.0, +22.4] |
| pipe:inpaint_erp | 0.3031 | +7.7% | 38% | [-0.8, +23.6] |
| oracle:inpaint_tangent | 0.2615 | +0.7% | 48% | [-5.3, +15.4] |
| oracle+1.5:inpaint_tangent | 0.3115 | +9.5% | 32% | [+0.8, +26.9] |
| detected:inpaint_tangent | 0.2615 | +2.0% | 45% | [-2.5, +15.4] |
| detected+1.5:inpaint_tangent | 0.3115 | +11.7% | 30% | [+1.3, +26.9] |
| pipe:inpaint_tangent | 0.2615 | +2.0% | 45% | [-2.5, +15.4] |
| oracle:plane_fill | 0.2136 | -5.3% | 62% | [-13.6, +0.7] |
| oracle+1.5:plane_fill | 0.2519 | +1.3% | 48% | [-5.8, +11.7] |
| detected:plane_fill | 0.2136 | -2.5% | 60% | [-13.0, +2.0] |
| detected+1.5:plane_fill | 0.2519 | +2.2% | 45% | [-5.8, +13.9] |
| pipe:plane_fill | 0.2136 | -2.5% | 60% | [-13.0, +2.0] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.0886)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0908 | +2.0% | 38% | [-0.6, +4.4] |
| oracle+1.5:inpaint_erp | 0.1010 | +8.7% | 18% | [+5.5, +13.2] |
| detected:inpaint_erp | 0.0908 | +2.8% | 35% | [-0.0, +5.2] |
| detected+1.5:inpaint_erp | 0.1010 | +9.2% | 18% | [+5.5, +15.4] |
| pipe:inpaint_erp | 0.0908 | +2.8% | 35% | [-0.0, +5.2] |
| oracle:inpaint_tangent | 0.0909 | +0.9% | 42% | [-0.2, +3.2] |
| oracle+1.5:inpaint_tangent | 0.1016 | +8.8% | 15% | [+6.6, +11.4] |
| detected:inpaint_tangent | 0.0909 | +1.5% | 40% | [-0.0, +4.8] |
| detected+1.5:inpaint_tangent | 0.1016 | +9.8% | 15% | [+6.9, +12.5] |
| pipe:inpaint_tangent | 0.0909 | +1.5% | 40% | [-0.0, +4.8] |
| oracle:plane_fill | 0.0866 | +0.4% | 48% | [-2.0, +2.5] |
| oracle+1.5:plane_fill | 0.0973 | +6.8% | 25% | [+4.3, +9.4] |
| detected:plane_fill | 0.0866 | +0.5% | 45% | [-1.9, +3.4] |
| detected+1.5:plane_fill | 0.0973 | +7.0% | 25% | [+4.7, +10.6] |
| pipe:plane_fill | 0.0866 | +0.5% | 45% | [-1.9, +3.4] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.1027)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1037 | +0.4% | 48% | [-5.3, +7.3] |
| oracle+1.5:inpaint_erp | 0.1158 | +15.5% | 25% | [+9.1, +31.0] |
| detected:inpaint_erp | 0.1118 | +0.4% | 48% | [-5.3, +7.7] |
| detected+1.5:inpaint_erp | 0.1181 | +15.5% | 25% | [+9.1, +31.0] |
| pipe:inpaint_erp | 0.1118 | +0.4% | 48% | [-5.3, +7.7] |
| oracle:inpaint_tangent | 0.1015 | +4.1% | 32% | [+1.2, +9.0] |
| oracle+1.5:inpaint_tangent | 0.1236 | +26.8% | 10% | [+15.4, +46.6] |
| detected:inpaint_tangent | 0.1071 | +5.6% | 30% | [+1.8, +11.6] |
| detected+1.5:inpaint_tangent | 0.1309 | +26.8% | 10% | [+15.4, +62.4] |
| pipe:inpaint_tangent | 0.1071 | +5.6% | 30% | [+1.8, +11.6] |
| oracle:plane_fill | 0.0987 | +1.0% | 45% | [-3.8, +4.0] |
| oracle+1.5:plane_fill | 0.1201 | +15.8% | 25% | [+6.5, +28.8] |
| detected:plane_fill | 0.1015 | +1.7% | 42% | [-2.9, +5.1] |
| detected+1.5:plane_fill | 0.1236 | +15.8% | 25% | [+6.5, +28.8] |
| pipe:plane_fill | 0.1015 | +1.7% | 42% | [-2.9, +5.1] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.1287)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1347 | +4.6% | 38% | [-0.7, +6.7] |
| oracle+1.5:inpaint_erp | 0.1399 | +6.8% | 28% | [+2.2, +12.0] |
| detected:inpaint_erp | 0.1350 | +5.1% | 32% | [+0.6, +7.6] |
| detected+1.5:inpaint_erp | 0.1399 | +7.7% | 28% | [+3.5, +13.2] |
| pipe:inpaint_erp | 0.1350 | +5.1% | 32% | [+0.6, +7.6] |
| oracle:inpaint_tangent | 0.1256 | +1.4% | 40% | [-0.5, +7.7] |
| oracle+1.5:inpaint_tangent | 0.1465 | +8.3% | 20% | [+5.0, +13.3] |
| detected:inpaint_tangent | 0.1289 | +2.3% | 35% | [+0.0, +9.5] |
| detected+1.5:inpaint_tangent | 0.1465 | +8.4% | 20% | [+5.9, +14.2] |
| pipe:inpaint_tangent | 0.1289 | +2.3% | 35% | [+0.0, +9.5] |
| oracle:plane_fill | 0.1205 | -0.3% | 52% | [-6.6, +1.9] |
| oracle+1.5:plane_fill | 0.1422 | +5.4% | 32% | [+1.0, +9.3] |
| detected:plane_fill | 0.1252 | +0.4% | 48% | [-5.2, +4.3] |
| detected+1.5:plane_fill | 0.1422 | +6.5% | 32% | [+1.7, +10.3] |
| pipe:plane_fill | 0.1252 | +0.4% | 48% | [-5.2, +4.3] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.1799)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1961 | -3.7% | 57% | [-9.9, +2.4] |
| oracle:inpaint_erp | 0.0813 | -42.3% | 80% | [-60.2, -14.5] |
| oracle+1.5:inpaint_erp | 0.0878 | -40.8% | 78% | [-60.9, -13.2] |
| detected:inpaint_erp | 0.0884 | -42.3% | 78% | [-59.2, -12.6] |
| detected+1.5:inpaint_erp | 0.0878 | -40.8% | 78% | [-61.8, -11.5] |
| deblock_oracle:inpaint_erp | 0.0830 | -50.2% | 80% | [-67.4, -33.3] |
| pipe_photometric:inpaint_erp | 0.0875 | -52.2% | 82% | [-64.5, -28.6] |
| pipe_cap_first:inpaint_erp | 0.0879 | -52.4% | 82% | [-64.0, -25.8] |
| oracle:inpaint_tangent | 0.0803 | -38.4% | 85% | [-57.0, -7.8] |
| oracle+1.5:inpaint_tangent | 0.0876 | -37.0% | 75% | [-50.9, -12.3] |
| detected:inpaint_tangent | 0.0850 | -34.0% | 80% | [-51.9, -6.1] |
| detected+1.5:inpaint_tangent | 0.0870 | -28.7% | 75% | [-48.1, -8.5] |
| deblock_oracle:inpaint_tangent | 0.0807 | -49.7% | 85% | [-65.6, -28.6] |
| pipe_photometric:inpaint_tangent | 0.0862 | -42.4% | 72% | [-54.3, -17.5] |
| pipe_cap_first:inpaint_tangent | 0.0866 | -43.1% | 72% | [-54.6, -16.8] |
| oracle:plane_fill | 0.0803 | -35.5% | 85% | [-55.1, -8.0] |
| oracle+1.5:plane_fill | 0.0876 | -38.5% | 78% | [-48.1, -9.7] |
| detected:plane_fill | 0.0850 | -34.0% | 80% | [-49.6, -7.1] |
| detected+1.5:plane_fill | 0.0870 | -28.7% | 78% | [-46.9, -8.3] |
| deblock_oracle:plane_fill | 0.0807 | -48.2% | 88% | [-65.2, -28.6] |
| pipe_photometric:plane_fill | 0.0862 | -42.1% | 75% | [-54.3, -17.5] |
| pipe_cap_first:plane_fill | 0.0866 | -43.1% | 75% | [-54.6, -16.8] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.1227)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1104 | -12.2% | 85% | [-21.5, -6.4] |
| oracle:inpaint_erp | 0.0845 | -10.9% | 72% | [-16.5, -3.8] |
| oracle+1.5:inpaint_erp | 0.0850 | -9.6% | 72% | [-16.1, -1.5] |
| detected:inpaint_erp | 0.0851 | -10.8% | 72% | [-15.7, -1.8] |
| detected+1.5:inpaint_erp | 0.0844 | -9.6% | 70% | [-16.1, -0.4] |
| deblock_oracle:inpaint_erp | 0.0746 | -27.9% | 88% | [-47.5, -20.0] |
| pipe_photometric:inpaint_erp | 0.0749 | -25.9% | 88% | [-40.6, -17.8] |
| pipe_cap_first:inpaint_erp | 0.0738 | -26.7% | 88% | [-41.5, -17.5] |
| oracle:inpaint_tangent | 0.0835 | -7.2% | 72% | [-13.6, -3.1] |
| oracle+1.5:inpaint_tangent | 0.0873 | -4.6% | 65% | [-10.2, +0.9] |
| detected:inpaint_tangent | 0.0837 | -6.4% | 72% | [-11.1, -1.8] |
| detected+1.5:inpaint_tangent | 0.0873 | -4.6% | 62% | [-10.2, +1.8] |
| deblock_oracle:inpaint_tangent | 0.0732 | -23.4% | 92% | [-39.5, -17.8] |
| pipe_photometric:inpaint_tangent | 0.0791 | -21.9% | 88% | [-31.3, -12.1] |
| pipe_cap_first:inpaint_tangent | 0.0774 | -21.5% | 90% | [-34.9, -12.2] |
| oracle:plane_fill | 0.0846 | -7.9% | 72% | [-13.6, -3.1] |
| oracle+1.5:plane_fill | 0.0913 | -4.6% | 65% | [-10.2, +0.8] |
| detected:plane_fill | 0.0846 | -6.6% | 72% | [-11.1, -1.8] |
| detected+1.5:plane_fill | 0.0913 | -4.6% | 62% | [-10.2, +1.8] |
| deblock_oracle:plane_fill | 0.0732 | -22.8% | 92% | [-39.3, -18.0] |
| pipe_photometric:plane_fill | 0.0802 | -21.8% | 88% | [-35.3, -12.1] |
| pipe_cap_first:plane_fill | 0.0795 | -21.3% | 90% | [-35.6, -12.2] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.1672)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1311 | -12.4% | 90% | [-17.4, -8.7] |
| oracle:inpaint_erp | 0.0932 | -21.5% | 78% | [-44.8, -9.5] |
| oracle+1.5:inpaint_erp | 0.1065 | -15.3% | 75% | [-41.4, -5.1] |
| detected:inpaint_erp | 0.0961 | -15.4% | 78% | [-41.3, -8.4] |
| detected+1.5:inpaint_erp | 0.1160 | -16.0% | 75% | [-37.4, -4.8] |
| deblock_oracle:inpaint_erp | 0.0853 | -37.7% | 82% | [-61.1, -27.5] |
| pipe_photometric:inpaint_erp | 0.0964 | -33.2% | 75% | [-53.6, -21.4] |
| pipe_cap_first:inpaint_erp | 0.0979 | -34.3% | 75% | [-53.0, -20.4] |
| oracle:inpaint_tangent | 0.1111 | -16.6% | 72% | [-33.2, -3.5] |
| oracle+1.5:inpaint_tangent | 0.1129 | -9.4% | 68% | [-31.0, -2.2] |
| detected:inpaint_tangent | 0.1065 | -9.1% | 72% | [-31.1, -3.0] |
| detected+1.5:inpaint_tangent | 0.1129 | -8.3% | 62% | [-31.0, +1.8] |
| deblock_oracle:inpaint_tangent | 0.1015 | -32.7% | 85% | [-51.8, -12.8] |
| pipe_photometric:inpaint_tangent | 0.1024 | -21.7% | 72% | [-50.3, -2.4] |
| pipe_cap_first:inpaint_tangent | 0.1022 | -23.1% | 80% | [-50.5, -2.2] |
| oracle:plane_fill | 0.1121 | -16.6% | 75% | [-31.1, -3.6] |
| oracle+1.5:plane_fill | 0.1129 | -9.4% | 70% | [-31.0, -2.4] |
| detected:plane_fill | 0.1065 | -9.1% | 75% | [-30.0, -3.1] |
| detected+1.5:plane_fill | 0.1129 | -8.3% | 65% | [-31.0, +0.1] |
| deblock_oracle:plane_fill | 0.1044 | -32.7% | 88% | [-50.9, -12.8] |
| pipe_photometric:plane_fill | 0.1039 | -21.7% | 72% | [-50.6, -2.4] |
| pipe_cap_first:plane_fill | 0.1042 | -23.1% | 80% | [-50.3, -2.2] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.1394)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1300 | -14.2% | 80% | [-18.7, -7.4] |
| oracle:inpaint_erp | 0.0877 | -12.8% | 78% | [-35.5, -7.1] |
| oracle+1.5:inpaint_erp | 0.0894 | -11.1% | 75% | [-33.2, -5.4] |
| detected:inpaint_erp | 0.0877 | -12.8% | 78% | [-34.5, -4.4] |
| detected+1.5:inpaint_erp | 0.0886 | -11.1% | 72% | [-31.8, -5.2] |
| deblock_oracle:inpaint_erp | 0.0770 | -31.4% | 90% | [-47.2, -22.4] |
| pipe_photometric:inpaint_erp | 0.0784 | -28.8% | 90% | [-45.2, -19.9] |
| pipe_cap_first:inpaint_erp | 0.0778 | -28.7% | 90% | [-45.3, -19.9] |
| oracle:inpaint_tangent | 0.0920 | -11.1% | 80% | [-31.6, -5.8] |
| oracle+1.5:inpaint_tangent | 0.0975 | -9.7% | 70% | [-27.5, -3.6] |
| detected:inpaint_tangent | 0.0920 | -10.4% | 80% | [-27.3, -3.6] |
| detected+1.5:inpaint_tangent | 0.0975 | -9.7% | 70% | [-24.6, -1.7] |
| deblock_oracle:inpaint_tangent | 0.0799 | -27.1% | 95% | [-42.5, -20.7] |
| pipe_photometric:inpaint_tangent | 0.0849 | -24.7% | 90% | [-36.8, -18.1] |
| pipe_cap_first:inpaint_tangent | 0.0843 | -24.6% | 92% | [-39.5, -17.8] |
| oracle:plane_fill | 0.0920 | -12.5% | 80% | [-31.6, -5.6] |
| oracle+1.5:plane_fill | 0.0975 | -10.4% | 70% | [-27.5, -3.7] |
| detected:plane_fill | 0.0920 | -10.5% | 80% | [-27.3, -2.7] |
| detected+1.5:plane_fill | 0.0975 | -10.5% | 70% | [-24.6, -1.7] |
| deblock_oracle:plane_fill | 0.0799 | -27.3% | 95% | [-42.5, -19.9] |
| pipe_photometric:plane_fill | 0.0860 | -25.4% | 90% | [-36.6, -18.2] |
| pipe_cap_first:plane_fill | 0.0854 | -25.2% | 92% | [-37.1, -17.9] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.609 | 0.641 | 0.611 |
| nadir+jpeg | 0.748 | 0.982 | 0.980 |
