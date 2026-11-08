# Capture-aware correction, end to end: dap_stanford

model `dap` · 373 frames · policy chosen on holo_in, holo_out, nyc, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "plane_fill", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.1500 | 0.1500 | 0.0848 | -39.0% | 99% | 1% | n/a |
| tilt | 100% | 0.1500 | 0.2194 | 0.1462 | -32.0% | 99% | 1% | 109% |
| nadir | 0% | 0.3145 | 0.3483 | 0.0711 | -69.2% | 96% | 4% | 282% |
| vfov | 100% | 0.2445 | 0.7598 | 0.5673 | -22.1% | 100% | 0% | 32% |
| yawblur | 0% | 0.1500 | 0.1665 | 0.0849 | -44.1% | 99% | 1% | 300% |
| jpeg | 0% | 0.1500 | 0.2739 | 0.1380 | -48.9% | 100% | 0% | 105% |
| nadir+jpeg | 0% | 0.3145 | 0.2689 | 0.0649 | -72.0% | 94% | 6% | 350% |
