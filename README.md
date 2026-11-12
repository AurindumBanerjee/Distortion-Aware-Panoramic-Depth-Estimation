# Distortion-Aware Panoramic Depth Estimation

**Coursework Project · IIT Jodhpur**  
**Authors:** Aurindum Banerjee (B23CS1006) · Harshita Vachhani (B23EE1026) · Lokesh Motwani (B23CS1033)

---

## 1. Problem

Monocular depth estimation models evaluated on equirectangular projection (ERP) 360° panoramas exhibit severe error spikes at high latitudes near the poles (floors and ceilings). In standard perspective backbones, polar AbsRel error roughly doubles compared to the equator.

Prior literature attributes this degradation primarily to ERP geometric distortion: horizontal stretching proportional to $1/\cos(\phi)$, reaching $3.9\times$ at $75^\circ$ latitude and diverging at the poles. However, diagnostic content-rotation sweeps (moving identical visual content from the equator to the pole) do not produce a polar error rise. Instead, investigation reveals that real-world polar error is predominantly caused by capture faults: camera tilt, tripod and nadir occlusion, vignetting, motion blur, and sensor quantization.

---

## 2. Approach

All depth backbones (**MiDaS DPT-Hybrid**, **DAP**, **DA360**, **DA²**) remain strictly frozen as black boxes; no weights are fine-tuned or retrained.

The framework addresses polar degradation through inference-time modular pipelines:
1. **Geometric Reprojection & Conformal Fusion:** Resampling polar caps into low-distortion tangent or stereographic pinhole projections, inferring depth with frozen models, and fusing back via gradient-domain Poisson blending (ACGF v2) or weighted spherical fusion without ground truth.
2. **Capture-Fault Catalogue & Correction Front-End:** A 10-fault detection catalogue paired with targeted photometric and geometric mitigations (e.g., planar ring fitting, inpainting, deblurring, exposure matching).
3. **Do-No-Harm Gating Policy:** Calibrated under a strict leave-one-dataset-out protocol, activating corrections only when detected faults warrant intervention, guaranteeing that clean panoramas suffer no regression.

---

## 3. Main Results

Evaluation across frozen foundation models and external test distributions demonstrates substantial polar error reductions:

| Dataset / Benchmark | Model | Scenario / Fault | Polar Error Reduction |
| :--- | :--- | :--- | :---: |
| **Stanford2D3D** (External) | DAP | Real polar caps (clean) | **−34.8%** |
| **Stanford2D3D** (External) | DAP | Camera tilt | **−32.0%** |
| **Stanford2D3D** (External) | DAP | Sensor shake | **−32.9%** |
| **Stanford2D3D** (External) | DAP | Heavy JPEG compression | **−47.1%** |
| **NYC Street Panoramas** (External) | DAP | Camera tilt | **−47.4%** |
| **NYC Street Panoramas** (External) | DAP | Tripod / nadir patch | **−89.3%** |
| **NYC Street Panoramas** (External) | DAP | Sensor shake | **−60.4%** |
| **NYC Street Panoramas** (External) | DAP | Vertical FOV crop | **−36.4%** |

On clean NYC panoramas the policy changes no frames (+0.0%), so clean inputs are left untouched.

---

## 4. Data

The benchmark evaluates six distinct panoramic datasets:
- **Core Datasets (used for calibration and analysis):**
  - `Structured3D` (Synthetic indoor architectural scenes)
  - `PanoX` (Real-world indoor and outdoor high-resolution panoramas)
  - `Holo360D Indoor` (Real indoor LiDAR-mesh ground truth)
  - `Holo360D Outdoor` (Real outdoor LiDAR-mesh ground truth)
- **External Held-Out Datasets (never used for policy selection or tuning):**
  - `Stanford2D3D` (Real-world building scale panoramas with real tripod/nadir occlusions)
  - `NYC Street Panoramas` (Real outdoor street scenes with kilometre-scale depth range)

---

## 5. Code-Only vs. Artifacts

To facilitate distribution and reproducibility within lightweight submission constraints (< 9.5 MB), the repository strictly decouples source code from large precomputed artifacts:
- **Code-Only Tree:** Contains the core library `pano`, inference methods in `methods`, experiment orchestrators in `experiments`, execution scripts in `scripts`, configurations in `configs`, the 173-test suite in `tests`, and the compiled report in `report/final_report.pdf`.
- **Artifacts Directory (`artifacts/`):** Houses precomputed evaluation rows (CSVs), JSON summary tables, generated figures, and cached sample outputs. It is excluded from version control archives via `.gitattributes` (`export-ignore`) and `.gitignore`.
- **Submission Archive:** Generated via `python scripts/make_submission_zip.py`, producing a clean, self-contained `submission_code.zip` under **8.52 MB**.

---

## 6. Repository Architecture

```text
Distortion-Aware-Panoramic-Depth-Estimation/
├── pano/                             # Core library (installed as pano-distortion-depth)
│   ├── geometry/                     # Spherical, ERP, tangent plane, and stereographic math
│   ├── models/                       # Frozen depth model wrappers (MiDaS, DAP, DA360, DA²)
│   ├── datasets/                     # Panorama dataset loaders, parsers, and synthetic rendering
│   ├── evaluation/                   # Latitude analysis, per-band error, and alignment protocols
│   ├── inference/                    # Projection, alignment, rotation, and fusion pipelines
│   ├── visualization/                # Error heatmaps, colormaps, and panoramic projections
│   └── paths.py                      # Canonical environment-configurable repository paths
├── methods/                          # Inference-time correction implementations
│   ├── projection/                   # Tangent plane, rotation ensemble, hybrid, 360MonoDepth, ACGF v2
│   ├── polar_fusion/                 # Gradient-domain Poisson polar fusion and planar priors
│   ├── mobius_tta/                   # Möbius test-time augmentation ensembling
│   └── capture_faults/               # 10-fault catalogue, detection, and mitigation front-end
├── experiments/                      # Experiment suites and evaluation runners
│   ├── benchmark/                    # Foundation model cross-dataset benchmark and tracking
│   ├── projection/                   # Projection correction ablation and comparison runner
│   └── followups/                    # Protocol, domain gating, distillation, and view sweeps
├── configs/                          # Experiment configuration YAMLs
│   ├── benchmark/                    # Foundation model benchmark configurations
│   ├── projection/                   # ACGF, tangent, and baseline configurations
│   └── followups/                    # Follow-up experiment configurations
├── scripts/                          # Entry-point execution and analysis scripts
│   ├── run/                          # Experiment runners (run_submission.sh, sweeps, studies)
│   ├── analysis/                     # Policy calibration, statistical checks, and reports
│   ├── figures/                      # Submission figure generation and paper panels
│   ├── data/                         # Dataset download and list manifest generators
│   ├── setup_third_party.sh          # Dependency cloning (DAP, external repos)
│   └── make_submission_zip.py        # Git archive code bundler (< 9.5 MB)
├── tests/                            # Test suite (173 tests)
│   ├── geometry/                     # Spherical and projective math validation
│   ├── models/                       # Model wrapper contracts
│   ├── methods/                      # Projection, fusion, TTA, and fault mitigations
│   ├── experiments/                  # Evaluation protocol and benchmark smoke tests
│   ├── figures/                      # Headless figure drawing verification
│   └── merge/                        # Union integration test verifying cross-module interop
├── report/                           # Technical reports and publication materials
│   ├── final_report.pdf              # Primary compiled technical report
│   ├── main.tex                      # LaTeX source document
│   ├── neurips_2025.sty              # Formatting style sheet
│   └── figs/                         # Vector and high-resolution figures
├── artifacts/                        # Heavy results, metrics CSVs, JSONs, logs, and figures
│   ├── results/                      # Precomputed benchmark, projection, NYC, and followup outputs
│   ├── logs/                         # Execution logs
│   ├── figures/                      # Generated visual artifacts
│   ├── notebooks/                    # Interactive exploration notebooks
│   └── archives/                     # Archived qualitative samples and legacy records
├── app/                              # Interactive Streamlit results explorer
│   └── streamlit_app.py              # Full interactive GUI with all 15 analysis views
├── pyproject.toml                    # Package build specification (pip install -e .)
├── requirements.txt                  # Pinned Python environment dependencies
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules (protects data, weights, and caches)
└── .gitattributes                    # Export ignore configuration for lightweight packaging
```

---

## 7. Installation & Setup

### Environment Setup
Python 3.10+ is recommended. In your environment:
```bash
# Clone the repository
git clone https://github.com/Distortion-Aware-Panoramic-Depth-Estimation/Distortion-Aware-Panoramic-Depth-Estimation.git
cd Distortion-Aware-Panoramic-Depth-Estimation

# Install pinned dependencies and editable package
pip install -r requirements.txt
pip install -e .
```

### Third-Party Dependencies (Optional for Live Model Inference)
To clone third-party repositories:
```bash
bash scripts/setup_third_party.sh
```

---

## 8. Verification & Testing

The repository maintains an automated test suite covering spherical geometry, model contracts, inference pipelines, and integration invariants:

```bash
# Run all automated tests
pytest -q

# Run specific subsystems
pytest tests/geometry/ -q
pytest tests/methods/ -q
pytest tests/experiments/ -q
pytest tests/merge/ -q
```

---

## 9. Interactive Results Explorer

An interactive Streamlit application visualizes all precomputed benchmark results, latitude error profiles, and qualitative comparisons across models without GPU requirements:

```bash
streamlit run app/streamlit_app.py
```

Available navigation pages include:
- **Overview & Headline Numbers:** High-level comparative summaries and metric tables.
- **Inference-Time Projection Corrections:** Detailed inspection of Tangent, Rotation, Hybrid, 360MonoDepth, and ACGF v2.
- **Latitude & Distortion Sweeps:** Controlled rotation, dilation, and flip experiments.
- **Capture-Fault Catalogue & Correction:** 10-fault analysis, detector response, and repair outcomes.
- **Real-World Evaluations (NYC & Stanford2D3D):** Quantitative results on outdoor city streets and real indoor spaces.
- **Follow-up Studies:** Scale-only evaluation protocols, domain gating, and view sweeps.

---

## 10. Building Code Submission Archive

To build a standalone, lightweight submission archive respecting `.gitattributes` export-ignore:
```bash
python scripts/make_submission_zip.py
```
This command creates `submission_code.zip` under **8.52 MB**, strictly complying with the 9.5 MB submission threshold.

---

## 11. License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.
