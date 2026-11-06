# Distortion study: da2_holo_out

model `da2` · 40 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.5161, polar >= 60 deg 0.5533

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.6230 | 0.6456 | 78% |
| blind lens-gain matching across the stitch lines | 0.5061 | 0.5392 | 32% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.5052 | 0.5344 | 8% |
| non-local-means denoising | 0.5076 | 0.5211 | 35% |
| bilateral smoothing (deblocking) | 0.4296 | 0.4493 | 8% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.4308 | 0.4209 |  |  |  |
| re-level, known tilt (IMU) | 0.4993 | 0.5111 |  | 100% | 28% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 9.4 deg) | 0.5865 | 0.6267 |  | -119% | 12% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 | 0.5561 |  |  |
| degraded, no mitigation | 0.6322 | 0.5883 | 0.5860 |  |  |
| inpaint on the ERP grid | 0.5449 | 0.5553 | 0.5525 | 46% | 52% |
| inpaint in a polar tangent view | 0.5641 | 0.5834 | 0.5749 | 19% | 50% |
| tangent inpaint + floor / ceiling plane fill | 0.5637 | 0.5802 | 0.5702 | 12% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 | 0.5459 |  |  |
| degraded, no mitigation | 0.5953 | 0.5908 | 0.5669 |  |  |
| inpaint on the ERP grid | 0.5327 | 0.5418 | 0.5375 | 75% | 65% |
| inpaint in a polar tangent view | 0.5351 | 0.5916 | 0.5716 | 50% | 62% |
| tangent inpaint + floor / ceiling plane fill | 0.5363 | 0.5914 | 0.5716 | 41% | 62% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.5188 | 0.5240 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.4803 | 0.5226 |  | 117% | 75% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 | 0.5113 |  |  |
| degraded, no mitigation | 0.5281 | 0.5612 | 0.5105 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.5373 | 0.5796 | 0.5256 | -59% | 35% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.4978 | 0.5078 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.5075 | 0.5227 |  | 15% | 22% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.5483 | 0.5248 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.5033 | 0.5161 |  | 112% | 57% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.4581 | 0.4600 |  |  |  |
| non-local-means denoising | 0.4927 | 0.5089 |  | -64% | 45% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.6008 | 0.5863 |  |  |  |
| bilateral smoothing (deblocking) | 0.5262 | 0.5306 |  | 34% | 70% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.5161 | 0.5533 |  |  |  |
| degraded, no mitigation | 0.6437 | 0.6580 |  |  |  |
