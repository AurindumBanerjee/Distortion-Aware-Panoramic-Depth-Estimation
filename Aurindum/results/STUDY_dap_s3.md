# Distortion study: dap_s3

model `dap` · 40 frames · 33 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0324, polar >= 60 deg 0.0255

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0495 | 0.0404 | 72% |
| blind lens-gain matching across the stitch lines | 0.0340 | 0.0250 | 40% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0331 | 0.0247 | 32% |
| non-local-means denoising | 0.0554 | 0.0375 | 88% |
| bilateral smoothing (deblocking) | 0.0343 | 0.0268 | 68% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.1203 | 0.1168 |  |  |  |
| re-level, known tilt (IMU) | 0.0379 | 0.0262 |  | 96% | 98% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 8.6 deg) | 0.0631 | 0.0519 |  | 66% | 88% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 | 0.0238 |  |  |
| degraded, no mitigation | 0.0868 | 0.1885 | 0.3721 |  |  |
| inpaint on the ERP grid | 0.0875 | 0.1823 | 0.3589 | -2% | 48% |
| inpaint in a polar tangent view | 0.0849 | 0.1829 | 0.3491 | 1% | 55% |
| tangent inpaint + floor / ceiling plane fill | 0.0801 | 0.1538 | 0.3064 | 6% | 68% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 | 0.0261 |  |  |
| degraded, no mitigation | 0.3659 | 0.7667 | 0.7610 |  |  |
| inpaint on the ERP grid | 0.1626 | 0.2932 | 0.2861 | 64% | 100% |
| inpaint in a polar tangent view | 0.3024 | 0.6144 | 0.6085 | 19% | 100% |
| tangent inpaint + floor / ceiling plane fill | 0.2805 | 0.5786 | 0.5666 | 25% | 100% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.0343 | 0.0262 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0339 | 0.0264 |  | 48% | 62% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 | 0.0323 |  |  |
| degraded, no mitigation | 0.0310 | 0.0251 | 0.0326 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0345 | 0.0246 | 0.0551 | -242% | 12% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.0331 | 0.0228 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0325 | 0.0247 |  | 47% | 38% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.0390 | 0.0279 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0347 | 0.0240 |  | 57% | 65% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.0558 | 0.0443 |  |  |  |
| non-local-means denoising | 0.0567 | 0.0422 |  | -13% | 42% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.0757 | 0.0614 |  |  |  |
| bilateral smoothing (deblocking) | 0.0674 | 0.0472 |  | 14% | 75% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0324 | 0.0255 |  |  |  |
| degraded, no mitigation | 0.0639 | 0.0461 |  |  |  |
