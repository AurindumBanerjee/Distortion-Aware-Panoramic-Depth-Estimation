# Capture-aware correction, end to end: dap_stanford

model `dap` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1518 | 0.1518 | 0.0942 | -35.7% | 100% | 0% | n/a |
| tilt | 100% | 0.1518 | 0.2156 | 0.1525 | -32.0% | 100% | 0% | 109% |
| nadir | 0% | 0.3135 | 0.3895 | 0.1737 | -40.9% | 98% | 2% | 167% |
| vfov | 100% | 0.2491 | 0.7560 | 0.3002 | -59.7% | 100% | 0% | 89% |
| yawblur | 0% | 0.1518 | 0.1737 | 0.1064 | -33.6% | 98% | 1% | 227% |
| jpeg | 0% | 0.1518 | 0.2860 | 0.1528 | -49.2% | 98% | 2% | 104% |
| nadir+jpeg | 0% | 0.3135 | 0.2671 | 0.0791 | -69.0% | 94% | 6% | 322% |
