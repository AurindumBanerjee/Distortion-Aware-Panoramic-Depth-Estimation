# Capture-aware correction, end to end: dap_holo_out

model `dap` · 71 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2725 | 0.2725 | 0.2725 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2725 | 0.3118 | 0.2959 | +4.2% | 32% | 62% | -11% |
| nadir | 100% | 0.1597 | 0.6445 | 0.1505 | -70.0% | 100% | 0% | 104% |
| vfov | 100% | 0.2461 | 0.6728 | 0.5074 | -29.8% | 89% | 11% | 49% |
| yawblur | 100% | 0.2725 | 0.3259 | 0.2909 | -9.8% | 89% | 10% | 56% |
| jpeg | 100% | 0.2725 | 0.4341 | 0.3721 | -8.2% | 66% | 30% | 48% |
| nadir+jpeg | 96% | 0.1597 | 0.3280 | 0.1506 | -39.2% | 89% | 11% | 59% |
