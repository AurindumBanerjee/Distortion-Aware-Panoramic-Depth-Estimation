# Capture-aware correction, end to end: dap_stanford

model `dap` · 40 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1596 | 0.1596 | 0.0912 | -34.6% | 100% | 0% | n/a |
| tilt | 100% | 0.1596 | 0.2281 | 0.1512 | -32.9% | 100% | 0% | 107% |
| nadir | 0% | 0.2974 | 0.3716 | 0.1207 | -47.8% | 98% | 2% | 263% |
| vfov | 100% | 0.2358 | 0.7405 | 0.2931 | -61.0% | 100% | 0% | 91% |
| yawblur | 0% | 0.1596 | 0.1694 | 0.1055 | -28.7% | 98% | 2% | 178% |
| jpeg | 0% | 0.1596 | 0.2644 | 0.1287 | -43.0% | 98% | 2% | 102% |
| nadir+jpeg | 0% | 0.2974 | 0.3352 | 0.0777 | -63.6% | 90% | 10% | 209% |
