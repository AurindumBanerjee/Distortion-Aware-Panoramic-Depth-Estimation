# Capture-aware correction, end to end: da360_stanford

model `da360` · 373 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1509 | 0.1509 | 0.1509 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1509 | 0.1662 | 0.1662 | +0.0% | 0% | 0% | 0% |
| nadir | 0% | 0.0897 | 0.0770 | 0.0770 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1379 | 0.0629 | 0.0629 | +0.0% | 0% | 0% | 0% |
| yawblur | 0% | 0.1509 | 0.1731 | 0.1565 | -6.2% | 73% | 24% | 49% |
| jpeg | 0% | 0.1509 | 0.1184 | 0.1184 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 0% | 0.0897 | 0.0453 | 0.0453 | +0.0% | 0% | 0% | 0% |
