# Distortion study: midas_panox

model `midas_dpt_hybrid_384` · 40 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1877, polar >= 60 deg 0.1351

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.2185 | 0.1538 | 57% |
| blind lens-gain matching across the stitch lines | 0.1910 | 0.1285 | 18% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1877 | 0.1339 | 15% |
| non-local-means denoising | 0.2648 | 0.1465 | 68% |
| bilateral smoothing (deblocking) | 0.1949 | 0.1472 | 57% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.2153 | 0.1643 |  |  |  |
| re-level, known tilt (IMU) | 0.1921 | 0.1331 |  | 87% | 75% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 9.9 deg) | 0.2058 | 0.1714 |  | 43% | 65% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 | 0.0701 |  |  |
| degraded, no mitigation | 0.1826 | 0.1316 | 0.0699 |  |  |
| inpaint on the ERP grid | 0.2343 | 0.1125 | 0.0584 | 123% | 45% |
| inpaint in a polar tangent view | 0.2461 | 0.1245 | 0.0667 | 104% | 40% |
| tangent inpaint + floor / ceiling plane fill | 0.1810 | 0.1152 | 0.0520 | 162% | 60% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 | 0.1430 |  |  |
| degraded, no mitigation | 0.3080 | 0.3221 | 0.3082 |  |  |
| inpaint on the ERP grid | 0.2393 | 0.1595 | 0.1579 | 98% | 65% |
| inpaint in a polar tangent view | 0.2510 | 0.1437 | 0.1414 | 100% | 80% |
| tangent inpaint + floor / ceiling plane fill | 0.2163 | 0.1268 | 0.1237 | 101% | 78% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.2028 | 0.1272 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1970 | 0.1221 |  | 52% | 65% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 | 0.1874 |  |  |
| degraded, no mitigation | 0.1851 | 0.1299 | 0.1881 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.2018 | 0.1509 | 0.2242 | 102% | 20% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.2055 | 0.1315 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1923 | 0.1327 |  | 28% | 55% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.2040 | 0.1317 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2014 | 0.1321 |  | 75% | 57% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.2383 | 0.1360 |  |  |  |
| non-local-means denoising | 0.2761 | 0.1652 |  | 2% | 48% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.3063 | 0.2092 |  |  |  |
| bilateral smoothing (deblocking) | 0.2999 | 0.2348 |  | -1% | 45% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1877 | 0.1351 |  |  |  |
| degraded, no mitigation | 0.2468 | 0.1493 |  |  |  |
