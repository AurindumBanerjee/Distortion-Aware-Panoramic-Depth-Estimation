# Capture-aware correction, end to end: dap_panox

model `dap` · 100 frames · policy chosen on holo_in, holo_out, s3 (held out: panox): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener", "jpeg": "bilateral"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2006 | 0.2006 | 0.2006 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2006 | 0.2672 | 0.1937 | -23.7% | 77% | 22% | 105% |
| nadir | 100% | 0.1391 | 0.3260 | 0.1529 | -20.4% | 81% | 17% | 85% |
| vfov | 100% | 0.1795 | 0.6670 | 0.3945 | -43.3% | 91% | 8% | 69% |
| yawblur | 100% | 0.2006 | 0.2715 | 0.1956 | -23.9% | 96% | 4% | 94% |
| jpeg | 100% | 0.2006 | 0.3795 | 0.3779 | -4.2% | 69% | 28% | 11% |
| nadir+jpeg | 100% | 0.1391 | 0.4706 | 0.3338 | -15.5% | 87% | 13% | 31% |
