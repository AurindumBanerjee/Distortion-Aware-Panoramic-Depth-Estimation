File: Distortion-Aware-Panoramic-Depth-Estimation/artifacts/results/followups/RESULTS.md





# Lokesh follow-up experiments — consolidated results

**Snapshot date:** 10 November 2026
**Evidence rule:** this document summarizes saved run artifacts only. A study is not called complete merely because its code or config exists. Lower AbsRel is better.

## Executive summary

| Study | Final evidence in this repo copy | Main result | Status |
|---|---|---|---|
| 01 — DA360 scale-only protocol | 200 Structured3D scenes | Scale-only is the principled DA360 protocol; its advantage is visible mainly under equatorial alignment, not consistently under align-all | Completed; sensitivity result |
| 02 — Domain-conditioned gate | 200 PanoX panoramas, 8 environments | Leave-one-environment-out selected **baseline/no correction in all 8 folds** | Completed; negative result |
| 03 — PanDA-style student | 50 held-out PanoX scenes, 2 held-out environments | Student is substantially worse than its DA360 teacher | Evaluation completed; training artifact not retained here |
| 04 — 20-view full-sphere | 200 PanoX panoramas, 8 environments | 20-view improves polar median AbsRel vs baseline, at 20 calls/image; direct paired significance vs two-pole tangent was not tested | Completed |
| 05 — FOV × resolution | 200 PanoX panoramas, 8 environments; 12 configs | Wider FOVs improve the 75–90° band; resolution changes have small effect; best raw median depends on alignment protocol | Completed on PanoX; Holo360D validation pending |
| 06 — Structure-at-the-poles gate | Code and design note only | No evaluation output or metrics | Not run |

The core experiment outputs and raw artifacts are kept in each study's `outputs/` folder. The selected runs below are the latest full runs in this repository snapshot; earlier timestamped runs remain available and were not deleted.

## Run provenance and selected runs

| Study | Selected run | Dataset / model | Execution recorded in summary |
|---|---|---|---|
| 01 | `01_scale_only_protocol/outputs/run_20261105_192854/` | Structured3D / DA360 | 200 scenes; 2 × Tesla T4 |
| 02 | `02_domain_conditioned_gate/outputs/run_20261105_193545/` | PanoX / DA360 | 200 scenes, 8 environments; 2 × Tesla T4 |
| 03 | `03_panda_style_finetuning/outputs/evaluation_20261105_210504/` | Held-out PanoX / DA360 teacher vs student | 50 scenes from ClothingStore and ModularBakeryShop; 1 × Tesla T4 |
| 04 | `04_mono360_20view/outputs/run_20261105_195950/` | PanoX / MiDaS DPT-Hybrid | 200 scenes, 8 environments; 2 × Tesla T4 |
| 05 | `05_fov_resolution_sweep/outputs/run_20261105_202824/` | PanoX / MiDaS DPT-Hybrid | 200 scenes, 8 environments; 12 configs; 2 × Tesla T4 |

Each selected run directory contains its report and machine-readable summary; studies 01, 02, 04 and 05 also retain per-scene CSVs. The corresponding execution logs are under each study's `logs/` directory.

## 01 — DA360: scale-only vs affine disparity alignment

**Question.** Does a scale-only fit change DA360's evaluation relative to a more permissive affine fit?

DA360 is specified as scale-invariant disparity, so scale-only is the methodologically preferred headline protocol. Affine fitting is retained as a sensitivity analysis. Both fits use the same scenes and validity masks; alignment is not refit separately per latitude band.

### align-all

| Band | Scale-only median AbsRel | Affine median AbsRel | Scale-only gain vs affine (95% bootstrap CI) |
|---|---:|---:|---:|
| All | 0.0127 | 0.0130 | +0.06% [−0.18%, +1.04%] |
| 45–60° | 0.0100 | 0.0097 | −0.55% [−2.23%, −0.00%] |
| 60–75° | 0.0079 | 0.0076 | −2.10% [−4.98%, −0.14%] |
| 75–90° | 0.0056 | 0.0054 | −0.45% [−6.27%, +1.85%] |

### align-equatorial

| Band | Scale-only median AbsRel | Affine median AbsRel | Scale-only gain vs affine (95% bootstrap CI) |
|---|---:|---:|---:|
| All | 0.0140 | 0.0148 | +2.63% [+0.10%, +5.74%] |
| 45–60° | 0.0112 | 0.0130 | +2.64% [+0.07%, +5.34%] |
| 60–75° | 0.0093 | 0.0112 | +4.51% [+0.02%, +13.14%] |
| 75–90° | 0.0070 | 0.0095 | +5.74% [+0.27%, +17.95%] |

**Reading.** The scale-only choice is supported by the model's output semantics. The empirical advantage is alignment-protocol dependent: under align-all, differences are small and mostly do not establish a consistent scale-only win; under align-equatorial, the paired intervals are positive in the reported bands. Do not summarize this as an unconditional improvement in DA360 accuracy.

Figure: [scale-only vs affine](figures/exp01_scale_vs_affine.png).
Raw report: [REPORT.md](01_scale_only_protocol/outputs/run_20261105_192854/REPORT.md).
Machine record: [summary.json](01_scale_only_protocol/outputs/run_20261105_192854/summary.json).

## 02 — DA360: leave-one-environment-out domain gate

**Question.** Can a rotation-correction threshold selected on other PanoX environments transfer to a held-out environment?

The 200-scene PanoX subset contains eight environment clusters. Candidate thresholds were 30°, 40°, 45°, 50°, 60° and 70°. The gate falls back to the uncorrected baseline unless calibration gain reaches 0.50%.

| Strategy | Mean AbsRel | Median AbsRel | Median relative gain |
|---|---:|---:|---:|
| LOEO-selected policy | **0.0389** | **0.0282** | 0.00% |
| Fixed 45° gate | 0.0877 | 0.0621 | −55.44% |
| Per-environment oracle (diagnostic upper bound) | 0.0720 | 0.0519 | −19.58% |

All eight held-out folds selected **baseline**. The oracle is diagnostic only; it is not a deployable method. The fixed threshold and even the per-environment oracle are worse in aggregate than doing nothing.

**Reading.** This is a useful negative result: the tested latitude/rotation gate did not transfer across PanoX environments. The fallback policy avoided applying a correction that the calibration data did not support. It does not prove that every image-conditioned gate must fail; that is the separate question posed by Experiment 06.

Raw report: [REPORT.md](02_domain_conditioned_gate/outputs/run_20261105_193545/REPORT.md).
Machine record: [summary.json](02_domain_conditioned_gate/outputs/run_20261105_193545/summary.json).

## 03 — PanDA-inspired teacher/student prototype

**Question.** Can a compact student learn useful pseudo-disparity from a frozen DA360 teacher?

The saved evaluation covers 50 scenes from the held-out PanoX environments `ClothingStore` and `ModularBakeryShop`. Ground truth is used in evaluation, not by the training script.

| Protocol / band | DA360 teacher median AbsRel | Student median AbsRel |
|---|---:|---:|
| align-all — all | 0.0637 | 0.3130 |
| align-all — 60–75° | 0.0270 | 0.2837 |
| align-all — 75–90° | 0.0130 | 0.3136 |
| align-equatorial — all | 0.0761 | 0.8123 |
| align-equatorial — 60–75° | 0.0435 | 1.1819 |
| align-equatorial — 75–90° | 0.0333 | 1.3171 |

**Reading.** The current student is not competitive with its teacher on these held-out groups. This should be reported as a negative/failed transfer result, not as a successful distillation result.

**Reproducibility gap.** `summary.json` records the checkpoint path as `/kaggle/working/Lokesh/followup_experiments/03_panda_style_finetuning/outputs/run_20261105_205624/best.pt`, but that checkpoint is not present in this repo copy, and the training log/output directory is not retained here. The evaluation report and CSV are preserved, but the student result is not fully reproducible from this checkout until the checkpoint and training record are restored.

Raw report: [REPORT.md](03_panda_style_finetuning/outputs/evaluation_20261105_210504/REPORT.md).
Machine record: [summary.json](03_panda_style_finetuning/outputs/evaluation_20261105_210504/summary.json).

## 04 — MiDaS: 20-view full-sphere inference

**Question.** Does a full-sphere 20-view icosahedral approach outperform the simpler two-pole tangent correction?

The 20-view method uses icosahedral tangent views, per-view disparity standardisation, deformable scale/offset alignment over overlaps, and frustum blending. It is compared on 200 PanoX panoramas with the baseline and two-pole tangent method.

### Median AbsRel by protocol

| Protocol | Method | All | 60–75° | 75–90° | Model calls / image |
|---|---|---:|---:|---:|---:|
| align-all | Baseline | 0.1898 | 0.1394 | 0.1514 | 1 |
| align-all | Two-pole tangent | 0.1632 | 0.1020 | 0.0950 | 3 |
| align-all | 20-view | 0.1645 | **0.0801** | **0.0832** | 20 |
| align-equatorial | Baseline | 0.2321 | 0.2389 | 0.3468 | 1 |
| align-equatorial | Two-pole tangent | 0.1913 | 0.1661 | 0.1659 | 3 |
| align-equatorial | 20-view | **0.1615** | **0.1429** | **0.1550** | 20 |

Paired environment-cluster bootstrap versus baseline for the 75–90° band:

| Protocol | Median gain | 95% CI |
|---|---:|---:|
| align-all | +56.81% | [+25.92%, +62.99%] |
| align-equatorial | +51.77% | [+12.49%, +54.53%] |

The bootstrap resamples the eight PanoX environment groups, not individual neighbouring frames as independent clusters.

**Reading.** The 20-view method improves the extreme-polar median relative to baseline in both protocols. It has lower reported 75–90° median AbsRel than the two-pole method, but it needs 20 rather than 3 model calls per image. The saved bootstrap compares each method with baseline, not 20-view directly with two-pole; therefore the table does **not** establish a statistically significant 20-view-vs-two-pole win. Under align-all, global median AbsRel is also nearly identical for two-pole and 20-view (0.1632 vs 0.1645).

Figure: [20-view comparison](figures/exp04_20view_comparison.png).
Raw report: [REPORT.md](04_mono360_20view/outputs/run_20261105_195950/REPORT.md).
Machine record: [summary.json](04_mono360_20view/outputs/run_20261105_195950/summary.json).

## 05 — MiDaS: FOV × tangent-resolution sweep

**Question.** How sensitive is two-pole tangent correction to tangent-view FOV and output resolution?

The selected run evaluates four FOVs (70°, 90°, 110°, 130°) at three resolutions (256², 384², 512²), giving 12 configurations on 200 PanoX panoramas. FOV and resolution are swept while the other inference settings stay fixed.

### Median AbsRel in the 75–90° band, using 512² views

| FOV | align-all | align-equatorial |
|---:|---:|---:|
| 70° | 0.1400 | 0.3269 |
| 90° | 0.1092 | 0.1807 |
| 110° | 0.0949 | **0.1644** |
| 130° | **0.0915** | 0.1702 |

Paired environment-cluster bootstrap gain versus baseline in the 75–90° band, 512² views:

| FOV | align-all gain (95% CI) | align-equatorial gain (95% CI) |
|---:|---:|---:|
| 70° | +10.33% [2.80%, 15.23%] | +6.38% [4.89%, 8.05%] |
| 90° | +42.07% [13.53%, 48.97%] | +34.64% [21.02%, 54.29%] |
| 110° | +46.52% [12.22%, 53.71%] | +41.46% [24.22%, 54.67%] |
| 130° | +46.28% [16.12%, 55.27%] | +45.96% [26.25%, 54.03%] |

**Reading.** Larger FOVs outperform 70° in the tested polar band. The best raw median is 130° under align-all and 110° under align-equatorial. The resolution curves are close at each FOV, so this run gives little evidence that increasing tangent resolution from 256² to 512² is worth the extra compute. The selected run's intervals compare each FOV with baseline; they do not provide pairwise significance tests between FOVs. Do not claim a universal optimal FOV.

Figure: [FOV × resolution sweep](figures/exp05_fov_resolution_sweep.png).
Raw report: [REPORT.md](05_fov_resolution_sweep/outputs/run_20261105_202824/REPORT.md).
Machine record: [summary.json](05_fov_resolution_sweep/outputs/run_20261105_202824/summary.json).

### Holo360D status for Experiment 05

The separate `config_holo360d_indoor.yaml` and `HOLO360D_INDOOR_VALIDATION.md` are preparation only. The 60-frame local subset from `train/Indoor_004`, `train/Indoor_005` and `train/Indoor_006` was used to smoke-test loading and masks; it is **not** a held-out benchmark and contributes no FOV metrics here. No Holo360D test-split validation run is present in the saved outputs.

## 06 — Structure-at-the-poles gate

The code and experiment design are present in `06_structure_at_poles_gate/`, motivated by the failure of a universal threshold in Study 02. There is no run directory, log, summary JSON, CSV or report from an evaluation. Status: **not run; no result to report**.

## 07 — Real NYC transfer: full-sphere 20-view vs two-pole tangent

**Question.** Does the 20-view method generalise from rendered PanoX panoramas to real NYC street panoramas, and does it outperform two-pole tangent directly?

The experiment runner and locked configuration are prepared under `07_real_nyc_20view/`. A deterministic manifest has been generated from the locally available 1,908 paired NYC RGB/range maps. It selects 182 frames (IDs 84–1894) across 91 assumed blocks of 20 IDs, using offsets 4 and 14 within each block. IDs 0–74 are excluded because they were used in Lokesh's earlier 75-frame NYC evaluation. The manifest and SHA256 metadata are saved in `manifests/`.

The manifest was generated and validated against all 1,908 paired source IDs. The preflight checked all 364 referenced files and decoded three RGB/range pairs (raw 1024×2048; 100% valid GT in those samples). Python syntax checks passed. The local Python 3.14 environment has no PyTorch, so CUDA/model preflight and inference must be run in the Kaggle GPU environment. **The GPU evaluation has not been run.** No Experiment 07 model-performance claim should be made yet.

The assumed 20-ID groups are not verified route/session identifiers. The cluster bootstrap is intentionally conservative relative to treating all 182 panoramas as independent, but it cannot establish route-level generalisation without true route metadata.

Guide: [Experiment 07 README](07_real_nyc_20view/README.md).
Configuration: [config.yaml](07_real_nyc_20view/config.yaml).
Runner: [run.py](07_real_nyc_20view/run.py).
Manifest: [nyc_holdout_182.txt](07_real_nyc_20view/manifests/nyc_holdout_182.txt).

## 08 — Direct paired PanoX significance audit

**Question.** Is the apparent 20-view advantage over two-pole tangent in Experiment 04 statistically supported by a direct paired comparison?

This analysis uses the saved 200-scene Experiment 04 `per_scene.csv`, compares identical scenes and resamples the eight PanoX environments as clusters. It performs no new GPU inference. Positive gain means the candidate has lower 75–90° AbsRel than the reference.

| Protocol | Direct 20-view vs two-pole median environment gain | 95% cluster-bootstrap CI |
|---|---:|---:|
| align-all | +15.55% | [−84.48%, +34.05%] |
| align-equatorial | −13.37% | [−69.33%, +18.00%] |

Both intervals include zero. Therefore, despite both corrections improving over baseline in the original experiment, the saved PanoX evidence does **not** establish that 20-view is better than two-pole tangent. The estimated ordering also changes with the alignment protocol. This is a useful result: it argues against claiming a direct 20-view win from the previous baseline-only confidence intervals.

The very broad intervals reflect substantial between-environment variability and only eight independent environment clusters. They should not be presented as tight uncertainty bounds or as a universal population guarantee.

Selected analysis output: [REPORT.md](08_paired_panox_analysis/outputs/run_20261110_135134_893955/REPORT.md).
Machine-readable comparisons: [pairwise.csv](08_paired_panox_analysis/outputs/run_20261110_135134_893955/pairwise.csv).
Guide and reproduction command: [Experiment 08 README](08_paired_panox_analysis/README.md).

## Interpretation across the follow-ups

1. Alignment protocol matters: the preferred DA360 scale-only evaluation is supported by the model's output definition, but its measured gain depends on where the fit is anchored.
2. Environment-conditioned rotation thresholds did not transfer: the LOEO procedure chose no correction in every fold.
3. The student prototype did not preserve teacher quality on the two held-out environments, and its checkpoint is missing from this checkout.
4. The 20-view method is promising for polar error but expensive; the current saved statistics do not prove it beats two-pole tangent directly.
5. The FOV sweep supports moving away from 70° but does not identify one alignment-independent optimum; resolution has a small observed effect.
6. Holo360D test validation, Study 06, and the new real-NYC Experiment 07 remain pending. None should be presented as completed benchmark evidence.

## Reproduction and artifact map

- Study plans/configs/runners: each `01_...` through `08_...` folder.
- Raw per-scene metrics: `outputs/<selected-run>/per_scene.csv` where produced.
- Machine-readable aggregate metrics and environment: `outputs/<selected-run>/summary.json`.
- Human-readable run report: `outputs/<selected-run>/REPORT.md`.
- Execution logs: the corresponding study's `logs/` folder.
- Figures regenerated from the selected `summary.json` files: `figures/` using `make_figures.py`.

All results here are from the saved 5 November 2026 runs. Earlier timestamped outputs are retained; this report identifies the runs selected for the summary rather than deleting historical runs.

## Experiment 07 — Real NYC 20-view transfer

- Canonical code: `experiments/followups/real_nyc_20view/`
- Config: `configs/followups/real_nyc_20view.yaml`
- Manifest and metadata: `artifacts/results/followups/real_nyc_20view/manifests/`
- Results: `artifacts/results/followups/real_nyc_20view/outputs/run_20261110_102032_346055/`
- Log: `artifacts/logs/followups/real_nyc_20view/run_20261110_101926.log`
- Interpretation draft: `report/draft/followup_experiments_07_08.md`

The 182-frame evaluation completed. The 20-view method has a positive paired cluster-bootstrap interval against two-pole tangent for the reported endpoints, but the 20-ID blocks are assumed dependence groups rather than verified route/session identifiers. This is held-out evaluation within the same NYC collection, not independent dataset replication. Runtime is materially higher (about 15.5x per image than two-pole tangent).

## Experiment 08 — Paired PanoX analysis

- Canonical code: `experiments/followups/paired_panox_analysis/`
- Results: `artifacts/results/followups/paired_panox_analysis/outputs/`

The direct 20-view-vs-two-pole intervals on eight PanoX environments include zero; this analysis does not establish a direct 20-view win. See the separate report draft for exact intervals and interpretation.
