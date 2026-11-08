# Capture-aware correction, end to end: da360_panox

model `da360` · 100 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0664 | 0.0664 | 0.0664 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0664 | 0.0680 | 0.0721 | +0.6% | 46% | 49% | 21% |
| nadir | 100% | 0.0110 | 0.0133 | 0.0133 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0333 | 0.0502 | 0.0502 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0664 | 0.1065 | 0.0776 | -18.0% | 76% | 22% | 70% |
| jpeg | 100% | 0.0664 | 0.1345 | 0.1403 | +2.2% | 43% | 56% | -4% |
| nadir+jpeg | 60% | 0.0110 | 0.0283 | 0.0274 | -1.1% | 52% | 44% | 6% |
