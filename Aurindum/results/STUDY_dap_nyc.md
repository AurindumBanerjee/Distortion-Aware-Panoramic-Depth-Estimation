# Distortion study: dap_nyc

model `dap` · 40 frames · 40 clusters · AbsRel (none)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0334, polar >= 60 deg 0.0233

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0630 | 0.0384 | 95% |
| blind lens-gain matching across the stitch lines | 0.0351 | 0.0240 | 65% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0328 | 0.0232 | 28% |
| non-local-means denoising | 0.0702 | 0.0724 | 100% |
| bilateral smoothing (deblocking) | 0.0445 | 0.0414 | 98% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.0936 | 0.0927 |  |  |  |
| re-level, known tilt (IMU) | 0.0478 | 0.0359 |  | 78% | 98% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 7.7 deg) | 0.1011 | 0.0784 |  | -9% | 45% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 | 0.0169 |  |  |
| degraded, no mitigation | 0.1328 | 0.4148 | 0.5031 |  |  |
| inpaint on the ERP grid | 0.0732 | 0.1557 | 0.1807 | 55% | 90% |
| inpaint in a polar tangent view | 0.0916 | 0.2281 | 0.2671 | 43% | 78% |
| tangent inpaint + floor / ceiling plane fill | 0.0496 | 0.0435 | 0.0437 | 93% | 92% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 | 0.0242 |  |  |
| degraded, no mitigation | 0.2999 | 0.7014 | 0.7170 |  |  |
| inpaint on the ERP grid | 0.1945 | 0.4364 | 0.4224 | 40% | 98% |
| inpaint in a polar tangent view | 0.2822 | 0.6509 | 0.6730 | 6% | 92% |
| tangent inpaint + floor / ceiling plane fill | 0.1603 | 0.2576 | 0.3128 | 58% | 100% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.0357 | 0.0236 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0358 | 0.0254 |  | 6% | 38% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 | 0.0368 |  |  |
| degraded, no mitigation | 0.0440 | 0.0342 | 0.0479 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.0523 | 0.0367 | 0.1057 | -598% | 0% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.0392 | 0.0279 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0359 | 0.0241 |  | 52% | 50% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.1234 | 0.1507 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0479 | 0.0408 |  | 87% | 92% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.0570 | 0.0380 |  |  |  |
| non-local-means denoising | 0.0590 | 0.0453 |  | -25% | 28% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.1664 | 0.1888 |  |  |  |
| bilateral smoothing (deblocking) | 0.1540 | 0.1749 |  | 11% | 80% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0334 | 0.0233 |  |  |  |
| degraded, no mitigation | 0.0976 | 0.0766 |  |  |  |
