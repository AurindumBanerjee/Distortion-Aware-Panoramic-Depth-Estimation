# Distortion study: s100_midas_holo_in

model `midas_dpt_hybrid_384` · 100 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2850, polar >= 60 deg 0.2335

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2811 | 0.2389 | 45% |
| blind lens-gain matching across the stitch lines | 0.2945 | 0.2637 | 45% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2871 | 0.2379 | 29% |
| non-local-means denoising | 0.2993 | 0.2108 | 49% |
| bilateral smoothing (deblocking) | 0.3155 | 0.2719 | 70% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3145 | 0.2553 |  |  |  |
| re-level, known tilt (IMU) | 0.2843 | 0.2309 |  | 86% | 71% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 14.9 deg) | 0.3065 | 0.2574 |  | 12% | 53% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 | 0.3427 |  |  |
| degraded, no mitigation | 0.3014 | 0.2568 | 0.3911 |  |  |
| inpaint on the ERP grid | 0.3369 | 0.3148 | 0.4051 | 23% | 55% |
| inpaint in a polar tangent view | 0.3320 | 0.3210 | 0.4041 | 9% | 48% |
| tangent inpaint + floor / ceiling plane fill | 0.3298 | 0.3092 | 0.3946 | 10% | 51% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 | 0.2432 |  |  |
| degraded, no mitigation | 0.2935 | 0.2435 | 0.2566 |  |  |
| inpaint on the ERP grid | 0.3446 | 0.3343 | 0.3308 | -59% | 27% |
| inpaint in a polar tangent view | 0.3384 | 0.2603 | 0.2728 | -15% | 34% |
| tangent inpaint + floor / ceiling plane fill | 0.3568 | 0.3079 | 0.3052 | -57% | 35% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3054 | 0.2843 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2912 | 0.2697 |  | 44% | 59% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 | 0.2846 |  |  |
| degraded, no mitigation | 0.2786 | 0.2319 | 0.2802 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2870 | 0.2307 | 0.2896 | 57% | 52% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3180 | 0.3221 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2936 | 0.2639 |  | 71% | 68% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3001 | 0.2491 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2873 | 0.2316 |  | 97% | 73% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3248 | 0.3251 |  |  |  |
| non-local-means denoising | 0.3438 | 0.3000 |  | 1% | 41% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3501 | 0.3492 |  |  |  |
| bilateral smoothing (deblocking) | 0.3417 | 0.3249 |  | 4% | 63% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2850 | 0.2335 |  |  |  |
| degraded, no mitigation | 0.3365 | 0.3156 |  |  |  |
