# Capture-aware correction, end to end: dap_holo_in

model `dap` · 100 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1289 | 0.1289 | 0.1289 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1289 | 0.1824 | 0.1387 | -22.0% | 87% | 13% | 91% |
| nadir | 100% | 0.1205 | 0.6926 | 0.5669 | -22.5% | 92% | 8% | 28% |
| vfov | 100% | 0.1179 | 0.7888 | 0.3158 | -57.7% | 99% | 1% | 68% |
| yawblur | 100% | 0.1289 | 0.2383 | 0.1414 | -30.3% | 89% | 10% | 84% |
| jpeg | 100% | 0.1289 | 0.4832 | 0.4231 | -9.6% | 92% | 7% | 13% |
| nadir+jpeg | 92% | 0.1205 | 0.6354 | 0.4563 | -23.0% | 94% | 4% | 29% |
