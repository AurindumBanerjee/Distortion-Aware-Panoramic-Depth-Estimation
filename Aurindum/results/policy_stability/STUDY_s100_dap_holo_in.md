# Distortion study: s100_dap_holo_in

model `dap` · 100 frames · 12 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1289, polar >= 60 deg 0.1208

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1247 | 0.1224 | 40% |
| blind lens-gain matching across the stitch lines | 0.1329 | 0.1211 | 35% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1321 | 0.1262 | 34% |
| non-local-means denoising | 0.1909 | 0.1875 | 86% |
| bilateral smoothing (deblocking) | 0.1440 | 0.1311 | 72% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.1824 | 0.1663 |  |  |  |
| re-level, known tilt (IMU) | 0.1387 | 0.1321 |  | 91% | 87% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 9.7 deg) | 0.1428 | 0.1405 |  | 95% | 76% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 | 0.1205 |  |  |
| degraded, no mitigation | 0.1663 | 0.2444 | 0.6926 |  |  |
| inpaint on the ERP grid | 0.1650 | 0.2154 | 0.4913 | 34% | 95% |
| inpaint in a polar tangent view | 0.1611 | 0.2211 | 0.5549 | 28% | 93% |
| tangent inpaint + floor / ceiling plane fill | 0.1594 | 0.2137 | 0.5263 | 32% | 93% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 | 0.1179 |  |  |
| degraded, no mitigation | 0.3896 | 0.7891 | 0.7888 |  |  |
| inpaint on the ERP grid | 0.2340 | 0.2998 | 0.3115 | 70% | 99% |
| inpaint in a polar tangent view | 0.3407 | 0.6546 | 0.6488 | 20% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.2740 | 0.3713 | 0.3801 | 56% | 99% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.1358 | 0.1257 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1347 | 0.1250 |  | 61% | 47% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 | 0.1341 |  |  |
| degraded, no mitigation | 0.1345 | 0.1346 | 0.1481 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1456 | 0.1353 | 0.1767 | -268% | 14% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.1394 | 0.1269 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1332 | 0.1324 |  | 61% | 54% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.2383 | 0.2293 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1414 | 0.1338 |  | 84% | 90% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.1979 | 0.1943 |  |  |  |
| non-local-means denoising | 0.1899 | 0.1798 |  | 27% | 58% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.4832 | 0.4402 |  |  |  |
| bilateral smoothing (deblocking) | 0.4231 | 0.3881 |  | 13% | 92% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1289 | 0.1208 |  |  |  |
| degraded, no mitigation | 0.3120 | 0.2974 |  |  |  |
