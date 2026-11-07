# Capture-aware correction, end to end: da360_panox

model `da360` · 40 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0644 | 0.0644 | 0.0644 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0644 | 0.0681 | 0.0696 | +2.6% | 40% | 55% | 23% |
| nadir | 100% | 0.0120 | 0.0132 | 0.0132 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0304 | 0.0517 | 0.0517 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0644 | 0.1080 | 0.0753 | -17.1% | 75% | 25% | 65% |
| jpeg | 100% | 0.0644 | 0.1523 | 0.1498 | +1.0% | 48% | 50% | -5% |
| nadir+jpeg | 68% | 0.0120 | 0.0368 | 0.0323 | +0.5% | 48% | 45% | 1% |
