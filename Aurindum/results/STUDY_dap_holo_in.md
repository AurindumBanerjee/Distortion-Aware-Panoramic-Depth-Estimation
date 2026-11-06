# Distortion study: dap_holo_in

model `dap` · 40 frames · 12 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.1387, polar >= 60 deg 0.1195

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1243 | 0.1031 | 40% |
| blind lens-gain matching across the stitch lines | 0.1433 | 0.1151 | 22% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1403 | 0.1194 | 35% |
| non-local-means denoising | 0.1924 | 0.1839 | 80% |
| bilateral smoothing (deblocking) | 0.1686 | 0.1229 | 72% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.2018 | 0.1903 |  |  |  |
| re-level, known tilt (IMU) | 0.1480 | 0.1201 |  | 92% | 88% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 9.2 deg) | 0.1500 | 0.1431 |  | 66% | 78% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 | 0.1296 |  |  |
| degraded, no mitigation | 0.1941 | 0.2409 | 0.7101 |  |  |
| inpaint on the ERP grid | 0.1856 | 0.2261 | 0.4996 | 36% | 92% |
| inpaint in a polar tangent view | 0.1849 | 0.2151 | 0.5549 | 28% | 92% |
| tangent inpaint + floor / ceiling plane fill | 0.1729 | 0.1938 | 0.5432 | 34% | 92% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 | 0.1180 |  |  |
| degraded, no mitigation | 0.3984 | 0.7876 | 0.7850 |  |  |
| inpaint on the ERP grid | 0.2548 | 0.3057 | 0.3056 | 72% | 98% |
| inpaint in a polar tangent view | 0.3521 | 0.6053 | 0.6124 | 22% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.2672 | 0.3738 | 0.3851 | 60% | 98% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.1446 | 0.1183 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.1462 | 0.1161 |  | 67% | 62% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 | 0.1459 |  |  |
| degraded, no mitigation | 0.1489 | 0.1279 | 0.1513 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1537 | 0.1218 | 0.1816 | -124% | 15% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.1519 | 0.1266 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1445 | 0.1145 |  | 83% | 70% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.2240 | 0.1998 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1785 | 0.1258 |  | 85% | 80% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.1996 | 0.1851 |  |  |  |
| non-local-means denoising | 0.1922 | 0.1833 |  | 30% | 57% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.4744 | 0.4056 |  |  |  |
| bilateral smoothing (deblocking) | 0.4156 | 0.4094 |  | 12% | 85% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.1387 | 0.1195 |  |  |  |
| degraded, no mitigation | 0.3451 | 0.2932 |  |  |  |
