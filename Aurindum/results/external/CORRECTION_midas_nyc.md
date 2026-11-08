# Capture-aware correction, end to end: midas_nyc

model `midas_dpt_hybrid_384` · 147 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2198 | 0.2198 | 0.2198 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2198 | 0.2433 | 0.2177 | -2.8% | 67% | 27% | 91% |
| nadir | 100% | 0.0658 | 0.0608 | 0.0608 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1550 | 0.3230 | 0.3230 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.2198 | 0.2574 | 0.2190 | -7.6% | 82% | 12% | 76% |
| jpeg | 100% | 0.2198 | 0.3225 | 0.3225 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 37% | 0.0658 | 0.1144 | 0.1144 | +0.0% | 0% | 0% | 0% |
