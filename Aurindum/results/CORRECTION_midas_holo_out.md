# Capture-aware correction, end to end: midas_holo_out

model `midas_dpt_hybrid_384` · 40 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.3139 | 0.3139 | 0.3139 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.3139 | 0.4142 | 0.3661 | -6.5% | 78% | 20% | 36% |
| nadir | 100% | 0.1468 | 0.0795 | 0.0859 | +10.7% | 45% | 55% | 125% |
| vfov | 100% | 0.2330 | 0.2784 | 0.2784 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.3139 | 0.4453 | 0.3344 | -19.1% | 98% | 2% | 81% |
| jpeg | 100% | 0.3139 | 0.5045 | 0.5045 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 72% | 0.1468 | 0.3647 | 0.2194 | -17.9% | 60% | 12% | 50% |
