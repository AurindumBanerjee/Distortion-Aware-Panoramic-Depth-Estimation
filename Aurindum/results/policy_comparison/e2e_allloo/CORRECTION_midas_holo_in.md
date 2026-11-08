# Capture-aware correction, end to end: midas_holo_in

model `midas_dpt_hybrid_384` · 100 frames · policy chosen on holo_out, nyc, panox, s3, stanford (held out: holo_in): `{"tilt": "relevel_known", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2850 | 0.2850 | 0.2850 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2850 | 0.3145 | 0.2843 | -5.1% | 71% | 27% | 86% |
| nadir | 100% | 0.3427 | 0.3911 | 0.3911 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.2432 | 0.2566 | 0.2728 | +6.5% | 38% | 59% | -1% |
| yawblur | 100% | 0.2850 | 0.3001 | 0.2873 | -6.7% | 71% | 22% | 97% |
| jpeg | 100% | 0.2850 | 0.3501 | 0.3501 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 26% | 0.3427 | 0.3716 | 0.3716 | +0.0% | 0% | 0% | 0% |
