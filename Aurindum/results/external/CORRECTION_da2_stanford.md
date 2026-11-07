# Capture-aware correction, end to end: da2_stanford

model `da2` · 40 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: stanford): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0% | 0.0738 | 0.0738 | 0.0672 | -5.5% | 70% | 30% | n/a |
| tilt | 100% | 0.0738 | 0.1000 | 0.0706 | -27.2% | 90% | 10% | 95% |
| nadir | 0% | 0.0476 | 0.1791 | 0.0380 | -78.5% | 100% | 0% | 108% |
| vfov | 100% | 0.0708 | 0.0955 | 0.0675 | -29.1% | 78% | 22% | 85% |
| yawblur | 0% | 0.0738 | 0.0774 | 0.0771 | -3.8% | 65% | 30% | 43% |
| jpeg | 0% | 0.0738 | 0.0785 | 0.0861 | +0.8% | 45% | 50% | -4% |
| nadir+jpeg | 0% | 0.0476 | 0.1702 | 0.1445 | +1.6% | 48% | 52% | -2% |
