# Capture-aware correction, end to end: da360_nyc

model `da360` · 147 frames · policy chosen on holo_in, holo_out, panox, s3, stanford (held out: nyc): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0629 | 0.0629 | 0.0629 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0629 | 0.0690 | 0.0660 | -1.9% | 65% | 28% | 50% |
| nadir | 100% | 0.0130 | 0.0157 | 0.0157 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0431 | 0.1964 | 0.1964 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0629 | 0.0909 | 0.0703 | -17.5% | 91% | 7% | 70% |
| jpeg | 100% | 0.0629 | 0.1299 | 0.1299 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 37% | 0.0130 | 0.0495 | 0.0495 | +0.0% | 0% | 0% | 0% |
