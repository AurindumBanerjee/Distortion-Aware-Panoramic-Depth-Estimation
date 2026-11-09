# Distortion study: s100_da360_s3

model `da360` · 100 frames · 66 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0147, polar >= 60 deg 0.0108

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0179 | 0.0133 | 67% |
| blind lens-gain matching across the stitch lines | 0.0150 | 0.0109 | 36% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0155 | 0.0114 | 42% |
| non-local-means denoising | 0.0374 | 0.0254 | 97% |
| bilateral smoothing (deblocking) | 0.0181 | 0.0142 | 82% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0182 | 0.0147 |  |  |  |
| re-level, known tilt (IMU) | 0.0170 | 0.0131 |  | 48% | 75% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 13.5 deg) | 0.0189 | 0.0146 |  | 0% | 44% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 | 0.0138 |  |  |
| degraded, no mitigation | 0.0175 | 0.0158 | 0.0225 |  |  |
| inpaint on the ERP grid | 0.0239 | 0.0292 | 0.0465 | -223% | 5% |
| inpaint in a polar tangent view | 0.0201 | 0.0206 | 0.0329 | -106% | 13% |
| tangent inpaint + floor / ceiling plane fill | 0.0206 | 0.0242 | 0.0365 | -128% | 13% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 | 0.0110 |  |  |
| degraded, no mitigation | 0.0461 | 0.0522 | 0.0515 |  |  |
| inpaint on the ERP grid | 0.1344 | 0.1689 | 0.1601 | -131% | 8% |
| inpaint in a polar tangent view | 0.1622 | 0.1965 | 0.1878 | -277% | 5% |
| tangent inpaint + floor / ceiling plane fill | 0.1668 | 0.2053 | 0.1964 | -283% | 3% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0153 | 0.0113 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0153 | 0.0110 |  | 49% | 49% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 | 0.0130 |  |  |
| degraded, no mitigation | 0.0165 | 0.0128 | 0.0145 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1031 | 0.0830 | 0.2135 | -4113% | 3% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0155 | 0.0112 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0153 | 0.0111 |  | 61% | 56% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0264 | 0.0178 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0201 | 0.0144 |  | 60% | 82% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0308 | 0.0189 |  |  |  |
| non-local-means denoising | 0.0399 | 0.0273 |  | -86% | 17% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0559 | 0.0386 |  |  |  |
| bilateral smoothing (deblocking) | 0.0515 | 0.0365 |  | 6% | 68% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0147 | 0.0108 |  |  |  |
| degraded, no mitigation | 0.0322 | 0.0240 |  |  |  |
