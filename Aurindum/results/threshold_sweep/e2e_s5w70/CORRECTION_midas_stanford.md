# Capture-aware correction, end to end: midas_stanford

model `midas_dpt_hybrid_384` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.2562 | 0.2562 | 0.2562 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2562 | 0.2519 | 0.2519 | +0.0% | 0% | 0% | 0% |
| nadir | 0% | 0.1008 | 0.0935 | 0.0935 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1229 | 0.1427 | 0.1427 | +0.0% | 0% | 0% | 0% |
| yawblur | 0% | 0.2562 | 0.2479 | 0.2533 | +0.4% | 42% | 41% | 75% |
| jpeg | 0% | 0.2562 | 0.2550 | 0.2550 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 0% | 0.1008 | 0.1003 | 0.1003 | +0.0% | 0% | 0% | 0% |
