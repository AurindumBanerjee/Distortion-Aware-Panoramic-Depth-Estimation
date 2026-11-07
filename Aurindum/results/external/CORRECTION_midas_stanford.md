# Capture-aware correction, end to end: midas_stanford

model `midas_dpt_hybrid_384` · 373 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.2515 | 0.2515 | 0.2515 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2515 | 0.2482 | 0.2500 | +0.6% | 42% | 46% | 71% |
| nadir | 0% | 0.0993 | 0.0939 | 0.0939 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1208 | 0.1359 | 0.1359 | +0.0% | 0% | 0% | 0% |
| yawblur | 0% | 0.2515 | 0.2455 | 0.2492 | +0.6% | 38% | 46% | 82% |
| jpeg | 0% | 0.2515 | 0.2505 | 0.2505 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 0% | 0.0993 | 0.0886 | 0.0886 | +0.0% | 0% | 0% | 0% |
