# Distortion study: s100_da2_panox

model `da2` · 100 frames · 8 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1391, polar >= 60 deg 0.1157

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1437 | 0.1443 | 51% |
| blind lens-gain matching across the stitch lines | 0.1382 | 0.1178 | 40% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1391 | 0.1175 | 5% |
| non-local-means denoising | 0.1963 | 0.1950 | 70% |
| bilateral smoothing (deblocking) | 0.1764 | 0.1298 | 45% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.1967 | 0.2012 |  |  |  |
| re-level, known tilt (IMU) | 0.1444 | 0.1177 |  | 97% | 52% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 4.8 deg) | 0.1924 | 0.1957 |  | 61% | 56% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 | 0.1267 |  |  |
| degraded, no mitigation | 0.2160 | 0.2319 | 0.3493 |  |  |
| inpaint on the ERP grid | 0.1527 | 0.1265 | 0.1779 | 80% | 74% |
| inpaint in a polar tangent view | 0.1498 | 0.1251 | 0.1711 | 92% | 65% |
| tangent inpaint + floor / ceiling plane fill | 0.1490 | 0.1225 | 0.1521 | 98% | 62% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 | 0.1151 |  |  |
| degraded, no mitigation | 0.2027 | 0.2963 | 0.2915 |  |  |
| inpaint on the ERP grid | 0.2218 | 0.3408 | 0.3526 | -25% | 54% |
| inpaint in a polar tangent view | 0.2407 | 0.3690 | 0.3710 | -43% | 45% |
| tangent inpaint + floor / ceiling plane fill | 0.2318 | 0.3621 | 0.3676 | -32% | 51% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.1367 | 0.1237 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1378 | 0.1179 |  | 48% | 57% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 | 0.1239 |  |  |
| degraded, no mitigation | 0.1452 | 0.1079 | 0.1303 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1596 | 0.1143 | 0.1382 | -92% | 21% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.1395 | 0.1210 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1428 | 0.1170 |  | 92% | 42% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.2205 | 0.1502 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1868 | 0.1383 |  | 66% | 76% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.1998 | 0.1817 |  |  |  |
| non-local-means denoising | 0.2383 | 0.1855 |  | -26% | 40% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.2419 | 0.2456 |  |  |  |
| bilateral smoothing (deblocking) | 0.2734 | 0.2608 |  | -11% | 37% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1391 | 0.1157 |  |  |  |
| degraded, no mitigation | 0.2141 | 0.1600 |  |  |  |
