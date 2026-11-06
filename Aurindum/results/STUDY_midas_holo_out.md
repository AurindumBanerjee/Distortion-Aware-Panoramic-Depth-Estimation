# Distortion study: midas_holo_out

model `midas_dpt_hybrid_384` · 40 frames · 3 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.3139, polar >= 60 deg 0.2014

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.3732 | 0.3234 | 68% |
| blind lens-gain matching across the stitch lines | 0.3240 | 0.1958 | 42% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.3080 | 0.2014 | 10% |
| non-local-means denoising | 0.3918 | 0.2855 | 90% |
| bilateral smoothing (deblocking) | 0.3770 | 0.3310 | 82% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.4142 | 0.3856 |  |  |  |
| re-level, known tilt (IMU) | 0.3661 | 0.3250 |  | 36% | 78% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 14.4 deg) | 0.4227 | 0.4072 |  | 0% | 50% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 | 0.1468 |  |  |
| degraded, no mitigation | 0.2766 | 0.1451 | 0.0795 |  |  |
| inpaint on the ERP grid | 0.3330 | 0.1922 | 0.1272 | 9% | 22% |
| inpaint in a polar tangent view | 0.3260 | 0.1841 | 0.1421 | 15% | 22% |
| tangent inpaint + floor / ceiling plane fill | 0.2985 | 0.1538 | 0.0859 | 125% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 | 0.2330 |  |  |
| degraded, no mitigation | 0.3145 | 0.2309 | 0.2784 |  |  |
| inpaint on the ERP grid | 0.3168 | 0.1961 | 0.2390 | 73% | 70% |
| inpaint in a polar tangent view | 0.3535 | 0.1886 | 0.2193 | 87% | 70% |
| tangent inpaint + floor / ceiling plane fill | 0.3543 | 0.1814 | 0.2262 | 100% | 62% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.3222 | 0.2243 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.3288 | 0.2029 |  | 90% | 50% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 | 0.3337 |  |  |
| degraded, no mitigation | 0.3387 | 0.2236 | 0.3664 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.3408 | 0.2160 | 0.3709 | -51% | 42% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.3270 | 0.1904 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.3305 | 0.1895 |  | 49% | 50% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.4453 | 0.3635 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.3344 | 0.1977 |  | 81% | 98% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.3944 | 0.2607 |  |  |  |
| non-local-means denoising | 0.4175 | 0.2811 |  | -25% | 40% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.5045 | 0.3734 |  |  |  |
| bilateral smoothing (deblocking) | 0.5363 | 0.4002 |  | -9% | 35% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.3139 | 0.2014 |  |  |  |
| degraded, no mitigation | 0.4848 | 0.4813 |  |  |  |
