# Capture-aware correction, end to end: da2_stanford

model `da2` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"nadir": "inpaint_erp", "vfov": "inpaint_erp"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.0692 | 0.0692 | 0.0622 | -7.1% | 79% | 19% | n/a |
| tilt | 100% | 0.0692 | 0.0988 | 0.0988 | +0.0% | 0% | 0% | 0% |
| nadir | 0% | 0.0460 | 0.1769 | 0.0365 | -78.8% | 100% | 0% | 107% |
| vfov | 100% | 0.0671 | 0.0958 | 0.0649 | -25.9% | 93% | 7% | 89% |
| yawblur | 0% | 0.0692 | 0.0710 | 0.0692 | -2.3% | 56% | 41% | -2% |
| jpeg | 0% | 0.0692 | 0.0761 | 0.0894 | +8.7% | 32% | 68% | -29% |
| nadir+jpeg | 0% | 0.0460 | 0.1568 | 0.1474 | +2.9% | 45% | 54% | -3% |
