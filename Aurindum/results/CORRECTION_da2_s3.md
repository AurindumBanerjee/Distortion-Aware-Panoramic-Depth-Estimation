# Capture-aware correction, end to end: da2_s3

model `da2` · 40 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"nadir": "inpaint_erp", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0430 | 0.0430 | 0.0430 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0430 | 0.0773 | 0.0773 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0324 | 0.1821 | 0.0563 | -64.7% | 95% | 5% | 84% |
| vfov | 100% | 0.0425 | 0.1632 | 0.0960 | -40.1% | 95% | 5% | 63% |
| yawblur | 100% | 0.0430 | 0.0549 | 0.0494 | -4.0% | 60% | 38% | 51% |
| jpeg | 98% | 0.0430 | 0.0845 | 0.0845 | +0.0% | 0% | 2% | 0% |
| nadir+jpeg | 52% | 0.0324 | 0.1229 | 0.1309 | +0.0% | 20% | 35% | 0% |
