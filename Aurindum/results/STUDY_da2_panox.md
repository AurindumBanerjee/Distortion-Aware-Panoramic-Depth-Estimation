# Distortion study: da2_panox

model `da2` · 40 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1619, polar >= 60 deg 0.1176

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1666 | 0.1372 | 52% |
| blind lens-gain matching across the stitch lines | 0.1633 | 0.1262 | 40% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1563 | 0.1176 | 10% |
| non-local-means denoising | 0.2026 | 0.1949 | 75% |
| bilateral smoothing (deblocking) | 0.1790 | 0.1278 | 48% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.1979 | 0.2068 |  |  |  |
| re-level, known tilt (IMU) | 0.1652 | 0.1108 |  | 89% | 50% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.2 deg) | 0.1969 | 0.2138 |  | 47% | 55% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 | 0.1325 |  |  |
| degraded, no mitigation | 0.2077 | 0.2154 | 0.3529 |  |  |
| inpaint on the ERP grid | 0.1556 | 0.1276 | 0.1764 | 83% | 70% |
| inpaint in a polar tangent view | 0.1558 | 0.1416 | 0.1912 | 91% | 62% |
| tangent inpaint + floor / ceiling plane fill | 0.1537 | 0.1416 | 0.1824 | 98% | 62% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 | 0.1334 |  |  |
| degraded, no mitigation | 0.1802 | 0.2942 | 0.2885 |  |  |
| inpaint on the ERP grid | 0.2232 | 0.2822 | 0.2751 | -25% | 52% |
| inpaint in a polar tangent view | 0.2339 | 0.3652 | 0.3686 | -24% | 48% |
| tangent inpaint + floor / ceiling plane fill | 0.2348 | 0.3607 | 0.3654 | 0% | 52% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.1569 | 0.1232 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1596 | 0.1258 |  | 47% | 55% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 | 0.1541 |  |  |
| degraded, no mitigation | 0.1723 | 0.1057 | 0.1632 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1827 | 0.1138 | 0.1685 | -107% | 18% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.1599 | 0.1230 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1548 | 0.1111 |  | 91% | 32% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.2071 | 0.1612 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1834 | 0.1339 |  | 62% | 78% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.1874 | 0.1782 |  |  |  |
| non-local-means denoising | 0.1971 | 0.1754 |  | 0% | 45% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.2465 | 0.2234 |  |  |  |
| bilateral smoothing (deblocking) | 0.2741 | 0.2644 |  | -13% | 25% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1619 | 0.1176 |  |  |  |
| degraded, no mitigation | 0.2321 | 0.1725 |  |  |  |
