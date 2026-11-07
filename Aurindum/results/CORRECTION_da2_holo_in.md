# Capture-aware correction, end to end: da2_holo_in

model `da2` · 40 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1240 | 0.1240 | 0.1240 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1240 | 0.1529 | 0.1529 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.1286 | 0.1367 | 0.1491 | -8.1% | 57% | 42% | 77% |
| vfov | 100% | 0.1427 | 0.2293 | 0.1825 | -19.2% | 80% | 20% | 62% |
| yawblur | 100% | 0.1240 | 0.1757 | 0.1643 | -1.1% | 52% | 45% | 13% |
| jpeg | 100% | 0.1240 | 0.2623 | 0.2623 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 28% | 0.1286 | 0.2134 | 0.1821 | +0.0% | 20% | 8% | 0% |
