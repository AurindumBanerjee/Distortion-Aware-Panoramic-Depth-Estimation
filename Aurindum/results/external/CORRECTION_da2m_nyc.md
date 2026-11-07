# Capture-aware correction, end to end: da2m_nyc

model `da2` · 147 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2052 | 0.2052 | 0.2052 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2052 | 0.2824 | 0.2244 | -22.8% | 92% | 7% | 84% |
| nadir | 100% | 0.0689 | 0.1291 | 0.0749 | -26.0% | 56% | 44% | 87% |
| vfov | 100% | 0.1282 | 0.1964 | 0.2064 | -1.8% | 52% | 47% | 18% |
| yawblur | 100% | 0.2052 | 0.2326 | 0.2194 | -6.7% | 65% | 31% | 59% |
| jpeg | 100% | 0.2052 | 0.2833 | 0.2833 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 37% | 0.0689 | 0.1290 | 0.1473 | +0.0% | 15% | 22% | 0% |
