# Distortion study: sd_midas_stanford

model `midas_dpt_hybrid_384` · 150 frames · 63 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2535, polar >= 60 deg 0.1207

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2512 | 0.1183 | 32% |
| blind lens-gain matching across the stitch lines | 0.2537 | 0.1209 | 7% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2518 | 0.1192 | 18% |
| non-local-means denoising | 0.2430 | 0.1513 | 25% |
| bilateral smoothing (deblocking) | 0.2504 | 0.1243 | 12% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2487 | 0.1337 |  |  |  |
| re-level, known tilt (IMU) | 0.2514 | 0.1188 |  | 64% | 47% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 11.2 deg) | 0.2462 | 0.1315 |  | -6% | 51% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 | 0.1023 |  |  |
| degraded, no mitigation | 0.2542 | 0.1349 | 0.0935 |  |  |
| inpaint on the ERP grid | 0.2508 | 0.1398 | 0.0948 | -2% | 39% |
| inpaint in a polar tangent view | 0.2527 | 0.1253 | 0.1011 | 93% | 40% |
| tangent inpaint + floor / ceiling plane fill | 0.2536 | 0.1487 | 0.1129 | 9% | 35% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 | 0.1298 |  |  |
| degraded, no mitigation | 0.2518 | 0.1267 | 0.1504 |  |  |
| inpaint on the ERP grid | 0.2427 | 0.1229 | 0.1383 | 47% | 61% |
| inpaint in a polar tangent view | 0.2528 | 0.1063 | 0.1257 | 110% | 81% |
| tangent inpaint + floor / ceiling plane fill | 0.2545 | 0.1132 | 0.1318 | 108% | 79% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2529 | 0.1236 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2535 | 0.1203 |  | n/a | 49% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 | 0.2567 |  |  |
| degraded, no mitigation | 0.2530 | 0.1222 | 0.2572 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2536 | 0.1204 | 0.2678 | -128% | 24% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2542 | 0.1165 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2497 | 0.1225 |  | 304% | 60% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2471 | 0.1190 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2493 | 0.1200 |  | 83% | 49% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2548 | 0.1628 |  |  |  |
| non-local-means denoising | 0.2629 | 0.1659 |  | -82% | 33% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2584 | 0.1779 |  |  |  |
| bilateral smoothing (deblocking) | 0.2468 | 0.1727 |  | 41% | 59% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2535 | 0.1207 |  |  |  |
| degraded, no mitigation | 0.2500 | 0.1188 |  |  |  |
