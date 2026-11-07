# Capture-aware correction, end to end: da2_holo_out

model `da2` · 40 frames · policy chosen on holo_in, panox, s3 (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.5161 | 0.5161 | 0.5161 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.5161 | 0.4308 | 0.4993 | +17.3% | 28% | 70% | 100% |
| nadir | 100% | 0.5561 | 0.5860 | 0.5702 | +1.1% | 45% | 50% | 12% |
| vfov | 100% | 0.5459 | 0.5669 | 0.5375 | -7.5% | 65% | 35% | 75% |
| yawblur | 100% | 0.5161 | 0.5483 | 0.5033 | -6.5% | 57% | 42% | 112% |
| jpeg | 100% | 0.5161 | 0.6008 | 0.6008 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 72% | 0.5561 | 0.5287 | 0.5606 | +0.0% | 35% | 38% | 0% |
