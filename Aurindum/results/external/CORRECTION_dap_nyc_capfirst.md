# Capture-aware correction, end to end: dap_nyc_capfirst

model `dap` · 40 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0334 | 0.0334 | 0.0334 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0334 | 0.0936 | 0.0478 | -46.9% | 98% | 2% | 78% |
| nadir | 100% | 0.0169 | 0.5031 | 0.0494 | -85.5% | 78% | 18% | 92% |
| vfov | 100% | 0.0242 | 0.7170 | 0.4224 | -39.4% | 98% | 2% | 40% |
| yawblur | 100% | 0.0334 | 0.1234 | 0.0479 | -61.2% | 92% | 8% | 87% |
| jpeg | 100% | 0.0334 | 0.1664 | 0.1540 | -7.7% | 78% | 8% | 11% |
| nadir+jpeg | 90% | 0.0169 | 0.3306 | 0.2648 | +0.8% | 48% | 50% | -1% |
