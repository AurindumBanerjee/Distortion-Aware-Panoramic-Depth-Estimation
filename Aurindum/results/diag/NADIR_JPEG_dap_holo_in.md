# Nadir + JPEG diagnosis: dap_holo_in

model `dap` · 40 frames · nadir cap below -62 deg · JPEG q8. Protocols: `none`, `align-all`. Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.

* `nadir`: cap detected as nadir in 100% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)
* `nadir+jpeg`: cap detected as nadir in 90% of frames; detected edge minus true edge: median -0.12 deg (p5 -2.23, p95 -0.12)

## nadir · protocol `none` · region AbsRel (raw median 0.7101)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.4996 | -30.7% | 92% | [-40.8, -24.8] |
| oracle+1.5:inpaint_erp | 0.5480 | -25.7% | 92% | [-29.8, -18.6] |
| detected:inpaint_erp | 0.5056 | -30.6% | 92% | [-35.7, -22.5] |
| detected+1.5:inpaint_erp | 0.5516 | -24.8% | 92% | [-28.3, -18.5] |
| pipe:inpaint_erp | 0.5056 | -30.6% | 92% | [-35.7, -22.5] |
| oracle:inpaint_tangent | 0.5549 | -23.3% | 92% | [-28.4, -18.2] |
| oracle+1.5:inpaint_tangent | 0.6525 | -10.4% | 82% | [-15.4, -7.2] |
| detected:inpaint_tangent | 0.5753 | -18.8% | 90% | [-25.2, -15.8] |
| detected+1.5:inpaint_tangent | 0.6511 | -9.8% | 82% | [-15.6, -7.0] |
| pipe:inpaint_tangent | 0.5753 | -18.8% | 90% | [-25.2, -15.8] |
| oracle:plane_fill | 0.5432 | -27.1% | 92% | [-34.5, -23.2] |
| oracle+1.5:plane_fill | 0.6126 | -12.8% | 90% | [-21.7, -8.5] |
| detected:plane_fill | 0.5667 | -23.5% | 90% | [-29.0, -16.9] |
| detected+1.5:plane_fill | 0.6409 | -11.5% | 90% | [-20.8, -8.4] |
| pipe:plane_fill | 0.5667 | -23.5% | 90% | [-29.0, -16.9] |

## nadir · protocol `none` · outside AbsRel (raw median 0.1631)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1680 | +4.2% | 28% | [+2.3, +10.4] |
| oracle+1.5:inpaint_erp | 0.1744 | +5.6% | 28% | [+2.7, +11.6] |
| detected:inpaint_erp | 0.1681 | +4.4% | 28% | [+2.5, +10.7] |
| detected+1.5:inpaint_erp | 0.1773 | +5.9% | 28% | [+4.1, +12.3] |
| pipe:inpaint_erp | 0.1681 | +4.4% | 28% | [+2.5, +10.7] |
| oracle:inpaint_tangent | 0.1640 | +0.9% | 45% | [-0.8, +4.6] |
| oracle+1.5:inpaint_tangent | 0.1647 | +3.1% | 30% | [+0.6, +4.7] |
| detected:inpaint_tangent | 0.1646 | +1.0% | 42% | [-0.8, +3.2] |
| detected+1.5:inpaint_tangent | 0.1648 | +3.4% | 30% | [+0.8, +5.7] |
| pipe:inpaint_tangent | 0.1646 | +1.0% | 42% | [-0.8, +3.2] |
| oracle:plane_fill | 0.1640 | +0.9% | 45% | [-0.8, +4.6] |
| oracle+1.5:plane_fill | 0.1643 | +3.1% | 38% | [-0.4, +4.7] |
| detected:plane_fill | 0.1646 | +1.0% | 42% | [-0.8, +3.2] |
| detected+1.5:plane_fill | 0.1648 | +3.4% | 38% | [-0.3, +5.7] |
| pipe:plane_fill | 0.1646 | +1.0% | 42% | [-0.8, +3.2] |

## nadir · protocol `none` · ring AbsRel (raw median 0.1356)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1511 | +9.8% | 30% | [+2.5, +15.9] |
| oracle+1.5:inpaint_erp | 0.1621 | +28.4% | 10% | [+18.2, +39.3] |
| detected:inpaint_erp | 0.1625 | +12.7% | 28% | [+4.4, +21.7] |
| detected+1.5:inpaint_erp | 0.1689 | +28.6% | 10% | [+22.5, +45.2] |
| pipe:inpaint_erp | 0.1625 | +12.7% | 28% | [+4.4, +21.7] |
| oracle:inpaint_tangent | 0.1309 | -1.3% | 52% | [-5.5, +4.6] |
| oracle+1.5:inpaint_tangent | 0.1510 | +20.4% | 10% | [+15.5, +27.5] |
| detected:inpaint_tangent | 0.1313 | +1.8% | 45% | [-3.1, +6.6] |
| detected+1.5:inpaint_tangent | 0.1599 | +22.0% | 8% | [+17.8, +32.2] |
| pipe:inpaint_tangent | 0.1313 | +1.8% | 45% | [-3.1, +6.6] |
| oracle:plane_fill | 0.1309 | -1.3% | 52% | [-5.5, +4.6] |
| oracle+1.5:plane_fill | 0.1510 | +17.5% | 18% | [+14.2, +22.5] |
| detected:plane_fill | 0.1313 | +1.8% | 45% | [-3.1, +6.6] |
| detected+1.5:plane_fill | 0.1599 | +20.9% | 15% | [+16.3, +28.2] |
| pipe:plane_fill | 0.1313 | +1.8% | 45% | [-3.1, +6.6] |

## nadir · protocol `none` · all AbsRel (raw median 0.1941)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1856 | -1.6% | 57% | [-5.7, +2.5] |
| oracle+1.5:inpaint_erp | 0.1896 | -0.0% | 50% | [-3.2, +4.1] |
| detected:inpaint_erp | 0.1873 | -0.9% | 55% | [-5.7, +3.5] |
| detected+1.5:inpaint_erp | 0.1901 | +0.7% | 42% | [-2.5, +4.1] |
| pipe:inpaint_erp | 0.1873 | -0.9% | 55% | [-5.7, +3.5] |
| oracle:inpaint_tangent | 0.1849 | -2.6% | 70% | [-5.1, -0.7] |
| oracle+1.5:inpaint_tangent | 0.1877 | +0.5% | 42% | [-1.3, +2.1] |
| detected:inpaint_tangent | 0.1868 | -1.9% | 68% | [-4.5, -0.5] |
| detected+1.5:inpaint_tangent | 0.1880 | +0.9% | 38% | [-0.4, +2.9] |
| pipe:inpaint_tangent | 0.1868 | -1.9% | 68% | [-4.5, -0.5] |
| oracle:plane_fill | 0.1729 | -4.5% | 72% | [-9.5, -1.0] |
| oracle+1.5:plane_fill | 0.1829 | -0.4% | 52% | [-4.9, +1.1] |
| detected:plane_fill | 0.1729 | -3.9% | 70% | [-7.6, -0.6] |
| detected+1.5:plane_fill | 0.1836 | +0.3% | 48% | [-4.6, +2.5] |
| pipe:plane_fill | 0.1729 | -3.9% | 70% | [-7.6, -0.6] |

## nadir+jpeg · protocol `none` · region AbsRel (raw median 0.6289)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.6575 | +2.0% | 30% | [+0.2, +3.8] |
| oracle:inpaint_erp | 0.5266 | -15.2% | 82% | [-26.9, -6.3] |
| oracle+1.5:inpaint_erp | 0.5344 | -14.0% | 82% | [-25.8, -5.2] |
| detected:inpaint_erp | 0.5290 | -15.1% | 75% | [-27.4, -6.3] |
| detected+1.5:inpaint_erp | 0.5417 | -14.0% | 72% | [-23.7, -5.0] |
| deblock_oracle:inpaint_erp | 0.4771 | -25.2% | 90% | [-41.7, -15.4] |
| pipe_photometric:inpaint_erp | 0.4946 | -21.6% | 90% | [-34.1, -11.8] |
| pipe_cap_first:inpaint_erp | 0.4925 | -21.8% | 90% | [-34.5, -11.6] |
| oracle:inpaint_tangent | 0.4890 | -22.5% | 90% | [-43.5, -13.7] |
| oracle+1.5:inpaint_tangent | 0.4899 | -21.3% | 88% | [-38.4, -14.3] |
| detected:inpaint_tangent | 0.4790 | -21.4% | 85% | [-39.1, -14.2] |
| detected+1.5:inpaint_tangent | 0.4812 | -20.3% | 82% | [-42.3, -12.9] |
| deblock_oracle:inpaint_tangent | 0.4232 | -31.4% | 95% | [-49.4, -20.3] |
| pipe_photometric:inpaint_tangent | 0.4421 | -28.8% | 92% | [-51.5, -20.2] |
| pipe_cap_first:inpaint_tangent | 0.4415 | -28.6% | 92% | [-51.3, -19.5] |
| oracle:plane_fill | 0.4890 | -22.5% | 90% | [-43.5, -13.7] |
| oracle+1.5:plane_fill | 0.4930 | -21.3% | 88% | [-38.4, -14.3] |
| detected:plane_fill | 0.4790 | -21.4% | 85% | [-39.1, -14.2] |
| detected+1.5:plane_fill | 0.4812 | -20.3% | 82% | [-42.3, -13.0] |
| deblock_oracle:plane_fill | 0.4232 | -31.4% | 95% | [-49.4, -20.4] |
| pipe_photometric:plane_fill | 0.4421 | -28.8% | 92% | [-51.5, -20.2] |
| pipe_cap_first:plane_fill | 0.4415 | -28.6% | 92% | [-51.3, -19.5] |

## nadir+jpeg · protocol `none` · outside AbsRel (raw median 0.4354)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3881 | -8.0% | 82% | [-10.9, -5.9] |
| oracle:inpaint_erp | 0.4886 | +8.4% | 8% | [+5.3, +10.2] |
| oracle+1.5:inpaint_erp | 0.4903 | +9.0% | 8% | [+6.2, +10.2] |
| detected:inpaint_erp | 0.4747 | +7.8% | 5% | [+3.2, +9.9] |
| detected+1.5:inpaint_erp | 0.4748 | +9.0% | 5% | [+5.7, +10.5] |
| deblock_oracle:inpaint_erp | 0.4336 | -2.7% | 60% | [-5.0, +2.3] |
| pipe_photometric:inpaint_erp | 0.4353 | -2.7% | 62% | [-5.2, +1.0] |
| pipe_cap_first:inpaint_erp | 0.4332 | -2.8% | 60% | [-5.2, +0.9] |
| oracle:inpaint_tangent | 0.4335 | +2.1% | 30% | [+1.1, +4.0] |
| oracle+1.5:inpaint_tangent | 0.4360 | +3.0% | 30% | [+1.3, +3.6] |
| detected:inpaint_tangent | 0.4371 | +1.5% | 30% | [+0.0, +3.3] |
| detected+1.5:inpaint_tangent | 0.4418 | +2.2% | 28% | [+0.0, +4.2] |
| deblock_oracle:inpaint_tangent | 0.3937 | -6.6% | 80% | [-10.3, -3.5] |
| pipe_photometric:inpaint_tangent | 0.3874 | -5.7% | 80% | [-10.9, -4.4] |
| pipe_cap_first:inpaint_tangent | 0.3871 | -5.7% | 80% | [-11.1, -4.2] |
| oracle:plane_fill | 0.4335 | +2.1% | 30% | [+1.1, +4.0] |
| oracle+1.5:plane_fill | 0.4360 | +3.0% | 30% | [+1.3, +3.6] |
| detected:plane_fill | 0.4371 | +1.5% | 30% | [+0.0, +3.3] |
| detected+1.5:plane_fill | 0.4418 | +2.2% | 28% | [+0.0, +4.2] |
| deblock_oracle:plane_fill | 0.3937 | -6.6% | 80% | [-10.3, -3.5] |
| pipe_photometric:plane_fill | 0.3874 | -5.7% | 80% | [-10.9, -4.4] |
| pipe_cap_first:plane_fill | 0.3871 | -5.7% | 80% | [-11.1, -4.2] |

## nadir+jpeg · protocol `none` · ring AbsRel (raw median 0.4357)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3654 | -10.3% | 95% | [-15.8, -8.9] |
| oracle:inpaint_erp | 0.5111 | +11.4% | 10% | [+9.2, +19.0] |
| oracle+1.5:inpaint_erp | 0.5181 | +15.8% | 10% | [+10.2, +20.1] |
| detected:inpaint_erp | 0.4888 | +13.3% | 10% | [+8.6, +18.3] |
| detected+1.5:inpaint_erp | 0.4897 | +12.9% | 5% | [+8.8, +21.5] |
| deblock_oracle:inpaint_erp | 0.4515 | +0.6% | 45% | [-2.2, +4.2] |
| pipe_photometric:inpaint_erp | 0.4276 | +0.5% | 45% | [-2.4, +6.4] |
| pipe_cap_first:inpaint_erp | 0.4249 | +0.5% | 48% | [-2.2, +5.7] |
| oracle:inpaint_tangent | 0.4704 | +2.9% | 32% | [+0.2, +5.1] |
| oracle+1.5:inpaint_tangent | 0.4635 | +3.4% | 32% | [+0.8, +6.0] |
| detected:inpaint_tangent | 0.4592 | +2.2% | 35% | [-1.0, +5.3] |
| detected+1.5:inpaint_tangent | 0.4611 | +3.6% | 30% | [+0.0, +6.0] |
| deblock_oracle:inpaint_tangent | 0.4005 | -6.7% | 75% | [-12.6, -2.7] |
| pipe_photometric:inpaint_tangent | 0.4006 | -4.4% | 72% | [-12.7, -2.4] |
| pipe_cap_first:inpaint_tangent | 0.4014 | -4.2% | 72% | [-12.3, -2.1] |
| oracle:plane_fill | 0.4704 | +2.9% | 32% | [+0.3, +5.1] |
| oracle+1.5:plane_fill | 0.4635 | +3.6% | 32% | [+0.8, +6.0] |
| detected:plane_fill | 0.4592 | +2.2% | 35% | [-1.0, +5.3] |
| detected+1.5:plane_fill | 0.4611 | +3.6% | 30% | [+0.0, +6.0] |
| deblock_oracle:plane_fill | 0.4005 | -6.7% | 75% | [-12.6, -2.7] |
| pipe_photometric:plane_fill | 0.4006 | -4.4% | 72% | [-12.7, -2.4] |
| pipe_cap_first:plane_fill | 0.4014 | -4.2% | 72% | [-12.3, -2.1] |

## nadir+jpeg · protocol `none` · all AbsRel (raw median 0.4463)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.4070 | -7.7% | 80% | [-9.9, -5.0] |
| oracle:inpaint_erp | 0.4910 | +5.2% | 18% | [+1.9, +7.5] |
| oracle+1.5:inpaint_erp | 0.4930 | +5.3% | 15% | [+3.5, +8.4] |
| detected:inpaint_erp | 0.4759 | +3.5% | 12% | [+1.5, +6.8] |
| detected+1.5:inpaint_erp | 0.4765 | +4.9% | 15% | [+2.6, +8.0] |
| deblock_oracle:inpaint_erp | 0.4381 | -4.7% | 70% | [-7.4, -0.3] |
| pipe_photometric:inpaint_erp | 0.4416 | -4.5% | 75% | [-6.0, -1.1] |
| pipe_cap_first:inpaint_erp | 0.4396 | -4.5% | 75% | [-6.3, -1.2] |
| oracle:inpaint_tangent | 0.4345 | +1.1% | 42% | [-0.8, +2.5] |
| oracle+1.5:inpaint_tangent | 0.4334 | +1.6% | 38% | [-0.2, +2.8] |
| detected:inpaint_tangent | 0.4337 | +0.3% | 40% | [-0.4, +2.2] |
| detected+1.5:inpaint_tangent | 0.4366 | +0.8% | 35% | [-0.1, +3.3] |
| deblock_oracle:inpaint_tangent | 0.3955 | -7.5% | 80% | [-11.3, -4.1] |
| pipe_photometric:inpaint_tangent | 0.3907 | -7.3% | 82% | [-11.7, -5.0] |
| pipe_cap_first:inpaint_tangent | 0.3905 | -7.3% | 82% | [-11.5, -4.9] |
| oracle:plane_fill | 0.4345 | +1.2% | 42% | [-0.8, +2.5] |
| oracle+1.5:plane_fill | 0.4334 | +1.8% | 38% | [-0.3, +2.8] |
| detected:plane_fill | 0.4337 | +0.3% | 40% | [-0.4, +2.2] |
| detected+1.5:plane_fill | 0.4366 | +0.8% | 35% | [-0.1, +3.3] |
| deblock_oracle:plane_fill | 0.3955 | -7.7% | 80% | [-11.3, -4.1] |
| pipe_photometric:plane_fill | 0.3907 | -7.3% | 82% | [-11.7, -5.0] |
| pipe_cap_first:plane_fill | 0.3905 | -7.3% | 82% | [-11.5, -4.9] |

## nadir · protocol `align-all` · region AbsRel (raw median 0.6750)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.4756 | -30.5% | 92% | [-42.3, -22.9] |
| oracle+1.5:inpaint_erp | 0.5031 | -25.5% | 92% | [-30.6, -18.1] |
| detected:inpaint_erp | 0.4847 | -28.1% | 90% | [-40.7, -20.3] |
| detected+1.5:inpaint_erp | 0.5057 | -24.9% | 92% | [-30.6, -18.4] |
| pipe:inpaint_erp | 0.4847 | -28.1% | 90% | [-40.7, -20.3] |
| oracle:inpaint_tangent | 0.5189 | -23.1% | 90% | [-28.9, -18.0] |
| oracle+1.5:inpaint_tangent | 0.6000 | -10.5% | 80% | [-16.6, -7.5] |
| detected:inpaint_tangent | 0.5496 | -19.3% | 88% | [-25.2, -16.2] |
| detected+1.5:inpaint_tangent | 0.6087 | -10.2% | 80% | [-16.6, -7.5] |
| pipe:inpaint_tangent | 0.5496 | -19.3% | 88% | [-25.2, -16.2] |
| oracle:plane_fill | 0.4929 | -28.5% | 92% | [-36.1, -21.0] |
| oracle+1.5:plane_fill | 0.5844 | -15.4% | 88% | [-18.8, -8.9] |
| detected:plane_fill | 0.5332 | -21.9% | 90% | [-32.0, -17.5] |
| detected+1.5:plane_fill | 0.5817 | -14.0% | 88% | [-19.3, -8.9] |
| pipe:plane_fill | 0.5332 | -21.9% | 90% | [-32.0, -17.5] |

## nadir · protocol `align-all` · outside AbsRel (raw median 0.1382)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1282 | +0.8% | 45% | [-1.5, +2.5] |
| oracle+1.5:inpaint_erp | 0.1355 | +2.8% | 25% | [+1.9, +4.5] |
| detected:inpaint_erp | 0.1288 | +0.8% | 42% | [-1.4, +2.1] |
| detected+1.5:inpaint_erp | 0.1364 | +3.0% | 25% | [+2.2, +4.7] |
| pipe:inpaint_erp | 0.1288 | +0.8% | 42% | [-1.4, +2.1] |
| oracle:inpaint_tangent | 0.1351 | -0.7% | 60% | [-2.4, +0.5] |
| oracle+1.5:inpaint_tangent | 0.1382 | +2.3% | 28% | [+0.9, +4.2] |
| detected:inpaint_tangent | 0.1351 | -0.5% | 57% | [-1.5, +0.5] |
| detected+1.5:inpaint_tangent | 0.1382 | +2.7% | 22% | [+1.5, +4.6] |
| pipe:inpaint_tangent | 0.1351 | -0.5% | 57% | [-1.5, +0.5] |
| oracle:plane_fill | 0.1351 | -0.8% | 65% | [-2.7, +0.2] |
| oracle+1.5:plane_fill | 0.1382 | +1.6% | 32% | [+0.5, +3.8] |
| detected:plane_fill | 0.1351 | -0.5% | 62% | [-2.2, +0.5] |
| detected+1.5:plane_fill | 0.1382 | +2.4% | 28% | [+1.3, +3.9] |
| pipe:plane_fill | 0.1351 | -0.5% | 62% | [-2.2, +0.5] |

## nadir · protocol `align-all` · ring AbsRel (raw median 0.1210)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1230 | +2.5% | 45% | [-4.6, +8.3] |
| oracle+1.5:inpaint_erp | 0.1505 | +23.3% | 22% | [+13.5, +34.2] |
| detected:inpaint_erp | 0.1279 | +5.0% | 45% | [-3.9, +10.5] |
| detected+1.5:inpaint_erp | 0.1557 | +27.1% | 20% | [+13.8, +35.9] |
| pipe:inpaint_erp | 0.1279 | +5.0% | 45% | [-3.9, +10.5] |
| oracle:inpaint_tangent | 0.1187 | -1.1% | 52% | [-4.3, +1.9] |
| oracle+1.5:inpaint_tangent | 0.1520 | +20.5% | 15% | [+8.5, +25.0] |
| detected:inpaint_tangent | 0.1319 | +0.6% | 48% | [-3.3, +5.8] |
| detected+1.5:inpaint_tangent | 0.1574 | +22.4% | 15% | [+14.0, +34.9] |
| pipe:inpaint_tangent | 0.1319 | +0.6% | 48% | [-3.3, +5.8] |
| oracle:plane_fill | 0.1187 | -0.3% | 55% | [-4.3, +1.9] |
| oracle+1.5:plane_fill | 0.1520 | +14.0% | 20% | [+6.6, +22.2] |
| detected:plane_fill | 0.1319 | +0.1% | 50% | [-2.4, +4.9] |
| detected+1.5:plane_fill | 0.1574 | +20.4% | 18% | [+8.7, +24.7] |
| pipe:plane_fill | 0.1319 | +0.1% | 50% | [-2.4, +4.9] |

## nadir · protocol `align-all` · all AbsRel (raw median 0.1648)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| oracle:inpaint_erp | 0.1524 | -5.6% | 88% | [-8.2, -4.3] |
| oracle+1.5:inpaint_erp | 0.1646 | -2.2% | 65% | [-4.4, -0.0] |
| detected:inpaint_erp | 0.1526 | -5.2% | 85% | [-7.7, -3.1] |
| detected+1.5:inpaint_erp | 0.1646 | -2.0% | 60% | [-3.9, +0.3] |
| pipe:inpaint_erp | 0.1526 | -5.2% | 85% | [-7.7, -3.1] |
| oracle:inpaint_tangent | 0.1543 | -6.0% | 88% | [-8.3, -4.0] |
| oracle+1.5:inpaint_tangent | 0.1680 | -0.2% | 50% | [-1.5, +1.0] |
| detected:inpaint_tangent | 0.1543 | -5.1% | 80% | [-6.8, -3.3] |
| detected+1.5:inpaint_tangent | 0.1680 | +0.5% | 45% | [-0.9, +1.4] |
| pipe:inpaint_tangent | 0.1543 | -5.1% | 80% | [-6.8, -3.3] |
| oracle:plane_fill | 0.1543 | -7.1% | 90% | [-10.5, -5.3] |
| oracle+1.5:plane_fill | 0.1680 | -1.2% | 60% | [-2.3, +0.4] |
| detected:plane_fill | 0.1543 | -5.8% | 85% | [-8.5, -3.8] |
| detected+1.5:plane_fill | 0.1680 | -0.6% | 55% | [-2.1, +0.7] |
| pipe:plane_fill | 0.1543 | -5.8% | 85% | [-8.5, -3.8] |

## nadir+jpeg · protocol `align-all` · region AbsRel (raw median 0.2989)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.3741 | +11.4% | 12% | [+6.7, +43.7] |
| oracle:inpaint_erp | 0.1958 | -39.8% | 75% | [-51.6, -24.3] |
| oracle+1.5:inpaint_erp | 0.1912 | -41.0% | 78% | [-50.8, -19.4] |
| detected:inpaint_erp | 0.1950 | -41.5% | 65% | [-51.8, -10.2] |
| detected+1.5:inpaint_erp | 0.1976 | -38.8% | 68% | [-51.2, -6.7] |
| deblock_oracle:inpaint_erp | 0.2034 | -43.0% | 75% | [-50.9, -16.5] |
| pipe_photometric:inpaint_erp | 0.2328 | -42.7% | 70% | [-48.1, -8.9] |
| pipe_cap_first:inpaint_erp | 0.2335 | -42.9% | 70% | [-48.2, -9.5] |
| oracle:inpaint_tangent | 0.1943 | -41.0% | 78% | [-53.6, -22.7] |
| oracle+1.5:inpaint_tangent | 0.1991 | -40.0% | 78% | [-50.4, -17.2] |
| detected:inpaint_tangent | 0.2051 | -38.9% | 70% | [-50.9, -10.2] |
| detected+1.5:inpaint_tangent | 0.2142 | -36.7% | 68% | [-48.8, -4.3] |
| deblock_oracle:inpaint_tangent | 0.2009 | -44.3% | 75% | [-52.7, -17.4] |
| pipe_photometric:inpaint_tangent | 0.2303 | -30.1% | 72% | [-46.0, -5.8] |
| pipe_cap_first:inpaint_tangent | 0.2361 | -30.5% | 72% | [-46.7, -6.4] |
| oracle:plane_fill | 0.1944 | -41.0% | 78% | [-53.6, -19.5] |
| oracle+1.5:plane_fill | 0.2001 | -40.0% | 78% | [-50.4, -17.2] |
| detected:plane_fill | 0.2052 | -38.9% | 70% | [-50.9, -10.2] |
| detected+1.5:plane_fill | 0.2142 | -36.7% | 68% | [-48.8, -4.3] |
| deblock_oracle:plane_fill | 0.2021 | -44.3% | 75% | [-52.7, -17.4] |
| pipe_photometric:plane_fill | 0.2303 | -30.1% | 70% | [-46.0, -5.8] |
| pipe_cap_first:plane_fill | 0.2374 | -30.5% | 70% | [-46.7, -6.4] |

## nadir+jpeg · protocol `align-all` · outside AbsRel (raw median 0.2011)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.1925 | -3.9% | 72% | [-9.0, -1.4] |
| oracle:inpaint_erp | 0.1939 | -1.6% | 55% | [-3.0, +1.1] |
| oracle+1.5:inpaint_erp | 0.1955 | -1.1% | 55% | [-3.1, +0.8] |
| detected:inpaint_erp | 0.1966 | -1.5% | 52% | [-3.2, +0.8] |
| detected+1.5:inpaint_erp | 0.2005 | -0.9% | 52% | [-2.0, +0.1] |
| deblock_oracle:inpaint_erp | 0.1933 | -8.6% | 75% | [-15.1, -3.0] |
| pipe_photometric:inpaint_erp | 0.1974 | -7.9% | 72% | [-15.4, -4.2] |
| pipe_cap_first:inpaint_erp | 0.1973 | -7.9% | 72% | [-15.5, -4.3] |
| oracle:inpaint_tangent | 0.1980 | -3.0% | 80% | [-4.8, -0.9] |
| oracle+1.5:inpaint_tangent | 0.1988 | -2.3% | 78% | [-4.4, -0.8] |
| detected:inpaint_tangent | 0.1996 | -2.9% | 68% | [-4.7, -0.3] |
| detected+1.5:inpaint_tangent | 0.2004 | -2.3% | 68% | [-4.3, -0.1] |
| deblock_oracle:inpaint_tangent | 0.1930 | -9.3% | 82% | [-17.8, -5.3] |
| pipe_photometric:inpaint_tangent | 0.1982 | -9.2% | 80% | [-15.8, -4.1] |
| pipe_cap_first:inpaint_tangent | 0.1980 | -9.0% | 80% | [-15.9, -4.1] |
| oracle:plane_fill | 0.1980 | -3.0% | 80% | [-4.8, -0.9] |
| oracle+1.5:plane_fill | 0.1988 | -2.3% | 78% | [-4.4, -0.7] |
| detected:plane_fill | 0.1996 | -2.9% | 68% | [-4.7, -0.3] |
| detected+1.5:plane_fill | 0.2004 | -2.3% | 68% | [-4.3, -0.1] |
| deblock_oracle:plane_fill | 0.1930 | -9.3% | 82% | [-17.8, -5.3] |
| pipe_photometric:plane_fill | 0.1982 | -9.2% | 80% | [-15.8, -4.1] |
| pipe_cap_first:plane_fill | 0.1980 | -9.0% | 80% | [-15.9, -4.1] |

## nadir+jpeg · protocol `align-all` · ring AbsRel (raw median 0.1764)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2105 | -0.2% | 50% | [-6.9, +6.7] |
| oracle:inpaint_erp | 0.1914 | -3.3% | 55% | [-7.8, +8.2] |
| oracle+1.5:inpaint_erp | 0.1831 | -2.7% | 55% | [-8.0, +8.0] |
| detected:inpaint_erp | 0.1914 | +0.0% | 45% | [-6.5, +9.2] |
| detected+1.5:inpaint_erp | 0.1961 | +0.0% | 48% | [-7.7, +11.2] |
| deblock_oracle:inpaint_erp | 0.1930 | -2.8% | 55% | [-9.9, +6.8] |
| pipe_photometric:inpaint_erp | 0.1980 | -0.2% | 50% | [-11.2, +12.7] |
| pipe_cap_first:inpaint_erp | 0.1971 | +0.1% | 50% | [-11.2, +13.2] |
| oracle:inpaint_tangent | 0.1773 | -3.2% | 60% | [-9.1, +1.8] |
| oracle+1.5:inpaint_tangent | 0.1822 | -1.8% | 57% | [-9.2, +5.2] |
| detected:inpaint_tangent | 0.1829 | -1.1% | 50% | [-7.6, +5.0] |
| detected+1.5:inpaint_tangent | 0.1822 | +0.0% | 48% | [-9.2, +8.3] |
| deblock_oracle:inpaint_tangent | 0.1830 | -3.0% | 57% | [-15.3, +2.2] |
| pipe_photometric:inpaint_tangent | 0.1926 | -0.4% | 50% | [-15.8, +6.5] |
| pipe_cap_first:inpaint_tangent | 0.1942 | -0.4% | 50% | [-16.2, +7.3] |
| oracle:plane_fill | 0.1773 | -3.4% | 60% | [-9.1, +1.8] |
| oracle+1.5:plane_fill | 0.1822 | -1.8% | 57% | [-9.4, +5.4] |
| detected:plane_fill | 0.1829 | -1.1% | 50% | [-7.6, +5.0] |
| detected+1.5:plane_fill | 0.1822 | +0.0% | 48% | [-9.4, +8.3] |
| deblock_oracle:plane_fill | 0.1829 | -2.8% | 60% | [-15.3, +2.2] |
| pipe_photometric:plane_fill | 0.1926 | -0.4% | 50% | [-15.8, +6.5] |
| pipe_cap_first:plane_fill | 0.1942 | -0.4% | 50% | [-16.2, +7.3] |

## nadir+jpeg · protocol `align-all` · all AbsRel (raw median 0.2141)

| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |
|---|---:|---:|---:|---:|
| bilateral_only | 0.2049 | -2.5% | 62% | [-6.0, +0.9] |
| oracle:inpaint_erp | 0.1901 | -3.5% | 65% | [-6.1, -0.8] |
| oracle+1.5:inpaint_erp | 0.1923 | -3.8% | 68% | [-5.8, -0.4] |
| detected:inpaint_erp | 0.1931 | -4.3% | 65% | [-6.2, -1.2] |
| detected+1.5:inpaint_erp | 0.1985 | -3.7% | 62% | [-5.3, +0.0] |
| deblock_oracle:inpaint_erp | 0.1940 | -9.4% | 80% | [-16.2, -5.3] |
| pipe_photometric:inpaint_erp | 0.1962 | -9.1% | 80% | [-15.8, -6.1] |
| pipe_cap_first:inpaint_erp | 0.1961 | -9.2% | 80% | [-15.8, -6.1] |
| oracle:inpaint_tangent | 0.1964 | -5.9% | 82% | [-9.5, -2.2] |
| oracle+1.5:inpaint_tangent | 0.1967 | -4.8% | 75% | [-8.3, -1.6] |
| detected:inpaint_tangent | 0.1971 | -4.5% | 68% | [-9.2, -0.7] |
| detected+1.5:inpaint_tangent | 0.2014 | -4.9% | 62% | [-8.5, +0.0] |
| deblock_oracle:inpaint_tangent | 0.1971 | -12.2% | 85% | [-16.5, -6.4] |
| pipe_photometric:inpaint_tangent | 0.2024 | -10.2% | 85% | [-16.5, -5.8] |
| pipe_cap_first:inpaint_tangent | 0.2023 | -10.4% | 85% | [-16.8, -5.8] |
| oracle:plane_fill | 0.1964 | -5.9% | 80% | [-9.5, -2.1] |
| oracle+1.5:plane_fill | 0.1967 | -4.8% | 72% | [-8.3, -1.6] |
| detected:plane_fill | 0.1971 | -4.5% | 68% | [-9.2, -0.7] |
| detected+1.5:plane_fill | 0.2014 | -4.9% | 62% | [-8.5, +0.0] |
| deblock_oracle:plane_fill | 0.1971 | -12.2% | 85% | [-16.5, -6.0] |
| pipe_photometric:plane_fill | 0.2024 | -10.2% | 85% | [-16.5, -5.8] |
| pipe_cap_first:plane_fill | 0.2023 | -10.4% | 85% | [-16.8, -5.8] |

## Median predicted / true depth inside the cap (bias), headline protocol

| input | raw | oracle plane_fill | oracle inpaint_erp |
|---|---:|---:|---:|
| nadir | 0.269 | 0.430 | 0.491 |
| nadir+jpeg | 0.336 | 0.497 | 0.460 |
