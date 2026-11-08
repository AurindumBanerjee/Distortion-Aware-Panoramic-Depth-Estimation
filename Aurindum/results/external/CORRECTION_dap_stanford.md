# Capture-aware correction, end to end: dap_stanford

model `dap` · 373 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1500 | 0.1500 | 0.0927 | -34.8% | 99% | 1% | n/a |
| tilt | 100% | 0.1500 | 0.2194 | 0.1462 | -32.0% | 99% | 1% | 109% |
| nadir | 0% | 0.3145 | 0.3483 | 0.1520 | -41.6% | 97% | 3% | 238% |
| vfov | 100% | 0.2445 | 0.7598 | 0.3065 | -59.1% | 100% | 0% | 87% |
| yawblur | 0% | 0.1500 | 0.1665 | 0.1047 | -32.9% | 97% | 2% | 226% |
| jpeg | 0% | 0.1500 | 0.2739 | 0.1403 | -47.1% | 98% | 2% | 105% |
| nadir+jpeg | 0% | 0.3145 | 0.2689 | 0.0655 | -71.7% | 94% | 6% | 278% |
