# Distortion study: da2_stanford

model `da2` · 40 frames · 28 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0738, polar >= 60 deg 0.0790

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0725 | 0.0802 | 40% |
| blind lens-gain matching across the stitch lines | 0.0735 | 0.0776 | 10% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0742 | 0.0856 | 75% |
| non-local-means denoising | 0.1609 | 0.1934 | 98% |
| bilateral smoothing (deblocking) | 0.0663 | 0.0739 | 32% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.1000 | 0.0896 |  |  |  |
| re-level, known tilt (IMU) | 0.0706 | 0.0818 |  | 95% | 90% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 3.0 deg) | 0.0896 | 0.0853 |  | 65% | 70% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 | 0.0476 |  |  |
| degraded, no mitigation | 0.1082 | 0.1391 | 0.1791 |  |  |
| inpaint on the ERP grid | 0.0640 | 0.0701 | 0.0295 | 111% | 100% |
| inpaint in a polar tangent view | 0.0614 | 0.0708 | 0.0314 | 114% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.0625 | 0.0711 | 0.0360 | 120% | 98% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 | 0.0708 |  |  |
| degraded, no mitigation | 0.1039 | 0.0900 | 0.0955 |  |  |
| inpaint on the ERP grid | 0.0660 | 0.0658 | 0.0675 | 85% | 78% |
| inpaint in a polar tangent view | 0.0926 | 0.1293 | 0.1295 | -47% | 32% |
| tangent inpaint + floor / ceiling plane fill | 0.0925 | 0.1230 | 0.1298 | -45% | 40% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.0736 | 0.0767 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0732 | 0.0768 |  | 94% | 72% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 | 0.0737 |  |  |
| degraded, no mitigation | 0.0722 | 0.0767 | 0.0737 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0719 | 0.0782 | 0.0804 | -238% | 10% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.0722 | 0.0731 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0731 | 0.0817 |  | 56% | 30% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.0774 | 0.0779 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0791 | 0.1012 |  | -12% | 45% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.0811 | 0.0932 |  |  |  |
| non-local-means denoising | 0.1188 | 0.1265 |  | -244% | 25% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.0785 | 0.0821 |  |  |  |
| bilateral smoothing (deblocking) | 0.0764 | 0.0847 |  | 36% | 62% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0738 | 0.0790 |  |  |  |
| degraded, no mitigation | 0.0724 | 0.0761 |  |  |  |
