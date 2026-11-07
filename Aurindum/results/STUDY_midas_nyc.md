# Distortion study: midas_nyc

model `midas_dpt_hybrid_384` · 40 frames · 40 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2214, polar >= 60 deg 0.1374

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2257 | 0.1332 | 18% |
| blind lens-gain matching across the stitch lines | 0.2279 | 0.1454 | 60% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2219 | 0.1373 | 15% |
| non-local-means denoising | 0.2560 | 0.1597 | 60% |
| bilateral smoothing (deblocking) | 0.2230 | 0.1434 | 28% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.2574 | 0.1613 |  |  |  |
| re-level, known tilt (IMU) | 0.2250 | 0.1448 |  | 93% | 62% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 16.0 deg) | 0.2512 | 0.1780 |  | 42% | 60% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 | 0.0708 |  |  |
| degraded, no mitigation | 0.2093 | 0.1298 | 0.0614 |  |  |
| inpaint on the ERP grid | 0.2198 | 0.1259 | 0.0609 | 227% | 45% |
| inpaint in a polar tangent view | 0.2465 | 0.1362 | 0.0886 | 176% | 38% |
| tangent inpaint + floor / ceiling plane fill | 0.2185 | 0.1378 | 0.0741 | 120% | 78% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 | 0.1571 |  |  |
| degraded, no mitigation | 0.3503 | 0.2821 | 0.3264 |  |  |
| inpaint on the ERP grid | 0.2586 | 0.1690 | 0.1904 | 81% | 72% |
| inpaint in a polar tangent view | 0.3162 | 0.1789 | 0.2164 | 66% | 95% |
| tangent inpaint + floor / ceiling plane fill | 0.3103 | 0.1638 | 0.2066 | 67% | 88% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.2239 | 0.1399 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2280 | 0.1446 |  | -13% | 30% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 | 0.2533 |  |  |
| degraded, no mitigation | 0.2112 | 0.1433 | 0.2413 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2137 | 0.1484 | 0.2541 | 14% | 35% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.2217 | 0.1367 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2289 | 0.1427 |  | 0% | 35% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.2676 | 0.1402 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2343 | 0.1339 |  | 70% | 80% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.2409 | 0.1608 |  |  |  |
| non-local-means denoising | 0.2428 | 0.1478 |  | 53% | 50% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.3238 | 0.1898 |  |  |  |
| bilateral smoothing (deblocking) | 0.3504 | 0.2172 |  | -2% | 35% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2214 | 0.1374 |  |  |  |
| degraded, no mitigation | 0.3251 | 0.1637 |  |  |  |
