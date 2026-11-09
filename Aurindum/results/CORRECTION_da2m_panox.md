# Capture-aware correction, end to end: da2m_panox

model `da2` · 100 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1006 | 0.1006 | 0.1006 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1006 | 0.1511 | 0.1182 | -23.8% | 90% | 10% | 90% |
| nadir | 100% | 0.0762 | 0.2492 | 0.0861 | -66.2% | 87% | 13% | 89% |
| vfov | 100% | 0.0742 | 0.1724 | 0.1304 | -3.1% | 53% | 47% | 9% |
| yawblur | 100% | 0.1006 | 0.1284 | 0.1284 | +0.0% | 0% | 0% | 0% |
| jpeg | 100% | 0.1006 | 0.1870 | 0.1870 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 60% | 0.0762 | 0.3005 | 0.1657 | -5.6% | 51% | 9% | 37% |
