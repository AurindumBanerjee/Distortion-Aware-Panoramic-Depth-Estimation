# Capture-aware correction, end to end: da360_s3

model `da360` · 40 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0139 | 0.0139 | 0.0139 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0139 | 0.0169 | 0.0169 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0134 | 0.0203 | 0.0203 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0104 | 0.0429 | 0.0429 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0139 | 0.0271 | 0.0190 | -24.1% | 85% | 12% | 57% |
| jpeg | 98% | 0.0139 | 0.0501 | 0.0501 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 52% | 0.0134 | 0.0474 | 0.0474 | +0.0% | 0% | 0% | 0% |
