# Capture-aware correction, end to end: da2m_s3

model `da2` · 100 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 99% | 0.0508 | 0.0508 | 0.0508 | +0.0% | 0% | 1% | n/a |
| tilt | 100% | 0.0508 | 0.0912 | 0.0526 | -38.4% | 88% | 12% | 98% |
| nadir | 99% | 0.0368 | 0.1819 | 0.0666 | -63.7% | 89% | 11% | 84% |
| vfov | 100% | 0.0455 | 0.1745 | 0.0888 | -42.8% | 90% | 9% | 71% |
| yawblur | 99% | 0.0508 | 0.0696 | 0.0696 | +0.0% | 1% | 0% | 0% |
| jpeg | 100% | 0.0508 | 0.1031 | 0.1031 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 63% | 0.0368 | 0.1286 | 0.1155 | +0.0% | 36% | 24% | 0% |
