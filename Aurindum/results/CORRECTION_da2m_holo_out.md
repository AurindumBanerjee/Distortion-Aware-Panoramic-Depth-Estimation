# Capture-aware correction, end to end: da2m_holo_out

model `da2` · 40 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2164 | 0.2164 | 0.2164 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2164 | 0.2214 | 0.2386 | +3.4% | 42% | 57% | 68% |
| nadir | 100% | 0.0905 | 0.1463 | 0.1009 | -44.7% | 62% | 38% | 106% |
| vfov | 100% | 0.1218 | 0.1599 | 0.1346 | -17.7% | 62% | 38% | 84% |
| yawblur | 100% | 0.2164 | 0.3251 | 0.2881 | -3.5% | 57% | 42% | 42% |
| jpeg | 100% | 0.2164 | 0.3289 | 0.3289 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 72% | 0.0905 | 0.1310 | 0.1622 | +0.0% | 32% | 40% | 0% |
