# Capture-aware correction, end to end: midas_hr_stanford

model `midas_dpt_hybrid_384` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.2554 | 0.2554 | 0.2554 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2554 | 0.2516 | 0.2558 | +1.4% | 30% | 55% | 86% |
| nadir | 0% | 0.0992 | 0.0843 | 0.0843 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1241 | 0.1362 | 0.1362 | +0.0% | 0% | 0% | 0% |
| yawblur | 0% | 0.2554 | 0.2482 | 0.2526 | -0.3% | 56% | 24% | 134% |
| jpeg | 0% | 0.2554 | 0.2489 | 0.2489 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 0% | 0.0992 | 0.0996 | 0.0996 | +0.0% | 0% | 0% | 0% |
