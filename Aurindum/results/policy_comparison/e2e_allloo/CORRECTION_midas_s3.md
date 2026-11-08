# Capture-aware correction, end to end: midas_s3

model `midas_dpt_hybrid_384` · 100 frames · policy chosen on holo_in, holo_out, nyc, panox, stanford (held out: s3): `{"tilt": "relevel_known", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 99% | 0.2465 | 0.2465 | 0.2465 | +0.0% | 1% | 0% | n/a |
| tilt | 100% | 0.2465 | 0.2447 | 0.2375 | -1.4% | 63% | 29% | 97% |
| nadir | 99% | 0.2799 | 0.2682 | 0.2682 | +0.0% | 1% | 0% | 0% |
| vfov | 100% | 0.2055 | 0.1888 | 0.2034 | +3.8% | 43% | 55% | 50% |
| yawblur | 99% | 0.2465 | 0.2460 | 0.2430 | -1.0% | 62% | 22% | 74% |
| jpeg | 100% | 0.2465 | 0.2554 | 0.2554 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 63% | 0.2799 | 0.2347 | 0.2347 | +0.0% | 0% | 0% | 0% |
