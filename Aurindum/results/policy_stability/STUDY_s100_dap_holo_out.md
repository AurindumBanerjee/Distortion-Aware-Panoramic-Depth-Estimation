# Distortion study: s100_dap_holo_out

model `dap` · 71 frames · 3 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2725, polar >= 60 deg 0.2417

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.3156 | 0.2765 | 80% |
| blind lens-gain matching across the stitch lines | 0.2762 | 0.2437 | 32% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2655 | 0.2417 | 13% |
| non-local-means denoising | 0.3053 | 0.2916 | 76% |
| bilateral smoothing (deblocking) | 0.2759 | 0.2473 | 35% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.3118 | 0.2892 |  |  |  |
| re-level, known tilt (IMU) | 0.2959 | 0.2630 |  | -11% | 34% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 20.5 deg) | 0.3493 | 0.3027 |  | -50% | 25% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 | 0.1597 |  |  |
| degraded, no mitigation | 0.3472 | 0.5641 | 0.6445 |  |  |
| inpaint on the ERP grid | 0.3228 | 0.4736 | 0.5211 | 31% | 99% |
| inpaint in a polar tangent view | 0.3183 | 0.4762 | 0.5267 | 32% | 97% |
| tangent inpaint + floor / ceiling plane fill | 0.3174 | 0.2827 | 0.1480 | 104% | 100% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 | 0.2461 |  |  |
| degraded, no mitigation | 0.4263 | 0.6758 | 0.6728 |  |  |
| inpaint on the ERP grid | 0.3544 | 0.4870 | 0.5130 | 56% | 89% |
| inpaint in a polar tangent view | 0.3988 | 0.6375 | 0.6420 | 16% | 87% |
| tangent inpaint + floor / ceiling plane fill | 0.3642 | 0.3718 | 0.3605 | 91% | 99% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.2643 | 0.2364 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2829 | 0.2505 |  | 69% | 48% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 | 0.2810 |  |  |
| degraded, no mitigation | 0.2725 | 0.2185 | 0.2786 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2756 | 0.2304 | 0.4072 | -1% | 49% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.2770 | 0.2513 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2737 | 0.2504 |  | 37% | 52% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.3259 | 0.3168 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2909 | 0.2657 |  | 56% | 89% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.2937 | 0.2373 |  |  |  |
| non-local-means denoising | 0.3132 | 0.2807 |  | -51% | 23% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.4341 | 0.3544 |  |  |  |
| bilateral smoothing (deblocking) | 0.3721 | 0.2840 |  | 48% | 68% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2725 | 0.2417 |  |  |  |
| degraded, no mitigation | 0.3596 | 0.3510 |  |  |  |
