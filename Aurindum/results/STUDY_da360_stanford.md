# Distortion study: da360_stanford

model `da360` · 40 frames · 28 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1448, polar >= 60 deg 0.1474

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1551 | 0.1526 | 40% |
| blind lens-gain matching across the stitch lines | 0.1461 | 0.1440 | 50% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1394 | 0.1343 | 50% |
| non-local-means denoising | 0.1349 | 0.1303 | 52% |
| bilateral smoothing (deblocking) | 0.0614 | 0.0545 | 5% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.1641 | 0.1385 |  |  |  |
| re-level, known tilt (IMU) | 0.1303 | 0.1390 |  | 100% | 70% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.0 deg) | 0.1576 | 0.1428 |  | 0% | 52% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 | 0.0766 |  |  |
| degraded, no mitigation | 0.1219 | 0.1418 | 0.0668 |  |  |
| inpaint on the ERP grid | 0.1221 | 0.1400 | 0.0685 | 19% | 70% |
| inpaint in a polar tangent view | 0.1256 | 0.1439 | 0.0689 | 6% | 62% |
| tangent inpaint + floor / ceiling plane fill | 0.1282 | 0.1411 | 0.0740 | 9% | 62% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 | 0.1349 |  |  |
| degraded, no mitigation | 0.0640 | 0.0777 | 0.0754 |  |  |
| inpaint on the ERP grid | 0.1168 | 0.1009 | 0.1022 | -651% | 35% |
| inpaint in a polar tangent view | 0.1625 | 0.1053 | 0.1161 | -647% | 30% |
| tangent inpaint + floor / ceiling plane fill | 0.1625 | 0.1053 | 0.1161 | -656% | 30% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.1516 | 0.1458 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1474 | 0.1425 |  | 80% | 68% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 | 0.1431 |  |  |
| degraded, no mitigation | 0.1486 | 0.1443 | 0.1449 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1969 | 0.1122 | 0.2970 | -1761% | 0% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.1595 | 0.1493 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1544 | 0.1385 |  | 76% | 60% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.1682 | 0.1412 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1506 | 0.1411 |  | 53% | 82% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.1726 | 0.1340 |  |  |  |
| non-local-means denoising | 0.1805 | 0.1297 |  | -10% | 40% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.1116 | 0.0959 |  |  |  |
| bilateral smoothing (deblocking) | 0.1082 | 0.0758 |  | 16% | 68% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1448 | 0.1474 |  |  |  |
| degraded, no mitigation | 0.0813 | 0.0691 |  |  |  |
