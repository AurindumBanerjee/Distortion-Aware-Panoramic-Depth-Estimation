# Capture-aware correction, end to end: midas_holo_out

model `midas_dpt_hybrid_384` · 71 frames · policy chosen on holo_in, nyc, panox, s3, stanford (held out: holo_out): `{"tilt": "relevel_known", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.3016 | 0.3016 | 0.3016 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.3016 | 0.4042 | 0.3688 | -6.4% | 77% | 20% | 45% |
| nadir | 100% | 0.1477 | 0.0811 | 0.0811 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.2428 | 0.2747 | 0.2280 | -9.4% | 61% | 38% | 87% |
| yawblur | 100% | 0.3016 | 0.4350 | 0.3391 | -18.0% | 93% | 7% | 80% |
| jpeg | 100% | 0.3016 | 0.5046 | 0.5046 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 65% | 0.1477 | 0.3752 | 0.3752 | +0.0% | 0% | 0% | 0% |
