# Distortion study: da360_holo_out

model `da360` · 40 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2053, polar >= 60 deg 0.1695

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1958 | 0.1795 | 15% |
| blind lens-gain matching across the stitch lines | 0.2042 | 0.1716 | 30% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2012 | 0.1652 | 10% |
| non-local-means denoising | 0.1730 | 0.1218 | 45% |
| bilateral smoothing (deblocking) | 0.2085 | 0.1664 | 57% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.2186 | 0.1888 |  |  |  |
| re-level, known tilt (IMU) | 0.1973 | 0.1650 |  | 115% | 65% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 12.9 deg) | 0.1796 | 0.1620 |  | 141% | 75% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 | 0.0911 |  |  |
| degraded, no mitigation | 0.1352 | 0.0832 | 0.0488 |  |  |
| inpaint on the ERP grid | 0.1584 | 0.0803 | 0.0403 | 118% | 60% |
| inpaint in a polar tangent view | 0.1300 | 0.0701 | 0.0303 | 128% | 78% |
| tangent inpaint + floor / ceiling plane fill | 0.1331 | 0.0701 | 0.0376 | 115% | 62% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 | 0.1823 |  |  |
| degraded, no mitigation | 0.1549 | 0.1154 | 0.1957 |  |  |
| inpaint on the ERP grid | 0.1363 | 0.0750 | 0.1456 | 5% | 45% |
| inpaint in a polar tangent view | 0.1454 | 0.0780 | 0.1697 | 4% | 52% |
| tangent inpaint + floor / ceiling plane fill | 0.1735 | 0.1166 | 0.2088 | -6% | 32% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.1933 | 0.1738 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2034 | 0.1696 |  | 24% | 45% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 | 0.2175 |  |  |
| degraded, no mitigation | 0.1865 | 0.1594 | 0.2048 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.5433 | 0.7946 | 0.5019 | -1713% | 5% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.1894 | 0.1533 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.1939 | 0.1625 |  | 18% | 38% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.2235 | 0.1624 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.2020 | 0.1761 |  | 73% | 70% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.1807 | 0.1080 |  |  |  |
| non-local-means denoising | 0.1872 | 0.0874 |  | -62% | 48% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.2906 | 0.1041 |  |  |  |
| bilateral smoothing (deblocking) | 0.2678 | 0.0756 |  | 6% | 55% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2053 | 0.1695 |  |  |  |
| degraded, no mitigation | 0.2074 | 0.1580 |  |  |  |
