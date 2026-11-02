# Research summary: distortion-aware panoramic depth estimation

> **Scope of the evidence.** Every number below comes from **MiDaS DPT-Hybrid** (main model) and
> **MiDaS Swin2-Tiny** (second model). Both are *perspective* relative-depth networks. They were run
> **zero-shot on 24 procedurally ray-cast indoor panoramas with exact ground truth** (512×1024, CPU).
> The target panoramic foundation model, **DAP**, and the real benchmarks (Stanford2D3D, Matterport3D)
> could not be run in the development environment: no GPU, and no access to Hugging Face or the gated
> datasets. The code, configs and wrapper for that experiment are ready (README §7). Nothing here
> should be read as a claim about DAP or about real data. All tables are regenerated from CSVs by
> `scripts/make_results_tables.py` into `results/RESULT_TABLES.md`.

## 1. Problem

ERP panoramas stretch each row by 1/cos φ (×2 at 60°, ×3.9 at 75°). Depth networks may therefore
treat polar content differently from equatorial content. The question is whether
**inference-time** use of alternative projections can repair any latitude-dependent degradation,
**without retraining or modifying the frozen model**.

## 2. Motivation

Panoramic depth foundation models are expensive to retrain, and they are increasingly used as black
boxes. A correction that wraps *any* model (input: an image; output: a depth map) would be
immediately reusable. This includes perspective models applied to panoramas, which is the setting
tested here.

## 3. Method

* **Selective tangent-plane inference.** Gnomonic views cover only the caps |φ| > φ_t: one view per
  pole, or a pole view plus a ring of views. Each prediction is converted from z-depth to range, or
  aligned with a geometry-aware 3-parameter fit for disparity models, then back-projected to ERP.
* **Rotation ensemble.** The sphere is rotated by a true SO(3) resampling. Pitch ±90° places each pole
  at the centre of a new ERP once. The model runs on each rotated ERP and the prediction is rotated
  back.
* **Hybrid.** Tangent and rotated views go into one pool.
* **Fusion.** Views are merged with a per-pixel *distortion prior* cos(λ_v)², where λ_v is the
  latitude or off-axis angle *inside the image the model saw*. The merged map is blended with the
  baseline by hard replacement, soft latitude ramps (linear/cosine/sigmoid/polynomial), or a heuristic
  confidence (prior × multi-view agreement × local consistency).
* **No ground truth at inference.** Views are aligned to the baseline only on pixels that are trusted
  in both frames.
* **Novelty claimed:** the method is model-agnostic and inference-only, applies only to the
  distorted caps, and fuses views by a per-view distortion coordinate. It includes the geometric
  bookkeeping (z vs range, disparity-affine alignment with cos-weighting, seam/pole-aware sampling)
  that makes heterogeneous views comparable.

## 4. Experimental setup

| item | value |
|---|---|
| models | MiDaS DPT-Hybrid (ERP run at 384×768, tangent views at 384²); MiDaS Swin2-Tiny (fixed 256², ERP squashed) |
| data | 24 synthetic indoor ERPs, 512×1024, exact range GT, seed 0 (`datasets/synthetic.py`) |
| evaluation | AbsRel, SqRel, RMSE, RMSElog, MAE, MedAE, δ1–3, error variance and %AbsRel>0.1; global and per |φ| band; pixel- and area-weighted |
| GT alignment | affine in disparity (MiDaS protocol), fitted per image on **all** pixels (`align-all`) *or* on **|φ|<30°** only (`align-equatorial`) |
| statistics | paired over images: ratio of means, median per-image change, bootstrap 95% CI, Wilcoxon signed-rank |
| default method | φ_t = 45°, 1 tangent view per pole, rotations pitch ±90°, cosine blending over φ_t ± 10° |
| geometry gate | point-level reprojection error ≤ 1.2e-12°; ERP→tangent→ERP mean relative error 3.8e-6 |

**Why two alignment protocols?** MiDaS output is defined up to an affine transform. One global fit
spreads polar errors over the whole image: the corrected poles change the fit, which then changes
the equator. Fitting on |φ|<30° makes the equator identical for every method, so polar differences are
read directly. This protocol mirrors the inference-time assumption that the equator is trusted. It
can extrapolate badly, though, as the Swin2-Tiny and 256×512 results show. Both protocols are
reported, and they lead to different conclusions.

## 5. Results (MiDaS DPT-Hybrid unless stated)

### 5.1 Does error increase towards the poles? (Observation)

| \|φ\| band | 0–15 | 15–30 | 30–45 | 45–60 | 60–75 | 75–90 |
|---|---|---|---|---|---|---|
| AbsRel, align-equatorial | 0.154 | 0.148 | 0.205 | 0.295 | 0.373 | **0.431** |
| AbsRel, align-all | 0.243 | 0.207 | 0.142 | **0.116** | 0.126 | 0.145 |

* With the scale anchored at the equator, error rises monotonically. The paired bootstrap finds it
  significantly above the |φ|<15° reference from **|φ| ≈ 36°** onward (onset bin 35–37.5°), reaching
  **2.9×** at the pole. For Swin2-Tiny the onset is about 29°.
* With a global fit, the curve is **U-shaped** and the equator is *worse* than the caps. The
  latitude effect for this model is therefore mainly a **latitude-dependent scale/shift
  inconsistency**: polar predictions disagree with equatorial ones. A global affine fit partly
  absorbs it by compromising both.

**Content vs distortion control** (`latitude_control/`). The same panoramas were rotated by pitch
0/30/60/90° with GT rotated identically, and the fit was anchored on the input's equator.
* Error follows **latitude in the model input** for every pitch.
* Floor and ceiling content (content |φ| 60–90°) placed on the input equator by a 90° pitch has
  AbsRel **0.15–0.16**, versus 0.37–0.43 when upright.
* Within the same image, pitch and content band, moving content further from the input equator raises
  the median AbsRel by +35/+79/+146/+173% at Δ = 30/45/60/75° (pitch 90).
* Under a global fit or a content-equator fit, no consistent latitude trend remains. The distortion
  effect is real for these models, but how large it looks depends on where the relative scale is
  anchored.

### 5.2 Main comparison (Exp. 1–4), polar AbsRel (|φ| ≥ 60°), 24 images

| method | model calls | cold runtime | polar AbsRel, align-eq | polar AbsRel, align-all | global AbsRel, align-all |
|---|---|---|---|---|---|
| baseline | 1 | 1.00× | 0.402 | 0.136 | 0.163 |
| tangent (t45, 1/pole) | 3 | 1.63× | 0.356 | 0.129 | 0.153 |
| rotation (pitch ±90) | 3 | 2.91× | 0.419 | 0.222 | 0.203 |
| **hybrid** | 5 | 3.59× | **0.259** | 0.130 | **0.151** |

Hybrid vs baseline, align-equatorial (paired):

| band | baseline → hybrid | ratio-of-means improvement | median per-image | Wilcoxon p | images improved |
|---|---|---|---|---|---|
| 30–45 | 0.205 → 0.188 | 8.2% | 8.1% | <0.001 | 21/24 |
| 45–60 | 0.295 → 0.202 | 31.8% | 37.0% | 0.003 | 20/24 |
| 60–75 | 0.373 → 0.245 | 34.1% | 49.5% | 0.011 | 18/24 |
| 75–90 | 0.431 → 0.273 | 36.8% | 51.0% | 0.005 | 19/24 |
| 0–30 | unchanged by construction | 0 | 0 | – | – |

Under **align-all**, the hybrid improves global AbsRel by 7.3% (p = 0.016, 18/24 images), but the
changes inside the polar bands are not significant (75–90: 7.3%, p = 0.22). The gain shows up mostly
at the equator (0–15: 18.5%, p < 0.001) because the repaired poles let the global fit serve the
equator better. The 30–45° band gets slightly worse (−9.6%, p = 0.20).

### 5.3 Ablations (align-equatorial, polar AbsRel unless stated)

* **Threshold (Exp. 5).** Hybrid: 0.254 / 0.259 / **0.239** / 0.305 at φ_t = 30/45/60/75°. Tangent
  only: 0.337 / 0.356 / 0.378 / 0.394. Starting the correction at 30–60° all work. 75° is too late:
  the 45–75° band, already degraded, is left uncorrected.
* **Tangent views (Exp. 6).** One view per pole gives 0.356, 2 give 0.285, **3 give 0.267** and 5 give
  0.324. Hybrid with 3 views per pole: **0.217** (9 calls, 5.5× runtime). More views help up to 3 per
  pole. With 5, the narrower FOVs give the model less context and the per-view alignment gets
  noisier.
* **Fusion (Exp. 7).** Soft ramps are within ±0.001 of each other at the poles. In the 45–60°
  transition band they beat hard replacement (linear 0.200 vs hard 0.209). **Confidence fusion is
  worse** (hybrid global 0.295 vs 0.202): agreement weighting also changes equatorial pixels
  (0–15: 0.154 → 0.209), and with only 2–4 views the agreement signal is unreliable. **Soft >
  hard > confidence.**
* **Merge rule.** `prior` (0.259) ≈ `mean` (0.257) > `median` (0.329).
* **Seam prior** (our addition after the v1 run): **not supported**. Hybrid 0.259 with vs 0.253
  without; rotation 0.419 vs 0.380. What fixed the v1 seam artefacts was the choice of rotations
  (±90° instead of two +90° variants), not the prior.
* **Rotation sets and controls.** Rotation-only gives 0.412 (pitch 90), 0.419 (±90), 0.380 (×4) and
  0.467 (±45). The **yaw-only control** (three extra ERP passes that do not move the poles) gives
  0.389, as good as the best pitch set. Rotation-only gains are therefore *ensembling*, not
  un-distortion. **Hybrid control:** tangent + yaw-only rotations scores 0.355, the same as tangent
  alone (0.356). Tangent + pitch rotations scores 0.259. The hybrid's gain specifically requires the
  pole-centring rotations.
* **Why the hybrid works** (`bias_analysis.csv`, 8 images, signed log error at |φ| ≥ 60°). At the
  south pole the baseline *under*-estimates range (−0.40) and so does the tangent view (−0.30).
  The pitch-rotated views *over*-estimate (+0.29, +0.41). The hybrid lands at +0.04. Much of the gain
  is **cancellation of opposite-signed biases** between projections. Individual views are not each
  "undistorted". This is an honest limit on the mechanism claim.
* **Resolution (Exp. 8, 12 images, model input height = ERP height).** Under align-eq the hybrid helps
  at every resolution (polar 0.357 → 0.229 at 384×768; 0.309 → 0.267 at 512×1024). The 256×512
  baseline fit is degenerate (2.83). Under align-all it helps only at 384×768 (0.128 → 0.123) and hurts
  at 256×512 and 512×1024.
* **Runtime (Exp. 9, CPU, cold).** Baseline 5.6 s per panorama. Overhead is 1.63× (tangent), 2.91×
  (rotation), 3.59× (hybrid), and 3.23× / 4.81× for 3 / 5 tangent views per pole. Cost is linear in
  model calls; reprojection and fusion add < 1.2 s. GPU memory could not be measured. The peak process
  RSS for the whole 49-method sweep was 2.35 GB.

### 5.4 Second model: MiDaS Swin2-Tiny (generalisation)

* Under **align-all**, no method gives a significant improvement. Hybrid global AbsRel is
  0.218 → 0.223 (n.s.). Rotation-only hurts at 75–90° (−19%, p = 0.03).
* Under align-equatorial the baseline fit degenerates on several images (mean polar AbsRel 5.0), so
  only medians are meaningful. Hybrid medians: 45–60° 0.453 → 0.260 (p = 0.03), 75–90°
  0.565 → 0.518 (n.s.).
* The content control again shows error rising with input latitude when the scale is anchored at
  the input equator: median +51% at Δ = 75°, pitch 90.
* This model squashes the 2:1 ERP into a 256² square, a different distortion from the one studied.
  **The correction does not transfer robustly to it.**

## 6. Answers to the research questions

| # | question | answer from this evidence |
|---|---|---|
| 1 | Does error increase toward the poles? | **Yes, relative to the equator's scale.** Monotone increase to 2.9× under equatorial anchoring; U-shaped under a global fit. Content control: driven by input latitude, not floor/ceiling content. |
| 2 | Where does it become significant? | ≈ 36° (DPT-Hybrid), ≈ 29° (Swin2-Tiny), equatorial anchoring |
| 3 | Does tangent inference help? | Modestly: −11% polar with 1 view per pole (n.s. at the poles), −34% with 3 views per pole |
| 4 | Does rotation help? | Not on its own: no better than the yaw-only ensembling control, and harmful under a global fit |
| 5 | Largest improvement? | **Hybrid** (−36% polar, p = 0.005 at 75–90°), largely through cancellation of opposite biases |
| 6 | Does it hurt the equator? | Not under latitude blending (0–30° untouched by construction). Confidence fusion does; 30–45° is mixed under a global fit |
| 7 | Extra compute? | 1.6× (tangent) to 3.6× (hybrid) on CPU; linear in the number of views |
| 8 | Soft vs hard? | Soft ramps slightly better in the transition band; no difference at the poles |
| 9 | Optimal threshold dataset-dependent? | Untestable with one dataset. On this one 30–60° are equivalent and 75° is too late |
| 10 | Useful across scenes? | Helped in 18–20 of 24 scenes (align-eq); heavy-tailed per-image changes |
| 11 | Across models? | **Not shown.** Clear for DPT-Hybrid; no robust gain for Swin2-Tiny; DAP untested |

## 7. Limitations

1. **The target model (DAP) and real data were not evaluated.** Synthetic scenes are simple
   (boxes, planar textures, Lambertian shading) and both models are perspective networks applied to
   ERP. A real ERP-trained model may show little polar degradation at all. That is exactly what the
   DAP configs will test.
2. The magnitude and even the sign of the effect depend on the GT alignment protocol of relative-depth
   models. Metric models (DAP, `eval_align: none`) avoid this ambiguity.
3. The hybrid's mechanism is partly bias cancellation, which is model-specific and not guaranteed.
4. Inference-time alignment assumes the equator is reliable. It fails if the baseline is wrong there.
5. n = 24 images; several per-image CIs are wide even where Wilcoxon tests are significant.
6. Pitch-rotated inputs violate the gravity-upright prior of most models. This is a confound that the
   bias analysis exposes but the design cannot remove.
7. Runtime was measured on CPU only, so GPU memory is not reported.

## 8. Future work

* Run `configs/dap_stanford2d3d.yaml`, `dap_matterport3d.yaml` and `dap_dav2_tangent.yaml`. The key
  question is whether a panoramic-native model shows the §5.1 effect at all.
* Learn the fusion weights (a tiny per-pixel gating network on frozen-model outputs, trained on held-out
  scenes) instead of using the cos² prior and heuristic confidence.
* Use gravity-preserving alternatives to pitch rotations, such as cubemap faces with a vertical up
  axis or small roll/pitch jitters, to separate un-distortion from the upright-prior confound.
* Apply test-time consistency across overlapping tangent views (joint alignment instead of per-view
  alignment to the baseline).
* Use real-data evaluation with area-weighted metrics on Stanford2D3D, Matterport3D and Structured3D.

## 9. Research log (transparency)

* **v1 run** (`results/archive/v1_before_seam_prior/`): used rotations (0,90,0) and (90,90,0), which
  both put the south pole on the rotated panorama's seam. This produced visible seams in the south cap.
  It was replaced by pitch ±90° plus a seam prior. The ablation later showed the prior itself is
  unnecessary, and this is reported. v1 numbers for the hybrid were similar (polar −36% under
  align-equatorial).
* After the first control experiment was ambiguous, an alignment-anchored analysis and a
  within-pitch analysis were added. A hybrid control with yaw-only rotations and the bias analysis
  were also added after the main results, to test alternative explanations. No method or
  hyper-parameter was tuned on the reported test images beyond what the ablation tables show.
