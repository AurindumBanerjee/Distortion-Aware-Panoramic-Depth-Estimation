# Capture-aware correction, end to end: da2m_holo_out

model `da2` · 71 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2139 | 0.2139 | 0.2139 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2139 | 0.2116 | 0.2366 | +5.8% | 39% | 61% | 66% |
| nadir | 100% | 0.0836 | 0.1499 | 0.0992 | -51.6% | 69% | 31% | 103% |
| vfov | 100% | 0.1167 | 0.1679 | 0.1328 | -16.3% | 56% | 44% | 82% |
| yawblur | 100% | 0.2139 | 0.3047 | 0.2891 | -1.6% | 55% | 44% | 49% |
| jpeg | 100% | 0.2139 | 0.3448 | 0.3448 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 65% | 0.0836 | 0.1437 | 0.1677 | +0.0% | 30% | 35% | 0% |
