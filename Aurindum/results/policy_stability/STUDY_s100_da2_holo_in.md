# Distortion study: s100_da2_holo_in

model `da2` · 100 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1153, polar >= 60 deg 0.1417

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1095 | 0.1319 | 42% |
| blind lens-gain matching across the stitch lines | 0.1137 | 0.1465 | 34% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1181 | 0.1440 | 51% |
| non-local-means denoising | 0.2488 | 0.2686 | 96% |
| bilateral smoothing (deblocking) | 0.1293 | 0.1558 | 74% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.1585 | 0.1643 |  |  |  |
| re-level, known tilt (IMU) | 0.1181 | 0.1429 |  | 90% | 76% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 11.9 deg) | 0.1353 | 0.1436 |  | 89% | 69% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 | 0.1322 |  |  |
| degraded, no mitigation | 0.1244 | 0.1366 | 0.1560 |  |  |
| inpaint on the ERP grid | 0.1165 | 0.1396 | 0.1309 | 76% | 58% |
| inpaint in a polar tangent view | 0.1206 | 0.1449 | 0.1473 | 86% | 53% |
| tangent inpaint + floor / ceiling plane fill | 0.1200 | 0.1449 | 0.1473 | 85% | 52% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 | 0.1298 |  |  |
| degraded, no mitigation | 0.1576 | 0.2440 | 0.2177 |  |  |
| inpaint on the ERP grid | 0.1386 | 0.1679 | 0.1677 | 61% | 80% |
| inpaint in a polar tangent view | 0.1482 | 0.1936 | 0.1866 | 48% | 70% |
| tangent inpaint + floor / ceiling plane fill | 0.1474 | 0.1739 | 0.1728 | 54% | 72% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.1180 | 0.1433 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1131 | 0.1477 |  | 34% | 52% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 | 0.1194 |  |  |
| degraded, no mitigation | 0.1150 | 0.1458 | 0.1244 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1171 | 0.1430 | 0.1542 | -143% | 19% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.1196 | 0.1461 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1229 | 0.1515 |  | 38% | 49% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.1620 | 0.1837 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1527 | 0.1802 |  | 11% | 54% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.1746 | 0.1920 |  |  |  |
| non-local-means denoising | 0.2754 | 0.2866 |  | -148% | 15% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.2370 | 0.2545 |  |  |  |
| bilateral smoothing (deblocking) | 0.2457 | 0.2739 |  | 1% | 51% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1153 | 0.1417 |  |  |  |
| degraded, no mitigation | 0.2215 | 0.2364 |  |  |  |
