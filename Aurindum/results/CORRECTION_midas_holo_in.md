# Capture-aware correction, end to end: midas_holo_in

model `midas_dpt_hybrid_384` · 40 frames · policy chosen on holo_out, panox, s3 (held out: holo_in): `{"tilt": "relevel_known", "nadir": "plane_fill", "vfov": "inpaint_tangent", "yawblur": "wiener"}`

Caps are detected from the image; tilt / shake come as IMU / gyro metadata; JPEG as a file flag. Metric: AbsRel on the occluded region for cap faults, else the whole panorama.

| scenario | cap detection correct | clean | uncorrected | corrected | change | frames improved | frames worse >1% | recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 100% | 0.2787 | 0.2787 | 0.2787 | +0.0% | 0% | 0% | n/a |
| tilt | 100% | 0.2787 | 0.3185 | 0.2871 | -7.3% | 72% | 28% | 107% |
| nadir | 100% | 0.4111 | 0.4823 | 0.4673 | +0.1% | 48% | 40% | 6% |
| vfov | 100% | 0.2657 | 0.2934 | 0.2923 | +2.9% | 38% | 60% | -7% |
| yawblur | 100% | 0.2787 | 0.3012 | 0.2817 | -6.4% | 70% | 25% | 97% |
| jpeg | 100% | 0.2787 | 0.3509 | 0.3509 | +0.0% | 0% | 0% | 0% |
| nadir+jpeg | 28% | 0.4111 | 0.3527 | 0.3747 | +0.0% | 12% | 15% | 0% |
