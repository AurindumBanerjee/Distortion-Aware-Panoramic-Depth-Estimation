# Distortion study: da360_panox

model `da360` · 40 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0644, polar >= 60 deg 0.0284

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0627 | 0.0283 | 38% |
| blind lens-gain matching across the stitch lines | 0.0649 | 0.0317 | 48% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0665 | 0.0288 | 20% |
| non-local-means denoising | 0.0973 | 0.0434 | 90% |
| bilateral smoothing (deblocking) | 0.0735 | 0.0380 | 82% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0681 | 0.0327 |  |  |  |
| re-level, known tilt (IMU) | 0.0696 | 0.0320 |  | 23% | 40% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 2.3 deg) | 0.0679 | 0.0340 |  | 1% | 45% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 | 0.0120 |  |  |
| degraded, no mitigation | 0.0691 | 0.0319 | 0.0132 |  |  |
| inpaint on the ERP grid | 0.0669 | 0.0371 | 0.0119 | 12% | 57% |
| inpaint in a polar tangent view | 0.0683 | 0.0318 | 0.0127 | 6% | 52% |
| tangent inpaint + floor / ceiling plane fill | 0.0683 | 0.0356 | 0.0120 | 28% | 52% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 | 0.0304 |  |  |
| degraded, no mitigation | 0.0787 | 0.0406 | 0.0517 |  |  |
| inpaint on the ERP grid | 0.1031 | 0.0598 | 0.0650 | -69% | 30% |
| inpaint in a polar tangent view | 0.1148 | 0.0524 | 0.0635 | -74% | 32% |
| tangent inpaint + floor / ceiling plane fill | 0.0939 | 0.0555 | 0.0559 | -26% | 25% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0645 | 0.0319 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0646 | 0.0353 |  | 44% | 52% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 | 0.0710 |  |  |
| degraded, no mitigation | 0.0626 | 0.0273 | 0.0646 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2834 | 0.2456 | 0.3501 | -1235% | 2% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0670 | 0.0312 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0644 | 0.0310 |  | 47% | 55% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.1080 | 0.0534 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0753 | 0.0387 |  | 65% | 75% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.1183 | 0.0468 |  |  |  |
| non-local-means denoising | 0.1300 | 0.0772 |  | -33% | 30% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.1523 | 0.0623 |  |  |  |
| bilateral smoothing (deblocking) | 0.1498 | 0.0573 |  | -5% | 48% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0644 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.1189 | 0.0534 |  |  |  |
