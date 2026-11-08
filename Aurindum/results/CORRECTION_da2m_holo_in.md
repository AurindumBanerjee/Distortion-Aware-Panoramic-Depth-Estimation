# Capture-aware correction, end to end: da2m_holo_in

model `da2` · 40 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1216 | 0.1216 | 0.1216 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1216 | 0.1534 | 0.1227 | -10.1% | 72% | 28% | 92% |
| nadir | 100% | 0.1459 | 0.1739 | 0.1621 | -26.1% | 57% | 42% | 85% |
| vfov | 100% | 0.1294 | 0.2243 | 0.1460 | -23.4% | 85% | 15% | 63% |
| yawblur | 100% | 0.1216 | 0.1499 | 0.1436 | +1.3% | 48% | 50% | 18% |
| jpeg | 100% | 0.1216 | 0.2216 | 0.2216 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 28% | 0.1459 | 0.2488 | 0.2528 | +0.0% | 15% | 12% | 0% |
