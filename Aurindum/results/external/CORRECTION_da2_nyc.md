# Capture-aware correction, end to end: da2_nyc

model `da2` · 40 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.6345 | 0.6345 | 0.6345 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.6345 | 0.5591 | 0.6504 | +15.3% | 10% | 88% | 49% |
| nadir | 100% | 0.7143 | 0.7203 | 0.7610 | +6.5% | 10% | 85% | -65% |
| vfov | 100% | 0.6709 | 0.7767 | 0.8348 | +5.1% | 25% | 68% | -33% |
| yawblur | 100% | 0.6345 | 0.6924 | 0.6517 | -4.3% | 72% | 28% | 85% |
| jpeg | 100% | 0.6345 | 0.6802 | 0.6802 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 45% | 0.7143 | 0.8240 | 0.8242 | +0.0% | 0% | 42% | 0% |
