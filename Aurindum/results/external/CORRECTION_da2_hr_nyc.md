# Capture-aware correction, end to end: da2_hr_nyc

model `da2` · 100 frames · policy chosen on holo_in, holo_out, panox, s3 (held out: nyc): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_erp", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.5888 | 0.5888 | 0.5888 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.5888 | 0.4934 | 0.5990 | +19.3% | 9% | 90% | 27% |
| nadir | 100% | 0.6710 | 0.6661 | 0.7040 | +6.6% | 8% | 92% | -61% |
| vfov | 100% | 0.6281 | 0.7378 | 0.6955 | -3.8% | 63% | 33% | 50% |
| yawblur | 100% | 0.5888 | 0.6101 | 0.6045 | -2.9% | 63% | 27% | 66% |
| jpeg | 100% | 0.5888 | 0.6653 | 0.6653 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 88% | 0.6710 | 0.7608 | 0.7339 | +1.1% | 30% | 50% | 1% |
