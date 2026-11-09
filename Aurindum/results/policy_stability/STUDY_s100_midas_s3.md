# Distortion study: s100_midas_s3

model `midas_dpt_hybrid_384` · 100 frames · 66 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2465, polar >= 60 deg 0.2055

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2320 | 0.1826 | 21% |
| blind lens-gain matching across the stitch lines | 0.2475 | 0.2149 | 32% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2477 | 0.2093 | 18% |
| non-local-means denoising | 0.2380 | 0.1936 | 40% |
| bilateral smoothing (deblocking) | 0.2446 | 0.1994 | 33% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2447 | 0.2015 |  |  |  |
| re-level, known tilt (IMU) | 0.2375 | 0.1989 |  | 97% | 64% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 11.7 deg) | 0.2375 | 0.1941 |  | 51% | 57% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 | 0.2799 |  |  |
| degraded, no mitigation | 0.2475 | 0.2215 | 0.2682 |  |  |
| inpaint on the ERP grid | 0.2553 | 0.2237 | 0.2443 | 55% | 72% |
| inpaint in a polar tangent view | 0.2560 | 0.2183 | 0.2270 | 80% | 79% |
| tangent inpaint + floor / ceiling plane fill | 0.2550 | 0.2127 | 0.2270 | 95% | 77% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 | 0.2055 |  |  |
| degraded, no mitigation | 0.2430 | 0.1830 | 0.1888 |  |  |
| inpaint on the ERP grid | 0.2454 | 0.2072 | 0.2127 | 76% | 42% |
| inpaint in a polar tangent view | 0.2478 | 0.1958 | 0.2037 | 50% | 43% |
| tangent inpaint + floor / ceiling plane fill | 0.2557 | 0.1980 | 0.2045 | 13% | 41% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2493 | 0.2273 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2479 | 0.2113 |  | 56% | 57% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 | 0.2446 |  |  |
| degraded, no mitigation | 0.2435 | 0.2060 | 0.2466 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2457 | 0.2094 | 0.2548 | -73% | 46% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2484 | 0.2154 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2491 | 0.2195 |  | 48% | 50% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2460 | 0.2059 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2430 | 0.2069 |  | 74% | 61% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2573 | 0.2198 |  |  |  |
| non-local-means denoising | 0.2470 | 0.2103 |  | 45% | 55% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2554 | 0.2006 |  |  |  |
| bilateral smoothing (deblocking) | 0.2447 | 0.1918 |  | 12% | 67% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2465 | 0.2055 |  |  |  |
| degraded, no mitigation | 0.2561 | 0.1946 |  |  |  |
