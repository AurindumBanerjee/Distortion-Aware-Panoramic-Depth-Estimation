# Capture-aware correction, end to end: da2_panox

model `da2` · 40 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "nadir": "inpaint_erp", "vfov": "inpaint_erp", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.1619 | 0.1619 | 0.1619 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.1619 | 0.1979 | 0.1652 | -0.9% | 50% | 45% | 89% |
| nadir | 100% | 0.1325 | 0.3529 | 0.1764 | -45.6% | 70% | 30% | 83% |
| vfov | 100% | 0.1334 | 0.2885 | 0.2751 | -2.5% | 52% | 48% | -25% |
| yawblur | 100% | 0.1619 | 0.2071 | 0.2071 | +0.0% | 0% | 0% | 0% |
| jpeg | 100% | 0.1619 | 0.2465 | 0.2741 | +6.2% | 25% | 72% | -13% |
| nadir+jpeg | 68% | 0.1325 | 0.5393 | 0.4912 | -1.7% | 50% | 48% | 13% |
