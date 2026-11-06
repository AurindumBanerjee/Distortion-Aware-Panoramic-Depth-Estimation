# Verified findings (distortion sweeps, round 3b, capture-fault study)

Checked against `ROUND3_ANALYSIS.md`, `SWEEP_*`, `SUMMARY_20261106_092652.md` and the 16 `STUDY_*.md` files (4 models x 4 datasets, 40 frames per cell). This file supersedes the earlier agent summary where they disagree.

## 1. Is the polar deficit caused by the ERP projection?
Mostly no.
- **Rotation sweeps** (the polar content is moved to the equator): no onset for MiDaS, DAP or DA²; DA360 has one only on PanoX (70 deg).
- **Dilation sweeps** (the content magnified as near the poles):
  - **DAP:** large global excess (0.79 / 1.70 at 77.5 / 87.5 deg), but the local estimator (scale re-fitted per bin) gives 0.011 / -0.14. The content there is shrunk 2.5-7x (log magnification -0.9 to -2.0), and DAP is a metric model scored in raw metres. The excess is a correct scale reading, not a distortion effect.
  - **DA360:** the effect survives the local re-fit (0.03-0.15, up to 1.86x the equator), a genuine moderate sensitivity.
  - **MiDaS, DA²:** essentially insensitive.
- **Flip penalties (up-is-up prior):**
  - DAP: +0.07 to +0.18
  - DA360: +0.02 (S3), +0.08 (PanoX)
  - DA² on S3: ratio 1.45-1.48
  - MiDaS on PanoX: +0.153 (ratio 1.84)

## 2. Inference-time ensembles (75-90 deg gain)
- **MiDaS on S3 and PanoX:** the one robust positive result; the intervals exclude zero.
  - X4 S3: +12.6% (align-all), +46.9% (align-equatorial)
  - X5 S3: +22.6% (align-all), +26.5% (align-equatorial)
  - X4 PanoX: +18.4%
- **DAP:** ensembling hurts it indoors. X4 on S3 is -32% under its headline raw-metre protocol (-56% under align-all).
- **X7:** ran only for DAP, correctly per the pre-registration, but it was triggered by the scale artefact above. Its result is not evidence for or against the method.
- **DA360:** X6 at -1288% on S3 comes from its tiny baseline (polar AbsRel ~0.011); read its changes in absolute terms.
- **Holo outdoor:** gains, but with only 3 clusters and wide intervals.
- **Yaw control:** within +-3% almost everywhere, so the ensemble effects are not just averaging.

## 3. Capture faults and mitigations
Recovery is the median share of the damage undone, counted only over frames the fault hurt by at least 5%. Wins are the share of all frames that come out better than with no fix.

**Faults that matter:**
- Limited vertical field of view
- Nadir occlusion (tripod or operator)
- JPEG compression (DAP Holo indoor 0.139 -> 0.474)
- Noise
- Low resolution
- Tilt

Exposure seams, vignetting and stitching parallax barely hurt most cells.

**Fixes that work:**

| fix | cell | result |
|---|---|---|
| re-level, known tilt (IMU) | DAP S3 | 96% recovery |
| | DAP PanoX | 105% recovery |
| | DAP Holo indoor | 92% recovery |
| | DA² S3 | 99% recovery |
| plane fill, limited vertical field of view (DAP) | S3 | 0.761 -> 0.567; ERP inpaint is better here, 64% |
| | PanoX | 0.643 -> 0.342 (73%, 98% wins) |
| | Holo indoor | 0.785 -> 0.385 (60%, 98% wins) |
| | Holo outdoor | 0.677 -> 0.346 (98%, 98% wins) |
| plane fill, nadir occlusion (DAP) | PanoX | 85% recovery, 80% wins |
| | Holo outdoor | 101% recovery, 100% wins |
| inpainting, nadir occlusion | DA², indoor sets | 84-92% recovery |
| Wiener deconvolution, known shake kernel | all models | broadly positive |

**Use with care:**
- **DA360 and inpainting:** inpainting makes DA360 worse. With nadir occlusion it is worse on 85-92% of frames, and with a limited vertical field of view the error is about 3x.
- **Low win rates:** gain matching and flat-field show high recovery but few wins where the fault barely hurts (dap_panox 97% / 28%, da2_panox 91% / 32%).

**Do not use:**
- Tilt estimated from the predicted floor (biased about 12 deg for MiDaS; worse on clean images)
- NLM denoising
- Bilateral deblocking
- Parallax seam inpainting

## 4. Conclusion
1. The polar error of modern panoramic models is mostly not a projection-distortion effect.
2. Rotation ensembling helps older relative-depth models such as MiDaS.
3. Geometry-aware fixes for realistic capture faults (known-tilt re-levelling, floor and ceiling plane fill) give large, reliable gains for DAP. They are the strongest practical results so far.
