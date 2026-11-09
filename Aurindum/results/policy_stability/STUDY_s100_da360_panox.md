# Distortion study: s100_da360_panox

model `da360` · 100 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0664, polar >= 60 deg 0.0283

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0665 | 0.0304 | 48% |
| blind lens-gain matching across the stitch lines | 0.0683 | 0.0309 | 40% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0667 | 0.0301 | 14% |
| non-local-means denoising | 0.0919 | 0.0379 | 90% |
| bilateral smoothing (deblocking) | 0.0753 | 0.0339 | 75% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.0680 | 0.0319 |  |  |  |
| re-level, known tilt (IMU) | 0.0721 | 0.0317 |  | 21% | 47% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 2.8 deg) | 0.0699 | 0.0335 |  | 12% | 51% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 | 0.0110 |  |  |
| degraded, no mitigation | 0.0707 | 0.0327 | 0.0133 |  |  |
| inpaint on the ERP grid | 0.0684 | 0.0368 | 0.0130 | 40% | 60% |
| inpaint in a polar tangent view | 0.0682 | 0.0333 | 0.0128 | 25% | 57% |
| tangent inpaint + floor / ceiling plane fill | 0.0684 | 0.0373 | 0.0124 | -11% | 47% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 | 0.0333 |  |  |
| degraded, no mitigation | 0.0759 | 0.0413 | 0.0502 |  |  |
| inpaint on the ERP grid | 0.1143 | 0.0514 | 0.0583 | -46% | 36% |
| inpaint in a polar tangent view | 0.1060 | 0.0455 | 0.0634 | -70% | 37% |
| tangent inpaint + floor / ceiling plane fill | 0.0937 | 0.0471 | 0.0540 | -32% | 32% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.0688 | 0.0296 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0675 | 0.0320 |  | 37% | 56% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 | 0.0658 |  |  |
| degraded, no mitigation | 0.0682 | 0.0311 | 0.0633 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2716 | 0.2310 | 0.3357 | -2010% | 3% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.0722 | 0.0312 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0701 | 0.0325 |  | 54% | 53% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.1065 | 0.0567 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0776 | 0.0387 |  | 70% | 76% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.1141 | 0.0401 |  |  |  |
| non-local-means denoising | 0.1251 | 0.0554 |  | -18% | 35% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.1345 | 0.0591 |  |  |  |
| bilateral smoothing (deblocking) | 0.1403 | 0.0659 |  | -4% | 43% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0664 | 0.0283 |  |  |  |
| degraded, no mitigation | 0.1146 | 0.0514 |  |  |  |
