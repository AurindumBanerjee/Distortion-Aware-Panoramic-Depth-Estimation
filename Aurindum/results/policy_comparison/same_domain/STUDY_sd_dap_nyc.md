# Distortion study: sd_dap_nyc

model `dap` · 147 frames · 82 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0352, polar >= 60 deg 0.0232

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0644 | 0.0405 | 95% |
| blind lens-gain matching across the stitch lines | 0.0359 | 0.0236 | 52% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0351 | 0.0232 | 16% |
| non-local-means denoising | 0.0702 | 0.0674 | 99% |
| bilateral smoothing (deblocking) | 0.0448 | 0.0401 | 95% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.0915 | 0.0876 |  |  |  |
| re-level, known tilt (IMU) | 0.0477 | 0.0359 |  | 77% | 98% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 7.6 deg) | 0.0975 | 0.0742 |  | -4% | 46% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 | 0.0182 |  |  |
| degraded, no mitigation | 0.1372 | 0.4207 | 0.5238 |  |  |
| inpaint on the ERP grid | 0.0729 | 0.1569 | 0.1902 | 50% | 87% |
| inpaint in a polar tangent view | 0.0981 | 0.2478 | 0.2923 | 37% | 82% |
| tangent inpaint + floor / ceiling plane fill | 0.0470 | 0.0447 | 0.0417 | 94% | 93% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 | 0.0245 |  |  |
| degraded, no mitigation | 0.2990 | 0.6945 | 0.7129 |  |  |
| inpaint on the ERP grid | 0.1938 | 0.4512 | 0.4401 | 37% | 99% |
| inpaint in a polar tangent view | 0.2831 | 0.6477 | 0.6694 | 5% | 90% |
| tangent inpaint + floor / ceiling plane fill | 0.1532 | 0.2495 | 0.2938 | 58% | 99% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.0360 | 0.0231 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0365 | 0.0246 |  | 14% | 41% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 | 0.0381 |  |  |
| degraded, no mitigation | 0.0434 | 0.0328 | 0.0491 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0552 | 0.0381 | 0.1203 | -546% | 1% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.0387 | 0.0259 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0371 | 0.0256 |  | 45% | 48% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.1272 | 0.1500 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0487 | 0.0392 |  | 87% | 92% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.0583 | 0.0428 |  |  |  |
| non-local-means denoising | 0.0591 | 0.0510 |  | -14% | 39% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.1764 | 0.2041 |  |  |  |
| bilateral smoothing (deblocking) | 0.1638 | 0.1839 |  | 11% | 83% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0352 | 0.0232 |  |  |  |
| degraded, no mitigation | 0.0980 | 0.0771 |  |  |  |
