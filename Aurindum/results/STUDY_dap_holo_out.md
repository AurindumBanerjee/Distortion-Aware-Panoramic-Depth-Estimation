# Distortion study: dap_holo_out

model `dap` · 40 frames · 3 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2800, polar >= 60 deg 0.2093

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.3140 | 0.2543 | 82% |
| blind lens-gain matching across the stitch lines | 0.2815 | 0.2096 | 35% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2765 | 0.2103 | 8% |
| non-local-means denoising | 0.3014 | 0.2686 | 75% |
| bilateral smoothing (deblocking) | 0.2742 | 0.2123 | 38% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.3007 | 0.2555 |  |  |  |
| re-level, known tilt (IMU) | 0.3002 | 0.2325 |  | -17% | 32% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 25.4 deg) | 0.3348 | 0.2757 |  | -40% | 25% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 | 0.1494 |  |  |
| degraded, no mitigation | 0.3461 | 0.5759 | 0.6432 |  |  |
| inpaint on the ERP grid | 0.3243 | 0.4837 | 0.5338 | 33% | 98% |
| inpaint in a polar tangent view | 0.3222 | 0.4817 | 0.5299 | 34% | 98% |
| tangent inpaint + floor / ceiling plane fill | 0.3178 | 0.2647 | 0.1683 | 101% | 100% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 | 0.2389 |  |  |
| degraded, no mitigation | 0.4070 | 0.6784 | 0.6769 |  |  |
| inpaint on the ERP grid | 0.3627 | 0.4675 | 0.5025 | 50% | 90% |
| inpaint in a polar tangent view | 0.3949 | 0.6292 | 0.6387 | 14% | 80% |
| tangent inpaint + floor / ceiling plane fill | 0.3596 | 0.3249 | 0.3458 | 98% | 98% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.2690 | 0.2141 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2849 | 0.2096 |  | 48% | 38% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 | 0.2826 |  |  |
| degraded, no mitigation | 0.2742 | 0.2035 | 0.2859 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2712 | 0.2025 | 0.4151 | 160% | 48% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.2779 | 0.2234 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2780 | 0.2142 |  | 67% | 57% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.3220 | 0.2813 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2892 | 0.2169 |  | 54% | 92% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.2757 | 0.2181 |  |  |  |
| non-local-means denoising | 0.3019 | 0.2438 |  | -75% | 28% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.4158 | 0.3312 |  |  |  |
| bilateral smoothing (deblocking) | 0.3593 | 0.2659 |  | 47% | 65% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2800 | 0.2093 |  |  |  |
| degraded, no mitigation | 0.3554 | 0.3217 |  |  |  |
