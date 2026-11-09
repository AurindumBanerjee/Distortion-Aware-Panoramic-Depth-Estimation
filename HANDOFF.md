# HANDOFF — Distortion-Aware Panoramic Depth Estimation

Written for a fresh agent (Gemini) picking this project up with no prior
context. Read this fully before touching code or re-running anything.

## 1. The project, in one paragraph

PS title: "Distortion-Aware Panoramic Depth Estimation." Original framing:
analyze how equirectangular distortion affects depth as a function of
latitude, then correct it at inference time (tangent-plane projection /
rotation ensembles) on top of a panoramic depth foundation model, in a
model-agnostic way. Team: Lokesh (own `Lokesh/` folder), Aurindum
(`Aurindum/`, cross-model benchmarking + the capture-fault study below),
Harshita (own folder, not in this clone -- see Section 6). Models in play:
DAP ("Depth Any Panoramas," arXiv 2512.16913), DA360 (the main model used
in Lokesh's experiments), DA2 (Depth Anything V2, not panoramic-native),
MiDaS (not panoramic-native, used as a "needs help" reference point).
Datasets: Structured3D (200-scene synthetic, experiment 01), PanoX
(8-environment synthetic, experiment 02), and -- as of Aurindum's Nov 6-7
work -- real NYC and Stanford2D3D panoramas, now actually in use (Section 3
below), not just a future target.

## 2. What Lokesh's five follow-up experiments found

All in `Lokesh/followup_experiments/`, each with its own `README.md`,
`config.yaml`, `run.py`/`run_*.py`, and timestamped `outputs/run_*/` with
`REPORT.md` + `summary.json` + (where saved locally) `per_scene.csv`.

- **01_scale_only_protocol** (DA360, Structured3D, 200 scenes): scale-only
  vs. affine alignment. No clear winner under `align-all`. Under
  `align-equatorial` scale-only wins on aggregate (+2.6% global, +5.7% at
  75-90 deg, CI excludes 0) -- but per-scene the result is strongly bimodal:
  61.5% of scenes favor scale-only (winners up to +70-90%), the rest lose
  badly (several scenes -150% to -1500%). This is NOT a pixel-count/noise
  artifact (checked: corr(valid-pixel-count, |gain|) ~ 0.01 on 88k-pixel
  medians). One scene, `scene_03202`, is a severe negative outlier in both
  the 16-scene pilot and the 200-scene run -- worth a manual look.

- **02_domain_conditioned_gate** (DA360, PanoX, 200 scenes, 8 environments,
  leave-one-environment-out): a latitude-threshold gate, calibrated on
  7 environments and tested on the 8th, NEVER selected anything but
  "baseline" (no correction) -- the LOEO-selected gate = baseline in every
  fold. A fixed 45-degree threshold is -55% vs baseline. Even the oracle
  (diagnostic only, per-environment-tuned, never deployable) is -19.6%
  overall. BUT broken down by environment, the oracle is clearly POSITIVE
  in 3/8 (ModularBakeryShop +25.5%, Warehouse +24.6%, SouthOfFrance +9.8%,
  56-64% of scenes win) and CATASTROPHIC in 2/8 (ClothingStore -629% median,
  8% win rate; Mountain_Environment_Set -824% median, 0/25 scenes win).
  Mountain's baseline error was already low before correction (0.0156
  median) -- the correction isn't fixing a known defect there, it's
  actively breaking something that worked.

- **03_panda_style_finetuning** (PanDA-style small-UNet student distilled
  from DA360 teacher pseudo-labels, PanoX, 50 held-out scenes across
  ClothingStore/ModularBakeryShop): student collapses, AbsRel 0.33 vs
  teacher's 0.06 overall, far worse at poles (0.34-0.70 vs 0.01-0.04).
  Not just "didn't help" -- something is likely broken (check
  `tests/test_scale_anchor.py`, the scale-invariant-disparity-anchor test,
  for a shift/scale bug). NOT YET DEBUGGED.

- **04_mono360_20view** (MiDaS, 20-view icosahedral tangent inference vs.
  2-pole tangent vs. baseline): both tangent methods roughly halve MiDaS's
  polar AbsRel vs. baseline (75-90 deg: 0.15 -> 0.08-0.10). 20-view wins at
  the poles specifically but costs 20x inference calls vs. 2-pole's 3x.

- **05_fov_resolution_sweep** (MiDaS, tangent-patch FOV x resolution):
  clean monotonic result -- FOV 70 -> 130 deg roughly halves polar AbsRel
  (0.140 -> 0.092); resolution 256 -> 512 barely matters. FOV, not sampling
  density, is the lever.

Aurindum's earlier cross-model baseline sweep (DAP/DA360/DA2/MiDaS x
Structured3D/PanoX/Holo360D indoor+outdoor, no correction applied) is the
context for all of the above: DA360 has almost no polar deficit in-domain
(Structured3D polar AbsRel 0.011), DAP is also good but ~2.5x worse than
DA360 there, DA2 and MiDaS are clearly worse. DA360's own weakest spot was
Holo360D OUTDOOR (polar 0.168 vs 0.052 indoor). His earlier Poisson-blend /
Mobius-TTA corrections (in `old_experiments/`) gave MiDaS big gains but hurt
DAP -- the same pattern Lokesh's 01/02 later confirmed for DA360.

## 3. SUPERSEDES SECTION 2's OPEN QUESTIONS: Aurindum's capture-fault study
   (Nov 6-7, after Lokesh's experiment commits -- read this before building
   anything new)

Harshita independently benchmarked MiDaS/DAP/DA360/DA2 and found the real
weak spots are NOT pole-latitude distortion per se -- they're everyday
capture problems: tilted camera, a tripod blocking the bottom of frame, the
top/bottom of the sphere not actually captured, and heavy compression. DAP
specifically breaks badly on these. Lokesh's 01/02 results above are
consistent with this (scale-only's bimodal failure, Mountain_Environment_Set
/ ClothingStore's collapse) but weren't designed to test it directly.

**Aurindum built and ran the real test.** `Aurindum/` now has a full
capture-fault study: an explicit fault taxonomy (`tilt`, `nadir` = tripod/
cap occlusion, `vfov` = missing top/bottom coverage, `yawblur`, `jpeg`, and
combos like `nadir+jpeg`), a matching fix per fault (`relevel_known`,
`plane_fill`, `inpaint_tangent`, `inpaint_erp`, `bilateral`, `wiener`), run
across **4 models x 6 datasets** -- Structured3D, PanoX, Holo360D
indoor/outdoor, AND real Stanford2D3D and NYC panoramas -- with bootstrap
95% CIs per cell. Key files:
- `Aurindum/results/FINAL_ablations.md` -- per-model, per-set, per-fault
  AbsRel change tables with CIs and %frames improved/worsened.
- `Aurindum/results/policy_comparison/POLICY_COMPARISON.md` and
  `finished.md` -- **a proper leave-one-out transfer test**: `core_loo`
  (fix chosen on other core sets, external sets never train), `all_loo`
  (chosen on everything including Stanford/NYC), `all_in` (in-sample,
  optimistic upper bound). 216 (model, fault, tested-set) cells: `core_loo`
  applies a fix in 76, improves 57, worsens 13 (mean -6.16%); `all_loo`
  applies 78, improves 63, worsens 11 (mean -6.03%).

**This is the real version of what experiment 06 (Section 4) was trying to
sketch** -- a per-image/per-fault gate, actually validated for transfer,
on real external data, not just a synthetic sanity check.

**What this means for DA360 specifically** (the model all of Lokesh's
experiments use): DA360 triggers far fewer fixable-fault detections than
the other models (8-12 of the 216 cells "applied," vs. DAP's 30, DA2's
18-22, MiDaS's 16-18) -- consistent with DA360 being comparatively robust.
But where it DOES respond, it's remarkably consistent: `relevel_known`
(de-tilting before inference) is independently chosen on nearly every
external held-out set -- s3, holo_in, holo_out, stanford, nyc -- under BOTH
`core_loo` and `all_loo`. Gains are modest but real and reproducible:
-1.8% (nyc) to -4.1% (s3). **This is the strongest, most-validated concrete
fix for DA360 that exists in this repo right now** -- stronger than
anything in Lokesh's 01/02/06, because it's cross-dataset-validated on real
NYC/Stanford data, not just synthetic PanoX/Structured3D. It is also
literally the PS's original "rotation-based inference ensemble" idea, just
correctly narrowed to the one fault (tilt) it actually fixes for DA360.

**DAP's story independently confirms Harshita's qualitative finding with
hard numbers:** DAP has by far the most applicable fixes (30/30 cells
tried, 29 improved, mean -17% to -18%) -- it breaks badly on these capture
faults exactly as she found, and targeted fixes recover most of the loss.

**One open question to resolve before citing the DA360 result as final:**
in `FINAL_ablations.md`, DA360's `nadir`, `vfov`, and `jpeg` rows are
EXACTLY `+0.0% [+0.0,+0.0] (0/0)` on both Stanford and NYC -- not small,
literally zero frames affected. This could mean (a) DA360 is genuinely
unaffected by those three fault types, which would be a real and useful
finding, or (b) those fix branches are silently not firing for DA360 in the
pipeline (a bug, not a result). Compare against `tilt` and `yawblur`, which
DO show real nonzero numbers for DA360 on the same sets -- so the pipeline
clearly CAN move DA360's numbers when something is actually being applied.
Check `Aurindum/scripts/` (whichever script produced `FINAL_ablations.md`
section 1) for whether the nadir/vfov/jpeg fix functions have a model-type
branch that's silently skipping DA360, before writing up "DA360 is immune
to nadir/vfov/jpeg faults" as a conclusion.

## 4. Experiment 06 (Lokesh's gate) -- status: MOSTLY SUPERSEDED, see above

`Lokesh/followup_experiments/06_structure_at_poles_gate/` (`gate.py`,
`run_gate_eval.py`, `config.yaml`, `README.md`) was built as a model-
agnostic, GT-free, per-image gate deciding whether a polar correction
should be applied, scoring four signals per pole: `tripod_occlusion_score`,
`missing_coverage_score`, `flat_sky_score`, `compression_blockiness_score`.
Only the pure-numpy scoring logic was tested, on synthetic data (caught and
fixed a real false-positive bug: an early version flagged ordinary flat
indoor surfaces as tripod occlusion 76% of the way to triggering; fixed by
requiring the flagged blob to be compact, connected, and touching the
bottom frame edge -- 0/15 false positives on clean synthetic scenes after
the fix, all 4 injected-artifact types still flagged correctly).
**`run_gate_eval.py` was never executed on GPU/real data.**

Given Section 3: most of what Exp 06 was built to discover (does a
per-fault gate transfer across held-out data?) is now answered, more
rigorously, by Aurindum's policy comparison -- answer: largely yes, it
transfers, especially for DAP, and for DA360 specifically the one fault
that reliably transfers is tilt.

**What's still genuinely distinct about Exp 06 and worth keeping:** the
`flat_sky_score` signal (low gradient + low texture = nothing real at the
pole to correct) does not have a direct equivalent in Aurindum's fault
taxonomy (`tilt`/`nadir`/`vfov`/`yawblur`/`jpeg` are all about what WENT
WRONG with the capture; `flat_sky` is about there being nothing there to
fix regardless of capture quality -- directly targets the
Mountain_Environment_Set collapse from Lokesh's 02, which doesn't obviously
map onto any of Aurindum's fault categories). **Recommendation: don't run
`06_structure_at_poles_gate/` as a standalone experiment. Instead, pull
just the `flat_sky_score` heuristic out of `gate.py` and propose it to
Aurindum as an additional fault/precondition category in his existing
pipeline**, so it gets the same rigorous multi-model/multi-dataset/LOO
treatment the other fault types already have, instead of a smaller
parallel validation.

## 5. What to do next, in order

1. **Resolve the DA360 nadir/vfov/jpeg "exactly 0/0" question** (Section 3)
   -- this determines whether "DA360 only needs tilt-correction" is a real
   finding or an artifact of a pipeline gap.
2. **Propose `flat_sky` as a new fault/precondition category** to
   Aurindum's capture-fault pipeline (Section 4) rather than running
   Exp 06 standalone -- test it the same way he tested the others: across
   all 4 models, all 6 sets, under `core_loo`/`all_loo`.
3. **If step 2 shows flat_sky is a real, transferable signal:** that
   becomes the PS's headline alongside Aurindum's tilt-correction result --
   "which faults matter depends on the model; DA360 specifically needs
   tilt-correction and (possibly) flat-sky-awareness, not latitude-based
   correction in general."
4. **Debug experiment 03** (student distillation collapse) -- check
   `test_scale_anchor.py`; also worth asking whether PanoX training scenes
   with capture artifacts are contaminating the teacher pseudo-labels, now
   that we know capture artifacts are the dominant real failure mode.
5. **Connect to Exp 01's outlier scenes:** pull `scene_03202`,
   `scene_03469`, `scene_03344`, `scene_03308` (consistently bad across
   runs) and check them against Aurindum's fault taxonomy directly (tilt?
   nadir? vfov? jpeg?) now that there's a concrete checklist to test
   against, rather than eyeballing for generic "artifacts."
6. **Write up the combined result**: Aurindum's `POLICY_COMPARISON.md` +
   `FINAL_ablations.md` are the quantitative backbone; Lokesh's 01/02 are
   the DA360-on-synthetic-data evidence that independently motivated the
   same reframe before the real-data study existed -- both should be cited
   together as converging evidence, not as separate findings.

## 6. Things that are settled / don't need re-litigating

- Latitude-threshold gating and environment-identity gating: both dead ends
  for DA360 on PanoX (02's full result).
- DA360 in-domain pole handling is already strong; don't expect blanket
  "distortion correction helps" results on it the way they show up for
  MiDaS (04/05) or DAP (Section 3). The one fault that reliably helps
  DA360 across real and synthetic external sets is **tilt** -- see Section
  3's `relevel_known` result. Don't re-chase generic latitude-band
  corrections for DA360; they were already tried (01/02) and don't
  transfer.
- Affine alignment, not scale-only, should be the default wherever a
  capture artifact might be present -- 01 already shows affine's intercept
  term is what rescues artifact-contaminated scenes from scale-only's
  catastrophic failures.
- Harshita's folder is not in this clone
 (`Harshita/` and `Lokesh/` are sibling co-author copies) -- her fix work
  and the NYC/Stanford validation plan she described are now partially
  superseded/absorbed by Aurindum's capture-fault study, which already
  uses real NYC/Stanford data. Check with her directly on how her track
  and Aurindum's now relate before duplicating effort.
