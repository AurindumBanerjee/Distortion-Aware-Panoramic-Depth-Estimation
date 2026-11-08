# Capture-aware correction, end to end: midas_hr_nyc

model `midas_dpt_hybrid_384` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2274 | 0.2274 | 0.2274 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2274 | 0.2357 | 0.2207 | -2.6% | 62% | 30% | 110% |
| nadir | 100% | 0.0675 | 0.0611 | 0.0611 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1535 | 0.2738 | 0.2738 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.2274 | 0.2427 | 0.2231 | -5.4% | 82% | 14% | 73% |
| jpeg | 100% | 0.2274 | 0.2931 | 0.2931 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 88% | 0.0675 | 0.0976 | 0.0976 | +0.0% | 0% | 0% | 0% |
