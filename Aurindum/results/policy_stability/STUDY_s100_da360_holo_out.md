# Distortion study: s100_da360_holo_out

model `da360` · 71 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.2008, polar >= 60 deg 0.1764

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.1983 | 0.1746 | 15% |
| blind lens-gain matching across the stitch lines | 0.1987 | 0.1797 | 28% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2095 | 0.1760 | 18% |
| non-local-means denoising | 0.1739 | 0.1300 | 51% |
| bilateral smoothing (deblocking) | 0.2141 | 0.1870 | 65% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.2136 | 0.1952 |  |  |  |
| re-level, known tilt (IMU) | 0.2007 | 0.1612 |  | 115% | 65% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 12.6 deg) | 0.1807 | 0.1668 |  | 126% | 68% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 | 0.1000 |  |  |
| degraded, no mitigation | 0.1416 | 0.0863 | 0.0490 |  |  |
| inpaint on the ERP grid | 0.1622 | 0.1036 | 0.0440 | 105% | 54% |
| inpaint in a polar tangent view | 0.1308 | 0.0707 | 0.0320 | 102% | 72% |
| tangent inpaint + floor / ceiling plane fill | 0.1324 | 0.0707 | 0.0395 | 94% | 62% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 | 0.1684 |  |  |
| degraded, no mitigation | 0.1562 | 0.1188 | 0.1651 |  |  |
| inpaint on the ERP grid | 0.1423 | 0.0730 | 0.1065 | 5% | 46% |
| inpaint in a polar tangent view | 0.1489 | 0.0542 | 0.1388 | 4% | 56% |
| tangent inpaint + floor / ceiling plane fill | 0.1656 | 0.1072 | 0.1717 | -5% | 37% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.1986 | 0.1826 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.2011 | 0.1826 |  | 99% | 38% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 | 0.2137 |  |  |
| degraded, no mitigation | 0.1896 | 0.1646 | 0.2014 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.5344 | 0.7782 | 0.4948 | -1713% | 7% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.2008 | 0.1760 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.2032 | 0.1772 |  | 22% | 41% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.2175 | 0.1704 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.1974 | 0.1749 |  | 74% | 72% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.1835 | 0.1229 |  |  |  |
| non-local-means denoising | 0.1761 | 0.0843 |  | -23% | 58% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.2735 | 0.1053 |  |  |  |
| bilateral smoothing (deblocking) | 0.2606 | 0.0743 |  | 2% | 54% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.2008 | 0.1764 |  |  |  |
| degraded, no mitigation | 0.2075 | 0.1728 |  |  |  |
