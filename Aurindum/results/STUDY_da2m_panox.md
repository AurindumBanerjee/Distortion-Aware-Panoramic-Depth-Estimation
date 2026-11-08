# Distortion study: da2m_panox

model `da2` · 40 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1040, polar >= 60 deg 0.0697

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1031 | 0.0787 | 50% |
| blind lens-gain matching across the stitch lines | 0.1037 | 0.0708 | 42% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1075 | 0.0709 | 10% |
| non-local-means denoising | 0.1540 | 0.1043 | 85% |
| bilateral smoothing (deblocking) | 0.1100 | 0.0941 | 70% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1498 | 0.1083 |  |  |  |
| re-level, known tilt (IMU) | 0.1199 | 0.0816 |  | 88% | 85% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.2 deg) | 0.1415 | 0.0857 |  | 59% | 75% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 | 0.0754 |  |  |
| degraded, no mitigation | 0.1482 | 0.1720 | 0.2502 |  |  |
| inpaint on the ERP grid | 0.1175 | 0.0830 | 0.1053 | 73% | 92% |
| inpaint in a polar tangent view | 0.1071 | 0.0844 | 0.0856 | 89% | 88% |
| tangent inpaint + floor / ceiling plane fill | 0.1042 | 0.0726 | 0.0709 | 97% | 90% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 | 0.0736 |  |  |
| degraded, no mitigation | 0.1976 | 0.1417 | 0.1484 |  |  |
| inpaint on the ERP grid | 0.1594 | 0.1066 | 0.1342 | 3% | 48% |
| inpaint in a polar tangent view | 0.2236 | 0.1495 | 0.1688 | -39% | 38% |
| tangent inpaint + floor / ceiling plane fill | 0.2103 | 0.1385 | 0.1392 | 29% | 52% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1021 | 0.0650 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1040 | 0.0709 |  | 41% | 40% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 | 0.0942 |  |  |
| degraded, no mitigation | 0.1090 | 0.0718 | 0.1011 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1055 | 0.0697 | 0.1128 | -139% | 22% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1075 | 0.0695 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1072 | 0.0681 |  | 45% | 42% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1254 | 0.0828 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1107 | 0.0879 |  | 54% | 72% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1395 | 0.0904 |  |  |  |
| non-local-means denoising | 0.1392 | 0.1096 |  | -7% | 38% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1764 | 0.1045 |  |  |  |
| bilateral smoothing (deblocking) | 0.1691 | 0.1110 |  | 4% | 60% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1040 | 0.0697 |  |  |  |
| degraded, no mitigation | 0.1450 | 0.0942 |  |  |  |
