# Distortion study: midas_holo_in

model `midas_dpt_hybrid_384` · 40 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2787, polar >= 60 deg 0.2571

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2857 | 0.2357 | 50% |
| blind lens-gain matching across the stitch lines | 0.2945 | 0.2673 | 38% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2811 | 0.2404 | 32% |
| non-local-means denoising | 0.2890 | 0.2147 | 55% |
| bilateral smoothing (deblocking) | 0.3167 | 0.2719 | 62% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3185 | 0.2706 |  |  |  |
| re-level, known tilt (IMU) | 0.2871 | 0.2442 |  | 107% | 72% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 14.5 deg) | 0.3101 | 0.2752 |  | -13% | 45% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 | 0.4111 |  |  |
| degraded, no mitigation | 0.2965 | 0.2760 | 0.4823 |  |  |
| inpaint on the ERP grid | 0.3414 | 0.3437 | 0.4627 | 4% | 45% |
| inpaint in a polar tangent view | 0.3420 | 0.3293 | 0.4673 | 2% | 45% |
| tangent inpaint + floor / ceiling plane fill | 0.3406 | 0.3293 | 0.4673 | 6% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 | 0.2657 |  |  |
| degraded, no mitigation | 0.2985 | 0.2998 | 0.2934 |  |  |
| inpaint on the ERP grid | 0.3569 | 0.3736 | 0.3402 | -51% | 25% |
| inpaint in a polar tangent view | 0.3507 | 0.2895 | 0.3003 | -24% | 32% |
| tangent inpaint + floor / ceiling plane fill | 0.3702 | 0.4013 | 0.3874 | -41% | 35% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3161 | 0.2856 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.3001 | 0.2699 |  | 11% | 48% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 | 0.2780 |  |  |
| degraded, no mitigation | 0.2762 | 0.2341 | 0.2816 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2893 | 0.2653 | 0.2994 | -178% | 38% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3322 | 0.3243 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2912 | 0.2439 |  | 85% | 72% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3012 | 0.2647 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2817 | 0.2365 |  | 97% | 70% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3554 | 0.3943 |  |  |  |
| non-local-means denoising | 0.3630 | 0.3410 |  | -1% | 45% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3509 | 0.3560 |  |  |  |
| bilateral smoothing (deblocking) | 0.3455 | 0.3377 |  | 8% | 72% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2787 | 0.2571 |  |  |  |
| degraded, no mitigation | 0.3493 | 0.3435 |  |  |  |
