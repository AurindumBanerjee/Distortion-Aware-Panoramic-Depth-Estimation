# Capture-aware correction, end to end: dap_holo_out

model `dap` · 40 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2800 | 0.2800 | 0.2800 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2800 | 0.3007 | 0.3002 | +6.0% | 30% | 62% | -17% |
| nadir | 100% | 0.1494 | 0.6432 | 0.1870 | -68.2% | 100% | 0% | 100% |
| vfov | 100% | 0.2389 | 0.6769 | 0.4846 | -31.4% | 90% | 10% | 49% |
| yawblur | 100% | 0.2800 | 0.3220 | 0.2892 | -10.2% | 92% | 8% | 54% |
| jpeg | 100% | 0.2800 | 0.4158 | 0.3593 | -8.3% | 62% | 32% | 47% |
| nadir+jpeg | 98% | 0.1494 | 0.3325 | 0.1574 | -39.9% | 92% | 8% | 59% |
