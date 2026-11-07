# Capture-aware correction, end to end: da360_nyc

model `da360` · 40 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0643 | 0.0643 | 0.0643 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0643 | 0.0688 | 0.0688 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0101 | 0.0140 | 0.0140 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0424 | 0.2007 | 0.2007 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0643 | 0.0912 | 0.0713 | -18.9% | 90% | 8% | 76% |
| jpeg | 100% | 0.0643 | 0.1289 | 0.1289 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 45% | 0.0101 | 0.0459 | 0.0459 | +0.0% | 0% | 0% | 0% |
