File: Distortion-Aware-Panoramic-Depth-Estimation/artifacts/results/followups/EXPERIMENT_TRACKER.md

# Follow-up Experiments Tracker & Audit Ledger

This document tracks the five follow-up experiments designed to evaluate panoramic depth estimation under distortion, scale protocols, rotation gating, and multi-view fusion on Kaggle 2x Tesla T4 GPUs.

---

## 1. Experiment Overview & Architecture Matrix

| ID | Name | Model | Dataset | Input Modality | Core Question / Hypothesis | Execution Script | Primary Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Scale-Only Protocol** | DA360 Large | Structured3D (200 scenes) | Full ERP | Does scale-only alignment ($s \cdot d$) reveal distortion that affine shift ($a \cdot d + b$) conceals? | `01_scale_only_protocol/run_gpu.sh` | `REPORT.md`, `per_scene.csv`, `summary.json` |
| **02** | **Domain-Conditioned Gate** | DA360 Large | PanoX (200 scenes, 8 envs) | ERP + Rotations | Can latitude rotation gates ($\theta \in [30^\circ..70^\circ]$) be calibrated via Leave-One-Environment-Out (LOEO)? | `02_domain_conditioned_gate/run_gpu.sh` | `REPORT.md`, `folds.json`, `summary.json` |
| **03** | **Student Fine-Tuning** | Student U-Net (Teacher: DA360) | PanoX (150 train, 50 test) | ERP | Can a student model trained on teacher pseudo-disparity with patch-normalization learn polar correction without GT? | `03_panda_style_finetuning/run_gpu.sh` | `best.pt`, `history.csv`, `training_summary.json` |
| **04** | **360MonoDepth 20-View** | MiDaS DPT-Hybrid | PanoX (200 scenes) | Tangent (20 views vs 2 poles) | Does 20-view icosahedral L-BFGS alignment outperform analytical 2-pole polar tangent correction? | `04_mono360_20view/run_gpu.sh` | `REPORT.md`, `per_scene.csv`, `summary.json` |
| **05** | **FOV $\times$ Resolution Sweep** | MiDaS DPT-Hybrid | PanoX (200 scenes) | Tangent views (12 configs) | How do tangent FOV ($70^\circ..130^\circ$) and resolution ($256..512$) trade off polar accuracy and latency? | `05_fov_resolution_sweep/run_gpu.sh` | `REPORT.md`, `summary.json` |

---

## 2. Infrastructure & Auto-Sync Architecture

- **Compute:** Kaggle Cloud Kernel (Linux x86_64 Ubuntu container).
- **Accelerators:** 2x NVIDIA Tesla T4 GPUs (16 GB GDDR6 VRAM each, 32 GB total).
- **Client:** VS Code on Windows connected to Kaggle via remote Jupyter Kernel Provider.
- **Python Runtime:** Python 3.10 / 3.11 (`/opt/conda/bin/python`), PyTorch with CUDA 12/13.
- **Instant Per-Stage Auto-Sync Pipeline:**
  1. Immediately after each individual experiment stage completes, `followup_experiments/shared/sync_stage.py` compresses its outputs and streams a base64 payload to stdout (`=== STAGE_SYNC_PAYLOAD_START: <id> ===`).
  2. Because VS Code streams stdout over the remote kernel websocket in real time, the outputs are automatically written to `kaggle_two_t4_runner.ipynb` on the local machine within seconds.
  3. Running `python Lokesh/scripts/sync_kaggle_outputs.py --watch` locally extracts and commits every completed stage to Git in the background. Even if Kaggle disconnects or terminates unexpectedly, zero data is lost.
  4. If `GITHUB_PAT` is configured, Kaggle also commits and pushes directly to GitHub after each stage.

---

## 3. Full-Scale Benchmark Results (`LIMIT = None`, 200 Scenes)

Executed across all 200 scenes on Structured3D and PanoX (8 independent environments).

### Experiment 01: DA360 Scale-Only vs Affine Protocol (`run_20261105_155600`)
- **Dataset:** Structured3D (200 test scenes).
- **Finding:** Under `align-equatorial`, scale-only fitting produces lower AbsRel in polar bands (+5.74% gain at 75°–90°), demonstrating that affine shift ($a \cdot d + b$) artificially masks polar degradation by absorbing geometric distortion into the unconstrained additive intercept.

| Band | Scale-only Median AbsRel | Affine Median AbsRel | Scale-Only vs Affine Gain (95% CI) |
| :--- | :---: | :---: | :---: |
| **Global (`align-all`)** | 0.0127 | 0.0130 | +0.06% [-0.18%, +1.04%] |
| **Polar 75°–90° (`align-all`)** | 0.0056 | 0.0054 | -0.45% [-6.27%, +1.85%] |
| **Global (`align-equatorial`)** | 0.0140 | 0.0148 | **+2.63% [+0.10%, +5.74%]** |
| **Polar 75°–90° (`align-equatorial`)** | 0.0070 | 0.0095 | **+5.74% [+0.27%, +17.95%]** |

---

### Experiment 02: Domain-Conditioned Rotation Gate (`run_20261105_160335`)
- **Dataset:** PanoX (200 scenes across 8 independent environments: `ClothingStore`, `Diner50`, `FeudalJapan_Meshingun`, `ModularBakeryShop`, `Mountain_Environment_Set`, `SouthOfFrance`, `Warehouse`, `YellowParrot`).
- **Candidates:** Thresholds $[30^\circ, 40^\circ, 45^\circ, 50^\circ, 60^\circ, 70^\circ]$.
- **Finding:** Unconditional rotation (e.g. fixed 45° gate) severely degrades predictions (-55.44% relative gain, AbsRel increases from 0.0389 to 0.0877) due to ground-plane tilt and indoor ceiling artifacts. The calibrated LOEO rule safely falls back to baseline for all 8 folds, preventing catastrophic out-of-distribution rotation errors.

| Strategy | Mean AbsRel | Median AbsRel | Relative Gain vs Baseline |
| :--- | :---: | :---: | :---: |
| **LOEO-Selected Gate** | **0.0389** | **0.0282** | **+0.00% (safe fallback)** |
| **Fixed 45° Rotation Gate** | 0.0877 | 0.0621 | -55.44% |
| **Per-Environment Oracle** | 0.0720 | 0.0519 | -19.58% |

---

### Experiment 04: 20-View 360MonoDepth vs 2-Pole Polar Tangent (`run_20261105_162943`)
- **Dataset:** PanoX (200 scenes).
- **Core Scientific Finding:**
  - In `align-equatorial`, baseline polar AbsRel at 75°–90° is **0.3468**.
  - **2-Pole Polar Tangent** cuts polar error down to **0.1659** (**>52% error reduction**) using only **3 neural network calls** (~0.3s).
  - **20-View 360MonoDepth** achieves **0.1550** polar error but requires **20 neural network calls** and an expensive non-linear L-BFGS optimization (~10s per scene).
  - **Conclusion:** 2-pole polar tangent captures >93% of 20-view multi-crop distortion correction at **15% of the computational cost**.

| Method | Calls / Image | Global AbsRel (`align-all`) | 75°–90° Polar AbsRel (`align-all`) | Global AbsRel (`align-equat`) | 75°–90° Polar AbsRel (`align-equat`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline ERP** | 1 | 0.1898 | 0.1514 | 0.2321 | 0.3468 |
| **2-Pole Polar Tangent** | **3** | **0.1632** | **0.0950** | **0.1913** | **0.1659** |
| **360MonoDepth 20-View** | 20 | 0.1645 | 0.0832 | 0.1615 | 0.1550 |

---

### Experiment 05: Tangent FOV $\times$ Resolution Sweep (`run_20261105_165811`)
- **Dataset:** PanoX (200 scenes across 12 configurations).
- **Core Scientific Finding:**
  - View geometry (FOV) strongly dominates sampling resolution:
    - At $70^\circ$ FOV: polar AbsRel is $\sim 0.140$ (`align-all`) / $\sim 0.327$ (`align-equat`).
    - At $90^\circ$ FOV: polar AbsRel drops to $\sim 0.105$ (`align-all`) / $\sim 0.178$ (`align-equat`).
    - At $130^\circ$ FOV: polar AbsRel reaches **0.0915** (`align-all`) / **0.1702** (`align-equat`).
  - At any fixed FOV (e.g. $130^\circ$), scaling resolution from $256^2 \to 384^2 \to 512^2$ yields minimal gain ($0.0941 \to 0.0919 \to 0.0915$).

| Config | FOV | Size | Calls | 75°–90° Polar AbsRel (`align-all`) | 75°–90° Polar AbsRel (`align-equat`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `fov70_size256` | 70° | 256² | 3 | 0.1402 | 0.3269 |
| `fov70_size512` | 70° | 512² | 3 | 0.1400 | 0.3269 |
| `fov90_size256` | 90° | 256² | 3 | 0.1041 | 0.1778 |
| `fov90_size512` | 90° | 512² | 3 | 0.1092 | 0.1807 |
| `fov110_size256` | 110° | 256² | 3 | 0.0963 | 0.1697 |
| `fov110_size512` | 110° | 512² | 3 | 0.0949 | 0.1644 |
| `fov130_size256` | 130° | 256² | 3 | 0.0941 | 0.1698 |
| `fov130_size512` | **130°** | **512²** | **3** | **0.0915** | **0.1702** |

---

### Experiment 03: Student Distillation Training & Evaluation (`evaluation_20261105_173454`)
- **Architecture:** Two-GPU DDP training with PanDA-style patch-normalized gradient loss.
- **Teacher:** DA360 Large (pseudo-disparity supervision, zero ground truth during training).
- **Test Set:** 50 held-out scenes from unseen environments (`ClothingStore`, `ModularBakeryShop`).
- **Results:**
  - `align-all`: Teacher DA360 median AbsRel = 0.0637; Student U-Net median AbsRel = 0.3267.
  - `align-equatorial`: Teacher DA360 median AbsRel = 0.0761; Student U-Net median AbsRel = 0.6652.

## Experiment 07 — Real NYC 20-view transfer

- Code: `experiments/followups/real_nyc_20view/`
- Config: `configs/followups/real_nyc_20view.yaml`
- Manifest and metadata: `artifacts/results/followups/real_nyc_20view/manifests/`
- Completed run: `artifacts/results/followups/real_nyc_20view/outputs/run_20261110_102032_346055/`
- Log: `artifacts/logs/followups/real_nyc_20view/run_20261110_101926.log`
- Analysis draft: `report/draft/followup_experiments_07_08.md`

The 182-frame evaluation completed. The 20-view method has a positive paired cluster-bootstrap interval against two-pole tangent for the reported endpoints, but 20-ID blocks are assumed dependence groups, not verified route/session identifiers. This is a held-out subset within the same NYC collection, not independent dataset replication. Runtime is materially higher (about 15.5x per image than two-pole tangent).

## Experiment 08 — Paired PanoX analysis

- Code: `experiments/followups/paired_panox_analysis/`
- Results: `artifacts/results/followups/paired_panox_analysis/outputs/`

Direct 20-view-vs-two-pole intervals on eight PanoX environments include zero; this analysis does not establish a direct 20-view win. See the separate report draft for exact intervals and interpretation.
