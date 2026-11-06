# Distortion study: dap_panox

model `dap` · 40 frames · 8 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1879, polar >= 60 deg 0.1704

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2183 | 0.2130 | 68% |
| blind lens-gain matching across the stitch lines | 0.1887 | 0.1726 | 35% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1875 | 0.1709 | 10% |
| non-local-means denoising | 0.2188 | 0.1994 | 80% |
| bilateral smoothing (deblocking) | 0.1996 | 0.1822 | 88% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.2493 | 0.2410 |  |  |  |
| re-level, known tilt (IMU) | 0.1905 | 0.1702 |  | 105% | 72% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.5 deg) | 0.2388 | 0.2203 |  | 61% | 72% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 | 0.1111 |  |  |
| degraded, no mitigation | 0.2160 | 0.2344 | 0.2223 |  |  |
| inpaint on the ERP grid | 0.2030 | 0.2369 | 0.2369 | 40% | 72% |
| inpaint in a polar tangent view | 0.2052 | 0.2357 | 0.2229 | 44% | 55% |
| tangent inpaint + floor / ceiling plane fill | 0.1981 | 0.1888 | 0.1425 | 85% | 80% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 | 0.1868 |  |  |
| degraded, no mitigation | 0.4195 | 0.6486 | 0.6426 |  |  |
| inpaint on the ERP grid | 0.2769 | 0.3841 | 0.3862 | 60% | 92% |
| inpaint in a polar tangent view | 0.3494 | 0.5376 | 0.5351 | 21% | 88% |
| tangent inpaint + floor / ceiling plane fill | 0.2480 | 0.3448 | 0.3419 | 73% | 98% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.1811 | 0.1672 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1898 | 0.1739 |  | 97% | 28% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 | 0.1970 |  |  |
| degraded, no mitigation | 0.1781 | 0.1695 | 0.1948 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1851 | 0.1756 | 0.2759 | -189% | 12% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.1915 | 0.1785 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1879 | 0.1760 |  | 86% | 60% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.2577 | 0.2563 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1928 | 0.1735 |  | 89% | 90% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.2358 | 0.2257 |  |  |  |
| non-local-means denoising | 0.2541 | 0.2494 |  | 16% | 55% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.3455 | 0.3096 |  |  |  |
| bilateral smoothing (deblocking) | 0.3070 | 0.2820 |  | 13% | 72% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1879 | 0.1704 |  |  |  |
| degraded, no mitigation | 0.2583 | 0.2768 |  |  |  |
