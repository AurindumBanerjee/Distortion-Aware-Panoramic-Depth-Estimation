# Capture-aware correction, end to end: da360_stanford

model `da360` · 40 frames · policy chosen on holo_in, holo_out, nyc, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1448 | 0.1448 | 0.1448 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1448 | 0.1641 | 0.1303 | -4.0% | 70% | 22% | 100% |
| nadir | 0% | 0.0766 | 0.0668 | 0.0668 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1349 | 0.0754 | 0.0754 | +0.0% | 0% | 0% | 0% |
| yawblur | 0% | 0.1448 | 0.1682 | 0.1506 | -6.7% | 80% | 15% | 53% |
| jpeg | 0% | 0.1448 | 0.1116 | 0.1116 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 0% | 0.0766 | 0.0435 | 0.0435 | +0.0% | 0% | 0% | 0% |
