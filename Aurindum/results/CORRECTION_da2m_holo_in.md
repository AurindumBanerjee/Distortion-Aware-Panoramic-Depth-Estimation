# Capture-aware correction, end to end: da2m_holo_in

model `da2` · 100 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1082 | 0.1082 | 0.1082 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1082 | 0.1492 | 0.1159 | -19.6% | 78% | 19% | 90% |
| nadir | 100% | 0.1490 | 0.1695 | 0.1670 | -4.0% | 53% | 45% | 84% |
| vfov | 100% | 0.1212 | 0.2125 | 0.1446 | -29.4% | 84% | 16% | 64% |
| yawblur | 100% | 0.1082 | 0.1402 | 0.1399 | +0.6% | 48% | 48% | 8% |
| jpeg | 100% | 0.1082 | 0.2150 | 0.2150 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 26% | 0.1490 | 0.2416 | 0.2447 | +0.0% | 8% | 17% | 0% |
