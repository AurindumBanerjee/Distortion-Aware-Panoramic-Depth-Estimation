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

## 10. ACGF and 360MonoDepth on real data (Kaggle T4, Nov 2026)

Runs: `results/acgf_midas_{structured3d,holo360d_indoor,holo360d_outdoor}` (full splits: 259 / 146 / 83 images)
and `*_ablation` (first 40 images of each). Model: MiDaS DPT-Hybrid. ACGF hyper-parameters were fixed on
`data/synthetic_dev` before these runs. Range guard on for tangent / rotation / hybrid.

Polar AbsRel (|lat| >= 60), GT alignment on |lat| < 30 (equator identical for all anchored methods):

| method | Structured3D | Holo360D indoor | Holo360D outdoor | runtime (x baseline, T4) |
|---|---|---|---|---|
| baseline | 0.536 | 0.363 | 0.707 | 1.0 |
| tangent | 0.379 | **0.321** | 0.784 | 2.6 |
| rotation | 0.256 | 0.566 | 0.841 | 4.4 |
| hybrid | 0.274 | 0.393 | **0.589** | 5.8 |
| 360MonoDepth (re-impl.) | **0.171** | 0.416 | 0.663 | 24 |
| ACGF | 0.327 | 0.385 | 1.076 | 26 |

**Verdict: ACGF does not beat the existing methods.** It helps clearly on Structured3D (-39%), is roughly neutral
on Holo360D indoor, and fails on Holo360D outdoor. It is also the slowest method on Kaggle, where the sparse
solve runs on a weak CPU. The gate did not deliver "do no harm": on outdoor scenes it made things worse than
no gate (0.82 vs 1.15 on the 40-image subset).

Why it failed (diagnosed, not tuned away):
1. **Sky.** MiDaS predicts near-zero disparity for sky; in log space this becomes huge values and huge jumps
   at sky boundaries, which the gradient solve integrates into nearby buildings (changes up to e^9). Value-domain
   fusion of the same views (`acgf|value`) does not have this problem (0.738 vs baseline 0.746 outdoors).
2. **Mixing gradients from different sources** (gamma * views + (1 - gamma) * baseline per edge) yields a
   non-integrable field; patchy gamma maps create artefacts.
3. **Shared view bias.** In up/down-looking views MiDaS has a "centre is far" prior that all pole views share, so
   view-view agreement does not certify correctness.

Other findings worth keeping:
* **360MonoDepth is the strongest method on Structured3D by a wide margin** (polar 0.171, also best at the equator),
  but it is not anchored to the ERP pass and is unstable on real captures (Holo360D indoor equator 0.41 -> 0.56).
* **The range guard did not fix the align-all blow-up**, and the blow-up is an *evaluation* artefact: ACGF leaves
  equatorial pixels bit-identical to the baseline, yet under align-all its 0-15 deg AbsRel on Holo360D indoor goes
  0.33 -> 1.18. The single affine disparity fit over the whole panorama, refitted after the poles change, maps
  equatorial disparities close to zero (depth clipped at 100 m). Align-all numbers for affine models on Holo360D
  should therefore not be used to rank methods.
* Ablations on Holo360D indoor (40 images): two gnomonic views (`acgf|GG`, 0.265) and the magnification law
  (`acgf|law`, 0.252) beat the default (0.306); the law hurt on the synthetic dev set, so the dev-set choice did not
  transfer to real data.
* No method helps consistently across all three datasets; real-data gains depend on scene type (indoor vs outdoor).

### 10.1 ACGF v2 (post-hoc fix, CPU check; `results/acgf_v2_local_check/`)

Two changes, motivated by the diagnosis above and fixed *before* evaluation (no parameter sweep):
`work: auto` (fuse in linear disparity for disparity models, log only for depth models) and `gate_mode: value`
(the gate blends the solved correction with the baseline instead of mixing gradient sources). v1 remains as the
ablation `acgf|v1`.

Held-out check: 12 images per dataset taken *after* the first 40 (not used by the ablations or the diagnosis).
Polar AbsRel, GT alignment on |lat| < 30:

| | Structured3D | Holo360D indoor | Holo360D outdoor |
|---|---|---|---|
| baseline | 0.498 | 0.396 | 0.466 |
| hybrid | **0.235** | 0.359 | 0.326 |
| ACGF v1 | 0.336 | 0.338 | 0.290 |
| ACGF v2 | 0.322 | **0.331** | **0.282** |

Failure check: the 12 outdoor images where v1 was 2.7-5.7x worse than the baseline on Kaggle (these informed the
diagnosis, so this tests the fix, not generalisation): baseline 0.824, hybrid 0.646, v1 2.837, **v2 0.763**;
v2 still harms 5/12 of these images by >5%.

Reading: v2 removes v1's catastrophic outdoor failure and is the best method at the poles on both real Holo360D
splits in this small sample, but it clearly loses to the hybrid (and to 360MonoDepth) on Structured3D. n = 12 per
set is small and v2 was designed after seeing real data, so the full-split Kaggle run (`CONFIRM_ONLY = True` in
`notebooks/kaggle_acgf.ipynb`, writes `results/acgf_midas_*_v2`) is needed before any claim.

### 10.2 ACGF v2 full-split confirmation (Kaggle T4; `results/acgf_midas_*_v2`)

Same images and evaluation as section 10 (the baseline numbers reproduce exactly); only baseline, hybrid and v2 were
re-run, the other rows are from section 10. Align-equatorial, MiDaS DPT-Hybrid; whole-image AbsRel / polar (60-90)
AbsRel, lower is better.

| method | Structured3D (259) | Holo360D indoor (146) | Holo360D outdoor (83) |
|---|---|---|---|
| baseline | 0.354 / 0.536 | 0.345 / 0.363 | 0.517 / 0.707 |
| tangent | 0.297 / 0.379 | **0.333 / 0.321** | 0.543 / 0.784 |
| rotation | 0.239 / 0.256 | 0.403 / 0.566 | 0.554 / 0.841 |
| hybrid | 0.248 / 0.274 | 0.352 / 0.393 | 0.486 / 0.589 |
| 360MonoDepth (re-impl.) | **0.170 / 0.171** | 0.399 / 0.416 | **0.475** / 0.663 |
| ACGF v1 | 0.273 / 0.327 | 0.349 / 0.385 | 0.592 / 1.076 |
| ACGF v2 | 0.276 / 0.329 | 0.349 / 0.386 | 0.476 / **0.579** |

Paired tests, v2 vs hybrid (Wilcoxon over images, whole-image AbsRel): Structured3D v2 worse (improves 42/259,
p < 1e-4); indoor no difference (76/146, p = 0.22); outdoor v2 better (55/83, median +5.7 %, p = 0.004).
Share of images made >5 % worse than the baseline (whole image): outdoor v2 22.9 % vs hybrid 47.0 %;
indoor 45.9 % vs 47.3 %; Structured3D 3.9 % vs 3.5 %.

Reading:
* The fix works: outdoor polar AbsRel 1.076 -> 0.579, the best of all methods on that split, with half the hybrid's
  harm rate. It changes nothing on Structured3D or indoor (v1 and v2 are within 0.002).
* The 12-image check in 10.1 was misleading for indoor (0.331 there, 0.386 on the full split): v2 is *worse than
  the baseline* at the indoor poles, as are all methods except plain tangent views.
* No method wins everywhere. 360MonoDepth is far ahead on Structured3D, tangent views on indoor, ACGF v2 (by a small
  margin over the hybrid) on outdoor. ACGF is therefore not "better than previous methods" in general; the defensible
  claim is narrower: it is the most reliable fusion on the hardest split (outdoor) and never catastrophic after the fix.
* ACGF costs ~22x the baseline runtime (5 model calls + CPU sparse solve) vs ~5x for the hybrid.

## 11. ACGF and the comparison methods with DAP (Kaggle T4; `results/acgf_dap_holo360d_*`)

DAP (the panoramic metric model this project targets), Holo360D full test splits, no alignment to ground truth
(`eval_align: none`, DAP's own protocol). All methods are scored on exactly the same pixels (checked from the
per-band pixel counts). AbsRel, lower is better.

| method | indoor whole | indoor equator 0-15 | indoor polar 60-90 | outdoor whole | outdoor equator 0-15 | outdoor polar 60-90 | runtime |
|---|---|---|---|---|---|---|---|
| baseline (DAP on ERP) | **0.175** | 0.179 | **0.179** | **0.535** | 0.653 | **0.502** | 1x |
| tangent | 0.309 | 0.179 | 0.482 | 0.585 | 0.653 | 0.640 | 2.0x |
| rotation | 0.244 | 0.179 | 0.355 | 0.553 | 0.653 | 0.566 | 3.2x |
| hybrid | 0.261 | 0.179 | 0.395 | 0.559 | 0.653 | 0.577 | 4.2x |
| ACGF v2 | 0.196 | 0.179 | 0.248 | 0.613 | 0.653 | 0.874 | 6.7-8.4x |

Share of images made >5 % worse (whole image) / >2x worse (severe): indoor tangent 94.5 / 71.2 %, rotation
74.0 / 48.0 %, hybrid 83.6 / 54.8 %, ACGF 69.9 / 2.1 %; outdoor tangent 59.0 / 26.5 %, rotation 44.6 / 18.1 %,
hybrid 48.2 / 20.5 %, ACGF 84.3 / 3.6 %.

ACGF ablations (first 40 images of each split; polar 60-90 AbsRel, baseline 0.173 indoor / 0.576 outdoor):
v2 0.237 / 0.982, nogate 0.330 / 1.309, **law (DAC magnification correction) 0.176 / 0.810**, screen-base
0.198 / 0.638, +rot 0.198 / 0.890, v1 0.245 / 1.080.

Reading:
* **DAP shows no polar degradation.** Indoor, its polar error equals its equatorial error (0.179 vs 0.179);
  outdoor, the poles are even better than the equator (0.502 vs 0.653). MiDaS, in contrast, doubles its error at the
  poles (Structured3D 0.25 -> 0.54). The problem this project targets is a problem of perspective-trained models;
  a model trained on ERP panoramas has largely learned the distortion.
* **Every inference-time correction makes DAP worse**, ACGF included. The corrections feed DAP pinhole or
  pitch-rotated images, which are outside what it was trained on, so their predictions are worse than its ERP
  prediction, and replacing the poles with them only adds error.
* ACGF does the least damage indoors (polar 0.248 vs 0.355-0.482 for the others) and its gate prevents severe
  failures (2-4 % of images >2x worse vs 18-71 %). Outdoors it is the worst at the poles (0.874): the two pole views
  agree with each other but not with the truth, which the gate cannot detect (the shared-bias caveat).
* The magnification correction from Depth Any Camera (`acgf|law`) matters for a metric model: it removes almost all
  of ACGF's indoor harm (0.176 vs baseline 0.173) and a third of the outdoor harm. It hurt with MiDaS (section 10),
  consistent with the law being about metric scale. It still does not beat the baseline, and it was not chosen in
  advance, so it is reported as an ablation, not as the method.
* Caveats: DAP reads about 1.24x too far on Holo360D (smoke test), which affects all methods equally; whether
  Holo360D is part of DAP's training data has not been checked.

## 12. acgf|ico: 360MonoDepth's icosahedral views as ACGF input (MiDaS)

**Question.** 360MonoDepth (20 icosahedral pinhole views, deformable per-view scale/offset grids fitted for *mutual*
consistency) is the most accurate method on Structured3D (polar 0.171) but harms about half of the real Holo360D
images (indoor 54.8 %, outdoor 42.2 % of images > 5 % worse). ACGF v2 is safe (severe harm 2-4 %) but only reaches
0.329 there. Hypothesis: feeding the 20 icosahedral views into ACGF, aligned to the ERP baseline instead of to each
other, and fused with ACGF's gate and solve, keeps 360MonoDepth's accuracy and ACGF's safety.

**Method** (`inference/conformal_fusion.py`: `ico_erp_views`, `ico_view_products`, `view_products`, `fuse_products`;
`inference/mono360.py`: `anchored_grid_align`). The 20 views are exactly mono360's (384 px, 30 % padding; shared cache,
so the 20 model calls are made once per image). Every view is aligned to the ERP baseline on anchor pixels
(|lat| < 45, inner 85 % of the view):
* `ico-affine`: ACGF's robust pinhole fit X = A cos P + B cos + C, range guard [0.5 p1, 2 p99] of the baseline;
* `ico-grid`: the affine X, then mono360's deformable (scale, offset) grids, coarse to fine, with mono360's mutual
  term replaced by a baseline data term on the anchors (smoothness kept; no-collapse term kept but averaged per
  cell: mono360's summed form, harmless when only mutual consistency matters, inflates every scale against a fixed
  target and made the variant worse than doing nothing in a unit test).
The adapter turns any number of views into the products the gate and solve consume (per-edge consensus t_e,
per-pixel v_bar, sigma_n^2, n); with ~3.4 views per pixel (2.3 at the poles) instead of 2. Gate and solve are v2's,
unchanged (spherical edge weights, one Cauchy pass, gamma gate applied to the solved values with a 3 deg blur,
spsolve, linear disparity). Scope `polar`: the caps |lat| > 35 deg as v2; scope `sphere`: every pixel unknown,
lambda_p = sphere_lambda everywhere, no fixed boundary, so the equator is protected only by the gate.

**v2 unchanged.** The refactor reproduces ACGF v1 and v2 bit-for-bit on two real MiDaS validation panoramas and on the
oracle scenes (checked before / after; `tests/test_acgf.py::test_acgf_v2_reproduces_pre_ico_outputs` guards it).
A quirk found on the way and deliberately left in place: `edges_to_pixels` counts a pixel's two horizontal edges as
one (bool + bool = OR), which scales per-pixel edge statistics by 4/3 in the interior. The factor is common to
sigma_n^2 and the baseline excess and cancels in gamma except at view borders; fixing it would change v2.

**Protocol.** Settings chosen on Structured3D's official validation scenes 03000-03249 (41 panoramas,
`data/structured3d/val_s3000.txt`; never used for any result before) by a rule fixed in `configs/acgf_ico.yaml`
before the validation run; then one run on the full test splits (Structured3D 259, Holo360D indoor 146, outdoor 83),
align-equatorial protocol. No Holo360D non-test scenes are available, so Holo360D is out of sample for both scenes
and dataset.

**Validation** (41 panoramas, Structured3D scenes 03000-03249; `results/acgf_ico_validation`, `selection.md`).
AbsRel, align-equatorial; harm = share of images > 5 % / > 50 % worse than the baseline (whole image).

| method | whole | equator 0-15 | polar 60-90 | harm >5 % / severe |
|---|---|---|---|---|
| baseline | 0.319 | 0.266 | 0.440 | - |
| 360MonoDepth | **0.168** | **0.198** | **0.181** | 7.3 / 2.4 % |
| ACGF v2 | 0.274 | 0.266 | 0.324 | 9.8 / 4.9 % |
| ico-affine, polar | 0.264 | 0.266 | 0.308 | 7.3 / 2.4 % |
| ico-affine, sphere (lambda 5) | 0.255 | 0.250 | 0.315 | 4.9 / 0 % |
| ico-grid, polar (chosen: 4x3, lam_smooth 400) | 0.269 | 0.266 | 0.318 | 7.3 / 0 % |

Selected by the pre-registered rule: grids 4x3 (4x3 -> 8x7 tied: 0.3184 vs 0.3183), lam_smooth 400 (polar 0.318 /
0.323 / 0.329 for 400 / 40 / 4), sphere_lambda 5 (whole 0.255 vs 0.260). Written into `configs/acgf_ico.yaml`
before the test run.

Reading of the validation (not a test result):
* The hypothesis does not hold on validation: the best acgf|ico variant reaches polar 0.308, close to v2 (0.324) and
  far from 360MonoDepth (0.181).
* The grid prefers to be as stiff as allowed (lam_smooth 400 best, softer grids worse) and is still slightly worse than
  the affine fit (0.318 vs 0.308): correcting within-view scale drift *towards the baseline* imports the baseline's own
  errors. A diagnostic on 3 validation panoramas located the limit: the plain prior-weighted mean of the baseline-
  aligned views, before any solve or gate, is already at polar 0.45 vs 0.24 for 360MonoDepth on those images; the
  ERP baseline is poor even in its trusted band (equator 0.27 here vs 0.20 for 360MonoDepth), and the anchor passes
  that on. 360MonoDepth's accuracy comes from the mutual consistency this design removes.
* The sphere scope did not hurt the equator on average here (0.266 -> 0.250) and has the lowest harm, but the gate is
  open over most of the equator (mean gamma 0.7-0.85 on the diagnostic images), so this is earned image by image.

**Test** (one run, full splits): pending the Kaggle run (`notebooks/kaggle_acgf.ipynb`, `RUN_ICO = True`).
