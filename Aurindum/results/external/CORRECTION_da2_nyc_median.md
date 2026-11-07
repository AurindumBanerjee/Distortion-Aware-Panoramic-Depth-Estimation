# Capture-aware correction, end to end: da2_nyc_median

model `da2` · 40 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2029 | 0.2029 | 0.2029 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2029 | 0.2861 | 0.2261 | -21.1% | 92% | 8% | 79% |
| nadir | 100% | 0.0692 | 0.1263 | 0.0708 | -41.7% | 62% | 38% | 86% |
| vfov | 100% | 0.1282 | 0.2107 | 0.2280 | -10.7% | 60% | 40% | 22% |
| yawblur | 100% | 0.2029 | 0.2355 | 0.2217 | -4.9% | 65% | 32% | 54% |
| jpeg | 100% | 0.2029 | 0.2776 | 0.2776 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 45% | 0.0692 | 0.1621 | 0.1666 | +0.0% | 20% | 25% | 0% |
