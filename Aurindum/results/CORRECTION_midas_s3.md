# Capture-aware correction, end to end: midas_s3

model `midas_dpt_hybrid_384` · 40 frames · policy chosen on holo_in, holo_out, panox (held out: s3): `{"tilt": "relevel_known", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2210 | 0.2210 | 0.2210 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2210 | 0.2199 | 0.2137 | -0.1% | 50% | 42% | 114% |
| nadir | 100% | 0.2282 | 0.2476 | 0.2476 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.1898 | 0.1652 | 0.2062 | +9.6% | 30% | 70% | 87% |
| yawblur | 100% | 0.2210 | 0.2190 | 0.2162 | -0.6% | 60% | 25% | 70% |
| jpeg | 98% | 0.2210 | 0.2467 | 0.2467 | +0.0% | 2% | 0% | 0% |
| nadir+jpeg | 52% | 0.2282 | 0.1718 | 0.1718 | +0.0% | 2% | 0% | 0% |
