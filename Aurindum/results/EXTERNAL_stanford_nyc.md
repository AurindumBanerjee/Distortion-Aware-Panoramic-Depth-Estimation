# External datasets: Stanford2D3D and NYC

Run, analysed and reported independently of the core datasets (Structured3D, PanoX, Holo360D). Nothing here was used to choose or tune a fix: the policy comes from the four core datasets only.

## stanford

**What each fault costs** (median AbsRel on the whole panorama, clean -> faulty; 40 frames)

| model | clean | tilt | nadir | vfov | yawblur | jpeg | noise | lowres |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| midas | 0.2420 | 0.242 -> 0.234 | 0.242 -> 0.246 | 0.242 -> 0.245 | 0.242 -> 0.230 | 0.242 -> 0.258 | 0.242 -> 0.251 | 0.242 -> 0.247 |
| dap | 0.1596 | 0.160 -> 0.228 | 0.160 -> 0.168 | 0.160 -> 0.371 | 0.160 -> 0.169 | 0.160 -> 0.264 | 0.160 -> 0.149 | 0.160 -> 0.152 |
| da360 | 0.1448 | 0.145 -> 0.164 | 0.145 -> 0.122 | 0.145 -> 0.064 | 0.145 -> 0.168 | 0.145 -> 0.112 | 0.145 -> 0.173 | 0.145 -> 0.081 |
| da2 | 0.0738 | 0.074 -> 0.100 | 0.074 -> 0.108 | 0.074 -> 0.104 | 0.074 -> 0.077 | 0.074 -> 0.078 | 0.074 -> 0.081 | 0.074 -> 0.072 |

*Stanford frames are already black above |lat| 65 deg (limited vertical FOV), so the simulated `nadir` / `vfov` faults mostly fall inside real occlusion and are not a meaningful fault test here.*

**End-to-end correction** (fixes detected and chosen as in deployment; policy learned on the core sets). Metric: affected region for cap faults, whole panorama otherwise. change = median per-frame change in error vs uncorrected; better / worse = share of frames improved / worse by >1%.

| model | scenario | uncorrected | corrected | change | better | worse | policy |
|---|---|---:|---:|---:|---:|---:|---|
| midas | clean | 0.2515 | 0.2515 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | tilt | 0.2482 | 0.2500 | +0.6% | 42% | 46% | tilt:relevel_known, yawblur:wiener |
| midas | nadir | 0.0939 | 0.0939 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | vfov | 0.1359 | 0.1359 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | yawblur | 0.2455 | 0.2492 | +0.6% | 38% | 46% | tilt:relevel_known, yawblur:wiener |
| midas | jpeg | 0.2505 | 0.2505 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | nadir+jpeg | 0.0886 | 0.0886 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| dap | clean | 0.1500 | 0.0927 | -34.8% | 99% | 1% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | tilt | 0.2194 | 0.1462 | -32.0% | 99% | 1% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir | 0.3483 | 0.1520 | -41.6% | 97% | 3% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | vfov | 0.7598 | 0.3065 | -59.1% | 100% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | yawblur | 0.1665 | 0.1047 | -32.9% | 97% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | jpeg | 0.2739 | 0.1403 | -47.1% | 98% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir+jpeg | 0.2689 | 0.0655 | -71.7% | 94% | 6% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| da360 | clean | 0.1509 | 0.1509 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | tilt | 0.1662 | 0.1662 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir | 0.0770 | 0.0770 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | vfov | 0.0629 | 0.0629 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | yawblur | 0.1731 | 0.1565 | -6.2% | 73% | 24% | yawblur:wiener |
| da360 | jpeg | 0.1184 | 0.1184 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir+jpeg | 0.0453 | 0.0453 | +0.0% | 0% | 0% | yawblur:wiener |
| da2 | clean | 0.0678 | 0.0629 | -6.6% | 77% | 21% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | tilt | 0.0962 | 0.0663 | -27.9% | 92% | 8% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir | 0.1741 | 0.0380 | -78.1% | 99% | 1% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | vfov | 0.0982 | 0.0672 | -23.3% | 87% | 13% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | yawblur | 0.0713 | 0.0698 | -6.5% | 68% | 28% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | jpeg | 0.0757 | 0.0894 | +8.0% | 35% | 64% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir+jpeg | 0.1602 | 0.1375 | -2.2% | 52% | 47% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |

*The `clean` row is the real-occlusion test: Stanford's own black caps are detected and filled (whole-panorama error; detection rate is not meaningful there because every frame has caps).*

## nyc

**What each fault costs** (median AbsRel on the whole panorama, clean -> faulty; 40 frames)

| model | clean | tilt | nadir | vfov | yawblur | jpeg | noise | lowres |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| midas | 0.2214 | 0.221 -> 0.257 | 0.221 -> 0.209 | 0.221 -> 0.350 | 0.221 -> 0.268 | 0.221 -> 0.324 | 0.221 -> 0.241 | 0.221 -> 0.325 |
| dap | 0.0334 | 0.033 -> 0.094 | 0.033 -> 0.133 | 0.033 -> 0.300 | 0.033 -> 0.123 | 0.033 -> 0.166 | 0.033 -> 0.057 | 0.033 -> 0.098 |
| da360 | 0.0643 | 0.064 -> 0.069 | 0.064 -> 0.067 | 0.064 -> 0.133 | 0.064 -> 0.091 | 0.064 -> 0.129 | 0.064 -> 0.079 | 0.064 -> 0.090 |
| da2 | 0.6345 | 0.635 -> 0.559 | 0.635 -> 0.633 | 0.635 -> 0.663 | 0.635 -> 0.692 | 0.635 -> 0.680 | 0.635 -> 0.671 | 0.635 -> 0.672 |

**End-to-end correction** (fixes detected and chosen as in deployment; policy learned on the core sets). Metric: affected region for cap faults, whole panorama otherwise. change = median per-frame change in error vs uncorrected; better / worse = share of frames improved / worse by >1%.

| model | scenario | uncorrected | corrected | change | better | worse | policy |
|---|---|---:|---:|---:|---:|---:|---|
| midas | clean | 0.2198 | 0.2198 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | tilt | 0.2433 | 0.2177 | -2.8% | 67% | 27% | tilt:relevel_known, yawblur:wiener |
| midas | nadir | 0.0608 | 0.0608 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | vfov | 0.3230 | 0.3230 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | yawblur | 0.2574 | 0.2190 | -7.6% | 82% | 12% | tilt:relevel_known, yawblur:wiener |
| midas | jpeg | 0.3225 | 0.3225 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | nadir+jpeg | 0.1144 | 0.1144 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| dap | clean | 0.0352 | 0.0352 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | tilt | 0.0915 | 0.0477 | -47.4% | 98% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir | 0.5238 | 0.0426 | -89.3% | 79% | 20% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | vfov | 0.7129 | 0.4396 | -36.4% | 99% | 1% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | yawblur | 0.1272 | 0.0487 | -60.4% | 92% | 7% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | jpeg | 0.1764 | 0.1638 | -7.9% | 82% | 12% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir+jpeg | 0.3219 | 0.2688 | +1.3% | 47% | 52% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| da360 | clean | 0.0629 | 0.0629 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | tilt | 0.0690 | 0.0690 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir | 0.0157 | 0.0157 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | vfov | 0.1964 | 0.1964 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | yawblur | 0.0909 | 0.0703 | -17.5% | 91% | 7% | yawblur:wiener |
| da360 | jpeg | 0.1299 | 0.1299 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir+jpeg | 0.0495 | 0.0495 | +0.0% | 0% | 0% | yawblur:wiener |
| da2 | clean | 0.6378 | 0.6378 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | tilt | 0.5629 | 0.6507 | +13.7% | 14% | 84% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir | 0.7210 | 0.7549 | +6.3% | 12% | 86% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | vfov | 0.7784 | 0.8290 | +6.1% | 20% | 74% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | yawblur | 0.6972 | 0.6553 | -4.5% | 72% | 24% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | jpeg | 0.6750 | 0.6750 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir+jpeg | 0.8072 | 0.8158 | +0.0% | 1% | 31% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |

