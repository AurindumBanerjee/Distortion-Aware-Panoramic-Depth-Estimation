# Distortion study: da2_nyc

model `da2` · 40 frames · 40 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.6345, polar >= 60 deg 0.6907

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.6264 | 0.6872 | 38% |
| blind lens-gain matching across the stitch lines | 0.6392 | 0.6871 | 28% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.6392 | 0.6914 | 15% |
| non-local-means denoising | 0.7198 | 0.7793 | 88% |
| bilateral smoothing (deblocking) | 0.6713 | 0.7323 | 90% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.5591 | 0.6501 |  |  |  |
| re-level, known tilt (IMU) | 0.6504 | 0.7217 |  | 49% | 10% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 7.9 deg) | 0.5910 | 0.6795 |  | 95% | 25% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 | 0.7143 |  |  |
| degraded, no mitigation | 0.6326 | 0.7027 | 0.7203 |  |  |
| inpaint on the ERP grid | 0.6305 | 0.7031 | 0.7306 | 18% | 32% |
| inpaint in a polar tangent view | 0.6346 | 0.7356 | 0.7516 | -65% | 10% |
| tangent inpaint + floor / ceiling plane fill | 0.6345 | 0.7359 | 0.7610 | -65% | 10% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 | 0.6709 |  |  |
| degraded, no mitigation | 0.6629 | 0.7937 | 0.7767 |  |  |
| inpaint on the ERP grid | 0.7589 | 0.8423 | 0.8348 | -33% | 25% |
| inpaint in a polar tangent view | 0.8484 | 0.9010 | 0.8915 | -110% | 2% |
| tangent inpaint + floor / ceiling plane fill | 0.8486 | 0.8988 | 0.8899 | -110% | 2% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.6274 | 0.6802 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.6372 | 0.6864 |  | n/a | 25% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 | 0.6374 |  |  |
| degraded, no mitigation | 0.6720 | 0.7265 | 0.6622 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.6804 | 0.7440 | 0.6940 | -34% | 20% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.6462 | 0.7043 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.6490 | 0.6957 |  | 38% | 60% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.6924 | 0.7359 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.6517 | 0.7214 |  | 85% | 72% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.6710 | 0.7437 |  |  |  |
| non-local-means denoising | 0.6501 | 0.7288 |  | 40% | 72% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.6802 | 0.7499 |  |  |  |
| bilateral smoothing (deblocking) | 0.6686 | 0.7501 |  | -1% | 45% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.6345 | 0.6907 |  |  |  |
| degraded, no mitigation | 0.6723 | 0.7476 |  |  |  |
