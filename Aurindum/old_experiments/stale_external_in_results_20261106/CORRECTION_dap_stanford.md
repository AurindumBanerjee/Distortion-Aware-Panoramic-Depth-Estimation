# Capture-aware correction, end to end: dap_stanford

model `dap` · 40 frames · policy chosen on holo_in, holo_out, nyc, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "plane_fill", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1596 | 0.1596 | 0.1596 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1596 | 0.2281 | 0.1512 | -32.9% | 100% | 0% | 107% |
| nadir | 100% | 0.2974 | 0.3716 | 0.0750 | -70.2% | 98% | 2% | 272% |
| vfov | 100% | 0.2358 | 0.7405 | 0.5204 | -26.6% | 100% | 0% | 37% |
| yawblur | 52% | 0.1596 | 0.1694 | 0.1152 | -19.6% | 90% | 10% | 128% |
| jpeg | 100% | 0.1596 | 0.2644 | 0.2215 | -12.4% | 90% | 2% | 29% |
| nadir+jpeg | 100% | 0.2974 | 0.3352 | 0.1027 | -50.0% | 90% | 10% | 217% |
