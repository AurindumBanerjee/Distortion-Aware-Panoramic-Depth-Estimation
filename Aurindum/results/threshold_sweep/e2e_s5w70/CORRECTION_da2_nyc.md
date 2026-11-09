# Capture-aware correction, end to end: da2_nyc

model `da2` · 147 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"nadir": "inpaint_erp", "vfov": "inpaint_erp"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.6378 | 0.6378 | 0.6378 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.6378 | 0.5629 | 0.5629 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.7261 | 0.7210 | 0.7204 | +3.0% | 28% | 69% | 67% |
| vfov | 100% | 0.6789 | 0.7784 | 0.8290 | +6.1% | 20% | 74% | -36% |
| yawblur | 100% | 0.6378 | 0.6972 | 0.6972 | +0.0% | 0% | 0% | 0% |
| jpeg | 100% | 0.6378 | 0.6750 | 0.6750 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 37% | 0.7261 | 0.8072 | 0.8159 | +0.0% | 1% | 35% | 0% |
