# Distortion study: dap_stanford

model `dap` · 40 frames · 28 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1596, polar >= 60 deg 0.3085

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1562 | 0.2775 | 28% |
| blind lens-gain matching across the stitch lines | 0.1630 | 0.3202 | 38% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1783 | 0.3463 | 100% |
| non-local-means denoising | 0.1755 | 0.2992 | 85% |
| bilateral smoothing (deblocking) | 0.1500 | 0.3201 | 80% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.2281 | 0.3691 |  |  |  |
| re-level, known tilt (IMU) | 0.1512 | 0.2691 |  | 107% | 100% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 3.7 deg) | 0.1515 | 0.2850 |  | 97% | 80% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 | 0.2974 |  |  |
| degraded, no mitigation | 0.1681 | 0.3372 | 0.3716 |  |  |
| inpaint on the ERP grid | 0.1294 | 0.2125 | 0.1446 | 243% | 95% |
| inpaint in a polar tangent view | 0.1368 | 0.2441 | 0.1921 | 126% | 82% |
| tangent inpaint + floor / ceiling plane fill | 0.1293 | 0.1839 | 0.0727 | 272% | 98% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 | 0.2358 |  |  |
| degraded, no mitigation | 0.3714 | 0.7419 | 0.7405 |  |  |
| inpaint on the ERP grid | 0.1818 | 0.3036 | 0.2931 | 91% | 100% |
| inpaint in a polar tangent view | 0.3079 | 0.6049 | 0.6026 | 30% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.2784 | 0.5245 | 0.5204 | 37% | 100% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.1674 | 0.3138 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1643 | 0.3240 |  | 74% | 62% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 | 0.1513 |  |  |
| degraded, no mitigation | 0.1540 | 0.2907 | 0.1397 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1791 | 0.3099 | 0.2519 | n/a | 0% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.1613 | 0.2998 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1775 | 0.3457 |  | -20% | 2% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.1694 | 0.2775 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1449 | 0.2864 |  | 93% | 80% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.1493 | 0.2630 |  |  |  |
| non-local-means denoising | 0.1861 | 0.3672 |  | -101% | 0% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.2644 | 0.3065 |  |  |  |
| bilateral smoothing (deblocking) | 0.2215 | 0.3063 |  | 29% | 90% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1596 | 0.3085 |  |  |  |
| degraded, no mitigation | 0.1520 | 0.1929 |  |  |  |
