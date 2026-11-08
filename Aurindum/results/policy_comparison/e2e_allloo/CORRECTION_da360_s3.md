# Capture-aware correction, end to end: da360_s3

model `da360` · 100 frames · policy chosen on holo_in, holo_out, nyc, panox, stanford (held out: s3): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 99% | 0.0147 | 0.0147 | 0.0147 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0147 | 0.0182 | 0.0170 | -8.0% | 74% | 25% | 48% |
| nadir | 99% | 0.0138 | 0.0225 | 0.0225 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0110 | 0.0515 | 0.0515 | +0.0% | 0% | 0% | 0% |
| yawblur | 99% | 0.0147 | 0.0264 | 0.0201 | -20.4% | 82% | 18% | 60% |
| jpeg | 100% | 0.0147 | 0.0559 | 0.0559 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 63% | 0.0138 | 0.0604 | 0.0604 | +0.0% | 0% | 0% | 0% |
