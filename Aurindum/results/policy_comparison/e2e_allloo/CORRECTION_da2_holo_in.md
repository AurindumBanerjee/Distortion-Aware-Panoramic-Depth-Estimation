# Capture-aware correction, end to end: da2_holo_in

model `da2` · 100 frames · policy chosen on holo_out, nyc, panox, s3, stanford (held out: holo_in): `{"nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1153 | 0.1153 | 0.1153 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1153 | 0.1585 | 0.1585 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.1322 | 0.1560 | 0.1485 | -9.7% | 52% | 48% | 87% |
| vfov | 100% | 0.1298 | 0.2177 | 0.1686 | -23.9% | 79% | 20% | 61% |
| yawblur | 100% | 0.1153 | 0.1620 | 0.1527 | -2.0% | 54% | 44% | 11% |
| jpeg | 100% | 0.1153 | 0.2370 | 0.2370 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 26% | 0.1322 | 0.2240 | 0.2216 | +0.0% | 11% | 14% | 0% |
