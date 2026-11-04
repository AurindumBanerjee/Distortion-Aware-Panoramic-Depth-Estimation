# Synthetic vs NYC Real-World: Experiment Comparison

> **Model**: MiDaS DPT-Hybrid-384 (CPU) | **Alignment**: affine-in-disparity (MiDaS protocol)
>
> Source files:
> - Synthetic: `results/midas_dpt_hybrid_synthetic/`
> - NYC (DAP dataset): `results/midas_dpt_hybrid_nyc/`

---

## 1. Setup Differences

| Property | Synthetic (Indoor) | NYC Outdoor (DAP) |
|---|---|---|
| **Data source** | Procedurally ray-cast (`datasets/synthetic.py`) | Real street-level panoramas (DAP dataset) |
| **Scene type** | Indoor rooms | Urban outdoor streets |
| **Ground truth** | Exact Euclidean range (ray-cast, no noise) | Float64 `.npy` range maps (LiDAR-derived) |
| **Depth range** | 0.05–100 m | 0.5–1000 m |
| **GT alignment** | `eval_align: auto` (affine-in-disparity) | `eval_align: auto` (affine-in-disparity) |
| **N images evaluated** | 24 | 75 |
| **ERP resolution** | 512 x 1024 | 512 x 1024 |
| **Config** | `configs/default.yaml` | `configs/midas_nyc_dap.yaml` |

> [!NOTE]
> MiDaS is a relative-disparity model (not metric). Ground truth alignment is always done per-image
> using a 3-parameter affine fit in disparity space. No GT is used at inference time.
> Two alignment protocols are compared: **align-all** (fit on all pixels) and
> **align-equatorial** (fit on |phi| < 30 deg only — isolates polar behaviour).

---

## 2. What Parameters Are Compared

| Parameter | Why it matters |
|---|---|
| **AbsRel (global)** | Overall depth error — lower is better |
| **AbsRel per latitude band** | Tests whether distortion degrades polar regions specifically |
| **Polar AbsRel (|phi| >= 60 deg)** | The primary claim of the paper |
| **d1 (% pixels with ratio < 1.25)** | Accuracy threshold metric — higher is better |
| **pct_bad (AbsRel > 0.10)** | Fraction of badly wrong pixels |
| **RMSE / MAE** | Scale-sensitive error (absolute metres after alignment) |
| **Method improvement %** | Tangent / Rotation / Hybrid vs baseline |
| **Cold runtime (seconds, ratio)** | Computational cost overhead |
| **Error-onset latitude** | At what |phi| does error significantly exceed equatorial baseline |

---

## 3. Baseline Error Profiles — align-all

### 3.1 Global Metrics (full image, align-all)

| Metric | Synthetic | NYC | NYC / Synthetic |
|---|---|---|---|
| **AbsRel** | 0.163 | 0.350 | **+115% worse** |
| **SqRel** | 0.110 | 108.46 | — (different depth scale) |
| **RMSE** | 0.577 m | 274.9 m | — (different depth scale) |
| **RMSE-log** | 0.219 | 1.090 | **+397% worse** |
| **MAE** | 0.371 m | 121.2 m | — |
| **MedAE** | 0.240 | 3.87 | — |
| **d1 (higher is better)** | 0.743 | 0.564 | **-24%** |
| **d2 (higher is better)** | 0.943 | 0.691 | **-27%** |
| **pct_bad (lower is better)** | 57.95% | 62.51% | **+4.6 pp** |
| **Baseline runtime (s)** | 5.50 | 5.13 | ~same (same resolution) |

> [!IMPORTANT]
> SqRel, RMSE and MAE are not directly comparable because depth scales differ drastically
> (indoor ~1-10 m vs outdoor ~4-974 m). Use AbsRel, RMSE-log, and delta metrics for cross-dataset
> comparisons. The NYC task is intrinsically harder: far-range outdoor scenes are much more
> ambiguous for a perspective, indoor-trained model like MiDaS.

### 3.2 Baseline AbsRel by Latitude Band (align-all)

| Band | Synthetic | NYC | NYC - Synthetic |
|---|---|---|---|
| **0-15 deg** | 0.243 | 0.367 | +0.124 |
| **15-30 deg** | 0.207 | 0.303 | +0.096 |
| **30-45 deg** | 0.142 | 0.280 | +0.139 |
| **45-60 deg** | 0.116 | 0.295 | +0.178 |
| **60-75 deg** | 0.126 | 0.363 | +0.237 |
| **75-90 deg** | 0.145 | 0.489 | +0.344 |
| **Polar (>=60 deg)** | **0.136** | **0.426** | **+0.291** |

> [!NOTE]
> The **polar error is 3.1x larger** on NYC vs synthetic (0.426 vs 0.136 AbsRel, align-all).
> This is driven by both the difficulty of outdoor scenes and the model's indoor training bias.

### 3.3 Baseline AbsRel by Latitude Band (align-equatorial)

| Band | Synthetic | NYC |
|---|---|---|
| **0-15 deg** | 0.154 | 0.305 |
| **15-30 deg** | 0.148 | 0.274 |
| **30-45 deg** | 0.205 | 0.279 |
| **45-60 deg** | 0.295 | 0.337 |
| **60-75 deg** | 0.373 | 0.465 |
| **75-90 deg** | **0.431** | **0.591** |
| **Polar (>=60 deg)** | **0.402** | **0.529** |

**Latitude error shape:**
- **Synthetic**: Classic monotonic rise from equator to poles when equatorial-aligned — confirms
  the distortion hypothesis clearly (3x-4x rise from 0-15 deg to 75-90 deg).
- **NYC**: Also monotonic but starting from a higher error floor at the equator. The *relative*
  rise from equator to poles is smaller (~2x) — real outdoor scenes have equatorial difficulty
  too (occlusion, texture-less sky, far-away objects).

---

## 4. Error Onset (at what latitude does distortion significantly kick in?)

| Dataset | Alignment | Error Onset |
|---|---|---|
| **Synthetic** | align-all | Not detected (U-shaped curve; global fit absorbs polar shift) |
| **NYC** | align-all | **|phi| ~ 73.75 deg** (first significant bin above equatorial baseline) |
| **Synthetic** | align-equatorial | ~36 deg (from RESULTS.md, error >2x ref from ~36 deg onward) |
| **NYC** | align-equatorial | Clear from band table above (monotonic rise from ~30 deg) |

> [!IMPORTANT]
> Under **align-all**, synthetic data shows a U-shaped error curve (the global affine fit absorbs
> polar scale shifts). Only align-equatorial reveals the true distortion onset. For NYC, the polar
> error increase under align-all is genuine and detected at |phi| ~74 deg, because the absolute
> depth errors at the poles are large enough to dominate even a global fit.

---

## 5. Main Method Comparison (align-all)

### 5.1 Global AbsRel

| Method | Synthetic | NYC | NYC delta vs baseline |
|---|---|---|---|
| **Baseline** | 0.1630 | 0.3497 | — |
| **Tangent (t45, v1)** | 0.1533 | 0.3393 | -3.0% (Synth: -6.0%) |
| **Rotation (pitch +-90)** | 0.2031 | 0.3875 | **+10.8% worse** (Synth: -24.6% worse) |
| **Hybrid (t45+rot)** | **0.1512** | 0.3606 | +3.1% worse (Synth: **-7.3%**) |

### 5.2 Polar AbsRel (|phi| >= 60 deg) — align-all

| Method | Synthetic | NYC |
|---|---|---|
| **Baseline** | 0.136 | 0.426 |
| **Tangent** | 0.129 | **0.407** |
| **Rotation** | 0.222 | 0.497 |
| **Hybrid** | **0.130** | 0.413 |

### 5.3 Polar AbsRel (|phi| >= 60 deg) — align-equatorial

| Method | Synthetic | NYC |
|---|---|---|
| **Baseline** | 0.402 | 0.529 |
| **Tangent** | 0.356 | 0.482 |
| **Rotation** | 0.419 | 0.651 |
| **Hybrid** | **0.259** | **0.482** |

---

## 6. Hybrid Method Improvement by Band (align-all)

*improvement_% = (baseline - corrected) / baseline x 100. Positive = better.*

| Band | Synthetic impr % | NYC impr % | Verdict |
|---|---|---|---|
| all | +7.3% | **-3.1%** | Hybrid hurts on NYC overall |
| 0-15 deg | +18.5% | -2.4% | Hurts equator on NYC |
| 15-30 deg | +13.5% | **-14.3%** | Strongly hurts lower-mid latitudes |
| 30-45 deg | -9.6% | -9.8% | Hurts both (transition region) |
| 45-60 deg | +0.3% | -4.5% | Slightly hurts NYC |
| 60-75 deg | +0.9% | -6.6% | Significantly hurts NYC polar |
| **75-90 deg** | **+7.3%** | **+10.1%** | **Only deep-polar band improves on NYC** |

> [!WARNING]
> **On NYC, the hybrid method harms most latitude bands** (align-all). Only the extreme poles
> (75-90 deg) benefit (+10%). This contrasts sharply with synthetic data where the equatorial
> bands also improve (+18% in 0-15 deg). Under align-equatorial the overall hybrid improvement
> on NYC is +5.2% (vs +24.7% synthetic).

---

## 7. Hybrid Method Improvement by Band (align-equatorial)

*The 0-15 deg and 15-30 deg bands are locked identical for all methods by definition of the equatorial fit.
Only bands above |phi|>30 deg show real correction.*

| Band | Synthetic impr % | NYC impr % |
|---|---|---|
| all | **+24.7%** | +5.2% |
| 0-15 deg | 0% (locked) | 0% (locked) |
| 15-30 deg | 0% (locked) | 0% (locked) |
| 30-45 deg | +8.2% | +3.7% |
| 45-60 deg | **+31.8%** | +3.8% |
| 60-75 deg | **+34.1%** | +4.9% |
| **75-90 deg** | **+36.8%** | **+12.0%** |

> [!NOTE]
> Under align-equatorial, the hybrid method improves all bands on both datasets. The synthetic
> data sees dramatically larger improvements at the poles (+37% vs +12%), suggesting the model's
> indoor-trained representations are better adapted to the correction heuristics than outdoor scenes.

---

## 8. Tangent Plane Improvement by Band (align-all)

| Band | Synthetic | NYC | Verdict |
|---|---|---|---|
| all | +6.0% | **+3.0%** | Works on both, but less on NYC |
| 0-15 deg | +7.5% | +0.0% | No gain at equator for NYC |
| 15-30 deg | +5.8% | +2.3% | Mild gain |
| 30-45 deg | +5.0% | **+8.8%** | Better on NYC than synthetic! |
| 45-60 deg | +6.1% | -2.6% | Slight regression NYC |
| 60-75 deg | +3.5% | -0.7% | Neutral-to-bad NYC |
| **75-90 deg** | +6.7% | **+8.2%** | **Strongest gain on NYC poles** |

---

## 9. Rotation Ensemble — Performance on Real Data

| Metric | Synthetic (align-all) | NYC (align-all) |
|---|---|---|
| Global AbsRel impr | **-24.6%** (much worse) | **-10.8%** (worse) |
| 0-15 deg impr | +10.7% | +13.5% |
| 60-75 deg impr | **-55.4%** | -27.9% |
| 75-90 deg impr | **-70.4%** | -8.5% |

The rotation ensemble **consistently hurts polar regions** on both datasets when evaluated with
align-all. Under align-equatorial, the pattern for NYC is also negative (-12.6% overall). The
rotation approach benefits only the equatorial bands (0-15 deg), but creates large-scale errors
in the mid and polar bands for MiDaS-style relative models. The large affine-in-disparity shift
introduced by rotating the sphere appears incompatible with the global alignment fit.

---

## 10. Cold Runtime Comparison

| Method | Synthetic (s) | NYC (s) | Model calls | Overhead (NYC) |
|---|---|---|---|---|
| **Baseline** | 6.64 | 5.82 | 1 | 1.00x |
| **Tangent (t45, v1)** | 13.35 | 10.76 | 3 | 1.85x |
| **Rotation (pitch +-90)** | 20.16 | 16.90 | 3 | 2.90x |
| **Hybrid** | 27.44 | 20.41 | 5 | 3.51x |
| **Tangent (v2 — 2/pole)** | 21.00 | 14.81 | 5 | 2.54x |
| **Tangent (v3 — 3/pole)** | 25.50 | 21.96 | 7 | 3.77x |
| **Tangent (v5 — 5/pole)** | 38.56 | 31.09 | 11 | 5.34x |

> [!TIP]
> NYC runtimes are slightly faster than synthetic (~12-24%), likely because the outdoor scenes
> have simpler structure. Both datasets run on CPU only, confirming that the overhead is primarily
> from additional model forward passes.

---

## 11. d1 Accuracy (% correct pixels at threshold 1.25)

| Method | Synthetic | NYC |
|---|---|---|
| Baseline | 0.743 | 0.564 |
| Tangent | 0.766 | 0.564 |
| Rotation | 0.606 | 0.422 |
| **Hybrid** | **0.766** | **0.524** |

The rotation ensemble degrades d1 severely (-14% on synthetic, -14% on NYC). The tangent and
hybrid methods partially restore accuracy but NYC d1 recovery is smaller.

---

## 12. Summary: Key Differences and Explanations

| Observation | Synthetic | NYC | Likely explanation |
|---|---|---|---|
| Baseline equatorial error | Low (0.154) | High (0.305) | MiDaS trained on perspective indoor data; outdoor scenes are OOD |
| Polar error severity | Monotonic rise x2.8 | Monotonic rise x1.9 | Equatorial floor already high on NYC; relative polar penalty smaller |
| Hybrid gains equatorial bands | Yes (+18%) | No (-6%) | NYC equatorial content is hard for the model; extra views add noise |
| Tangent correction at poles (75-90 deg) | +6.7% | +8.2% | Polar tangent views still help even on real data |
| Rotation ensemble overall | Harmful globally | Harmful globally | Scale/affine inconsistency between rotated ERP and baseline |
| Best method (align-equatorial) | Hybrid (+36.8% poles) | Hybrid (+12% poles) | Correction principle holds but magnitude shrinks on real data |
| Error onset latitude (align-all) | Not detectable | ~74 deg | NYC polar errors large enough to survive global affine fit |

> [!IMPORTANT]
> **The core distortion correction principle holds on real data** (tangent and hybrid improve the
> 75-90 deg polar band on both datasets). However, the magnitude of improvement is dramatically
> smaller on NYC (~12% vs ~37% under align-equatorial), and the equatorial bands actually
> regress under align-all. The harder real-world data (equatorial ambiguity, scale uncertainty,
> far range) limits how much the polar correction can contribute globally.

---

## 13. Recommended Next Steps

1. **Use align-equatorial as the primary protocol** — it isolates the polar correction and shows
   genuine positive improvements on NYC at all bands above |phi| > 30 deg.
2. **Run with tags `E1_baseline E2_tangent E4_hybrid`** — rotation consistently regresses; omit
   it from the main evaluation.
3. **Increase `dataset.limit`** — 75 images is a good start; 200+ would tighten the CIs
   (currently +-1-5% at 95% level for NYC polar bands).
4. **Try DAP** — as a panorama-native metric model it should behave very differently: no affine
   alignment needed and polar distortion may be smaller to start with.
