# Capture-aware correction, end to end: da360_holo_out

model `da360` · 40 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2053 | 0.2053 | 0.2053 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2053 | 0.2186 | 0.2186 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0911 | 0.0488 | 0.0488 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1823 | 0.1957 | 0.1957 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.2053 | 0.2235 | 0.2020 | -8.5% | 70% | 28% | 73% |
| jpeg | 100% | 0.2053 | 0.2906 | 0.2906 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 72% | 0.0911 | 0.0339 | 0.0339 | +0.0% | 0% | 0% | 0% |
