# Capture-aware correction, end to end: dap_panox

model `dap` · 40 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1879 | 0.1879 | 0.1879 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1879 | 0.2493 | 0.1905 | -24.2% | 72% | 25% | 105% |
| nadir | 100% | 0.1111 | 0.2223 | 0.1425 | -23.5% | 80% | 20% | 85% |
| vfov | 100% | 0.1868 | 0.6426 | 0.3761 | -43.9% | 92% | 8% | 64% |
| yawblur | 100% | 0.1879 | 0.2577 | 0.1928 | -19.4% | 90% | 10% | 89% |
| jpeg | 100% | 0.1879 | 0.3455 | 0.3070 | -3.6% | 72% | 28% | 13% |
| nadir+jpeg | 100% | 0.1111 | 0.4063 | 0.2620 | -15.9% | 88% | 12% | 28% |
