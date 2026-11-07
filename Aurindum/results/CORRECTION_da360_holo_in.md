# Capture-aware correction, end to end: da360_holo_in

model `da360` · 40 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.0561 | 0.0561 | 0.0561 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.0561 | 0.0637 | 0.0637 | +0.0% | 0% | 0% | 0% |
| nadir | 100% | 0.0837 | 0.0906 | 0.0906 | +0.0% | 0% | 0% | 0% |
| vfov | 100% | 0.0458 | 0.0676 | 0.0676 | +0.0% | 0% | 0% | 0% |
| yawblur | 100% | 0.0561 | 0.0750 | 0.0669 | -3.2% | 57% | 38% | 44% |
| jpeg | 100% | 0.0561 | 0.1893 | 0.1893 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 28% | 0.0837 | 0.1680 | 0.1680 | +0.0% | 0% | 0% | 0% |
