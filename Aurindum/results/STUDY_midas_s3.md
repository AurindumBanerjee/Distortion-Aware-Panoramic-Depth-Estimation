# Distortion study: midas_s3

model `midas_dpt_hybrid_384` · 40 frames · 33 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2210, polar >= 60 deg 0.1960

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2123 | 0.1721 | 15% |
| blind lens-gain matching across the stitch lines | 0.2221 | 0.2020 | 30% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2256 | 0.1972 | 25% |
| non-local-means denoising | 0.2133 | 0.1613 | 38% |
| bilateral smoothing (deblocking) | 0.2160 | 0.1966 | 42% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2199 | 0.1760 |  |  |  |
| re-level, known tilt (IMU) | 0.2137 | 0.1868 |  | 114% | 50% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 11.0 deg) | 0.2101 | 0.1857 |  | 65% | 57% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 | 0.2282 |  |  |
| degraded, no mitigation | 0.2227 | 0.1983 | 0.2476 |  |  |
| inpaint on the ERP grid | 0.2453 | 0.2075 | 0.2388 | 29% | 72% |
| inpaint in a polar tangent view | 0.2439 | 0.2038 | 0.2173 | 56% | 80% |
| tangent inpaint + floor / ceiling plane fill | 0.2437 | 0.2023 | 0.2173 | 56% | 75% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 | 0.1898 |  |  |
| degraded, no mitigation | 0.2221 | 0.1622 | 0.1652 |  |  |
| inpaint on the ERP grid | 0.2471 | 0.2070 | 0.2150 | 83% | 30% |
| inpaint in a polar tangent view | 0.2455 | 0.2010 | 0.2062 | 87% | 30% |
| tangent inpaint + floor / ceiling plane fill | 0.2526 | 0.1903 | 0.2072 | 87% | 28% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2304 | 0.2163 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2197 | 0.1961 |  | 66% | 65% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 | 0.2352 |  |  |
| degraded, no mitigation | 0.2176 | 0.1943 | 0.2310 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2145 | 0.2021 | 0.2441 | 324% | 52% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2134 | 0.2062 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2281 | 0.2110 |  | 45% | 57% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2190 | 0.1774 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2162 | 0.1895 |  | 70% | 60% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2367 | 0.2114 |  |  |  |
| non-local-means denoising | 0.2440 | 0.1979 |  | 4% | 52% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2467 | 0.1879 |  |  |  |
| bilateral smoothing (deblocking) | 0.2291 | 0.1770 |  | 7% | 62% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2210 | 0.1960 |  |  |  |
| degraded, no mitigation | 0.2233 | 0.1745 |  |  |  |
