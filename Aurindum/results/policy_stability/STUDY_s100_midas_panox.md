# Distortion study: s100_midas_panox

model `midas_dpt_hybrid_384` · 100 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1887, polar >= 60 deg 0.1427

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2053 | 0.1554 | 63% |
| blind lens-gain matching across the stitch lines | 0.1931 | 0.1505 | 30% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1871 | 0.1427 | 11% |
| non-local-means denoising | 0.2553 | 0.1512 | 66% |
| bilateral smoothing (deblocking) | 0.1934 | 0.1511 | 50% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.2154 | 0.1667 |  |  |  |
| re-level, known tilt (IMU) | 0.1961 | 0.1431 |  | 85% | 80% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 9.6 deg) | 0.2143 | 0.1716 |  | 32% | 70% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 | 0.0676 |  |  |
| degraded, no mitigation | 0.1810 | 0.1463 | 0.0723 |  |  |
| inpaint on the ERP grid | 0.2186 | 0.1249 | 0.0602 | 116% | 49% |
| inpaint in a polar tangent view | 0.2380 | 0.1386 | 0.0670 | 98% | 47% |
| tangent inpaint + floor / ceiling plane fill | 0.1823 | 0.1332 | 0.0521 | 162% | 60% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 | 0.1484 |  |  |
| degraded, no mitigation | 0.3098 | 0.3403 | 0.3337 |  |  |
| inpaint on the ERP grid | 0.2434 | 0.1653 | 0.1675 | 94% | 67% |
| inpaint in a polar tangent view | 0.2437 | 0.1458 | 0.1574 | 99% | 78% |
| tangent inpaint + floor / ceiling plane fill | 0.2225 | 0.1180 | 0.1212 | 101% | 78% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.1988 | 0.1403 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1961 | 0.1435 |  | 54% | 63% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 | 0.1942 |  |  |
| degraded, no mitigation | 0.1881 | 0.1392 | 0.1912 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2060 | 0.1513 | 0.2213 | 39% | 21% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.1986 | 0.1494 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1952 | 0.1401 |  | 51% | 54% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.2024 | 0.1370 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2040 | 0.1406 |  | 71% | 57% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.2216 | 0.1271 |  |  |  |
| non-local-means denoising | 0.2791 | 0.1684 |  | 12% | 45% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.3027 | 0.2102 |  |  |  |
| bilateral smoothing (deblocking) | 0.2981 | 0.2334 |  | 0% | 48% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1887 | 0.1427 |  |  |  |
| degraded, no mitigation | 0.2383 | 0.1451 |  |  |  |
