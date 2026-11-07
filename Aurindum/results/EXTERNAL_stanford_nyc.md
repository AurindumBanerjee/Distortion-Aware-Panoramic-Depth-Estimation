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
| midas | clean | 0.2420 | 0.2420 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | tilt | 0.2338 | 0.2418 | +2.0% | 40% | 57% | tilt:relevel_known, yawblur:wiener |
| midas | nadir | 0.0906 | 0.0906 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | vfov | 0.1255 | 0.1255 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | yawblur | 0.2305 | 0.2410 | +0.1% | 45% | 45% | tilt:relevel_known, yawblur:wiener |
| midas | jpeg | 0.2584 | 0.2584 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | nadir+jpeg | 0.0886 | 0.0886 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| dap | clean | 0.1596 | 0.1596 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | tilt | 0.2281 | 0.1512 | -32.9% | 100% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir | 0.3716 | 0.0750 | -70.2% | 98% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | vfov | 0.7405 | 0.2931 | -61.0% | 100% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | yawblur | 0.1694 | 0.1557 | -9.5% | 80% | 20% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | jpeg | 0.2644 | 0.2215 | -12.4% | 90% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir+jpeg | 0.3352 | 0.1027 | -50.0% | 90% | 10% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| da360 | clean | 0.1448 | 0.1448 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | tilt | 0.1641 | 0.1641 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir | 0.0668 | 0.0668 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | vfov | 0.0754 | 0.0754 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | yawblur | 0.1682 | 0.1506 | -6.7% | 80% | 15% | yawblur:wiener |
| da360 | jpeg | 0.1116 | 0.1116 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir+jpeg | 0.0435 | 0.0435 | +0.0% | 0% | 0% | yawblur:wiener |
| da2 | clean | 0.0738 | 0.0737 | +1.1% | 38% | 50% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | tilt | 0.1000 | 0.0706 | -27.2% | 90% | 10% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir | 0.1791 | 0.0349 | -81.0% | 100% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | vfov | 0.0955 | 0.0675 | -29.1% | 78% | 22% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | yawblur | 0.0774 | 0.0811 | +0.8% | 48% | 48% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | jpeg | 0.0785 | 0.2208 | +55.0% | 10% | 90% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir+jpeg | 0.1702 | 0.1607 | +4.4% | 45% | 52% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |

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
| midas | clean | 0.2214 | 0.2214 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | tilt | 0.2574 | 0.2250 | -2.8% | 62% | 32% | tilt:relevel_known, yawblur:wiener |
| midas | nadir | 0.0614 | 0.0614 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | vfov | 0.3264 | 0.3264 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | yawblur | 0.2676 | 0.2343 | -8.3% | 80% | 10% | tilt:relevel_known, yawblur:wiener |
| midas | jpeg | 0.3238 | 0.3238 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| midas | nadir+jpeg | 0.1140 | 0.1140 | +0.0% | 0% | 0% | tilt:relevel_known, yawblur:wiener |
| dap | clean | 0.0334 | 0.0334 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | tilt | 0.0936 | 0.0478 | -46.9% | 98% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir | 0.5031 | 0.0437 | -88.9% | 92% | 5% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | vfov | 0.7170 | 0.4224 | -39.4% | 98% | 2% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | yawblur | 0.1234 | 0.0479 | -61.2% | 92% | 8% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | jpeg | 0.1664 | 0.1540 | -7.7% | 78% | 8% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| dap | nadir+jpeg | 0.3306 | 0.2478 | -1.3% | 52% | 45% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener, jpeg:bilateral |
| da360 | clean | 0.0643 | 0.0643 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | tilt | 0.0688 | 0.0688 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir | 0.0140 | 0.0140 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | vfov | 0.2007 | 0.2007 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | yawblur | 0.0912 | 0.0713 | -18.9% | 90% | 8% | yawblur:wiener |
| da360 | jpeg | 0.1289 | 0.1289 | +0.0% | 0% | 0% | yawblur:wiener |
| da360 | nadir+jpeg | 0.0459 | 0.0459 | +0.0% | 0% | 0% | yawblur:wiener |
| da2 | clean | 0.6345 | 0.6345 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | tilt | 0.5591 | 0.6504 | +15.3% | 10% | 88% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir | 0.7203 | 0.7610 | +6.5% | 10% | 85% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | vfov | 0.7767 | 0.8348 | +5.1% | 25% | 68% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | yawblur | 0.6924 | 0.6517 | -4.3% | 72% | 28% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | jpeg | 0.6802 | 0.6802 | +0.0% | 0% | 0% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |
| da2 | nadir+jpeg | 0.8240 | 0.8242 | +0.0% | 0% | 42% | tilt:relevel_known, nadir:plane_fill, vfov:inpaint_erp, yawblur:wiener |

