# Nadir + JPEG diagnosis: da360_s3

model `da360` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -1.57, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 52% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +4.09)

## nadir · protocol `align-all` · region AbsRel (raw median 0.0203)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0324 | +72.8% | 8% | [+40.1, +114.4] |
| oracle+1.5:inpaint_erp | 0.0375 | +77.5% | 8% | [+43.1, +126.9] |
| detected:inpaint_erp | 0.0324 | +80.3% | 8% | [+40.1, +119.5] |
| detected+1.5:inpaint_erp | 0.0375 | +79.3% | 8% | [+43.3, +139.2] |
| pipe:inpaint_erp | 0.0324 | +80.3% | 8% | [+40.1, +119.5] |
| oracle:inpaint_tangent | 0.0303 | +39.5% | 12% | [+26.2, +73.0] |
| oracle+1.5:inpaint_tangent | 0.0396 | +61.5% | 10% | [+33.9, +102.4] |
| detected:inpaint_tangent | 0.0303 | +39.5% | 12% | [+26.2, +75.9] |
| detected+1.5:inpaint_tangent | 0.0406 | +60.5% | 10% | [+33.9, +109.8] |
| pipe:inpaint_tangent | 0.0303 | +39.5% | 12% | [+26.2, +75.9] |
| oracle:plane_fill | 0.0319 | +46.2% | 15% | [+30.2, +83.8] |
| oracle+1.5:plane_fill | 0.0445 | +65.0% | 8% | [+35.4, +158.7] |
| detected:plane_fill | 0.0349 | +49.9% | 12% | [+30.2, +113.5] |
| detected+1.5:plane_fill | 0.0457 | +62.5% | 8% | [+35.4, +181.1] |
| pipe:plane_fill | 0.0349 | +49.9% | 12% | [+30.2, +113.5] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.0149)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0180 | +14.0% | 15% | [+6.9, +23.9] |
| oracle+1.5:inpaint_erp | 0.0173 | +17.5% | 15% | [+9.5, +26.5] |
| detected:inpaint_erp | 0.0180 | +14.0% | 15% | [+7.1, +23.9] |
| detected+1.5:inpaint_erp | 0.0173 | +17.5% | 15% | [+9.5, +28.7] |
| pipe:inpaint_erp | 0.0180 | +14.0% | 15% | [+7.1, +23.9] |
| oracle:inpaint_tangent | 0.0153 | +7.5% | 25% | [+1.8, +13.2] |
| oracle+1.5:inpaint_tangent | 0.0181 | +12.6% | 15% | [+5.9, +24.2] |
| detected:inpaint_tangent | 0.0158 | +7.5% | 22% | [+2.6, +13.2] |
| detected+1.5:inpaint_tangent | 0.0181 | +12.6% | 15% | [+5.9, +24.2] |
| pipe:inpaint_tangent | 0.0158 | +7.5% | 22% | [+2.6, +13.2] |
| oracle:plane_fill | 0.0165 | +10.8% | 25% | [+3.3, +17.5] |
| oracle+1.5:plane_fill | 0.0188 | +17.6% | 15% | [+6.8, +34.9] |
| detected:plane_fill | 0.0169 | +10.8% | 22% | [+4.7, +17.8] |
| detected+1.5:plane_fill | 0.0187 | +17.6% | 15% | [+6.8, +34.9] |
| pipe:plane_fill | 0.0169 | +10.8% | 22% | [+4.7, +17.8] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0139)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0169 | +15.3% | 28% | [+6.9, +35.1] |
| oracle+1.5:inpaint_erp | 0.0187 | +30.0% | 22% | [+13.4, +45.4] |
| detected:inpaint_erp | 0.0169 | +15.1% | 25% | [+8.6, +35.1] |
| detected+1.5:inpaint_erp | 0.0194 | +35.2% | 20% | [+14.3, +47.1] |
| pipe:inpaint_erp | 0.0169 | +15.1% | 25% | [+8.6, +35.1] |
| oracle:inpaint_tangent | 0.0160 | +16.5% | 30% | [+6.1, +24.8] |
| oracle+1.5:inpaint_tangent | 0.0192 | +33.2% | 12% | [+15.8, +42.6] |
| detected:inpaint_tangent | 0.0160 | +18.0% | 28% | [+8.9, +27.4] |
| detected+1.5:inpaint_tangent | 0.0192 | +33.2% | 10% | [+18.9, +42.6] |
| pipe:inpaint_tangent | 0.0160 | +18.0% | 28% | [+8.9, +27.4] |
| oracle:plane_fill | 0.0163 | +22.7% | 30% | [+6.1, +29.9] |
| oracle+1.5:plane_fill | 0.0192 | +35.9% | 10% | [+15.8, +45.7] |
| detected:plane_fill | 0.0163 | +23.8% | 28% | [+10.0, +34.5] |
| detected+1.5:plane_fill | 0.0192 | +38.0% | 8% | [+18.9, +50.2] |
| pipe:plane_fill | 0.0163 | +23.8% | 28% | [+10.0, +34.5] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.0162)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0202 | +25.2% | 8% | [+12.8, +38.0] |
| oracle+1.5:inpaint_erp | 0.0210 | +28.8% | 8% | [+16.0, +49.2] |
| detected:inpaint_erp | 0.0202 | +26.0% | 8% | [+12.8, +38.0] |
| detected+1.5:inpaint_erp | 0.0210 | +29.0% | 8% | [+16.0, +52.1] |
| pipe:inpaint_erp | 0.0202 | +26.0% | 8% | [+12.8, +38.0] |
| oracle:inpaint_tangent | 0.0184 | +15.1% | 15% | [+9.5, +21.9] |
| oracle+1.5:inpaint_tangent | 0.0201 | +21.9% | 10% | [+14.8, +31.4] |
| detected:inpaint_tangent | 0.0184 | +16.2% | 15% | [+9.5, +23.6] |
| detected+1.5:inpaint_tangent | 0.0201 | +21.9% | 10% | [+14.8, +37.5] |
| pipe:inpaint_tangent | 0.0184 | +16.2% | 15% | [+9.5, +23.6] |
| oracle:plane_fill | 0.0190 | +17.6% | 15% | [+10.1, +26.1] |
| oracle+1.5:plane_fill | 0.0204 | +28.3% | 8% | [+14.9, +46.6] |
| detected:plane_fill | 0.0190 | +18.7% | 18% | [+11.8, +31.4] |
| detected+1.5:plane_fill | 0.0204 | +28.3% | 8% | [+14.9, +51.5] |
| pipe:plane_fill | 0.0190 | +18.7% | 18% | [+11.8, +31.4] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.0474)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0498 | +0.2% | 50% | [-10.5, +8.0] |
| oracle:inpaint_erp | 0.0736 | +24.9% | 30% | [+10.3, +42.0] |
| oracle+1.5:inpaint_erp | 0.0713 | +21.7% | 30% | [+10.2, +30.8] |
| detected:inpaint_erp | 0.0679 | +0.0% | 18% | [+0.0, +1.1] |
| detected+1.5:inpaint_erp | 0.0679 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.0621 | +17.0% | 35% | [-3.5, +29.7] |
| pipe_photometric:inpaint_erp | 0.0614 | +0.2% | 50% | [-12.7, +9.4] |
| pipe_cap_first:inpaint_erp | 0.0621 | +0.2% | 50% | [-10.1, +11.1] |
| oracle:inpaint_tangent | 0.0666 | +18.5% | 35% | [+1.1, +31.3] |
| oracle+1.5:inpaint_tangent | 0.0618 | +25.4% | 32% | [+4.9, +38.9] |
| detected:inpaint_tangent | 0.0676 | +0.0% | 18% | [+0.0, +1.1] |
| detected+1.5:inpaint_tangent | 0.0679 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0622 | +16.2% | 35% | [+1.3, +27.2] |
| pipe_photometric:inpaint_tangent | 0.0617 | +5.4% | 45% | [-9.2, +19.3] |
| pipe_cap_first:inpaint_tangent | 0.0612 | +5.8% | 42% | [-5.7, +21.8] |
| oracle:plane_fill | 0.0666 | +25.5% | 30% | [+9.2, +46.7] |
| oracle+1.5:plane_fill | 0.0618 | +31.7% | 30% | [+11.1, +50.2] |
| detected:plane_fill | 0.0676 | +0.0% | 15% | [+0.0, +8.7] |
| detected+1.5:plane_fill | 0.0679 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.0622 | +16.2% | 38% | [-12.3, +25.3] |
| pipe_photometric:plane_fill | 0.0617 | +5.4% | 45% | [-9.2, +23.1] |
| pipe_cap_first:plane_fill | 0.0612 | +5.8% | 42% | [-5.7, +23.4] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.0591)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0547 | -5.6% | 62% | [-9.2, +0.7] |
| oracle:inpaint_erp | 0.0645 | +5.0% | 30% | [+2.1, +11.2] |
| oracle+1.5:inpaint_erp | 0.0651 | +6.9% | 30% | [+1.4, +10.8] |
| detected:inpaint_erp | 0.0627 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.0627 | +0.0% | 18% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.0631 | +2.6% | 42% | [-6.0, +14.4] |
| pipe_photometric:inpaint_erp | 0.0567 | -0.5% | 52% | [-7.5, +6.3] |
| pipe_cap_first:inpaint_erp | 0.0568 | -0.2% | 52% | [-6.6, +6.3] |
| oracle:inpaint_tangent | 0.0644 | +7.6% | 25% | [+3.9, +10.0] |
| oracle+1.5:inpaint_tangent | 0.0667 | +9.5% | 22% | [+3.2, +12.7] |
| detected:inpaint_tangent | 0.0606 | +0.0% | 12% | [+0.0, +1.4] |
| detected+1.5:inpaint_tangent | 0.0605 | +0.0% | 12% | [+0.0, +2.9] |
| deblock_oracle:inpaint_tangent | 0.0644 | +6.7% | 38% | [-1.5, +10.3] |
| pipe_photometric:inpaint_tangent | 0.0571 | -0.4% | 52% | [-8.5, +6.1] |
| pipe_cap_first:inpaint_tangent | 0.0571 | +0.1% | 50% | [-7.4, +6.3] |
| oracle:plane_fill | 0.0668 | +7.5% | 25% | [+3.3, +11.0] |
| oracle+1.5:plane_fill | 0.0667 | +9.3% | 22% | [+3.2, +13.0] |
| detected:plane_fill | 0.0606 | +0.0% | 12% | [+0.0, +1.4] |
| detected+1.5:plane_fill | 0.0604 | +0.0% | 12% | [+0.0, +2.9] |
| deblock_oracle:plane_fill | 0.0644 | +6.4% | 35% | [-1.5, +10.3] |
| pipe_photometric:plane_fill | 0.0569 | +0.2% | 50% | [-8.5, +6.4] |
| pipe_cap_first:plane_fill | 0.0568 | +0.2% | 50% | [-7.4, +7.1] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.0509)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0516 | -1.8% | 62% | [-8.4, +3.8] |
| oracle:inpaint_erp | 0.0587 | +21.4% | 20% | [+13.8, +27.4] |
| oracle+1.5:inpaint_erp | 0.0613 | +19.0% | 20% | [+12.2, +29.6] |
| detected:inpaint_erp | 0.0509 | +0.0% | 15% | [+0.0, +3.3] |
| detected+1.5:inpaint_erp | 0.0502 | +0.0% | 15% | [+0.0, +4.3] |
| deblock_oracle:inpaint_erp | 0.0555 | +5.3% | 42% | [-3.8, +23.9] |
| pipe_photometric:inpaint_erp | 0.0501 | -2.6% | 60% | [-15.3, +6.9] |
| pipe_cap_first:inpaint_erp | 0.0501 | -2.2% | 60% | [-15.3, +5.5] |
| oracle:inpaint_tangent | 0.0607 | +18.4% | 28% | [+8.6, +22.7] |
| oracle+1.5:inpaint_tangent | 0.0626 | +25.3% | 15% | [+16.2, +41.1] |
| detected:inpaint_tangent | 0.0518 | +0.0% | 12% | [+0.0, +4.6] |
| detected+1.5:inpaint_tangent | 0.0509 | +0.0% | 15% | [+0.0, +7.1] |
| deblock_oracle:inpaint_tangent | 0.0592 | +3.1% | 40% | [-3.9, +22.1] |
| pipe_photometric:inpaint_tangent | 0.0489 | -1.8% | 57% | [-13.9, +9.6] |
| pipe_cap_first:inpaint_tangent | 0.0489 | -1.4% | 55% | [-11.7, +11.1] |
| oracle:plane_fill | 0.0607 | +17.0% | 30% | [+7.2, +20.9] |
| oracle+1.5:plane_fill | 0.0625 | +23.0% | 18% | [+15.3, +41.1] |
| detected:plane_fill | 0.0518 | +0.0% | 12% | [+0.0, +5.5] |
| detected+1.5:plane_fill | 0.0509 | +0.0% | 12% | [+0.0, +6.8] |
| deblock_oracle:plane_fill | 0.0592 | +4.8% | 38% | [-2.9, +22.1] |
| pipe_photometric:plane_fill | 0.0489 | -1.4% | 55% | [-8.4, +9.6] |
| pipe_cap_first:plane_fill | 0.0489 | -1.4% | 55% | [-5.6, +11.1] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.0581)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0590 | -2.6% | 60% | [-8.5, +1.1] |
| oracle:inpaint_erp | 0.0672 | +7.2% | 30% | [+2.0, +12.2] |
| oracle+1.5:inpaint_erp | 0.0666 | +8.4% | 25% | [+3.7, +15.1] |
| detected:inpaint_erp | 0.0631 | +0.0% | 18% | [+0.0, +1.3] |
| detected+1.5:inpaint_erp | 0.0668 | +0.0% | 18% | [+0.0, +2.2] |
| deblock_oracle:inpaint_erp | 0.0667 | +4.1% | 45% | [-3.2, +17.6] |
| pipe_photometric:inpaint_erp | 0.0609 | +0.6% | 48% | [-6.5, +5.1] |
| pipe_cap_first:inpaint_erp | 0.0614 | +1.2% | 48% | [-6.0, +5.0] |
| oracle:inpaint_tangent | 0.0682 | +7.5% | 32% | [+1.9, +11.7] |
| oracle+1.5:inpaint_tangent | 0.0691 | +9.2% | 20% | [+4.6, +14.0] |
| detected:inpaint_tangent | 0.0620 | +0.0% | 12% | [+0.0, +3.6] |
| detected+1.5:inpaint_tangent | 0.0620 | +0.0% | 12% | [+0.0, +3.7] |
| deblock_oracle:inpaint_tangent | 0.0697 | +6.4% | 40% | [-2.1, +11.3] |
| pipe_photometric:inpaint_tangent | 0.0599 | +1.0% | 48% | [-7.6, +5.9] |
| pipe_cap_first:inpaint_tangent | 0.0600 | +1.2% | 48% | [-7.5, +7.9] |
| oracle:plane_fill | 0.0690 | +8.9% | 28% | [+3.4, +13.0] |
| oracle+1.5:plane_fill | 0.0683 | +10.9% | 18% | [+7.0, +15.8] |
| detected:plane_fill | 0.0595 | +0.0% | 15% | [+0.0, +3.1] |
| detected+1.5:plane_fill | 0.0606 | +0.0% | 12% | [+0.0, +3.0] |
| deblock_oracle:plane_fill | 0.0697 | +6.4% | 38% | [-2.1, +11.5] |
| pipe_photometric:plane_fill | 0.0599 | +1.2% | 48% | [-7.6, +6.7] |
| pipe_cap_first:plane_fill | 0.0600 | +1.2% | 48% | [-7.5, +8.7] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.990 | 0.989 | 0.986 |
| nadir+jpeg | 1.000 | 0.986 | 1.001 |
