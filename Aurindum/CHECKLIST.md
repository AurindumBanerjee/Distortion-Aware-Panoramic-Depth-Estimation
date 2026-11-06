# Checklist: Distortion-Aware Panoramic Depth Estimation (round 3)

**Problem statement.** Analyse how equirectangular (ERP) distortion affects depth estimation as a function of latitude,
then improve inference by applying tangent-plane projections or rotation-based inference ensembles specifically to the
distorted polar regions. Novelty: turning the distortion analysis into a model-agnostic, inference-time correction
strategy for the new panoramic depth foundation model.

Everything run before 4 Nov 2026 is in `old_experiments/v2_20261104/` (conclusions: `results/WRITEUP_20261104.md` there).
This round re-does the work in the order the statement asks for: **measure first, then correct only what was measured.**

---

## What the previous rounds taught us (design constraints for this round)

- [ ] **Polar error mixes three things.** Distortion, content (the caps are mostly floor and ceiling), and the alignment protocol.
      The old benchmark never separated them, and that is why "polar gains" did not transfer. Part A must separate them.
- [ ] **Panoramic foundation models (DAP, DA360, DA²) show no polar deficit** at the band level (75-90 AbsRel at or below global).
      The correction must therefore be able to do nothing: if the analysis finds no distortion effect, the output must
      equal the baseline (do no harm).
- [ ] **Rotation ensembles work as decorrelated ensembles, not as "a better view".** A rotated pass alone is worse at the pole on
      Structured3D, but averaging it with the baseline helps. Weighting must be based on measured error, not on cos²(lat).
- [ ] **Label-free re-anchoring of rotated passes is the weak point on real data.** On Holo indoor it turns an intrinsic +1% into
      a realised -30%. The fit guard, joint re-anchoring and consensus did not fix it.
- [ ] **Tangent results depend on the alignment fit.** Use the exact 3-term fit (`method1.shift_model: cos`) only.
- [ ] **Dilation-only Möbius passes add nothing.** Use rotations only.
- [ ] **Statistics:** cluster by house / environment / scene. PanoX has 8 environments, Holo indoor 12 scenes, outdoor 3. Use spread
      subsets for capped runs (`data.subset=spread`). Fix decision rules before running. DA360 trained on Structured3D,
      so its S3 numbers are in-domain.

## Models and data

- [ ] **Target ("the new panoramic foundation model"):** DAP (metric, ERP-native). **Generality:** DA360 and DA²
      (2026 panoramic models). **Reference:** MiDaS DPT-Hybrid (perspective model on ERP), where distortion is known to matter.
- [ ] **Datasets:** Structured3D (300, 182 houses, rendered), PanoX (200, 8 environments, rendered, indoor and outdoor),
      Holo360D indoor (12 scenes, real LiDAR mesh). Holo360D outdoor is anecdote only (3 scenes).
- [x] **Calibration split.** Curves, gates and weights are fitted on the Structured3D CALIBRATION houses (cluster-hash
      split, `data.split` / `--split calib|eval`, deterministic, never splits a house) and evaluated on the S3 evaluation
      houses, PanoX and Holo360D. The curve is treated as a model property measured once. Never tune on reported scenes.

---

## Part A: Distortion analysis as a function of latitude

### A1. Latitude error profiles (descriptive)
- [ ] For every model × dataset × protocol (`none` for metric models, `align-all`, `align-equatorial`), compute the mean AbsRel
      and δ1 in 2.5° latitude bins. Report pixel-weighted and solid-angle-weighted versions (`erp_area_weights`).
- [ ] Find the onset latitude: the first bin significantly above the equatorial reference, by paired cluster bootstrap
      (`evaluation/latitude_analysis.onset_latitude`, made cluster-robust).
- [x] *Built:* `scripts/latitude_profile.py` writes `results/profile_<tag>.json` / `PROFILE_<tag>.md` / `.png` (within a 2.5° bin pixel- and area-weighting coincide, so only the pixel mean is kept).

### A2. Causal distortion sweep (the key new experiment)
- [x] *(built: `evaluation/distortion_analysis.sweep_frame`, `scripts/distortion_sweep.py`)* Rotate each panorama by pitch θ ∈ {-90, -60, -30, 0, 30, 60, 90}° (every pixel is then seen below 15° in at least one pass; tested), run the model, rotate the prediction back, and score
      the **same content** under every θ. Each original pixel is then scored at several "seen latitudes", with content fixed.
- [ ] Output: a distortion response curve E_m(L), the error as a function of the latitude L at which content was seen, per model.
      Content is fixed and only the distortion changes. This separates "distortion hurts" from "floors and ceilings are hard".
- [ ] Two estimators, both reported:
  - (a) global GT alignment per θ, as in the benchmark;
  - (b) GT alignment re-fitted inside each seen-latitude bin ('local'). **Sensitivity only:** on a synthetic content-only model it reports a spurious onset (content mix leaks through the per-bin fit), while (a) correctly reports none. Decisions use (a).
- [x] Control: a **resampling floor** (GT rotated there and back = a perfect model) per bin, because rotation costs interpolation error near depth edges. It replaces the yaw-only idea: a deterministic model re-run on a shifted image measures nothing about distortion.
- [ ] Expected (pre-registered): MiDaS rises steeply above a clear onset; DAP, DA360 and DA² are flat or shallow. If a
      panoramic model is flat, report that its residual polar error is content, not distortion.
- [x] Onset rule: two consecutive bins whose cluster-CI lower bound of dE exceeds 10% of the same pixels' equator-seen error (a bare "CI > 0" fires on interpolation noise; validated on synthetic models).
- [x] Output: `results/sweep_<tag>.json` / `SWEEP_<tag>.md` / `sweep_<tag>.png`.

### A3. Protocol sensitivity
- [ ] Show how much of the polar deficit in A1 disappears between `align-equatorial` and `align-all`, and against the A2(b) curve.
      This is the "how much of the polar problem is the evaluation" result.

### A4. Content decomposition (uses the existing planar-prior fit)
- [ ] Label each cap pixel as planar (floor or ceiling plane accepted) or non-planar. Report A1 and A2 separately for the two,
      to see whether errors near the poles come from distortion or from content.

**Decision after Part A:** a model gets a correction only where its A2 curve shows a significant distortion effect
(E_m(L) - E_m(0) with a cluster CI excluding 0). Record the per-model onset latitude L*_m. If a model has no onset,
Part B must output its baseline (verified as an identity check).

---

## Part B: Turning the analysis into a model-agnostic inference-time correction

### B1. Analysis-driven gate (the novelty, in one line: correct where the measured curve says it hurts)
- [ ] The gate for model m is a smooth ramp starting at L*_m, from the calibration split. There is no hand-set 30/55° gate.
- [x] *Built:* top-level `distortion_curve: results/sweep_<model>_s3_calib.json`; `mobius_tta.curve_gate`, `mobius_tta.curve_weights`, `method1.curve_gate` (ramp starts at the onset).

### B2. Rotation-based inference ensemble, weighted by the measured curve
- [ ] Passes: identity plus pitch ±90 (rotation only). Optionally pitch ±45 if A2 shows the 45-60 band is affected.
- [ ] Weights: w_pass(pixel) ∝ 1 / E_m(L_seen)², from the A2 curve (inverse expected error), instead of cos²(L_seen).
      This is the decorrelated-ensemble weighting that the S3 diagnostic calls for.
- [ ] Re-anchoring: keep `identity` scope. Report the stage-F intrinsic vs realised gain for each dataset, so that any loss
      from anchoring is visible.
- [ ] Control: compute-matched yaw ensemble with the same weights scheme.

### B3. Tangent-plane correction (Method 1)
- [ ] Polar views: tangent crops for perspective models, rotated ERP for ERP-native models (`polar_source: auto`). Exact
      3-term alignment, gradient-domain fusion, ramp starting at L*_m (B1).
- [ ] Also report the plain value blend (`Tangent_Spatial`) as the "is Poisson needed" control.

### B4. Content prior as a separate, clearly labelled add-on
- [ ] The planar prior is not a distortion correction. Report it separately, with its acceptance rates (logging added). Diagnose
      why it hurts Holo indoor before any claim.

### B5. Identity and do-no-harm checks (must pass before any result is reported)
- [ ] With a flat curve (no onset), the B1-B3 output equals the baseline bit for bit.
- [ ] Equatorial bands (0-30°) are never worse than the baseline under `align-equatorial`.

---

## Part C: Evaluation matrix

| | MiDaS | DAP | DA360 | DA² |
|---|---|---|---|---|
| A1 profiles, A2 sweep, A3, A4 | all datasets | all | all | all |
| B1+B2 (gated rotation ensemble) | all | all | all | all |
| B1+B3 (gated tangent / rotated-view Poisson) | all | all | all | all |
| Yaw control | all | all | all | all |

- [ ] Report on the evaluation split only (calibration houses excluded). Show cluster-robust 75-90 gain, 60-75 gain, 0-30 change
      and δ1, under the headline protocol of each model and under `align-equatorial`.
- [ ] Pre-registered rule for a positive claim on a dataset: the 75-90 gain CI excludes 0, the 0-30 change is not worse, the yaw
      control is near 0, and there are at least 8 clusters.
- [ ] For a model with no measured distortion effect, the expected and reportable result is **no change** (the correction
      switches itself off). That is a success of the method, not a failure.

## Part D: Deliverables

- [ ] Figures: A2 distortion response curves for the four models (the central figure), A1 profiles, the A3 protocol gap, B gains
      with CIs.
- [ ] Write-up claims, in order:
  1. how distortion affects each model as a function of latitude (with the content and protocol confounds removed);
  2. a correction that is driven by that measurement and model-agnostic (same code, any model);
  3. the result that it helps where distortion is measured (MiDaS-class perspective models) and correctly does nothing for
     panoramic foundation models.
- [ ] Refresh the project breakdown page with round-3 results.

## How to run (built 4 Nov)

`scripts/run_round3.sh start` (status / stop). Stages `A1` (calibration curves), `A2` (description on evaluation data),
`B` (curve-driven correction + ablations `r3wonly`, `r3gonly`), `D` (`results/ROUND3_ANALYSIS.md` + summary). Env:
`MODELS`, `N_CALIB`, `N_DESC`, `ESC`. Tests: `tests/test_distortion_analysis.py` (sweep separates distortion from content,
onset rule, split, do-no-harm bit-for-bit for Tangent / Method 1 / Method 2).

## Round 3b (after the round-3 results, 4 Nov)

Round 3 found no causal onset in any model, but the content split showed the rotation sweep confounds distortion with
orientation (a pitch rotation tips the scene; floors stop being "below"). Round 3b, pre-registered in
`PREREG_round3b.md`, adds:
- [x] dilation sweep (`--mode dilation`: content moves in latitude, up stays up; magnification reported), flip sweep
      (`--mode flip`: same latitude upside down = orientation penalty), onset on non-planar content (validated on
      synthetic orientation-only and distortion-only models: the three modes separate the two effects)
- [x] uniform-weight ensembles (`mobius_tta.weight_power: 0`): X4 confirmatory 3-pass rotation, X5 5/7-pass dose-response,
      X6 orientation-preserving dilation ensemble, X7 curve correction only for models with an onset in BOTH the dilation
      and the non-planar rotation sweep
- [ ] run `scripts/run_round3b.sh start` (stages S, B, R), then judge against PREREG_round3b.md

## Run order

1. A2 sweep and A1 profiles on the calibration split (fit L*_m and E_m(L)) → **decide** which models get corrections.
2. B5 identity checks (unit tests plus one smoke run).
3. A1–A4 and B1–B3 on the evaluation split, all models and datasets.
4. Summary (`scripts/collect_results.py`), figures, write-up.

## Capture-aware correction (model-agnostic front end, `distortions/correction.py`)

- [x] policy learned from the 16 study files, leave-one-dataset-out (`scripts/calibrate_correction.py`, CPU, seconds):
      `results/CORRECTION_POLICY.md`, `results/correction_policy.json`
- [x] cap detection from the image (`detect_caps`): 0 false alarms on 96 clean / photometrically degraded real frames,
      138/144 simulated caps found (with and without JPEG q8), edge within 1.6 deg; misses fall back to no fix
- [x] end-to-end smoke on CPU (MiDaS, 4 S3 frames): clean images pass through unchanged
- [ ] server: `scripts/run_correction.sh start` (needs the study JSONs in results/; ~same cost as the study) ->
      `results/CORRECTION_<model>_<set>.md`: held-out gains of the whole front end per model and dataset
