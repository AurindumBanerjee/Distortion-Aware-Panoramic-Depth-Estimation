# Distortion study: s100_midas_holo_out

model `midas_dpt_hybrid_384` · 71 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.3016, polar >= 60 deg 0.2088

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.3751 | 0.3110 | 63% |
| blind lens-gain matching across the stitch lines | 0.3150 | 0.2283 | 44% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.3016 | 0.2038 | 13% |
| non-local-means denoising | 0.3991 | 0.3067 | 85% |
| bilateral smoothing (deblocking) | 0.3723 | 0.3585 | 85% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.4042 | 0.3723 |  |  |  |
| re-level, known tilt (IMU) | 0.3688 | 0.3211 |  | 45% | 77% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 14.4 deg) | 0.4154 | 0.3970 |  | 0% | 48% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 | 0.1477 |  |  |
| degraded, no mitigation | 0.2757 | 0.1474 | 0.0811 |  |  |
| inpaint on the ERP grid | 0.3299 | 0.1945 | 0.1317 | 62% | 24% |
| inpaint in a polar tangent view | 0.3158 | 0.1905 | 0.1419 | 47% | 24% |
| tangent inpaint + floor / ceiling plane fill | 0.2892 | 0.1490 | 0.0877 | 137% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 | 0.2428 |  |  |
| degraded, no mitigation | 0.3187 | 0.2323 | 0.2747 |  |  |
| inpaint on the ERP grid | 0.3184 | 0.1975 | 0.2268 | 89% | 63% |
| inpaint in a polar tangent view | 0.3480 | 0.1979 | 0.2209 | 91% | 62% |
| tangent inpaint + floor / ceiling plane fill | 0.3480 | 0.1821 | 0.2217 | 90% | 56% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.3195 | 0.2261 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.3056 | 0.2080 |  | 95% | 46% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 | 0.3400 |  |  |
| degraded, no mitigation | 0.3370 | 0.2582 | 0.3493 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.3391 | 0.2363 | 0.3663 | -39% | 41% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.3237 | 0.1909 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.3279 | 0.2104 |  | 40% | 49% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.4350 | 0.3371 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.3391 | 0.2240 |  | 80% | 93% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.4135 | 0.2525 |  |  |  |
| non-local-means denoising | 0.3907 | 0.2538 |  | -13% | 41% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.5046 | 0.3797 |  |  |  |
| bilateral smoothing (deblocking) | 0.5317 | 0.3981 |  | -9% | 35% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3016 | 0.2088 |  |  |  |
| degraded, no mitigation | 0.4729 | 0.4914 |  |  |  |
