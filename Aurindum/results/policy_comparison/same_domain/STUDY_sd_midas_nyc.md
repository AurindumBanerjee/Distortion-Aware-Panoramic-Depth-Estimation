# Distortion study: sd_midas_nyc

model `midas_dpt_hybrid_384` · 147 frames · 82 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2198, polar >= 60 deg 0.1341

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2262 | 0.1339 | 19% |
| blind lens-gain matching across the stitch lines | 0.2253 | 0.1371 | 51% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2202 | 0.1345 | 20% |
| non-local-means denoising | 0.2530 | 0.1530 | 69% |
| bilateral smoothing (deblocking) | 0.2245 | 0.1286 | 35% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.2433 | 0.1561 |  |  |  |
| re-level, known tilt (IMU) | 0.2177 | 0.1398 |  | 91% | 68% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 15.1 deg) | 0.2439 | 0.1637 |  | 21% | 61% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 | 0.0658 |  |  |
| degraded, no mitigation | 0.2071 | 0.1162 | 0.0608 |  |  |
| inpaint on the ERP grid | 0.2164 | 0.1153 | 0.0540 | 149% | 41% |
| inpaint in a polar tangent view | 0.2335 | 0.1326 | 0.0766 | 75% | 44% |
| tangent inpaint + floor / ceiling plane fill | 0.2128 | 0.1144 | 0.0561 | 132% | 76% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 | 0.1550 |  |  |
| degraded, no mitigation | 0.3448 | 0.2869 | 0.3230 |  |  |
| inpaint on the ERP grid | 0.2539 | 0.1674 | 0.1934 | 82% | 75% |
| inpaint in a polar tangent view | 0.3159 | 0.1772 | 0.2169 | 65% | 96% |
| tangent inpaint + floor / ceiling plane fill | 0.3138 | 0.1705 | 0.2106 | 68% | 91% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.2218 | 0.1355 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2240 | 0.1386 |  | 1% | 32% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 | 0.2395 |  |  |
| degraded, no mitigation | 0.2100 | 0.1384 | 0.2362 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2182 | 0.1445 | 0.2474 | -89% | 31% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.2249 | 0.1326 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2285 | 0.1354 |  | 10% | 41% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.2574 | 0.1323 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2190 | 0.1328 |  | 76% | 83% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.2494 | 0.1500 |  |  |  |
| non-local-means denoising | 0.2429 | 0.1422 |  | 44% | 42% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.3225 | 0.1794 |  |  |  |
| bilateral smoothing (deblocking) | 0.3468 | 0.1895 |  | -8% | 42% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2198 | 0.1341 |  |  |  |
| degraded, no mitigation | 0.3132 | 0.1487 |  |  |  |
