# Distortion study: sd_da2_nyc

model `da2` · 147 frames · 82 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.6378, polar >= 60 deg 0.6955

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.6274 | 0.6959 | 39% |
| blind lens-gain matching across the stitch lines | 0.6402 | 0.6982 | 21% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.6421 | 0.7010 | 14% |
| non-local-means denoising | 0.7172 | 0.7673 | 85% |
| bilateral smoothing (deblocking) | 0.6662 | 0.7326 | 84% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.5629 | 0.6566 |  |  |  |
| re-level, known tilt (IMU) | 0.6507 | 0.7189 |  | 71% | 14% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 8.2 deg) | 0.5944 | 0.6780 |  | 88% | 24% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 | 0.7261 |  |  |
| degraded, no mitigation | 0.6305 | 0.7033 | 0.7210 |  |  |
| inpaint on the ERP grid | 0.6304 | 0.7042 | 0.7258 | 22% | 27% |
| inpaint in a polar tangent view | 0.6357 | 0.7353 | 0.7524 | -50% | 10% |
| tangent inpaint + floor / ceiling plane fill | 0.6355 | 0.7349 | 0.7555 | -50% | 11% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 | 0.6789 |  |  |
| degraded, no mitigation | 0.6688 | 0.7959 | 0.7784 |  |  |
| inpaint on the ERP grid | 0.7702 | 0.8390 | 0.8290 | -36% | 20% |
| inpaint in a polar tangent view | 0.8642 | 0.9052 | 0.8959 | -115% | 1% |
| tangent inpaint + floor / ceiling plane fill | 0.8640 | 0.9015 | 0.8941 | -111% | 1% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.6296 | 0.6896 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.6420 | 0.6980 |  | n/a | 20% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 | 0.6366 |  |  |
| degraded, no mitigation | 0.6596 | 0.7167 | 0.6557 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.6840 | 0.7481 | 0.6931 | -30% | 13% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.6475 | 0.7095 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.6487 | 0.7109 |  | 29% | 57% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.6972 | 0.7540 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.6553 | 0.7202 |  | 75% | 74% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.6712 | 0.7395 |  |  |  |
| non-local-means denoising | 0.6519 | 0.7243 |  | 61% | 74% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.6750 | 0.7483 |  |  |  |
| bilateral smoothing (deblocking) | 0.6628 | 0.7383 |  | 8% | 56% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6378 | 0.6955 |  |  |  |
| degraded, no mitigation | 0.6567 | 0.7402 |  |  |  |
