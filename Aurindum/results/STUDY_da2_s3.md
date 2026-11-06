# Distortion study: da2_s3

model `da2` · 40 frames · 33 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0430, polar >= 60 deg 0.0439

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0547 | 0.0494 | 72% |
| blind lens-gain matching across the stitch lines | 0.0429 | 0.0439 | 20% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0418 | 0.0437 | 22% |
| non-local-means denoising | 0.0786 | 0.0595 | 88% |
| bilateral smoothing (deblocking) | 0.0472 | 0.0429 | 50% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0773 | 0.0743 |  |  |  |
| re-level, known tilt (IMU) | 0.0477 | 0.0416 |  | 99% | 92% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.1 deg) | 0.0676 | 0.0588 |  | 65% | 68% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 | 0.0324 |  |  |
| degraded, no mitigation | 0.1064 | 0.1404 | 0.1821 |  |  |
| inpaint on the ERP grid | 0.0444 | 0.0494 | 0.0563 | 84% | 95% |
| inpaint in a polar tangent view | 0.0437 | 0.0453 | 0.0524 | 90% | 95% |
| tangent inpaint + floor / ceiling plane fill | 0.0461 | 0.0455 | 0.0524 | 92% | 95% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 | 0.0425 |  |  |
| degraded, no mitigation | 0.1163 | 0.1721 | 0.1632 |  |  |
| inpaint on the ERP grid | 0.0812 | 0.0820 | 0.0960 | 63% | 95% |
| inpaint in a polar tangent view | 0.1176 | 0.1664 | 0.1626 | -23% | 50% |
| tangent inpaint + floor / ceiling plane fill | 0.1173 | 0.1650 | 0.1605 | -23% | 50% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0462 | 0.0450 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0447 | 0.0452 |  | 60% | 65% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 | 0.0452 |  |  |
| degraded, no mitigation | 0.0421 | 0.0422 | 0.0472 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0419 | 0.0415 | 0.0526 | -175% | 22% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0459 | 0.0397 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0435 | 0.0442 |  | 36% | 22% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0549 | 0.0449 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0494 | 0.0471 |  | 51% | 60% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0737 | 0.0629 |  |  |  |
| non-local-means denoising | 0.0917 | 0.0652 |  | -47% | 38% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0845 | 0.0820 |  |  |  |
| bilateral smoothing (deblocking) | 0.0784 | 0.0734 |  | 6% | 60% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0430 | 0.0439 |  |  |  |
| degraded, no mitigation | 0.0691 | 0.0570 |  |  |  |
