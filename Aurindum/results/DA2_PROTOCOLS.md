# DA2 under both alignment protocols

`lsq`: least-squares scale fit (core protocol, tag `da2`). `median`: median scale fit (tag `da2m`; the policy is learned from `study_da2m_<core>.json` under the same protocol). All comparisons use the frame ids both runs contain.

## 1. Clean AbsRel (median over frames)

| dataset | frames | lsq | median |
|---|---:|---:|---:|
| s3 | 100 | 0.053 | 0.051 |
| panox | 100 | 0.139 | 0.101 |
| holo_in | 100 | 0.115 | 0.108 |
| holo_out | 71 | 0.543 | 0.214 |
| stanford | 373 | 0.068 | 0.067 |
| nyc | 147 | 0.638 | 0.205 |

## 2. Correction per scenario: median change [95% CI] (% improved / % worse)

### s3

| protocol | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---|---|---|---|---|
| lsq | +0.0% [+0.0, +0.0] (0/0) | -58.5% [-62.2, -52.4] (84/16) | -37.4% [-45.5, -30.2] (92/7) | -4.6% [-7.9, -1.5] (64/32) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (24/39) |
| median | -38.4% [-43.4, -32.0] (88/12) | -63.7% [-68.1, -56.9] (89/11) | -42.8% [-55.2, -35.9] (90/9) | +0.0% [+0.0, +0.0] (1/0) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (36/24) |

### panox

| protocol | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---|---|---|---|---|
| lsq | -4.3% [-23.2, +6.5] (52/47) | -47.3% [-54.3, -36.4] (74/23) | -3.4% [-7.8, +12.3] (52/47) | +0.0% [+0.0, +0.0] (0/0) | +5.0% [+1.4, +8.7] (37/61) | -0.9% [-11.0, +4.7] (52/47) |
| median | -23.8% [-31.3, -20.0] (90/10) | -66.2% [-70.5, -61.4] (87/13) | -3.1% [-25.5, +13.0] (53/47) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (0/0) | -5.6% [-36.9, +0.0] (51/9) |

### holo_in

| protocol | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---|---|---|---|---|
| lsq | +0.0% [+0.0, +0.0] (0/0) | -9.7% [-31.9, +18.1] (52/48) | -23.9% [-28.1, -14.7] (79/20) | -2.0% [-4.1, +2.3] (54/44) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (11/14) |
| median | -19.6% [-27.3, -11.4] (78/19) | -4.0% [-19.3, +18.4] (53/45) | -29.4% [-34.8, -20.6] (84/16) | +0.6% [-2.3, +6.4] (48/48) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (8/17) |

### holo_out

| protocol | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---|---|---|---|---|
| lsq | +19.4% [+13.3, +30.3] (21/73) | +0.5% [-0.6, +4.6] (44/48) | -6.7% [-10.1, -0.6] (62/35) | -6.2% [-11.0, +0.9] (61/38) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (38/27) |
| median | +5.8% [-0.2, +9.5] (39/61) | -51.6% [-64.0, -21.2] (69/31) | -16.3% [-27.5, +14.5] (56/44) | -1.6% [-9.0, +3.5] (55/44) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (30/35) |

### stanford

| protocol | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---|---|---|---|---|
| lsq | -27.9% [-30.0, -25.1] (92/8) | -78.1% [-80.2, -75.2] (99/1) | -23.3% [-28.2, -21.5] (87/13) | -6.5% [-7.8, -5.2] (68/28) | +8.0% [+5.0, +11.1] (35/64) | -2.2% [-6.1, +2.7] (52/47) |
| median | -26.7% [-28.2, -24.5] (91/8) | -71.2% [-72.6, -68.6] (99/1) | -23.7% [-27.2, -19.8] (79/20) | -6.1% [-7.4, -4.6] (65/31) | +19.5% [+16.6, +23.4] (27/72) | -0.1% [-2.2, +0.8] (50/45) |

### nyc

| protocol | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---|---|---|---|---|
| lsq | +13.7% [+11.9, +16.2] (14/84) | +6.3% [+5.3, +7.0] (12/86) | +6.1% [+4.6, +8.2] (20/74) | -4.5% [-6.3, -2.8] (72/24) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (1/31) |
| median | -22.8% [-26.5, -20.1] (92/7) | -26.0% [-38.9, +5.4] (56/44) | -1.8% [-14.3, +5.1] (52/47) | -6.7% [-9.8, -4.7] (65/31) | +0.0% [+0.0, +0.0] (0/0) | +0.0% [+0.0, +0.0] (15/22) |

## 3. Policy chosen per fault (held-out) and harmful cells

| dataset | lsq policy | median policy | harmful under lsq | harmful under median |
|---|---|---|---|---|
| s3 | `{"nadir": "inpaint_erp", "vfov": "inpaint_erp", "yawblur": "wiener"}` | `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp"}` | none | none |
| panox | `{"tilt": "relevel_known", "nadir": "inpaint_erp", "vfov": "inpaint_erp", "jpeg": "bilateral"}` | `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp"}` | jpeg +5.0% | none |
| holo_in | `{"nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}` | `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}` | none | none |
| holo_out | `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}` | `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}` | tilt +19.4% | tilt +5.8% |
| stanford | `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}` | `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp", "yawblur": "wiener"}` | jpeg +8.0% | jpeg +19.5% |
| nyc | `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}` | `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp", "yawblur": "wiener"}` | tilt +13.7%, nadir +6.3%, vfov +6.1% | none |

## 4. Sweeps (global estimator): onset, mean excess error 75-90 deg, ratio

| mode | dataset | lsq onset | lsq dE | lsq ratio | median onset | median dE | median ratio |
|---|---|---:|---:|---:|---:|---:|---:|
| rotation | s3_eval | None | 0.010 | 1.08 | None | 0.015 | 1.13 |
| rotation | panox_all | None | -0.534 | 0.42 | None | -0.052 | 0.79 |
| rotation | holo_in_all | None | 0.001 | 1.01 | None | 0.016 | 1.08 |
| rotation | holo_out_all | None | -0.122 | 0.81 | None | 0.092 | 1.26 |
| rotation | nyc_all | 50.0 | 0.194 | 1.45 | None | -0.063 | 0.74 |
| dilation | s3_eval | None | -0.164 | 0.64 | None | -0.133 | 0.72 |
| dilation | panox_all | None | 0.294 | 1.49 | None | 0.015 | 1.06 |
| dilation | holo_in_all | None | 0.117 | 1.34 | None | 0.037 | 1.12 |
| dilation | holo_out_all | 80.0 | 0.570 | 1.88 | None | 0.128 | 1.28 |
| dilation | nyc_all | None | -0.263 | 0.63 | 55.0 | -0.040 | 0.94 |
