# Capture-aware correction, end to end: midas_nyc

model `midas_dpt_hybrid_384` · 40 frames · policy chosen on holo_in, holo_out, panox, s3, stanford (held out: nyc): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2214 | 0.2214 | 0.2214 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2214 | 0.2574 | 0.2250 | -2.8% | 62% | 32% | 93% |
| nadir | 100% | 0.0708 | 0.0614 | 0.0614 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1571 | 0.3264 | 0.3264 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.2214 | 0.2676 | 0.2343 | -8.3% | 80% | 10% | 70% |
| jpeg | 100% | 0.2214 | 0.3238 | 0.3238 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 45% | 0.0708 | 0.1140 | 0.1140 | +0.0% | 0% | 0% | 0% |
