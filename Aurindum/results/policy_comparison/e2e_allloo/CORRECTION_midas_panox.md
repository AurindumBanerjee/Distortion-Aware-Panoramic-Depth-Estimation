# Capture-aware correction, end to end: midas_panox

model `midas_dpt_hybrid_384` · 100 frames · policy chosen on holo_in, holo_out, nyc, s3, stanford (held out: panox): `{"tilt": "relevel_known", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1887 | 0.1887 | 0.1887 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1887 | 0.2154 | 0.1961 | -9.8% | 80% | 20% | 85% |
| nadir | 100% | 0.0676 | 0.0723 | 0.0723 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1484 | 0.3337 | 0.1574 | -38.8% | 78% | 21% | 99% |
| yawblur | 100% | 0.1887 | 0.2024 | 0.2040 | -2.3% | 57% | 38% | 71% |
| jpeg | 100% | 0.1887 | 0.3027 | 0.3027 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 60% | 0.0676 | 0.1044 | 0.1044 | +0.0% | 0% | 0% | 0% |
