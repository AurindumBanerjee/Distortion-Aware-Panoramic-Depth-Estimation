# Distortion study: da360_nyc

model `da360` · 40 frames · 40 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0643, polar >= 60 deg 0.0373

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0663 | 0.0391 | 45% |
| blind lens-gain matching across the stitch lines | 0.0652 | 0.0380 | 35% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0642 | 0.0393 | 8% |
| non-local-means denoising | 0.0817 | 0.0475 | 92% |
| bilateral smoothing (deblocking) | 0.0712 | 0.0439 | 75% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.0688 | 0.0406 |  |  |  |
| re-level, known tilt (IMU) | 0.0682 | 0.0377 |  | 56% | 65% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 1.3 deg) | 0.0700 | 0.0406 |  | 23% | 52% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 | 0.0101 |  |  |
| degraded, no mitigation | 0.0665 | 0.0439 | 0.0140 |  |  |
| inpaint on the ERP grid | 0.0701 | 0.0446 | 0.0282 | -40% | 12% |
| inpaint in a polar tangent view | 0.0680 | 0.0446 | 0.0148 | -28% | 22% |
| tangent inpaint + floor / ceiling plane fill | 0.0732 | 0.0531 | 0.0276 | -28% | 42% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 | 0.0424 |  |  |
| degraded, no mitigation | 0.1328 | 0.1873 | 0.2007 |  |  |
| inpaint on the ERP grid | 0.1658 | 0.2335 | 0.2245 | -20% | 42% |
| inpaint in a polar tangent view | 0.1849 | 0.2249 | 0.2385 | -25% | 25% |
| tangent inpaint + floor / ceiling plane fill | 0.1788 | 0.2342 | 0.2450 | -29% | 28% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.0649 | 0.0374 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0650 | 0.0376 |  | -9% | 50% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 | 0.0599 |  |  |
| degraded, no mitigation | 0.0675 | 0.0395 | 0.0658 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.3763 | 0.3607 | 0.4199 | -2069% | 2% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.0668 | 0.0381 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0672 | 0.0391 |  | 24% | 50% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.0912 | 0.0498 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0713 | 0.0383 |  | 76% | 92% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.0786 | 0.0433 |  |  |  |
| non-local-means denoising | 0.0838 | 0.0457 |  | -17% | 40% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.1289 | 0.0674 |  |  |  |
| bilateral smoothing (deblocking) | 0.1258 | 0.0666 |  | -3% | 42% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0643 | 0.0373 |  |  |  |
| degraded, no mitigation | 0.0897 | 0.0464 |  |  |  |
