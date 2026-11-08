# Distortion study: sd_dap_stanford

model `dap` · 150 frames · 63 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1616, polar >= 60 deg 0.3568

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1619 | 0.3411 | 39% |
| blind lens-gain matching across the stitch lines | 0.1626 | 0.3584 | 27% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1877 | 0.4119 | 96% |
| non-local-means denoising | 0.1791 | 0.3469 | 77% |
| bilateral smoothing (deblocking) | 0.1716 | 0.3810 | 85% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.2224 | 0.4119 |  |  |  |
| re-level, known tilt (IMU) | 0.1535 | 0.3311 |  | 108% | 99% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 4.0 deg) | 0.1696 | 0.3340 |  | 94% | 83% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 | 0.3504 |  |  |
| degraded, no mitigation | 0.1683 | 0.3591 | 0.4043 |  |  |
| inpaint on the ERP grid | 0.1363 | 0.2690 | 0.2151 | 209% | 94% |
| inpaint in a polar tangent view | 0.1404 | 0.3108 | 0.2840 | 120% | 87% |
| tangent inpaint + floor / ceiling plane fill | 0.1344 | 0.2660 | 0.0892 | 271% | 96% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 | 0.2797 |  |  |
| degraded, no mitigation | 0.3839 | 0.7692 | 0.7646 |  |  |
| inpaint on the ERP grid | 0.1953 | 0.3390 | 0.3236 | 87% | 100% |
| inpaint in a polar tangent view | 0.3172 | 0.6247 | 0.6147 | 29% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.2934 | 0.5877 | 0.5775 | 32% | 100% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.1660 | 0.3677 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1659 | 0.3616 |  | 65% | 67% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 | 0.1528 |  |  |
| degraded, no mitigation | 0.1539 | 0.3347 | 0.1472 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1893 | 0.3785 | 0.2666 | -1058% | 3% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.1608 | 0.3485 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1806 | 0.4000 |  | -234% | 2% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.1837 | 0.3289 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1613 | 0.3412 |  | 88% | 82% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.1645 | 0.3119 |  |  |  |
| non-local-means denoising | 0.1993 | 0.4087 |  | -140% | 3% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.2911 | 0.3369 |  |  |  |
| bilateral smoothing (deblocking) | 0.2479 | 0.3353 |  | 27% | 89% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1616 | 0.3568 |  |  |  |
| degraded, no mitigation | 0.1560 | 0.2061 |  |  |  |
