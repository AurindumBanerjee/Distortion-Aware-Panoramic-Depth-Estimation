# Distortion study: s100_da2_holo_out

model `da2` · 71 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.5434, polar >= 60 deg 0.5677

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.6834 | 0.6785 | 80% |
| blind lens-gain matching across the stitch lines | 0.5274 | 0.5497 | 28% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.5277 | 0.5578 | 13% |
| non-local-means denoising | 0.4868 | 0.5231 | 37% |
| bilateral smoothing (deblocking) | 0.4307 | 0.4484 | 10% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.4512 | 0.4538 |  |  |  |
| re-level, known tilt (IMU) | 0.5364 | 0.5532 |  | 100% | 21% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 8.8 deg) | 0.6327 | 0.6422 |  | -57% | 13% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 | 0.5687 |  |  |
| degraded, no mitigation | 0.6314 | 0.6058 | 0.6002 |  |  |
| inpaint on the ERP grid | 0.5751 | 0.5863 | 0.5887 | 46% | 55% |
| inpaint in a polar tangent view | 0.5768 | 0.5961 | 0.6061 | 19% | 51% |
| tangent inpaint + floor / ceiling plane fill | 0.5761 | 0.5939 | 0.6000 | 27% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 | 0.5656 |  |  |
| degraded, no mitigation | 0.6163 | 0.6219 | 0.6027 |  |  |
| inpaint on the ERP grid | 0.5423 | 0.5531 | 0.5493 | 84% | 62% |
| inpaint in a polar tangent view | 0.5482 | 0.5794 | 0.5704 | 52% | 62% |
| tangent inpaint + floor / ceiling plane fill | 0.5395 | 0.5731 | 0.5666 | 46% | 59% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.5201 | 0.5471 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.4995 | 0.5376 |  | 74% | 79% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 | 0.5207 |  |  |
| degraded, no mitigation | 0.5458 | 0.5686 | 0.5416 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.5464 | 0.5861 | 0.5697 | -57% | 37% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.4740 | 0.5008 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.5084 | 0.5368 |  | 21% | 25% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.5696 | 0.6207 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.5072 | 0.5347 |  | 112% | 61% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.5000 | 0.5274 |  |  |  |
| non-local-means denoising | 0.4920 | 0.5544 |  | -96% | 48% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.6102 | 0.6229 |  |  |  |
| bilateral smoothing (deblocking) | 0.5898 | 0.6155 |  | 31% | 61% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5434 | 0.5677 |  |  |  |
| degraded, no mitigation | 0.6187 | 0.6565 |  |  |  |
