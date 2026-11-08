# Capture-aware correction, end to end: dap_s3

model `dap` · 100 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "plane_fill", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0346 | 0.0346 | 0.0346 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0346 | 0.1329 | 0.0404 | -70.5% | 97% | 3% | 96% |
| nadir | 100% | 0.0236 | 0.3682 | 0.3609 | -0.7% | 56% | 43% | 1% |
| vfov | 100% | 0.0287 | 0.7705 | 0.6109 | -19.3% | 100% | 0% | 20% |
| yawblur | 99% | 0.0346 | 0.0423 | 0.0377 | -11.9% | 67% | 32% | 53% |
| jpeg | 99% | 0.0346 | 0.0968 | 0.0842 | -10.3% | 86% | 13% | 16% |
| nadir+jpeg | 98% | 0.0236 | 0.2245 | 0.1120 | -44.5% | 79% | 20% | 55% |
