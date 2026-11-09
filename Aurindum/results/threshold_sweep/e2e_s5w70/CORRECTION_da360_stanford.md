# Capture-aware correction, end to end: da360_stanford

model `da360` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1458 | 0.1458 | 0.1458 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1458 | 0.1676 | 0.1676 | +0.0% | 0% | 0% | 0% |
| nadir | 0% | 0.0760 | 0.0725 | 0.0725 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1366 | 0.0646 | 0.0646 | +0.0% | 0% | 0% | 0% |
| yawblur | 0% | 0.1458 | 0.1692 | 0.1516 | -7.2% | 76% | 22% | 52% |
| jpeg | 0% | 0.1458 | 0.1193 | 0.1193 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 0% | 0.0760 | 0.0420 | 0.0420 | +0.0% | 0% | 0% | 0% |
