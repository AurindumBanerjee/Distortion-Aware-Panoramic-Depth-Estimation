# Distortion study: s100_da360_holo_in

model `da360` · 100 frames · 12 clusters · AbsRel (align-all)

Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.

Clean: all 0.0589, polar >= 60 deg 0.0536

**Blind mitigations on CLEAN images (do-no-harm check)**

| mitigation | all | polar | worse than clean (frames) |
|---|---:|---:|---:|
| re-level, tilt estimated from the predicted floor / ceiling | 0.0598 | 0.0551 | 46% |
| blind lens-gain matching across the stitch lines | 0.0593 | 0.0537 | 35% |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0602 | 0.0564 | 40% |
| non-local-means denoising | 0.0799 | 0.0658 | 72% |
| bilateral smoothing (deblocking) | 0.0619 | 0.0530 | 70% |

## Camera tilt (12 deg pitch, 8 deg roll)

*Cause:* Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.0645 | 0.0555 |  |  |  |
| re-level, known tilt (IMU) | 0.0580 | 0.0566 |  | 83% | 64% |
| re-level, tilt estimated from the predicted floor / ceiling (residual tilt median 12.2 deg) | 0.0608 | 0.0523 |  | 57% | 57% |

## Tripod / operator occlusion at the nadir (below -62 deg)

*Cause:* Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black disk over it. The floor under the camera is then unknown to the model.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 | 0.0853 |  |  |
| degraded, no mitigation | 0.0556 | 0.0501 | 0.0895 |  |  |
| inpaint on the ERP grid | 0.0611 | 0.0570 | 0.1056 | -37% | 34% |
| inpaint in a polar tangent view | 0.0555 | 0.0483 | 0.0893 | 0% | 51% |
| tangent inpaint + floor / ceiling plane fill | 0.0570 | 0.0495 | 0.0893 | -3% | 48% |

## Limited vertical field of view (only +-50 deg captured)

*Cause:* Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 | 0.0547 |  |  |
| degraded, no mitigation | 0.0749 | 0.0795 | 0.0709 |  |  |
| inpaint on the ERP grid | 0.1002 | 0.1082 | 0.1053 | -81% | 26% |
| inpaint in a polar tangent view | 0.1024 | 0.1053 | 0.1016 | -46% | 31% |
| tangent inpaint + floor / ceiling plane fill | 0.0936 | 0.1085 | 0.1063 | -75% | 29% |

## Exposure / white-balance mismatch between the two lenses

*Cause:* Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and the stitch lines (longitude +-90 deg) show a step.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.0598 | 0.0589 |  |  |  |
| blind lens-gain matching across the stitch lines | 0.0603 | 0.0557 |  | 64% | 44% |

## Stitching parallax of a dual-lens rig (5 cm baseline)

*Cause:* The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, so nearer objects are displaced differently in each lens and tear or double at the stitch lines (longitude +-90 deg), worst for furniture and people close to the camera.

| method | all | polar >= 60 | affected region | recovery (region) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 | 0.0579 |  |  |
| degraded, no mitigation | 0.0596 | 0.0563 | 0.0569 |  |  |
| inpaint the stitch blend band (known seam geometry) | 0.1814 | 0.1546 | 0.2748 | -1282% | 5% |

## Residual fisheye vignetting (seams 55% darker)

*Cause:* Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.0592 | 0.0562 |  |  |  |
| blind flat-field from the brightness-vs-lens-angle profile | 0.0601 | 0.0577 |  | 72% | 45% |

## Camera shake during exposure (yaw, 9 px)

*Cause:* Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every row by the same longitude arc.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.0753 | 0.0669 |  |  |  |
| Wiener deconvolution, known yaw kernel (gyro) | 0.0689 | 0.0672 |  | 47% | 68% |

## Low-light sensor noise

*Cause:* Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.0747 | 0.0680 |  |  |  |
| non-local-means denoising | 0.0857 | 0.0759 |  | -18% | 28% |

## Heavy JPEG compression (quality 8)

*Cause:* Streaming 360 video, web / social uploads and storage-limited capture.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.1668 | 0.1211 |  |  |  |
| bilateral smoothing (deblocking) | 0.1497 | 0.1184 |  | 2% | 51% |

## Low resolution (4x down-sampled)

*Cause:* Thumbnails, low-bit-rate streams, cheap cameras.

| method | all | polar >= 60 | - | recovery (all) | better than degraded |
|---|---:|---:|---:|---:|---:|
| clean image | 0.0589 | 0.0536 |  |  |  |
| degraded, no mitigation | 0.0852 | 0.0753 |  |  |  |
