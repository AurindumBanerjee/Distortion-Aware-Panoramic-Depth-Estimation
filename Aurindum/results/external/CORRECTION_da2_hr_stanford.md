# Capture-aware correction, end to end: da2_hr_stanford

model `da2` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.0615 | 0.0615 | 0.0615 | +1.0% | 44% | 50% | n/a |
| tilt | 100% | 0.0615 | 0.0876 | 0.0612 | -30.4% | 91% | 9% | 100% |
| nadir | 0% | 0.0425 | 0.1585 | 0.0422 | -73.6% | 98% | 2% | 102% |
| vfov | 100% | 0.0670 | 0.1017 | 0.0683 | -26.6% | 89% | 11% | 86% |
| yawblur | 0% | 0.0615 | 0.0595 | 0.0622 | +2.3% | 37% | 58% | 28% |
| jpeg | 0% | 0.0615 | 0.0645 | 0.0695 | +5.9% | 38% | 60% | -43% |
| nadir+jpeg | 0% | 0.0425 | 0.1831 | 0.0299 | -83.0% | 94% | 6% | 112% |
