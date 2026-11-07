# Capture-aware correction, end to end: dap_holo_in

model `dap` · 40 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1387 | 0.1387 | 0.1387 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1387 | 0.2018 | 0.1480 | -23.9% | 88% | 12% | 92% |
| nadir | 100% | 0.1296 | 0.7101 | 0.5667 | -23.5% | 90% | 8% | 32% |
| vfov | 100% | 0.1180 | 0.7850 | 0.3066 | -59.2% | 98% | 2% | 72% |
| yawblur | 100% | 0.1387 | 0.2240 | 0.1785 | -28.5% | 80% | 20% | 85% |
| jpeg | 100% | 0.1387 | 0.4744 | 0.4156 | -8.6% | 85% | 12% | 12% |
| nadir+jpeg | 90% | 0.1296 | 0.6289 | 0.4421 | -28.8% | 92% | 2% | 38% |
