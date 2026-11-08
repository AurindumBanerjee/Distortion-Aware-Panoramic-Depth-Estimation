# Distortion study: sd_da2_stanford

model `da2` · 150 frames · 63 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0698, polar >= 60 deg 0.0769

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0707 | 0.0762 | 46% |
| blind lens-gain matching across the stitch lines | 0.0697 | 0.0762 | 15% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0720 | 0.0793 | 63% |
| non-local-means denoising | 0.1467 | 0.1693 | 98% |
| bilateral smoothing (deblocking) | 0.0657 | 0.0788 | 45% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.1000 | 0.0923 |  |  |  |
| re-level, known tilt (IMU) | 0.0678 | 0.0794 |  | 98% | 93% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 4.0 deg) | 0.0802 | 0.0845 |  | 69% | 73% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 | 0.0470 |  |  |
| degraded, no mitigation | 0.1048 | 0.1353 | 0.1733 |  |  |
| inpaint on the ERP grid | 0.0640 | 0.0712 | 0.0360 | 107% | 98% |
| inpaint in a polar tangent view | 0.0609 | 0.0676 | 0.0279 | 116% | 98% |
| tangent inpaint + floor / ceiling plane fill | 0.0623 | 0.0715 | 0.0307 | 116% | 97% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 | 0.0683 |  |  |
| degraded, no mitigation | 0.1055 | 0.1072 | 0.1089 |  |  |
| inpaint on the ERP grid | 0.0710 | 0.0723 | 0.0704 | 81% | 87% |
| inpaint in a polar tangent view | 0.1030 | 0.1360 | 0.1384 | -32% | 37% |
| tangent inpaint + floor / ceiling plane fill | 0.1023 | 0.1360 | 0.1362 | -33% | 37% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.0702 | 0.0763 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0697 | 0.0764 |  | 86% | 72% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 | 0.0698 |  |  |
| degraded, no mitigation | 0.0698 | 0.0730 | 0.0672 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0679 | 0.0719 | 0.0768 | -189% | 18% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.0695 | 0.0740 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0720 | 0.0796 |  | 155% | 33% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.0746 | 0.0830 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0759 | 0.0922 |  | 21% | 52% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.0775 | 0.0884 |  |  |  |
| non-local-means denoising | 0.1096 | 0.1159 |  | -152% | 19% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.0833 | 0.0883 |  |  |  |
| bilateral smoothing (deblocking) | 0.0821 | 0.0919 |  | 19% | 56% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0698 | 0.0769 |  |  |  |
| degraded, no mitigation | 0.0720 | 0.0779 |  |  |  |
