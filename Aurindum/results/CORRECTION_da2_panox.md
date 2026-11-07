# Capture-aware correction, end to end: da2_panox

model `da2` · 100 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "nadir": "inpaint_erp", "vfov": "inpaint_erp", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1391 | 0.1391 | 0.1391 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1391 | 0.1967 | 0.1444 | -4.3% | 52% | 47% | 97% |
| nadir | 100% | 0.1267 | 0.3493 | 0.1779 | -47.3% | 74% | 23% | 80% |
| vfov | 100% | 0.1151 | 0.2915 | 0.3526 | -3.4% | 52% | 47% | -44% |
| yawblur | 100% | 0.1391 | 0.2205 | 0.2205 | +0.0% | 0% | 0% | 0% |
| jpeg | 100% | 0.1391 | 0.2419 | 0.2734 | +5.0% | 37% | 61% | -11% |
| nadir+jpeg | 60% | 0.1267 | 0.4894 | 0.4410 | -0.9% | 52% | 47% | 8% |
