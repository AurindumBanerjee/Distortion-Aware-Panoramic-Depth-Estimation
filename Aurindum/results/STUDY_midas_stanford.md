# Distortion study: midas_stanford

model `midas_dpt_hybrid_384` · 40 frames · 28 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2420, polar >= 60 deg 0.1064

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2424 | 0.1041 | 45% |
| blind lens-gain matching across the stitch lines | 0.2437 | 0.1080 | 10% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2376 | 0.1171 | 18% |
| non-local-means denoising | 0.2366 | 0.1634 | 32% |
| bilateral smoothing (deblocking) | 0.2330 | 0.1072 | 15% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2338 | 0.1303 |  |  |  |
| re-level, known tilt (IMU) | 0.2418 | 0.1149 |  | 59% | 40% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 12.0 deg) | 0.2426 | 0.1257 |  | -10% | 32% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 | 0.1050 |  |  |
| degraded, no mitigation | 0.2459 | 0.1176 | 0.0906 |  |  |
| inpaint on the ERP grid | 0.2429 | 0.1074 | 0.0897 | 26% | 42% |
| inpaint in a polar tangent view | 0.2432 | 0.1116 | 0.1082 | 42% | 38% |
| tangent inpaint + floor / ceiling plane fill | 0.2453 | 0.1227 | 0.1107 | -23% | 38% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 | 0.1070 |  |  |
| degraded, no mitigation | 0.2449 | 0.1084 | 0.1255 |  |  |
| inpaint on the ERP grid | 0.2204 | 0.1041 | 0.1166 | 46% | 60% |
| inpaint in a polar tangent view | 0.2467 | 0.0884 | 0.1057 | 94% | 78% |
| tangent inpaint + floor / ceiling plane fill | 0.2471 | 0.0931 | 0.1090 | 93% | 72% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2439 | 0.1085 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2441 | 0.1071 |  | n/a | 55% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 | 0.2360 |  |  |
| degraded, no mitigation | 0.2429 | 0.1111 | 0.2365 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2456 | 0.1091 | 0.2418 | -147% | 20% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2424 | 0.1020 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2342 | 0.1186 |  | 457% | 65% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2305 | 0.1044 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2410 | 0.1139 |  | 75% | 48% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2511 | 0.1556 |  |  |  |
| non-local-means denoising | 0.2662 | 0.1628 |  | -46% | 35% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2584 | 0.1765 |  |  |  |
| bilateral smoothing (deblocking) | 0.2497 | 0.1867 |  | 29% | 55% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2420 | 0.1064 |  |  |  |
| degraded, no mitigation | 0.2468 | 0.1107 |  |  |  |
