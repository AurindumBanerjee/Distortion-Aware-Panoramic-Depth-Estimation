# Distortion study: da360_holo_in

model `da360` · 40 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0561, polar >= 60 deg 0.0457

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0653 | 0.0504 | 45% |
| blind lens-gain matching across the stitch lines | 0.0572 | 0.0460 | 30% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0571 | 0.0449 | 40% |
| non-local-means denoising | 0.0779 | 0.0593 | 80% |
| bilateral smoothing (deblocking) | 0.0593 | 0.0455 | 75% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.0637 | 0.0465 |  |  |  |
| re-level, known tilt (IMU) | 0.0610 | 0.0444 |  | 75% | 60% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 13.8 deg) | 0.0631 | 0.0498 |  | 47% | 52% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 | 0.0837 |  |  |
| degraded, no mitigation | 0.0570 | 0.0486 | 0.0906 |  |  |
| inpaint on the ERP grid | 0.0579 | 0.0490 | 0.1095 | -57% | 42% |
| inpaint in a polar tangent view | 0.0563 | 0.0439 | 0.0894 | 18% | 48% |
| tangent inpaint + floor / ceiling plane fill | 0.0563 | 0.0443 | 0.0894 | 18% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 | 0.0458 |  |  |
| degraded, no mitigation | 0.0667 | 0.0670 | 0.0676 |  |  |
| inpaint on the ERP grid | 0.0992 | 0.0994 | 0.0993 | -78% | 15% |
| inpaint in a polar tangent view | 0.0904 | 0.0963 | 0.0864 | -76% | 32% |
| tangent inpaint + floor / ceiling plane fill | 0.0907 | 0.0894 | 0.0852 | -56% | 32% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.0573 | 0.0469 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0588 | 0.0485 |  | 22% | 42% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 | 0.0583 |  |  |
| degraded, no mitigation | 0.0633 | 0.0492 | 0.0583 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1683 | 0.1278 | 0.2698 | -1282% | 2% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.0590 | 0.0418 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0606 | 0.0472 |  | 79% | 42% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.0750 | 0.0516 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0669 | 0.0535 |  | 44% | 57% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.0738 | 0.0578 |  |  |  |
| non-local-means denoising | 0.0824 | 0.0591 |  | -9% | 40% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.1893 | 0.1144 |  |  |  |
| bilateral smoothing (deblocking) | 0.1732 | 0.1190 |  | 7% | 60% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0561 | 0.0457 |  |  |  |
| degraded, no mitigation | 0.0792 | 0.0611 |  |  |  |
