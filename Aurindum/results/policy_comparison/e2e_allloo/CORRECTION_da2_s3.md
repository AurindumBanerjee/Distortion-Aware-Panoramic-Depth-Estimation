# Capture-aware correction, end to end: da2_s3

model `da2` · 100 frames · policy chosen on holo_in, holo_out, nyc, panox, stanford (held out: s3): `{"nadir": "inpaint_erp", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 99% | 0.0525 | 0.0525 | 0.0525 | +0.0% | 0% | 1% | n/a |
| tilt | 100% | 0.0525 | 0.0891 | 0.0891 | +0.0% | 0% | 0% | 0% |
| nadir | 99% | 0.0333 | 0.1765 | 0.0733 | -58.5% | 84% | 16% | 78% |
| vfov | 100% | 0.0472 | 0.1727 | 0.0980 | -37.4% | 92% | 7% | 63% |
| yawblur | 99% | 0.0525 | 0.0702 | 0.0596 | -4.6% | 64% | 32% | 44% |
| jpeg | 100% | 0.0525 | 0.1003 | 0.1003 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 63% | 0.0333 | 0.1260 | 0.1474 | +0.0% | 24% | 39% | 0% |
