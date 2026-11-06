# Distortion study: da360_s3

model `da360` · 40 frames · 33 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0139, polar >= 60 deg 0.0102

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0162 | 0.0125 | 70% |
| blind lens-gain matching across the stitch lines | 0.0144 | 0.0103 | 40% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0143 | 0.0109 | 50% |
| non-local-means denoising | 0.0342 | 0.0231 | 98% |
| bilateral smoothing (deblocking) | 0.0166 | 0.0117 | 85% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0169 | 0.0124 |  |  |  |
| re-level, known tilt (IMU) | 0.0159 | 0.0113 |  | 39% | 70% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 8.6 deg) | 0.0168 | 0.0132 |  | 0% | 42% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 | 0.0134 |  |  |
| degraded, no mitigation | 0.0162 | 0.0136 | 0.0203 |  |  |
| inpaint on the ERP grid | 0.0202 | 0.0215 | 0.0324 | -221% | 8% |
| inpaint in a polar tangent view | 0.0184 | 0.0183 | 0.0303 | -102% | 12% |
| tangent inpaint + floor / ceiling plane fill | 0.0190 | 0.0189 | 0.0319 | -102% | 15% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 | 0.0104 |  |  |
| degraded, no mitigation | 0.0323 | 0.0422 | 0.0429 |  |  |
| inpaint on the ERP grid | 0.1089 | 0.1503 | 0.1391 | -109% | 10% |
| inpaint in a polar tangent view | 0.1253 | 0.1484 | 0.1420 | -123% | 2% |
| tangent inpaint + floor / ceiling plane fill | 0.1191 | 0.1532 | 0.1463 | -145% | 5% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0149 | 0.0104 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0148 | 0.0100 |  | 61% | 42% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 | 0.0121 |  |  |
| degraded, no mitigation | 0.0162 | 0.0127 | 0.0134 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1068 | 0.0799 | 0.2321 | -7315% | 2% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0151 | 0.0111 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0143 | 0.0114 |  | 43% | 65% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0271 | 0.0203 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0190 | 0.0147 |  | 57% | 85% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0248 | 0.0163 |  |  |  |
| non-local-means denoising | 0.0331 | 0.0217 |  | -54% | 15% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0501 | 0.0328 |  |  |  |
| bilateral smoothing (deblocking) | 0.0490 | 0.0320 |  | 3% | 65% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0139 | 0.0102 |  |  |  |
| degraded, no mitigation | 0.0289 | 0.0215 |  |  |  |
