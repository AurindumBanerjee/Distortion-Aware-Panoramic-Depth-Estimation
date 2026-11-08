# Distortion study: da2m_holo_out

model `da2` · 40 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2164, polar >= 60 deg 0.1027

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1969 | 0.0867 | 57% |
| blind lens-gain matching across the stitch lines | 0.2205 | 0.1030 | 38% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2131 | 0.1027 | 8% |
| non-local-means denoising | 0.2713 | 0.1606 | 60% |
| bilateral smoothing (deblocking) | 0.1931 | 0.1150 | 35% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.2214 | 0.1274 |  |  |  |
| re-level, known tilt (IMU) | 0.2386 | 0.1122 |  | 68% | 42% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 9.4 deg) | 0.2134 | 0.0864 |  | -0% | 45% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 | 0.0905 |  |  |
| degraded, no mitigation | 0.2327 | 0.1904 | 0.1463 |  |  |
| inpaint on the ERP grid | 0.2206 | 0.1155 | 0.0816 | 107% | 70% |
| inpaint in a polar tangent view | 0.2178 | 0.1344 | 0.0906 | 104% | 65% |
| tangent inpaint + floor / ceiling plane fill | 0.2198 | 0.1364 | 0.1008 | 110% | 62% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 | 0.1218 |  |  |
| degraded, no mitigation | 0.2231 | 0.1569 | 0.1599 |  |  |
| inpaint on the ERP grid | 0.2245 | 0.1200 | 0.1458 | 75% | 60% |
| inpaint in a polar tangent view | 0.2247 | 0.0839 | 0.1343 | 93% | 57% |
| tangent inpaint + floor / ceiling plane fill | 0.2241 | 0.0939 | 0.1249 | 113% | 55% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.2135 | 0.1000 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2091 | 0.1055 |  | 108% | 52% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 | 0.2469 |  |  |
| degraded, no mitigation | 0.2169 | 0.1082 | 0.2101 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2258 | 0.1078 | 0.2513 | 4% | 32% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.2120 | 0.1170 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2191 | 0.1100 |  | 48% | 52% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.3251 | 0.2672 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2881 | 0.1799 |  | 42% | 57% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.2504 | 0.1938 |  |  |  |
| non-local-means denoising | 0.3197 | 0.1713 |  | 19% | 68% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.3289 | 0.1670 |  |  |  |
| bilateral smoothing (deblocking) | 0.3399 | 0.2164 |  | 5% | 55% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2164 | 0.1027 |  |  |  |
| degraded, no mitigation | 0.3354 | 0.2559 |  |  |  |
