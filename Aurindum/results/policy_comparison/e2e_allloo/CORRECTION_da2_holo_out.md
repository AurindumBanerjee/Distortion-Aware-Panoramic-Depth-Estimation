# Capture-aware correction, end to end: da2_holo_out

model `da2` · 71 frames · policy chosen on holo_in, nyc, panox, s3, stanford (held out: holo_out): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.5434 | 0.5434 | 0.5434 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.5434 | 0.4512 | 0.5364 | +19.4% | 21% | 73% | 100% |
| nadir | 100% | 0.5687 | 0.6002 | 0.6000 | +0.5% | 44% | 48% | 20% |
| vfov | 100% | 0.5656 | 0.6027 | 0.5493 | -6.7% | 62% | 35% | 79% |
| yawblur | 100% | 0.5434 | 0.5696 | 0.5072 | -6.2% | 61% | 38% | 112% |
| jpeg | 100% | 0.5434 | 0.6102 | 0.6102 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 65% | 0.5687 | 0.5615 | 0.5615 | +0.0% | 38% | 27% | 0% |
