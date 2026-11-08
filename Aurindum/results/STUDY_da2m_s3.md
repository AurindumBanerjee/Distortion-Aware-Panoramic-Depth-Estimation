# Distortion study: da2m_s3

model `da2` · 40 frames · 33 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0429, polar >= 60 deg 0.0434

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0548 | 0.0473 | 78% |
| blind lens-gain matching across the stitch lines | 0.0428 | 0.0429 | 20% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0418 | 0.0425 | 25% |
| non-local-means denoising | 0.0785 | 0.0542 | 88% |
| bilateral smoothing (deblocking) | 0.0470 | 0.0421 | 48% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0809 | 0.0721 |  |  |  |
| re-level, known tilt (IMU) | 0.0489 | 0.0437 |  | 99% | 90% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 5.1 deg) | 0.0708 | 0.0628 |  | 58% | 62% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 | 0.0322 |  |  |
| degraded, no mitigation | 0.1067 | 0.1382 | 0.1998 |  |  |
| inpaint on the ERP grid | 0.0435 | 0.0505 | 0.0604 | 88% | 95% |
| inpaint in a polar tangent view | 0.0449 | 0.0434 | 0.0520 | 93% | 95% |
| tangent inpaint + floor / ceiling plane fill | 0.0475 | 0.0448 | 0.0520 | 91% | 95% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 | 0.0438 |  |  |
| degraded, no mitigation | 0.1369 | 0.1566 | 0.1632 |  |  |
| inpaint on the ERP grid | 0.0871 | 0.0752 | 0.0900 | 67% | 92% |
| inpaint in a polar tangent view | 0.1256 | 0.1584 | 0.1642 | 21% | 50% |
| tangent inpaint + floor / ceiling plane fill | 0.1256 | 0.1566 | 0.1634 | 21% | 50% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0461 | 0.0405 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0453 | 0.0429 |  | 56% | 60% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 | 0.0450 |  |  |
| degraded, no mitigation | 0.0420 | 0.0427 | 0.0455 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0422 | 0.0412 | 0.0521 | -189% | 28% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0452 | 0.0383 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0434 | 0.0447 |  | 64% | 28% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0556 | 0.0432 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0499 | 0.0461 |  | 55% | 62% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0737 | 0.0577 |  |  |  |
| non-local-means denoising | 0.0784 | 0.0588 |  | -29% | 42% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0842 | 0.0699 |  |  |  |
| bilateral smoothing (deblocking) | 0.0783 | 0.0603 |  | 5% | 62% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0429 | 0.0434 |  |  |  |
| degraded, no mitigation | 0.0673 | 0.0527 |  |  |  |
