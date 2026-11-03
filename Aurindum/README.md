# Aurindum: Advanced Distortion-Aware Panoramic Depth Estimation

This folder contains the complete, streamlined implementation of three independent novel research proposals for panoramic depth estimation, a centralized **`best_model/`** tracker, and GPU-server execution scripts for headless sequential training via `nohup`.

---

## 📁 Directory Structure Overview

```text
Aurindum/
├── README.md                      <- Master guide & documentation
├── run_all_experiments_gpu.sh     <- Master script to run all 3 series sequentially on GPU
├── start_nohup_experiments.sh     <- One-click background launcher with PID tracking
│
├── best_model/                    <- Automatically updated winning model & method registry
│   ├── BEST_MODEL.md              <- Markdown report of the current best performing model
│   ├── best_metrics.json          <- Metrics record (AbsRel, RMSE, delta1, per-band metrics)
│   ├── best_config.yaml           <- Hyperparameters of the winning configuration
│   ├── tracker.py                 <- BestModelTracker class used across all experiments
│   └── sample_predictions/        <- Qualitative depth maps & error heatmaps
│
├── 1_gradient_polar_fusion/       <- Proposal A: Poisson Gradient Blending & Shift Alignment
│   ├── run.py                     <- Standalone execution script
│   ├── run_gpu.sh                 <- GPU execution script
│   ├── gradient_blending.py       <- Poisson 2D solver for seamless polar fusion
│   ├── shift_alignment.py         <- Shift-decoupled affine disparity alignment (DA360-style)
│   ├── config.yaml                <- Method 1 settings
│   ├── logs/                      <- Detailed logs
│   └── outputs/                   <- Metric summaries and figures
│
├── 2_mobius_tta_ensembling/       <- Proposal B: Test-Time Möbius Augmentation Ensembling
│   ├── run.py                     <- Standalone execution script
│   ├── run_gpu.sh                 <- GPU execution script
│   ├── mobius_transform.py        <- Conformal Riemann sphere stereographic mappings
│   ├── tta_ensemble.py            <- Multi-scale test-time augmentation & prior fusion
│   ├── config.yaml                <- Method 2 settings
│   ├── logs/                      <- Detailed logs
│   └── outputs/                   <- Metric summaries and figures
│
├── 3_structured3d_benchmark/      <- Proposal C: Structured3D Real Foundation Benchmark
│   ├── run.py                     <- Standalone comparative benchmark runner
│   ├── run_gpu.sh                 <- GPU execution script
│   ├── prepare_data.py            <- Structured3D archive parser & millimeter-to-meter converter
│   ├── benchmark_evaluator.py     <- 4-way evaluation (Baseline vs Tangent vs M1 vs M2)
│   ├── config.yaml                <- Benchmark settings
│   ├── logs/                      <- Detailed logs
│   └── outputs/                   <- Benchmark tables (CSV & JSON)
│
└── core modules/                  <- Shared geometry, models, datasets & evaluation libraries
    ├── geometry/                  <- Spherical, tangent plane & projection transformations
    ├── models/                    <- Foundation model wrappers (DAP, DA360, MiDaS, Oracle)
    ├── datasets/                  <- Structured3D, PanoX, and synthetic procedural generators
    └── evaluation/                <- Per-latitude band metrics (AbsRel, RMSE, delta1-3)
```

---

## 🔧 v2 fixes after the first GPU run (Nov 2026)

The first full run (commit `4d88a2a`) exposed evaluation and method bugs; numbers from it are **not** comparable
with v2 and should not be reported.

| Area | Bug | Fix |
|---|---|---|
| Evaluation (all series) | Affine disparity fitted on \|φ\|<30° only, then extrapolated to the poles with a 1e3 m clip → single-scene blow-ups (AbsRel 385) dominated means | `evaluation/protocol.py`: both `align-all` (headline) and `align-equatorial` protocols, predictions clamped to the GT range, **median + mean** over scenes and per-band **win rate** vs baseline |
| Series 1 | Tangent alignment returned *range* but was fused with ERP *disparity* | `align_tangent_disparity_to_erp` returns ERP disparity |
| Series 1 | Anchor ring \|φ\|≤35° barely overlaps a 90° polar view → silent fit on the pole | anchor ring \|φ\|≤60° (45–60° overlap), fallback = lowest-latitude 20 % of the overlap |
| Series 1 | Poisson: central-diff gradients vs 5-point Laplacian, pole rows wrapped (np.roll), 100 SOR iterations | consistent forward-difference least-squares integration, Neumann at the poles, exact sparse solve |
| Series 1 | — | optional texture gating (`blending.texture_tau`, `texture_gate_mode`) |
| Series 2 | `sample_erp` was given lon/lat in **radians** instead of pixel coordinates → every warped image was a blurred top-left corner | coordinates go through `lonlat_to_pixel` |
| Series 2 | Pure dilations fix both poles → poles never reached the equator | passes are `{pitch, scale}`; default includes pitch ±90° |
| Series 2 | Fusion weight used warped-frame latitude on the original grid | weight = latitude at which each original pixel was *seen* |
| Series 2 | No per-pass (s, t) handling | equatorial re-anchoring of every pass to the identity pass (`reanchor: auto`) |
| Series 3 | `Tangent_Spatial` blended raw tangent disparity (AbsRel ~146) | uses the aligned tangent views (same as Method 1) |
| Tracker | Synthetic and Structured3D results competed in one registry | per-benchmark registries `best_model/<benchmark>/` (top-level files = legacy v1) |
| Models | DAP load failure silently fell back to MiDaS | fatal unless `model.allow_model_fallback: true` |

Regression tests: `pytest -q tests/test_methods.py`. On a controlled affine-disparity oracle (random (s, t) per call,
latitude-growing ERP noise) all three corrections now reduce 75–90° AbsRel in every scene.

---

## 🚀 Running on Remote GPU Server via `nohup`

All experiments are configured for headless execution on a remote Linux/Unix GPU server.

### Option 1: Run All 3 Experiments Sequentially (Recommended)
This runs Method 1 $\to$ Method 2 $\to$ Method 3 $\to$ Best Model evaluation in sequence:
```bash
cd Aurindum
chmod +x start_nohup_experiments.sh run_all_experiments_gpu.sh */run_gpu.sh

# Launch in background with nohup
./start_nohup_experiments.sh
```

To monitor progress:
```bash
tail -f logs/nohup_runner.log
```

### Option 2: Run an Individual Experiment on GPU
```bash
# Example: Run Method 1 only
cd Aurindum/1_gradient_polar_fusion
nohup bash run_gpu.sh > logs/gpu_run.log 2>&1 &
```

---

## 🏆 Automatic `best_model/` Tracking

Whenever any experiment script runs, it reports its results to [`best_model/tracker.py`](best_model/tracker.py).
If the run outperforms the current best polar AbsRel ($|\phi| \ge 60^\circ$) or global AbsRel:
1. `best_model/best_metrics.json` is updated with complete global and band-by-band metrics.
2. `best_model/best_config.yaml` saves the exact winning configuration.
3. `best_model/BEST_MODEL.md` is re-generated with formatted Markdown comparison tables.
4. `best_model/sample_predictions/` updates with colorized RGB, ground-truth depth, predicted depth, and error heatmap.
