# Repository guide (for review): Distortion-Aware Panoramic Depth Estimation

State on 4 Nov 2026, commit `27340cd` (folder `Aurindum/`). Written so that a reviewer with no prior context can
check the code and the claims. Sibling folders `Harshita/` and `Lokesh/` are co-authors' independent copies of an
older version of this code base and are not covered here.

---

## 1. What the project is

**Original problem statement.** Analyse how equirectangular (ERP) distortion affects monocular depth estimation as a
function of latitude, then improve inference with tangent-plane projections or rotation-based ensembles applied to
the distorted polar regions, as a model-agnostic, inference-time correction for panoramic depth foundation models.

**Constraints.** Every depth model is frozen (no training, no fine-tuning). All corrections run at inference time
around the model (`model.predict(image)` is the only call).

**Models** (wrappers in `models/depth_model.py`):

| key | model | output | scored with |
|---|---|---|---|
| `midas` | MiDaS DPT-Hybrid 384 (perspective) | affine-invariant disparity | affine fit to GT (align-all) |
| `dap` | DAP, Depth Any Panoramas (CVPR 2026) | metric range, metres (sky = NaN) | raw metres (`none`) and median scale |
| `da360` | DA360 (Depth Anything V2 fine-tuned on ERP) | scale-invariant disparity | affine fit |
| `da2` | DA^2 (SphereViT) | scale-invariant range | least-squares scale |

**Datasets** (loader `datasets/panorama.py`, split lists `test.txt` / `indoor.txt` / `outdoor.txt`):

| dataset | kind | size used | clusters (for statistics) |
|---|---|---|---|
| Structured3D | rendered indoor, depth mm PNG | 300 panoramas | 182 houses (`scene_NNNNN`) |
| PanoX | rendered UE5, indoor + outdoor, depth cm EXR | 200 frames | 8 environments |
| Holo360D | real capture, LiDAR-mesh depth EXR + rig mask | indoor 12 scenes, outdoor 3 scenes | scene (`Indoor_NNN`) |
| Stanford2D3D, NYC (DAP release) | real | optional, not in default runs | room / blocks of 20 frames |

DA360 was trained on Structured3D, so its Structured3D numbers are in-domain.

---

## 2. Where the research stands (short)

1. **Rounds 1-2** (`old_experiments/v2_20261104/`): Method 1 (gradient-domain Poisson fusion of polar views) and Method 2
   (Moebius / rotation test-time augmentation) help MiDaS on rendered Structured3D only. They fail on PanoX and real
   Holo360D. The 2-term tangent alignment gain on S3 was largely an alignment artefact (exact 3-term fit added).
2. **Round 3** (`results/ROUND3_ANALYSIS.md`): a causal "distortion sweep" (rotate the panorama so the same content is
   seen at different latitudes) finds **no model with a significant polar distortion effect**, but the rotation sweep
   confounds distortion with **orientation**: tipping the scene by pitch 90 deg makes the floor a wall, and models rely on
   "floor is below". Panoramic models (DAP, DA360, DA^2) show no polar deficit at all. A near-uniformly weighted
   rotation ensemble helped MiDaS on S3 (+15.9%) and PanoX (+21.4%), post hoc.
3. **Round 3b** (`PREREG_round3b.md`, queued, not yet run): dilation sweep (moves content in latitude without tipping),
   flip sweep (same latitude upside down = pure orientation penalty), pre-registered uniform ensembles X4-X7.
4. **Pivot under exploration**: real-world *capture* faults (camera tilt, missing caps, nadir occlusion, lens seams,
   parallax, vignetting, blur, noise, JPEG, low resolution) with inference-time fixes (`distortions/catalogue.py`,
   `scripts/distortion_study.py`). First pass: MiDaS on 18 frames only; full run on the server queued.

---

## 3. Conventions (check these first)

* **Sphere / ERP** (`geometry/spherical.py`): camera axes x right, y down, z forward. Pixel centre (u, v):
  lon = (u+0.5)/W * 2pi - pi, lat = pi/2 - (v+0.5)/H * pi. Direction d = (cos lat sin lon, -sin lat, cos lat cos lon).
  The top row is the north pole (+lat, -y = up).
* **Rotations** (`geometry/erp_projection.py`): `rotate_erp(img, R)` returns I_rot(d) = I(R d). An original direction o
  appears in the rotated image at R^T o (`rotated_latitude`). Prediction back to the original grid: `rotate_erp(pred, R.T)`.
  `rotation_from_ypr(pitch=+90)` brings the north pole to the image centre.
* **Sampling** is seam- and pole-aware (circular in longitude, row -k = row k-1 shifted by W/2 across a pole).
* **Depth semantics**: ERP ground truth is range (distance along the ray). Perspective views predict planar z;
  r = z / cos(angle to axis). Disparity models: d = s/z + t.
* **Alignment protocols** (`evaluation/protocol.py`): `align-all` (fit on all valid pixels), `align-equatorial`
  (fit on |lat| < 30), `none` (raw metres, metric models only). Aligned depth is clamped to [min_depth, max_depth].
* **Statistics**: paired over the same frames; median relative gain of 75-90 deg AbsRel, bootstrap 95% CI and Wilcoxon
  computed over **clusters** (frames averaged per house / environment / scene first, `group_of`). Win rate per frame.

---

## 4. Directory map

### Core library

| path | role |
|---|---|
| `geometry/spherical.py` | pixel <-> lon/lat <-> unit vector, rotations, area weights |
| `geometry/erp_projection.py` | `sample_erp` (seam/pole aware), `rotate_erp`, `rotated_latitude` |
| `geometry/tangent_plane.py` | gnomonic views: `generate_tangent_plane`, `erp_to_tangent`, `tangent_to_erp` (with cos-to-axis) |
| `models/depth_model.py` | wrappers MiDaS, DAP, DA360, DA^2, DepthAnythingV2, `EncodedDepthOracle` (test-only fake model), `build_panoramic_model` |
| `datasets/panorama.py` | list-driven loader, presets per dataset (units, valid range, EXR scale, optional mask column), `subset` first/spread, `id_filter` (split), `sample_id` |
| `evaluation/metrics.py` | AbsRel, d1, ...; `to_metric_depth` (affine for disparity, median / lsq / none for depth) |
| `evaluation/protocol.py` | `align_to_gt`, protocols, `group_of` (cluster ids), `paired_test`, `summarize_methods`, table formatting |
| `evaluation/latitude_analysis.py` | per-band metrics (0-15 ... 75-90), latitude profiles, onset helper |
| `evaluation/distortion_analysis.py` | **round 3**: calibration split `split_of` (hash of cluster id), latitude profile, **distortion sweep** (`sweep_frame`, modes rotation / dilation / flip), cluster-robust curves, onset rule, curve loading for Part B |
| `distortions/catalogue.py` | **capture faults + fixes** (section 6) |
| `distortions/correction.py` | **capture-aware correction front end** for any model: `correct(model, rgb, CaptureMeta, policy)`; caps detected from the image (`detect_caps`), tilt / shake from sensor metadata, fix per fault from a learned policy |

### Methods

| path | role |
|---|---|
| `1_gradient_polar_fusion/polar_views.py` | polar views (tangent crops or rotated ERP), alignment to the ERP prediction in a fusion space (disparity or log depth) |
| `1_gradient_polar_fusion/shift_alignment.py` | tangent disparity alignment; `shift_model: cos` = exact 3-term fit d_erp = a(cos d_t) + c cos + b |
| `1_gradient_polar_fusion/gradient_blending.py` | exact sparse least-squares Poisson integration, hard Dirichlet pin where the blend weight is 0, periodic longitude, Neumann at poles |
| `1_gradient_polar_fusion/planar_prior.py` | floor / ceiling plane fitted to the model's own prediction on a latitude ring (1/r linear in the ray direction), with acceptance tests |
| `2_mobius_tta_ensembling/mobius_transform.py` | Moebius passes: pitch rotation + stereographic dilation, warp / unwarp |
| `2_mobius_tta_ensembling/tta_ensemble.py` | Method 2 ensemble: presets, re-anchoring (identity or joint), fit guard, consensus, latitude gate, curve-driven gate and weights, `weight_power: 0` = uniform; `yaw_shift_ensemble` = compute-matched control |
| `3_structured3d_benchmark/benchmark_evaluator.py` | runs Baseline, Tangent_Spatial, Method1_GradientFusion, Method1_PlanarPrior (opt-in), Method2_MobiusTTA, Control_YawEnsemble on one frame, all protocols |
| `3_structured3d_benchmark/run.py` | **main benchmark runner**: `--config`, `--set key=value`, `--tag`, `--max_scenes`; writes `outputs_<...>/benchmark_summary.json` + csv |
| `3_structured3d_benchmark/config*.yaml` | one config per model x dataset (MiDaS = `config*.yaml`, DAP = `config_dap*.yaml`) |

`1_*/run.py` and `2_*/run.py` are older per-method runners (series 1 / 2, series 2 is synthetic only). `inference/`,
`experiments/`, `run_experiment.py`, `configs/` are the v1 pipeline, kept for reference, not used by current results.

### Scripts

| script | what it does |
|---|---|
| `scripts/distortion_sweep.py` | A2 sweep for one model x dataset (`--mode rotation|dilation|flip`) -> `results/SWEEP_<tag>.md/.json/.png` |
| `scripts/latitude_profile.py` | A1 profile per protocol -> `results/PROFILE_<tag>.*` |
| `scripts/distortion_study.py` | capture faults x fixes for one model x dataset -> `results/STUDY_<tag>.md`, `study_<tag>.json`, example images |
| `scripts/analysis_common.py` | shared config / model / dataset loading for the three scripts above |
| `scripts/round3_report.py` | Part A table `results/ROUND3_ANALYSIS.md` |
| `scripts/collect_results.py` | cluster-robust summary of every `outputs*/` json -> `results/SUMMARY_<ts>.md` |
| `scripts/diagnose_reanchor.py` | per-pass intrinsic vs realised gain of rotated passes |
| `scripts/run_tasks.sh` | **current driver**: `setup`, `smoke`, `start` (distortion study, then round 3b, then summaries), `status`, `stop` |
| `scripts/run_distortion_study.sh` | the study queue (MODELS, SETS, N, ONLY, TAG_PREFIX) |
| `scripts/calibrate_correction.py` | learns the correction policy from `study_*.json` (leave-one-dataset-out; keeps no fix unless one wins) -> `results/correction_policy.json`, `CORRECTION_POLICY.md`; CPU only |
| `scripts/run_correction.py` | end-to-end held-out test of `correct()` on a real model -> `results/CORRECTION_<tag>.md` |
| `scripts/run_correction.sh` | queue for the two above (MODELS, SETS, N, TAG_PREFIX) |
| `scripts/run_round3b.sh`, `run_round3.sh` | round 3b / 3 queues (stages S/B/R, A1/A2/B/D) |
| `scripts/run_next_experiments.sh`, `run_mobius_ablation.sh` | round 2 queues (stages A-I), ablation |
| `scripts/make_*_list.py`, `download_extra_datasets.sh` | dataset lists; optional Stanford2D3D / NYC download |
| `scripts/archive_old_experiments.sh` | move all outputs into `old_experiments/<name>/` |

### Documents and results

| path | content |
|---|---|
| `CHECKLIST.md` | round-3 plan (Part A measure, Part B correct only where measured) and round-3b additions |
| `PREREG_round3b.md` | pre-registered hypotheses and decision rules for round 3b (written before running) |
| `results/` | round-3 outputs: `ROUND3_ANALYSIS.md`, `SWEEP_*`, `PROFILE_*`, `SUMMARY_20261104_182454.md` (Part B) |
| `old_experiments/v2_20261104/` | everything before 4 Nov, incl. `results/WRITEUP_20261104.md` (round-2 conclusions) |
| `best_model/` | tracker records written by the runners (not results) |

### Tests (`tests/`, 93 tests, `python -m pytest tests -q`)

| file | covers |
|---|---|
| `test_geometry.py`, `test_scene_projection.py` | conventions, sampling, rotations, tangent projection, range vs z |
| `test_methods.py` | Poisson exactness, alignment (3-term fit), Moebius round trip, ensembles, gates, presets, fit guard, joint re-anchoring, planar prior, `group_of`, dataset subset / mask loading |
| `test_distortion_analysis.py` | sweep separates distortion from content and orientation (synthetic models with known answers), onset rule, split, do-no-harm (corrections return the baseline bit for bit when no onset is measured) |
| `test_correction.py` | cap detection (simulated masks reproduced, rendered flat pole rows ignored), routing in `correct()`, policy selection |
| `test_distortions.py` | catalogue geometry: tilt round trip and re-levelling, occlusion fixes, gain matching, Wiener, parallax, vignetting, flat-field |
| `test_pipeline.py`, `test_dap_wrapper.py` | end-to-end oracle pipeline, DAP wrapper plumbing (fake repo) |

---

## 5. Data flow of the main experiments

**Benchmark (Methods 1 / 2)**: `3_structured3d_benchmark/run.py --config <cfg> [--set ...] [--tag t]`
-> load list (`datasets/panorama.py`, optional `data.split`, `data.subset`) -> per frame `run_single_benchmark_scene`
-> baseline prediction, polar views / passes, fusion -> `align_to_gt` per protocol -> per-band metrics
-> `summarize_methods` with cluster groups -> `outputs_<tag>/benchmark_summary.json`.

**Distortion sweep**: `distortion_sweep.py` -> for each pass (pitch / lambda / roll) predict, map back to the original grid,
record the latitude at which each pixel was seen -> per pixel, error at seen latitude L minus error of the same pixel in
the pass where it is seen lowest (flip: minus the upright pass) -> per-bin means per frame -> cluster bootstrap ->
onset = first two consecutive bins whose CI lower bound exceeds 10% of the equator-seen error.

**Distortion study**: `distortion_study.py` -> per frame: clean prediction; per fault: degraded image, prediction with
no fix and with each fix (returned in the degraded frame, mapped back with `to_original`) -> all scored against the
same GT -> medians, per-frame recovery (only frames where the fault cost >= 5% of the clean error), win rate; blind
fixes (re-levelling, gain matching, flat-field, denoising, deblocking) also applied to clean images (do-no-harm).

---

## 6. Capture-fault catalogue (`distortions/catalogue.py`)

| key | fault (cause) | fixes |
|---|---|---|
| `tilt` | non-level capture, 12 deg pitch + 8 deg roll | `relevel_known` (IMU), `relevel_self` (gravity from floor / ceiling planes of the model's own prediction, 2 iterations) |
| `nadir` | tripod / logo patch below -62 deg | `inpaint_erp`, `inpaint_tangent` (inpaint in a polar gnomonic view), `plane_fill` (tangent inpaint + floor plane, gradient fusion pinned on visible pixels) |
| `vfov` | phone / cylindrical capture, only +-50 deg | same three |
| `seam` | dual-lens exposure / white-balance step at lon +-90 | `gain_match` (blind, from bands beside the stitch lines) |
| `parallax` | dual-lens baseline 5 cm, stitch sphere 2 m (physically re-imaged with GT depth) | `seam_inpaint` |
| `vignette` | residual fisheye falloff towards the seams | `flatfield` (blind brightness-vs-lens-angle profile) |
| `yawblur` | yaw shake during exposure (circular row blur) | `wiener` (known kernel) |
| `noise` | low-light shot + read noise | `denoise` |
| `jpeg` | quality 8 | `bilateral` |
| `lowres` | 4x down-sampled | none |

---

## 7. How to run and check

```bash
cd Aurindum
python -m pytest tests -q                                   # 93 passed expected
bash scripts/run_tasks.sh setup                             # checks GPU, weights, data lists
bash scripts/run_tasks.sh smoke                             # 2 frames per model x dataset (outputs removed)
bash scripts/run_tasks.sh start                             # full queue, detached; status / stop
python 3_structured3d_benchmark/run.py --config config.yaml --max_scenes 5 --set data.subset=spread   # one benchmark run (config path is relative to 3_structured3d_benchmark/)
python scripts/distortion_sweep.py --config 3_structured3d_benchmark/config.yaml --mode dilation --tag t --max_scenes 4
python scripts/distortion_study.py --config 3_structured3d_benchmark/config.yaml --tag t --max_scenes 4
```

Model weights: `weights/dpt_hybrid_384.pt` (MiDaS, needs timm), `weights/dap/model.pth` + `third_party/DAP`,
`weights/da360/DA360_large.pth` + `third_party/DA360`, `third_party/DA2` + offline HF cache (`HF_HOME`).

---

## 8. Points a reviewer should verify

Correctness
1. `rotate_erp` / `rotated_latitude` / `tilt_to_original` / `releveled` agree on the I_rot(d) = I(R d) convention
   (`tests/test_distortions.py::test_tilt_round_trip...`).
2. `sweep_frame`: the reference pass is the one with the smallest seen latitude per pixel (flip: the upright pass), the
   common pixel set is identical across passes, and the resampling floor uses the same two resamplings as predictions.
3. `onset_from_curve`: the 10% practical-significance threshold (without it, interpolation noise produced onsets).
4. `MobiusTTAEnsemble`: with `curve_gate` and no onset the output equals the baseline exactly and runs no extra pass;
   with `weight_power: 0, min_weight: 1` all passes are weighted equally.
5. `group_of`: clusters for every id format (S3 house, PanoX environment incl. names with digits / underscores,
   Holo scene, Stanford room, NYC blocks of 20).
6. `align_tangent_disparity_to_erp` 3-term fit; `gradient_blending` exactness and the hard Dirichlet pin.
7. `parallax_apply`: displacement direction (away from each lens axis), exact stitch-sphere intersection.

Statistics / claims
8. Cluster-robust CIs in `collect_results.py` use the stored per-frame metrics and `scene_ids`; PanoX has 8 clusters
   (summaries before 4 Nov 12:20 used a wrong 80-group clustering and are superseded).
9. Capped runs must use `data.subset=spread` (the first N lines of a list cover only the first scenes).
10. The rotation sweep's negative excess errors are attributed to orientation; round 3b's flip and dilation sweeps are
    the test of that explanation.
11. The capture-fault findings (`STUDY_*`) so far rest on 18 frames with MiDaS only; nothing is claimed yet for DAP.

Known limitations
* DAP / DA360 / DA^2 cannot run without their weights; all their results come from the GPU server.
* `relevel_self` recovers the tilt exactly on a perfect model but not with MiDaS: on 8 tilted Structured3D frames its
  'down' estimate is off by ~12 deg (about the whole applied tilt) because the model predicts the floor as if the image
  were level. A joint floor + ceiling fit with a shared disparity offset (removing the c_y / beta trade-off) was tested
  and does not help (11.3 vs 11.9 deg). Estimates more than 45 deg from the image's down are refused (one frame produced
  a flipped normal). A model-independent tilt cue (vanishing lines, IMU) is the open item.
* `plane_fill` rarely triggers with MiDaS (its floor ring fails the plane test).
* DAP clips depth at 100 m; NYC configs for DAP evaluate up to 100 m.
