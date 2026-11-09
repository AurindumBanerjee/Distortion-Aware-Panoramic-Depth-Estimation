# Distortion study: s100_dap_s3

model `dap` · 100 frames · 66 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0346, polar >= 60 deg 0.0284

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0543 | 0.0441 | 71% |
| blind lens-gain matching across the stitch lines | 0.0364 | 0.0293 | 37% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0344 | 0.0281 | 26% |
| non-local-means denoising | 0.0593 | 0.0435 | 91% |
| bilateral smoothing (deblocking) | 0.0352 | 0.0272 | 54% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.1329 | 0.1318 |  |  |  |
| re-level, known tilt (IMU) | 0.0404 | 0.0309 |  | 96% | 97% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 8.6 deg) | 0.0693 | 0.0590 |  | 57% | 81% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 | 0.0236 |  |  |
| degraded, no mitigation | 0.0929 | 0.1921 | 0.3682 |  |  |
| inpaint on the ERP grid | 0.0992 | 0.2100 | 0.3960 | -1% | 45% |
| inpaint in a polar tangent view | 0.0903 | 0.1923 | 0.3697 | 0% | 52% |
| tangent inpaint + floor / ceiling plane fill | 0.0888 | 0.1870 | 0.3609 | 1% | 59% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 | 0.0287 |  |  |
| degraded, no mitigation | 0.3751 | 0.7780 | 0.7705 |  |  |
| inpaint on the ERP grid | 0.1838 | 0.3100 | 0.2988 | 62% | 100% |
| inpaint in a polar tangent view | 0.3089 | 0.6230 | 0.6165 | 18% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.3024 | 0.6194 | 0.6125 | 20% | 100% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0360 | 0.0296 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0373 | 0.0276 |  | 34% | 55% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 | 0.0329 |  |  |
| degraded, no mitigation | 0.0353 | 0.0283 | 0.0363 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0385 | 0.0304 | 0.0570 | -245% | 16% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0343 | 0.0291 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0348 | 0.0286 |  | 74% | 50% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0423 | 0.0306 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0377 | 0.0280 |  | 53% | 67% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0637 | 0.0505 |  |  |  |
| non-local-means denoising | 0.0665 | 0.0469 |  | -10% | 34% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0968 | 0.0725 |  |  |  |
| bilateral smoothing (deblocking) | 0.0842 | 0.0652 |  | 15% | 86% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0346 | 0.0284 |  |  |  |
| degraded, no mitigation | 0.0764 | 0.0515 |  |  |  |
