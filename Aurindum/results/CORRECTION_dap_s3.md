# Capture-aware correction, end to end: dap_s3

model `dap` · 40 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "plane_fill", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0324 | 0.0324 | 0.0324 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0324 | 0.1203 | 0.0379 | -70.7% | 98% | 2% | 96% |
| nadir | 100% | 0.0238 | 0.3721 | 0.3064 | -4.4% | 62% | 38% | 5% |
| vfov | 100% | 0.0261 | 0.7610 | 0.5895 | -22.1% | 100% | 0% | 24% |
| yawblur | 100% | 0.0324 | 0.0390 | 0.0347 | -12.4% | 65% | 32% | 57% |
| jpeg | 98% | 0.0324 | 0.0757 | 0.0675 | -7.4% | 75% | 25% | 14% |
| nadir+jpeg | 98% | 0.0238 | 0.2586 | 0.0897 | -46.3% | 82% | 15% | 58% |
