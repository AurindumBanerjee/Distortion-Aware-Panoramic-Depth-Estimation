# Capture-aware correction, end to end: da360_holo_in

model `da360` · 100 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0589 | 0.0589 | 0.0589 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0589 | 0.0645 | 0.0645 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0853 | 0.0895 | 0.0895 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0547 | 0.0709 | 0.0709 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0589 | 0.0753 | 0.0689 | -8.2% | 68% | 30% | 47% |
| jpeg | 100% | 0.0589 | 0.1668 | 0.1668 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 26% | 0.0853 | 0.1671 | 0.1671 | +0.0% | 0% | 0% | 0% |
