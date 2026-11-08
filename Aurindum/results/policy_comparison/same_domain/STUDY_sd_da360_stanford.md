# Distortion study: sd_da360_stanford

model `da360` · 150 frames · 63 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1502, polar >= 60 deg 0.1588

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1675 | 0.1565 | 45% |
| blind lens-gain matching across the stitch lines | 0.1569 | 0.1663 | 41% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1580 | 0.1524 | 53% |
| non-local-means denoising | 0.1702 | 0.1580 | 54% |
| bilateral smoothing (deblocking) | 0.0687 | 0.0680 | 7% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1740 | 0.1637 |  |  |  |
| re-level, known tilt (IMU) | 0.1472 | 0.1481 |  | 107% | 84% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 7.2 deg) | 0.1756 | 0.1622 |  | 0% | 51% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 | 0.0911 |  |  |
| degraded, no mitigation | 0.1310 | 0.1492 | 0.0742 |  |  |
| inpaint on the ERP grid | 0.1318 | 0.1511 | 0.0706 | 11% | 71% |
| inpaint in a polar tangent view | 0.1314 | 0.1543 | 0.0747 | 5% | 70% |
| tangent inpaint + floor / ceiling plane fill | 0.1358 | 0.1558 | 0.0780 | 5% | 64% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 | 0.1453 |  |  |
| degraded, no mitigation | 0.0625 | 0.0685 | 0.0660 |  |  |
| inpaint on the ERP grid | 0.1072 | 0.1060 | 0.0991 | -23% | 24% |
| inpaint in a polar tangent view | 0.1654 | 0.1263 | 0.1332 | -176% | 21% |
| tangent inpaint + floor / ceiling plane fill | 0.1621 | 0.1217 | 0.1278 | -73% | 21% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1646 | 0.1548 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1586 | 0.1696 |  | 88% | 71% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 | 0.1596 |  |  |
| degraded, no mitigation | 0.1594 | 0.1559 | 0.1570 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2067 | 0.1378 | 0.3068 | -797% | 1% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1738 | 0.1601 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1636 | 0.1590 |  | 45% | 57% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1850 | 0.1591 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1641 | 0.1527 |  | 54% | 75% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1733 | 0.1657 |  |  |  |
| non-local-means denoising | 0.1982 | 0.1609 |  | -22% | 33% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1266 | 0.1195 |  |  |  |
| bilateral smoothing (deblocking) | 0.1229 | 0.1005 |  | 16% | 58% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1502 | 0.1588 |  |  |  |
| degraded, no mitigation | 0.1016 | 0.1084 |  |  |  |
