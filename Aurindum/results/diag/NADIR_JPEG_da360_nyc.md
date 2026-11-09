# Nadir + JPEG diagnosis: da360_nyc

model `da360` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 45% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +0.61)

## nadir · protocol `align-all` · region AbsRel (raw median 0.0140)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0282 | +14.5% | 12% | [+8.6, +22.7] |
| oracle+1.5:inpaint_erp | 0.0269 | +19.8% | 12% | [+14.8, +32.1] |
| detected:inpaint_erp | 0.0283 | +17.9% | 12% | [+11.7, +26.6] |
| detected+1.5:inpaint_erp | 0.0283 | +21.6% | 15% | [+13.7, +31.1] |
| pipe:inpaint_erp | 0.0283 | +17.9% | 12% | [+11.7, +26.6] |
| oracle:inpaint_tangent | 0.0148 | +10.0% | 22% | [+6.1, +14.3] |
| oracle+1.5:inpaint_tangent | 0.0164 | +16.1% | 15% | [+10.7, +25.9] |
| detected:inpaint_tangent | 0.0187 | +13.8% | 20% | [+7.9, +23.6] |
| detected+1.5:inpaint_tangent | 0.0231 | +21.2% | 18% | [+11.7, +32.4] |
| pipe:inpaint_tangent | 0.0187 | +13.8% | 20% | [+7.9, +23.6] |
| oracle:plane_fill | 0.0276 | +8.3% | 42% | [-4.8, +13.3] |
| oracle+1.5:plane_fill | 0.0297 | +9.3% | 45% | [-6.8, +25.9] |
| detected:plane_fill | 0.0276 | +8.1% | 40% | [-5.1, +14.8] |
| detected+1.5:plane_fill | 0.0294 | +11.2% | 48% | [-6.8, +27.1] |
| pipe:plane_fill | 0.0276 | +8.1% | 40% | [-5.1, +14.8] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.0785)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0788 | +1.1% | 35% | [+0.1, +1.8] |
| oracle+1.5:inpaint_erp | 0.0772 | +1.3% | 28% | [+0.5, +2.6] |
| detected:inpaint_erp | 0.0788 | +1.0% | 32% | [+0.3, +1.8] |
| detected+1.5:inpaint_erp | 0.0802 | +1.6% | 25% | [+1.1, +5.0] |
| pipe:inpaint_erp | 0.0788 | +1.0% | 32% | [+0.3, +1.8] |
| oracle:inpaint_tangent | 0.0781 | +0.4% | 42% | [-0.6, +0.9] |
| oracle+1.5:inpaint_tangent | 0.0786 | +0.9% | 38% | [-0.1, +2.2] |
| detected:inpaint_tangent | 0.0786 | +0.7% | 38% | [-0.5, +1.1] |
| detected+1.5:inpaint_tangent | 0.0793 | +0.9% | 35% | [+0.1, +2.8] |
| pipe:inpaint_tangent | 0.0786 | +0.7% | 38% | [-0.5, +1.1] |
| oracle:plane_fill | 0.0825 | +0.1% | 45% | [-0.4, +1.1] |
| oracle+1.5:plane_fill | 0.0825 | +0.3% | 42% | [-0.3, +3.5] |
| detected:plane_fill | 0.0825 | +0.1% | 42% | [-0.4, +0.9] |
| detected+1.5:plane_fill | 0.0825 | +0.2% | 42% | [-0.3, +3.5] |
| pipe:plane_fill | 0.0825 | +0.1% | 42% | [-0.4, +0.9] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.0173)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0237 | +10.1% | 28% | [+3.5, +14.4] |
| oracle+1.5:inpaint_erp | 0.0264 | +13.2% | 30% | [+6.3, +16.6] |
| detected:inpaint_erp | 0.0222 | +11.0% | 22% | [+4.9, +16.7] |
| detected+1.5:inpaint_erp | 0.0348 | +14.4% | 22% | [+7.8, +18.6] |
| pipe:inpaint_erp | 0.0222 | +11.0% | 22% | [+4.9, +16.7] |
| oracle:inpaint_tangent | 0.0132 | +4.3% | 32% | [+0.2, +8.0] |
| oracle+1.5:inpaint_tangent | 0.0158 | +10.8% | 32% | [+1.1, +16.6] |
| detected:inpaint_tangent | 0.0132 | +7.8% | 30% | [+2.6, +10.1] |
| detected+1.5:inpaint_tangent | 0.0183 | +11.2% | 28% | [+4.1, +17.4] |
| pipe:inpaint_tangent | 0.0132 | +7.8% | 30% | [+2.6, +10.1] |
| oracle:plane_fill | 0.0230 | +7.6% | 35% | [+0.0, +13.7] |
| oracle+1.5:plane_fill | 0.0272 | +15.3% | 28% | [+2.1, +22.6] |
| detected:plane_fill | 0.0230 | +8.4% | 35% | [+0.3, +15.9] |
| detected+1.5:plane_fill | 0.0272 | +14.1% | 28% | [+2.3, +22.6] |
| pipe:plane_fill | 0.0230 | +8.4% | 35% | [+0.3, +15.9] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.0665)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.0701 | +1.5% | 30% | [+0.7, +2.2] |
| oracle+1.5:inpaint_erp | 0.0698 | +2.3% | 28% | [+0.9, +4.6] |
| detected:inpaint_erp | 0.0702 | +1.7% | 28% | [+1.1, +4.0] |
| detected+1.5:inpaint_erp | 0.0726 | +2.6% | 25% | [+1.3, +5.5] |
| pipe:inpaint_erp | 0.0702 | +1.7% | 28% | [+1.1, +4.0] |
| oracle:inpaint_tangent | 0.0680 | +0.6% | 40% | [-0.3, +1.6] |
| oracle+1.5:inpaint_tangent | 0.0696 | +0.9% | 38% | [-0.1, +2.4] |
| detected:inpaint_tangent | 0.0687 | +0.9% | 35% | [+0.1, +1.6] |
| detected+1.5:inpaint_tangent | 0.0696 | +0.9% | 35% | [+0.2, +4.1] |
| pipe:inpaint_tangent | 0.0687 | +0.9% | 35% | [+0.1, +1.6] |
| oracle:plane_fill | 0.0732 | +0.1% | 48% | [-0.3, +1.5] |
| oracle+1.5:plane_fill | 0.0741 | +0.2% | 40% | [-0.2, +5.9] |
| detected:plane_fill | 0.0739 | +0.3% | 48% | [-0.3, +1.5] |
| detected+1.5:plane_fill | 0.0761 | +0.3% | 40% | [-0.2, +5.9] |
| pipe:plane_fill | 0.0739 | +0.3% | 48% | [-0.3, +1.5] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.0459)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0373 | +5.8% | 40% | [-0.4, +13.0] |
| oracle:inpaint_erp | 0.0541 | +26.3% | 20% | [+8.5, +34.6] |
| oracle+1.5:inpaint_erp | 0.0602 | +24.9% | 22% | [+9.0, +36.3] |
| detected:inpaint_erp | 0.0462 | +0.0% | 15% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.0538 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.0442 | +41.2% | 25% | [+8.6, +50.6] |
| pipe_photometric:inpaint_erp | 0.0394 | +8.5% | 40% | [-2.6, +16.4] |
| pipe_cap_first:inpaint_erp | 0.0379 | +8.4% | 40% | [-2.6, +16.3] |
| oracle:inpaint_tangent | 0.0369 | +6.5% | 38% | [-0.8, +16.6] |
| oracle+1.5:inpaint_tangent | 0.0415 | +16.2% | 38% | [-3.0, +32.9] |
| detected:inpaint_tangent | 0.0478 | +0.0% | 25% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.0493 | +0.0% | 22% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0377 | +20.3% | 35% | [-1.0, +38.2] |
| pipe_photometric:inpaint_tangent | 0.0355 | +5.0% | 45% | [-4.3, +16.3] |
| pipe_cap_first:inpaint_tangent | 0.0350 | +5.0% | 42% | [-4.0, +16.3] |
| oracle:plane_fill | 0.0435 | +6.1% | 38% | [-2.5, +15.8] |
| oracle+1.5:plane_fill | 0.0506 | +11.9% | 38% | [-3.2, +37.2] |
| detected:plane_fill | 0.0538 | +0.0% | 28% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.0525 | +0.0% | 28% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.0397 | +15.2% | 42% | [-8.0, +41.9] |
| pipe_photometric:plane_fill | 0.0359 | +3.4% | 42% | [-2.6, +15.6] |
| pipe_cap_first:plane_fill | 0.0354 | +3.8% | 40% | [-2.6, +15.6] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.1547)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1570 | +1.0% | 45% | [-2.8, +3.4] |
| oracle:inpaint_erp | 0.1553 | +1.6% | 30% | [+0.4, +4.2] |
| oracle+1.5:inpaint_erp | 0.1578 | +1.7% | 32% | [+0.3, +5.2] |
| detected:inpaint_erp | 0.1546 | +0.0% | 12% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.1539 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.1682 | +2.9% | 42% | [-3.3, +11.2] |
| pipe_photometric:inpaint_erp | 0.1580 | +1.7% | 42% | [-2.6, +5.1] |
| pipe_cap_first:inpaint_erp | 0.1580 | +1.6% | 42% | [-2.6, +5.1] |
| oracle:inpaint_tangent | 0.1576 | +0.3% | 48% | [-1.2, +2.9] |
| oracle+1.5:inpaint_tangent | 0.1650 | +1.0% | 45% | [-1.7, +4.0] |
| detected:inpaint_tangent | 0.1545 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1544 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1616 | +2.9% | 45% | [-5.0, +6.1] |
| pipe_photometric:inpaint_tangent | 0.1589 | +1.8% | 42% | [-2.4, +4.3] |
| pipe_cap_first:inpaint_tangent | 0.1590 | +1.8% | 42% | [-2.5, +4.4] |
| oracle:plane_fill | 0.1578 | +0.3% | 45% | [-0.9, +2.6] |
| oracle+1.5:plane_fill | 0.1650 | +1.0% | 45% | [-1.0, +3.6] |
| detected:plane_fill | 0.1551 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1547 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.1624 | +2.8% | 45% | [-5.1, +5.8] |
| pipe_photometric:plane_fill | 0.1590 | +1.8% | 42% | [-2.2, +4.9] |
| pipe_cap_first:plane_fill | 0.1590 | +1.8% | 42% | [-2.3, +4.9] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.0656)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.0736 | +1.2% | 48% | [-7.4, +8.6] |
| oracle:inpaint_erp | 0.0967 | +3.9% | 40% | [-0.8, +15.7] |
| oracle+1.5:inpaint_erp | 0.1020 | +6.6% | 35% | [-0.4, +15.6] |
| detected:inpaint_erp | 0.0691 | +0.0% | 15% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.0711 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.0796 | +11.0% | 45% | [-14.7, +28.8] |
| pipe_photometric:inpaint_erp | 0.0782 | +2.9% | 45% | [-10.5, +13.8] |
| pipe_cap_first:inpaint_erp | 0.0777 | +2.9% | 45% | [-10.5, +13.8] |
| oracle:inpaint_tangent | 0.0722 | -0.0% | 50% | [-3.6, +6.2] |
| oracle+1.5:inpaint_tangent | 0.0839 | +5.5% | 38% | [-1.0, +13.8] |
| detected:inpaint_tangent | 0.0711 | +0.0% | 15% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.0711 | +0.0% | 15% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.0738 | +3.1% | 48% | [-15.7, +25.2] |
| pipe_photometric:inpaint_tangent | 0.0740 | +2.9% | 45% | [-10.5, +13.5] |
| pipe_cap_first:inpaint_tangent | 0.0737 | +2.9% | 45% | [-10.5, +13.8] |
| oracle:plane_fill | 0.0730 | -2.0% | 52% | [-4.8, +6.4] |
| oracle+1.5:plane_fill | 0.0858 | +3.7% | 40% | [-4.3, +15.9] |
| detected:plane_fill | 0.0711 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.0711 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.0747 | +4.6% | 45% | [-16.7, +28.3] |
| pipe_photometric:plane_fill | 0.0749 | +3.1% | 42% | [-7.9, +13.5] |
| pipe_cap_first:plane_fill | 0.0746 | +3.0% | 42% | [-8.6, +13.8] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.1349)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1402 | +1.9% | 42% | [-0.7, +5.0] |
| oracle:inpaint_erp | 0.1620 | +2.6% | 28% | [+1.4, +7.1] |
| oracle+1.5:inpaint_erp | 0.1643 | +3.0% | 28% | [+1.2, +7.6] |
| detected:inpaint_erp | 0.1360 | +0.0% | 12% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.1372 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.1584 | +4.6% | 38% | [-2.0, +15.9] |
| pipe_photometric:inpaint_erp | 0.1465 | +2.5% | 40% | [-0.7, +6.2] |
| pipe_cap_first:inpaint_erp | 0.1465 | +2.6% | 40% | [-0.7, +6.4] |
| oracle:inpaint_tangent | 0.1510 | +1.4% | 32% | [+0.0, +3.8] |
| oracle+1.5:inpaint_tangent | 0.1648 | +2.1% | 38% | [-0.3, +5.6] |
| detected:inpaint_tangent | 0.1372 | +0.0% | 15% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.1372 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1510 | +4.0% | 45% | [-4.2, +10.1] |
| pipe_photometric:inpaint_tangent | 0.1452 | +2.5% | 42% | [-0.8, +5.7] |
| pipe_cap_first:inpaint_tangent | 0.1451 | +2.5% | 42% | [-0.8, +5.8] |
| oracle:plane_fill | 0.1510 | +1.7% | 30% | [+0.3, +3.8] |
| oracle+1.5:plane_fill | 0.1650 | +2.2% | 35% | [-0.0, +4.7] |
| detected:plane_fill | 0.1372 | +0.0% | 12% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.1372 | +0.0% | 12% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.1511 | +3.8% | 45% | [-4.3, +9.9] |
| pipe_photometric:plane_fill | 0.1453 | +3.0% | 42% | [-0.8, +5.8] |
| pipe_cap_first:plane_fill | 0.1452 | +2.9% | 42% | [-0.8, +5.8] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.996 | 0.997 | 0.997 |
| nadir+jpeg | 0.999 | 0.998 | 0.998 |
