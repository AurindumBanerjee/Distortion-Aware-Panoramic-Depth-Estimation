# Nadir + JPEG diagnosis: da2_nyc

model `da2` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 45% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 +0.61)

## nadir · protocol `align-all` · region AbsRel (raw median 0.7203)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.7306 | +2.9% | 32% | [+0.9, +5.1] |
| oracle+1.5:inpaint_erp | 0.7314 | +3.5% | 28% | [+1.2, +5.2] |
| detected:inpaint_erp | 0.7199 | +2.8% | 32% | [+0.9, +5.1] |
| detected+1.5:inpaint_erp | 0.7191 | +2.9% | 30% | [+1.2, +4.6] |
| pipe:inpaint_erp | 0.7199 | +2.8% | 32% | [+0.9, +5.1] |
| oracle:inpaint_tangent | 0.7516 | +6.5% | 10% | [+4.6, +7.4] |
| oracle+1.5:inpaint_tangent | 0.7602 | +6.7% | 10% | [+4.6, +8.6] |
| detected:inpaint_tangent | 0.7514 | +6.4% | 12% | [+4.5, +7.7] |
| detected+1.5:inpaint_tangent | 0.7544 | +6.5% | 15% | [+4.4, +8.3] |
| pipe:inpaint_tangent | 0.7514 | +6.4% | 12% | [+4.5, +7.7] |
| oracle:plane_fill | 0.7610 | +6.5% | 10% | [+5.2, +7.4] |
| oracle+1.5:plane_fill | 0.7604 | +6.6% | 10% | [+5.1, +8.5] |
| detected:plane_fill | 0.7610 | +6.2% | 12% | [+4.8, +8.0] |
| detected+1.5:plane_fill | 0.7513 | +6.2% | 15% | [+4.9, +8.4] |
| pipe:plane_fill | 0.7610 | +6.2% | 12% | [+4.8, +8.0] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.6243)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.6194 | -1.9% | 80% | [-3.0, -1.3] |
| oracle+1.5:inpaint_erp | 0.6121 | -1.9% | 80% | [-3.2, -1.3] |
| detected:inpaint_erp | 0.6192 | -1.9% | 80% | [-3.0, -1.4] |
| detected+1.5:inpaint_erp | 0.6120 | -1.7% | 78% | [-2.8, -1.2] |
| pipe:inpaint_erp | 0.6192 | -1.9% | 80% | [-3.0, -1.4] |
| oracle:inpaint_tangent | 0.6204 | -1.2% | 68% | [-2.3, -0.5] |
| oracle+1.5:inpaint_tangent | 0.6137 | -1.2% | 68% | [-2.1, -0.1] |
| detected:inpaint_tangent | 0.6198 | -1.1% | 65% | [-2.1, -0.1] |
| detected+1.5:inpaint_tangent | 0.6138 | -1.3% | 68% | [-2.4, -0.2] |
| pipe:inpaint_tangent | 0.6198 | -1.1% | 65% | [-2.1, -0.1] |
| oracle:plane_fill | 0.6204 | -1.2% | 68% | [-2.3, -0.5] |
| oracle+1.5:plane_fill | 0.6137 | -1.2% | 68% | [-2.1, -0.1] |
| detected:plane_fill | 0.6198 | -1.1% | 65% | [-2.1, -0.1] |
| detected+1.5:plane_fill | 0.6139 | -1.3% | 68% | [-2.4, -0.2] |
| pipe:plane_fill | 0.6198 | -1.1% | 65% | [-2.1, -0.1] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.6758)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.6914 | +2.3% | 25% | [+1.6, +3.9] |
| oracle+1.5:inpaint_erp | 0.6907 | +2.3% | 28% | [+1.5, +4.4] |
| detected:inpaint_erp | 0.6912 | +2.3% | 25% | [+1.6, +4.5] |
| detected+1.5:inpaint_erp | 0.6898 | +2.2% | 30% | [+1.5, +4.2] |
| pipe:inpaint_erp | 0.6912 | +2.3% | 25% | [+1.6, +4.5] |
| oracle:inpaint_tangent | 0.6948 | +4.0% | 8% | [+2.8, +5.7] |
| oracle+1.5:inpaint_tangent | 0.6946 | +4.2% | 12% | [+2.7, +5.9] |
| detected:inpaint_tangent | 0.6950 | +4.0% | 10% | [+2.8, +5.9] |
| detected+1.5:inpaint_tangent | 0.6943 | +4.1% | 20% | [+2.5, +5.7] |
| pipe:inpaint_tangent | 0.6950 | +4.0% | 10% | [+2.8, +5.9] |
| oracle:plane_fill | 0.6948 | +4.0% | 8% | [+2.8, +5.8] |
| oracle+1.5:plane_fill | 0.6949 | +4.2% | 12% | [+2.7, +5.9] |
| detected:plane_fill | 0.6951 | +4.0% | 10% | [+2.8, +5.9] |
| detected+1.5:plane_fill | 0.6947 | +4.1% | 20% | [+2.6, +5.7] |
| pipe:plane_fill | 0.6951 | +4.0% | 10% | [+2.8, +5.9] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.6326)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.6305 | -0.5% | 65% | [-1.7, -0.0] |
| oracle+1.5:inpaint_erp | 0.6299 | -0.5% | 65% | [-1.3, +0.1] |
| detected:inpaint_erp | 0.6305 | -0.6% | 68% | [-1.6, -0.0] |
| detected+1.5:inpaint_erp | 0.6294 | -0.6% | 70% | [-2.6, -0.1] |
| pipe:inpaint_erp | 0.6305 | -0.6% | 68% | [-1.6, -0.0] |
| oracle:inpaint_tangent | 0.6346 | +0.6% | 38% | [-0.1, +2.1] |
| oracle+1.5:inpaint_tangent | 0.6345 | +0.6% | 35% | [+0.0, +2.3] |
| detected:inpaint_tangent | 0.6344 | +0.4% | 38% | [-0.3, +2.0] |
| detected+1.5:inpaint_tangent | 0.6345 | +0.4% | 38% | [-0.2, +2.1] |
| pipe:inpaint_tangent | 0.6344 | +0.4% | 38% | [-0.3, +2.0] |
| oracle:plane_fill | 0.6345 | +0.6% | 35% | [-0.1, +2.1] |
| oracle+1.5:plane_fill | 0.6344 | +0.6% | 32% | [+0.1, +2.3] |
| detected:plane_fill | 0.6341 | +0.5% | 38% | [-0.3, +2.0] |
| detected+1.5:plane_fill | 0.6344 | +0.6% | 38% | [-0.2, +2.1] |
| pipe:plane_fill | 0.6341 | +0.5% | 38% | [-0.3, +2.0] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.8240)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.7877 | -1.3% | 60% | [-1.8, +0.3] |
| oracle:inpaint_erp | 0.8229 | +3.9% | 15% | [+2.9, +6.5] |
| oracle+1.5:inpaint_erp | 0.8256 | +6.2% | 10% | [+3.3, +8.0] |
| detected:inpaint_erp | 0.8245 | +0.0% | 2% | [+0.0, +2.7] |
| detected+1.5:inpaint_erp | 0.8249 | +0.0% | 0% | [+0.0, +2.3] |
| deblock_oracle:inpaint_erp | 0.8024 | +3.4% | 30% | [+1.8, +5.7] |
| pipe_photometric:inpaint_erp | 0.8130 | +2.4% | 32% | [+0.3, +4.4] |
| pipe_cap_first:inpaint_erp | 0.8119 | +2.3% | 32% | [+0.3, +4.4] |
| oracle:inpaint_tangent | 0.7704 | +2.2% | 32% | [+0.9, +4.4] |
| oracle+1.5:inpaint_tangent | 0.7803 | +2.2% | 32% | [+0.8, +4.8] |
| detected:inpaint_tangent | 0.8243 | +0.0% | 0% | [+0.0, +2.0] |
| detected+1.5:inpaint_tangent | 0.8247 | +0.0% | 0% | [+0.0, +2.0] |
| deblock_oracle:inpaint_tangent | 0.7797 | +2.0% | 32% | [+0.1, +4.1] |
| pipe_photometric:inpaint_tangent | 0.8161 | +2.2% | 30% | [+0.4, +4.4] |
| pipe_cap_first:inpaint_tangent | 0.8159 | +2.2% | 30% | [+0.4, +4.4] |
| oracle:plane_fill | 0.7683 | +2.0% | 30% | [+0.6, +4.2] |
| oracle+1.5:plane_fill | 0.7762 | +2.1% | 30% | [+0.7, +4.5] |
| detected:plane_fill | 0.8242 | +0.0% | 0% | [+0.0, +1.3] |
| detected+1.5:plane_fill | 0.8242 | +0.0% | 0% | [+0.0, +1.3] |
| deblock_oracle:plane_fill | 0.7785 | +2.2% | 38% | [-0.0, +3.5] |
| pipe_photometric:plane_fill | 0.8138 | +2.2% | 32% | [+0.2, +4.0] |
| pipe_cap_first:plane_fill | 0.8135 | +2.2% | 32% | [+0.2, +3.8] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.6450)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.6204 | -0.0% | 50% | [-1.7, +1.1] |
| oracle:inpaint_erp | 0.6515 | +0.2% | 48% | [-2.4, +2.7] |
| oracle+1.5:inpaint_erp | 0.6481 | -0.1% | 50% | [-1.8, +2.9] |
| detected:inpaint_erp | 0.6447 | +0.0% | 25% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.6456 | +0.0% | 28% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.6564 | -0.1% | 52% | [-3.3, +0.8] |
| pipe_photometric:inpaint_erp | 0.6366 | +0.1% | 45% | [-2.4, +1.3] |
| pipe_cap_first:inpaint_erp | 0.6368 | -0.1% | 52% | [-2.5, +1.3] |
| oracle:inpaint_tangent | 0.6452 | -0.7% | 70% | [-1.3, -0.2] |
| oracle+1.5:inpaint_tangent | 0.6441 | -0.6% | 60% | [-1.4, +0.4] |
| detected:inpaint_tangent | 0.6360 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.6376 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.6626 | -0.5% | 52% | [-1.7, +1.0] |
| pipe_photometric:inpaint_tangent | 0.6380 | +0.1% | 48% | [-1.8, +1.3] |
| pipe_cap_first:inpaint_tangent | 0.6379 | +0.1% | 48% | [-1.8, +1.3] |
| oracle:plane_fill | 0.6452 | -0.7% | 70% | [-1.3, -0.2] |
| oracle+1.5:plane_fill | 0.6441 | -0.6% | 60% | [-1.2, +0.4] |
| detected:plane_fill | 0.6360 | +0.0% | 30% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.6376 | +0.0% | 30% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.6626 | -0.2% | 50% | [-1.7, +1.0] |
| pipe_photometric:plane_fill | 0.6380 | +0.1% | 48% | [-1.8, +1.3] |
| pipe_cap_first:plane_fill | 0.6379 | +0.1% | 48% | [-1.8, +1.3] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.7231)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.6893 | -0.8% | 55% | [-1.7, +0.9] |
| oracle:inpaint_erp | 0.7656 | +5.0% | 20% | [+2.6, +7.9] |
| oracle+1.5:inpaint_erp | 0.7613 | +6.5% | 15% | [+3.1, +9.9] |
| detected:inpaint_erp | 0.7528 | +0.0% | 5% | [+0.0, +1.6] |
| detected+1.5:inpaint_erp | 0.7533 | +0.0% | 2% | [+0.0, +1.3] |
| deblock_oracle:inpaint_erp | 0.7540 | +3.8% | 30% | [+1.4, +6.1] |
| pipe_photometric:inpaint_erp | 0.7458 | +1.5% | 28% | [+0.5, +4.7] |
| pipe_cap_first:inpaint_erp | 0.7425 | +1.5% | 28% | [+0.4, +4.5] |
| oracle:inpaint_tangent | 0.7459 | +4.8% | 12% | [+3.1, +8.9] |
| oracle+1.5:inpaint_tangent | 0.7457 | +5.1% | 10% | [+2.7, +9.6] |
| detected:inpaint_tangent | 0.7405 | +0.0% | 2% | [+0.0, +0.8] |
| detected+1.5:inpaint_tangent | 0.7414 | +0.0% | 2% | [+0.0, +0.9] |
| deblock_oracle:inpaint_tangent | 0.7414 | +4.4% | 20% | [+2.7, +7.8] |
| pipe_photometric:inpaint_tangent | 0.7216 | +1.3% | 30% | [+0.4, +4.2] |
| pipe_cap_first:inpaint_tangent | 0.7206 | +1.3% | 30% | [+0.4, +4.2] |
| oracle:plane_fill | 0.7458 | +4.8% | 12% | [+3.1, +8.9] |
| oracle+1.5:plane_fill | 0.7455 | +5.1% | 10% | [+2.7, +9.6] |
| detected:plane_fill | 0.7404 | +0.0% | 2% | [+0.0, +0.8] |
| detected+1.5:plane_fill | 0.7409 | +0.0% | 2% | [+0.0, +0.9] |
| deblock_oracle:plane_fill | 0.7413 | +4.4% | 20% | [+2.7, +7.8] |
| pipe_photometric:plane_fill | 0.7211 | +1.3% | 30% | [+0.4, +4.1] |
| pipe_cap_first:plane_fill | 0.7200 | +1.3% | 30% | [+0.4, +4.2] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.6754)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.6674 | -0.1% | 52% | [-1.4, +1.1] |
| oracle:inpaint_erp | 0.6865 | +0.7% | 42% | [-1.7, +3.0] |
| oracle+1.5:inpaint_erp | 0.6930 | +0.7% | 42% | [-1.0, +4.2] |
| detected:inpaint_erp | 0.6746 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:inpaint_erp | 0.6743 | +0.0% | 20% | [+0.0, +0.0] |
| deblock_oracle:inpaint_erp | 0.6862 | +0.7% | 45% | [-2.9, +2.0] |
| pipe_photometric:inpaint_erp | 0.6762 | +1.0% | 45% | [-1.2, +1.8] |
| pipe_cap_first:inpaint_erp | 0.6763 | +1.0% | 45% | [-1.3, +1.8] |
| oracle:inpaint_tangent | 0.6770 | -0.5% | 55% | [-2.3, +0.4] |
| oracle+1.5:inpaint_tangent | 0.6774 | -0.4% | 60% | [-2.4, +0.8] |
| detected:inpaint_tangent | 0.6723 | +0.0% | 18% | [+0.0, +0.0] |
| detected+1.5:inpaint_tangent | 0.6723 | +0.0% | 25% | [+0.0, +0.0] |
| deblock_oracle:inpaint_tangent | 0.6851 | -0.6% | 55% | [-1.7, +0.8] |
| pipe_photometric:inpaint_tangent | 0.6703 | +1.0% | 42% | [-0.3, +1.8] |
| pipe_cap_first:inpaint_tangent | 0.6706 | +1.0% | 42% | [-0.4, +1.8] |
| oracle:plane_fill | 0.6764 | -0.5% | 57% | [-2.2, +0.3] |
| oracle+1.5:plane_fill | 0.6767 | -0.5% | 60% | [-2.5, +0.7] |
| detected:plane_fill | 0.6723 | +0.0% | 22% | [+0.0, +0.0] |
| detected+1.5:plane_fill | 0.6723 | +0.0% | 25% | [+0.0, +0.0] |
| deblock_oracle:plane_fill | 0.6849 | -0.6% | 55% | [-1.6, +0.8] |
| pipe_photometric:plane_fill | 0.6699 | +1.0% | 42% | [-0.4, +1.7] |
| pipe_cap_first:plane_fill | 0.6703 | +1.0% | 42% | [-0.5, +1.6] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.272 | 0.246 | 0.266 |
| nadir+jpeg | 0.174 | 0.224 | 0.175 |
