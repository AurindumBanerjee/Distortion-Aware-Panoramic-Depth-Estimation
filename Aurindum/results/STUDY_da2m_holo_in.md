# Distortion study: da2m_holo_in

model `da2` · 40 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1216, polar >= 60 deg 0.1309

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1011 | 0.1069 | 32% |
| blind lens-gain matching across the stitch lines | 0.1242 | 0.1342 | 38% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1266 | 0.1294 | 40% |
| non-local-means denoising | 0.2210 | 0.2294 | 92% |
| bilateral smoothing (deblocking) | 0.1222 | 0.1367 | 75% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.1534 | 0.1453 |  |  |  |
| re-level, known tilt (IMU) | 0.1227 | 0.1400 |  | 92% | 72% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 12.6 deg) | 0.1192 | 0.1159 |  | 62% | 75% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 | 0.1459 |  |  |
| degraded, no mitigation | 0.1306 | 0.1324 | 0.1739 |  |  |
| inpaint on the ERP grid | 0.1143 | 0.1182 | 0.1439 | 93% | 68% |
| inpaint in a polar tangent view | 0.1210 | 0.1243 | 0.1629 | 86% | 55% |
| tangent inpaint + floor / ceiling plane fill | 0.1210 | 0.1243 | 0.1629 | 85% | 55% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 | 0.1294 |  |  |
| degraded, no mitigation | 0.1760 | 0.2254 | 0.2243 |  |  |
| inpaint on the ERP grid | 0.1451 | 0.1422 | 0.1442 | 67% | 88% |
| inpaint in a polar tangent view | 0.1449 | 0.1617 | 0.1650 | 71% | 78% |
| tangent inpaint + floor / ceiling plane fill | 0.1462 | 0.1455 | 0.1457 | 72% | 78% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.1201 | 0.1296 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1241 | 0.1372 |  | 45% | 42% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 | 0.1159 |  |  |
| degraded, no mitigation | 0.1213 | 0.1365 | 0.1211 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1315 | 0.1295 | 0.1423 | -223% | 35% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.1312 | 0.1279 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1260 | 0.1325 |  | 72% | 55% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.1499 | 0.1544 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1436 | 0.1649 |  | 18% | 48% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.1644 | 0.1635 |  |  |  |
| non-local-means denoising | 0.2350 | 0.2482 |  | -145% | 22% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.2216 | 0.2516 |  |  |  |
| bilateral smoothing (deblocking) | 0.2177 | 0.2306 |  | 6% | 60% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1216 | 0.1309 |  |  |  |
| degraded, no mitigation | 0.1899 | 0.1734 |  |  |  |
