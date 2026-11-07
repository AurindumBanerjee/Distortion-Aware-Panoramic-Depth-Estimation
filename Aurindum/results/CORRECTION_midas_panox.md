# Capture-aware correction, end to end: midas_panox

model `midas_dpt_hybrid_384` · 40 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1877 | 0.1877 | 0.1877 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1877 | 0.2153 | 0.1921 | -8.9% | 75% | 25% | 87% |
| nadir | 100% | 0.0701 | 0.0699 | 0.0699 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1430 | 0.3082 | 0.3082 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.1877 | 0.2040 | 0.2014 | -4.7% | 57% | 38% | 75% |
| jpeg | 100% | 0.1877 | 0.3063 | 0.3063 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 68% | 0.0701 | 0.0997 | 0.0997 | +0.0% | 0% | 0% | 0% |
