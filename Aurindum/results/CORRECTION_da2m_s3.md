# Capture-aware correction, end to end: da2m_s3

model `da2` · 40 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0429 | 0.0429 | 0.0429 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0429 | 0.0809 | 0.0489 | -39.4% | 90% | 10% | 99% |
| nadir | 100% | 0.0322 | 0.1998 | 0.0520 | -72.5% | 95% | 5% | 94% |
| vfov | 100% | 0.0438 | 0.1632 | 0.0900 | -40.4% | 92% | 8% | 67% |
| yawblur | 100% | 0.0429 | 0.0556 | 0.0556 | +0.0% | 0% | 0% | 0% |
| jpeg | 98% | 0.0429 | 0.0842 | 0.0842 | +0.0% | 0% | 2% | 0% |
| nadir+jpeg | 52% | 0.0322 | 0.1292 | 0.0917 | +0.0% | 32% | 22% | 0% |
