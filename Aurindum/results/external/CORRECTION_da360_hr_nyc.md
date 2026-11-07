# Capture-aware correction, end to end: da360_hr_nyc

model `da360` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0614 | 0.0614 | 0.0614 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0614 | 0.0666 | 0.0666 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0121 | 0.0172 | 0.0172 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0421 | 0.2340 | 0.2340 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0614 | 0.0719 | 0.0636 | -8.4% | 79% | 16% | 71% |
| jpeg | 100% | 0.0614 | 0.0915 | 0.0915 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 88% | 0.0121 | 0.0259 | 0.0259 | +0.0% | 0% | 0% | 0% |
