# Distortion study: s100_dap_panox

model `dap` · 100 frames · 8 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2006, polar >= 60 deg 0.1773

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2411 | 0.2249 | 59% |
| blind lens-gain matching across the stitch lines | 0.2008 | 0.1789 | 33% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1996 | 0.1783 | 9% |
| non-local-means denoising | 0.2392 | 0.2147 | 83% |
| bilateral smoothing (deblocking) | 0.2162 | 0.2091 | 85% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.2672 | 0.2513 |  |  |  |
| re-level, known tilt (IMU) | 0.1937 | 0.1784 |  | 105% | 77% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.4 deg) | 0.2565 | 0.2282 |  | 70% | 73% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 | 0.1391 |  |  |
| degraded, no mitigation | 0.2383 | 0.2915 | 0.3260 |  |  |
| inpaint on the ERP grid | 0.2125 | 0.2572 | 0.2625 | 41% | 81% |
| inpaint in a polar tangent view | 0.2171 | 0.2464 | 0.2576 | 46% | 65% |
| tangent inpaint + floor / ceiling plane fill | 0.2177 | 0.1988 | 0.1529 | 85% | 81% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 | 0.1795 |  |  |
| degraded, no mitigation | 0.4275 | 0.6640 | 0.6670 |  |  |
| inpaint on the ERP grid | 0.3029 | 0.4059 | 0.4015 | 69% | 91% |
| inpaint in a polar tangent view | 0.3639 | 0.5823 | 0.5875 | 21% | 84% |
| tangent inpaint + floor / ceiling plane fill | 0.2842 | 0.3740 | 0.3664 | 76% | 95% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.1979 | 0.1735 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2017 | 0.1788 |  | 52% | 29% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 | 0.2201 |  |  |
| degraded, no mitigation | 0.2025 | 0.1853 | 0.2201 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2076 | 0.1876 | 0.2783 | -336% | 11% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.2109 | 0.1927 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1982 | 0.1788 |  | 100% | 67% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.2715 | 0.2634 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1956 | 0.1988 |  | 94% | 96% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.2332 | 0.2364 |  |  |  |
| non-local-means denoising | 0.2434 | 0.2365 |  | 12% | 51% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.3795 | 0.3419 |  |  |  |
| bilateral smoothing (deblocking) | 0.3779 | 0.3213 |  | 11% | 69% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2006 | 0.1773 |  |  |  |
| degraded, no mitigation | 0.2515 | 0.2444 |  |  |  |
