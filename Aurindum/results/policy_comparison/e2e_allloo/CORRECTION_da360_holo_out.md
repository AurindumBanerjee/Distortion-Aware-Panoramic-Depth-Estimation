# Capture-aware correction, end to end: da360_holo_out

model `da360` · 71 frames · policy chosen on holo_in, nyc, panox, s3, stanford (held out: holo_out): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2008 | 0.2008 | 0.2008 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2008 | 0.2136 | 0.2007 | -2.1% | 65% | 32% | 115% |
| nadir | 100% | 0.1000 | 0.0490 | 0.0490 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1684 | 0.1651 | 0.1651 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.2008 | 0.2175 | 0.1974 | -7.6% | 70% | 25% | 74% |
| jpeg | 100% | 0.2008 | 0.2735 | 0.2735 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 65% | 0.1000 | 0.0324 | 0.0324 | +0.0% | 0% | 0% | 0% |
