# Capture-aware correction, end to end: da2_stanford

model `da2` · 373 frames · policy chosen on holo_in, holo_out, nyc, panox, s3 (held out: stanford): `{"nadir": "inpaint_erp", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.0678 | 0.0678 | 0.0629 | -6.6% | 77% | 21% | n/a |
| tilt | 100% | 0.0678 | 0.0962 | 0.0962 | +0.0% | 0% | 0% | 0% |
| nadir | 0% | 0.0487 | 0.1741 | 0.0380 | -78.1% | 99% | 1% | 106% |
| vfov | 100% | 0.0659 | 0.0982 | 0.0672 | -23.3% | 87% | 13% | 86% |
| yawblur | 0% | 0.0678 | 0.0713 | 0.0698 | -6.5% | 68% | 28% | 56% |
| jpeg | 0% | 0.0678 | 0.0757 | 0.0894 | +8.0% | 35% | 64% | -28% |
| nadir+jpeg | 0% | 0.0487 | 0.1602 | 0.1375 | -2.2% | 52% | 47% | 3% |
