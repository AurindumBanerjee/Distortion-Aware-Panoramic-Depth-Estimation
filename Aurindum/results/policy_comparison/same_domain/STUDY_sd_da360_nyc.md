# Distortion study: sd_da360_nyc

model `da360` · 147 frames · 82 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0629, polar >= 60 deg 0.0355

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0662 | 0.0366 | 47% |
| blind lens-gain matching across the stitch lines | 0.0640 | 0.0353 | 37% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0628 | 0.0363 | 12% |
| non-local-means denoising | 0.0805 | 0.0453 | 91% |
| bilateral smoothing (deblocking) | 0.0699 | 0.0397 | 76% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.0690 | 0.0402 |  |  |  |
| re-level, known tilt (IMU) | 0.0660 | 0.0361 |  | 50% | 66% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 1.3 deg) | 0.0690 | 0.0371 |  | 14% | 49% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 | 0.0130 |  |  |
| degraded, no mitigation | 0.0664 | 0.0404 | 0.0157 |  |  |
| inpaint on the ERP grid | 0.0699 | 0.0418 | 0.0173 | -38% | 26% |
| inpaint in a polar tangent view | 0.0675 | 0.0424 | 0.0154 | -32% | 24% |
| tangent inpaint + floor / ceiling plane fill | 0.0686 | 0.0450 | 0.0230 | -29% | 44% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 | 0.0431 |  |  |
| degraded, no mitigation | 0.1371 | 0.1810 | 0.1964 |  |  |
| inpaint on the ERP grid | 0.1439 | 0.1792 | 0.2051 | -5% | 46% |
| inpaint in a polar tangent view | 0.1758 | 0.2083 | 0.2359 | -24% | 31% |
| tangent inpaint + floor / ceiling plane fill | 0.1749 | 0.2185 | 0.2412 | -29% | 30% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.0637 | 0.0348 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0646 | 0.0358 |  | -38% | 46% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 | 0.0607 |  |  |
| degraded, no mitigation | 0.0672 | 0.0366 | 0.0696 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.4242 | 0.4313 | 0.4518 | -2492% | 2% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.0654 | 0.0375 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0650 | 0.0376 |  | 26% | 55% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.0909 | 0.0462 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0703 | 0.0364 |  | 70% | 92% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.0793 | 0.0431 |  |  |  |
| non-local-means denoising | 0.0829 | 0.0489 |  | -28% | 31% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.1299 | 0.0689 |  |  |  |
| bilateral smoothing (deblocking) | 0.1281 | 0.0681 |  | 3% | 56% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0629 | 0.0355 |  |  |  |
| degraded, no mitigation | 0.0931 | 0.0449 |  |  |  |
