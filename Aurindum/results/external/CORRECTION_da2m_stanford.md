# Capture-aware correction, end to end: da2m_stanford

model `da2` · 373 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "inpaint_tangent", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.0671 | 0.0671 | 0.0630 | -6.1% | 76% | 22% | n/a |
| tilt | 100% | 0.0671 | 0.0949 | 0.0680 | -26.7% | 91% | 8% | 97% |
| nadir | 0% | 0.0458 | 0.1334 | 0.0377 | -71.2% | 99% | 1% | 108% |
| vfov | 100% | 0.0631 | 0.0924 | 0.0683 | -23.7% | 79% | 20% | 86% |
| yawblur | 0% | 0.0671 | 0.0712 | 0.0682 | -6.1% | 65% | 31% | 57% |
| jpeg | 0% | 0.0671 | 0.0751 | 0.0968 | +19.5% | 27% | 72% | -47% |
| nadir+jpeg | 0% | 0.0458 | 0.1351 | 0.1144 | -0.1% | 50% | 45% | 1% |
