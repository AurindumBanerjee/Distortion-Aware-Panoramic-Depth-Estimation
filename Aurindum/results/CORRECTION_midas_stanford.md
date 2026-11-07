# Capture-aware correction, end to end: midas_stanford

model `midas_dpt_hybrid_384` · 40 frames · policy chosen on holo_in, holo_out, nyc, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.2420 | 0.2420 | 0.2417 | -0.6% | 72% | 20% | n/a |
| tilt | 100% | 0.2420 | 0.2338 | 0.2418 | +2.0% | 40% | 57% | 59% |
| nadir | 0% | 0.1050 | 0.0906 | 0.0831 | +9.7% | 40% | 60% | 71% |
| vfov | 100% | 0.1070 | 0.1255 | 0.1057 | -10.6% | 78% | 20% | 94% |
| yawblur | 0% | 0.2420 | 0.2305 | 0.2288 | +0.4% | 48% | 42% | 129% |
| jpeg | 0% | 0.2420 | 0.2584 | 0.2594 | +0.8% | 42% | 48% | 13% |
| nadir+jpeg | 0% | 0.1050 | 0.0886 | 0.1135 | -2.3% | 52% | 48% | -38% |
