# Capture-aware correction, end to end: dap_nyc

model `dap` · 147 frames · policy chosen on holo_in, holo_out, panox, s3, stanford (held out: nyc): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0352 | 0.0352 | 0.0352 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0352 | 0.0915 | 0.0477 | -47.4% | 98% | 2% | 77% |
| nadir | 100% | 0.0182 | 0.5238 | 0.0426 | -89.3% | 79% | 20% | 93% |
| vfov | 100% | 0.0245 | 0.7129 | 0.4396 | -36.4% | 99% | 1% | 37% |
| yawblur | 100% | 0.0352 | 0.1272 | 0.0487 | -60.4% | 92% | 7% | 87% |
| jpeg | 100% | 0.0352 | 0.1764 | 0.1638 | -7.9% | 82% | 12% | 11% |
| nadir+jpeg | 88% | 0.0182 | 0.3219 | 0.2688 | +1.3% | 47% | 52% | -1% |
