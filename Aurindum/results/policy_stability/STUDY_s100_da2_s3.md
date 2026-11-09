# Distortion study: s100_da2_s3

model `da2` · 100 frames · 66 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0525, polar >= 60 deg 0.0458

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0684 | 0.0619 | 74% |
| blind lens-gain matching across the stitch lines | 0.0515 | 0.0458 | 24% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0511 | 0.0477 | 16% |
| non-local-means denoising | 0.0842 | 0.0669 | 88% |
| bilateral smoothing (deblocking) | 0.0549 | 0.0486 | 50% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.0891 | 0.0821 |  |  |  |
| re-level, known tilt (IMU) | 0.0540 | 0.0491 |  | 97% | 90% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.9 deg) | 0.0829 | 0.0712 |  | 50% | 67% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 | 0.0333 |  |  |
| degraded, no mitigation | 0.1090 | 0.1387 | 0.1765 |  |  |
| inpaint on the ERP grid | 0.0561 | 0.0578 | 0.0733 | 78% | 85% |
| inpaint in a polar tangent view | 0.0536 | 0.0545 | 0.0623 | 85% | 85% |
| tangent inpaint + floor / ceiling plane fill | 0.0543 | 0.0553 | 0.0615 | 85% | 85% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 | 0.0472 |  |  |
| degraded, no mitigation | 0.1273 | 0.1821 | 0.1727 |  |  |
| inpaint on the ERP grid | 0.0909 | 0.0940 | 0.0980 | 63% | 92% |
| inpaint in a polar tangent view | 0.1529 | 0.2455 | 0.2341 | -33% | 38% |
| tangent inpaint + floor / ceiling plane fill | 0.1529 | 0.2438 | 0.2339 | -28% | 39% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.0532 | 0.0480 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0521 | 0.0467 |  | 25% | 60% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 | 0.0488 |  |  |
| degraded, no mitigation | 0.0491 | 0.0460 | 0.0497 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0508 | 0.0454 | 0.0570 | -165% | 22% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.0509 | 0.0420 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0520 | 0.0488 |  | -13% | 27% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.0702 | 0.0547 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0596 | 0.0529 |  | 44% | 66% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.0850 | 0.0811 |  |  |  |
| non-local-means denoising | 0.0934 | 0.0770 |  | -23% | 38% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.1003 | 0.0882 |  |  |  |
| bilateral smoothing (deblocking) | 0.0963 | 0.0809 |  | 7% | 62% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0525 | 0.0458 |  |  |  |
| degraded, no mitigation | 0.0879 | 0.0662 |  |  |  |
