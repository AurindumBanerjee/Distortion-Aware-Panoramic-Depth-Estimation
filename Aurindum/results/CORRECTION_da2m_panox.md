# Capture-aware correction, end to end: da2m_panox

model `da2` · 40 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1040 | 0.1040 | 0.1040 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1040 | 0.1498 | 0.1199 | -22.9% | 82% | 12% | 88% |
| nadir | 100% | 0.0754 | 0.2502 | 0.0856 | -64.9% | 88% | 12% | 89% |
| vfov | 100% | 0.0736 | 0.1484 | 0.1346 | +8.6% | 48% | 52% | 3% |
| yawblur | 100% | 0.1040 | 0.1254 | 0.1254 | +0.0% | 0% | 0% | 0% |
| jpeg | 100% | 0.1040 | 0.1764 | 0.1764 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 68% | 0.0754 | 0.2713 | 0.1610 | -33.6% | 60% | 8% | 47% |
