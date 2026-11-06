# Distortion study: da2_holo_in

model `da2` · 40 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1240, polar >= 60 deg 0.1483

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1123 | 0.1481 | 42% |
| blind lens-gain matching across the stitch lines | 0.1268 | 0.1464 | 38% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1291 | 0.1547 | 42% |
| non-local-means denoising | 0.2461 | 0.2892 | 95% |
| bilateral smoothing (deblocking) | 0.1394 | 0.1673 | 80% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.1529 | 0.1578 |  |  |  |
| re-level, known tilt (IMU) | 0.1312 | 0.1654 |  | 90% | 75% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 12.6 deg) | 0.1371 | 0.1786 |  | 55% | 70% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 | 0.1286 |  |  |
| degraded, no mitigation | 0.1359 | 0.1703 | 0.1367 |  |  |
| inpaint on the ERP grid | 0.1184 | 0.1432 | 0.1356 | 76% | 62% |
| inpaint in a polar tangent view | 0.1204 | 0.1504 | 0.1473 | 77% | 57% |
| tangent inpaint + floor / ceiling plane fill | 0.1204 | 0.1504 | 0.1473 | 77% | 57% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 | 0.1427 |  |  |
| degraded, no mitigation | 0.1666 | 0.2627 | 0.2293 |  |  |
| inpaint on the ERP grid | 0.1478 | 0.1869 | 0.1799 | 62% | 80% |
| inpaint in a polar tangent view | 0.1403 | 0.1842 | 0.1814 | 69% | 68% |
| tangent inpaint + floor / ceiling plane fill | 0.1403 | 0.1721 | 0.1672 | 80% | 70% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.1213 | 0.1467 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1259 | 0.1503 |  | 40% | 45% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 | 0.1255 |  |  |
| degraded, no mitigation | 0.1245 | 0.1530 | 0.1288 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1367 | 0.1503 | 0.1545 | -97% | 25% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.1300 | 0.1617 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1284 | 0.1618 |  | 62% | 57% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.1757 | 0.1980 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1643 | 0.2007 |  | 13% | 52% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.1829 | 0.2314 |  |  |  |
| non-local-means denoising | 0.2626 | 0.3171 |  | -128% | 20% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.2623 | 0.2683 |  |  |  |
| bilateral smoothing (deblocking) | 0.2599 | 0.2754 |  | 6% | 60% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1240 | 0.1483 |  |  |  |
| degraded, no mitigation | 0.2090 | 0.2769 |  |  |  |
