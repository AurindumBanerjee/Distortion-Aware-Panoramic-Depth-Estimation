


﻿# Distortion-Aware Panoramic Depth Estimation

This project studies inference-time methods for monocular depth estimation on 360-degree equirectangular (ERP) panoramas. The backbone is kept frozen; the experiments change the view geometry, align predictions to a baseline, and fuse views back into the ERP grid.

## Status and evidence scope (10 November 2026)

The repository contains several related but distinct evidence sets. Keep their model and dataset scopes separate.

- **Core MiDaS study:** MiDaS DPT-Hybrid and MiDaS Swin2-Tiny on 24 procedurally rendered indoor panoramas with exact range ground truth.
- **External real-data comparison:** MiDaS DPT-Hybrid on 75 NYC street panoramas from the DAP dataset. This is a MiDaS evaluation using DAP data; it is not an evaluation of the DAP network.
- **Follow-up GPU studies:** DA360 on 200 Structured3D scenes (Study 01); a DA360 LOEO gate on 200 PanoX panoramas across eight environments (Study 02); a 50-scene held-out DA360 student evaluation (Study 03); and MiDaS 20-view and FOV-resolution experiments on 200 PanoX panoramas (Studies 04 and 05).
- **Unfinished work:** Study 06 is code/design only. The Experiment 03 student checkpoint is missing from this checkout. Holo360D test-split validation for Experiment 05 is pending.
- **DAP:** the wrapper and configurations exist, but no verified DAP benchmark is included in the Lokesh result folders. Do not generalise MiDaS or DA360 results to DAP.

## Research report

The consolidated NeurIPS-style technical report is available as:

- [`Final_Report.pdf`](Final_Report.pdf)
- Source: [`Report/draft/main.tex`](Report/draft/main.tex)
- Style: [`Report/draft/neurips_2025.sty`](Report/draft/neurips_2025.sty)
- Figures: [`Report/draft/figs/`](Report/draft/figs/)

The report uses the NeurIPS 2025 LaTeX style for formatting only. It is an IIT Jodhpur project technical report, not a claim of NeurIPS submission, review, or acceptance. To rebuild from the `Lokesh/` directory, run:

```bash
tectonic Report/draft/main.tex
```

The report draws from the saved run artifacts and explicitly records the missing checkpoint, unrun study, and pending Holo360D/DAP evaluations.

## Motivation and geometry

ERP maps longitude and latitude linearly to image columns and rows. The local horizontal stretch grows approximately as `1 / cos(latitude)`, so appearance statistics change toward the poles. A latitude-dependent error trend is not, by itself, proof that projection distortion caused the error: scale anchoring, scene content, orientation, and model domain can also change the measured result.

The project tests alternative views while keeping the depth model frozen:

1. **Tangent-plane inference:** one or more gnomonic views centred near a pole.
2. **Rotation inference:** rotate the sphere so polar content is moved toward the centre of the ERP input, predict, and rotate the result back.
3. **Hybrid inference:** combine tangent and rotated views, align them to the baseline without using ground truth at inference time, and blend the result into the ERP prediction.
4. **Full-sphere 20-view inference:** use icosahedral tangent views, overlap alignment, and frustum blending.

For affine-invariant disparity models, the evaluation uses a global affine fit in disparity space. Both `align-all` (fit on all valid pixels) and `align-equatorial` (fit only on `|latitude| < 30 degrees`) are reported. The second protocol keeps the trusted equatorial anchor fixed while polar predictions change; it can extrapolate poorly, so it must be shown alongside the global fit.

## Repository layout

```text
Lokesh/
  Report/                    NeurIPS-style report source and figures
  configs/                   Model and dataset configurations
  datasets/                  Panorama loaders and synthetic renderer
  geometry/                  Spherical and ERP/tangent projection geometry
  inference/                 Baseline, tangent, rotation, alignment and fusion
  evaluation/                Metrics, latitude profiles and statistical analysis
  experiments/               Core experiment entry points
  results/                   Core run outputs, CSV tables, JSON and figures
  scripts/                   Data-list builders and result-table generation
  tests/                     Geometry, loader and inference tests
  followup_experiments/      Eight isolated experiments/evaluation studies
  weights/                   Local model checkpoints (git-ignored)
  _archives/                 Preserved prior runs and debug samples
```

The parent repository also contains the broader project work from Aurindum and Harshita. This README describes the `Lokesh/` contribution only.

## Models and data

### Models

| Model | Role in this folder | Output/evaluation note |
|---|---|---|
| MiDaS DPT-Hybrid | Main perspective relative-depth model | Affine-in-disparity alignment; ERP at 384 x 768, tangent views at 384 x 384 |
| MiDaS Swin2-Tiny | Second-model check | Perspective relative-depth model; fixed 256-pixel inference wrapper |
| DA360 | Scale-protocol and domain-gate follow-ups | Scale-invariant disparity; scale-only is the preferred headline fit |
| DAP | Target-model wrapper/configuration only | No verified DAP result is included in this folder |

### Datasets

| Dataset | Local root / list | Use and current status |
|---|---|---|
| Synthetic | `data/synthetic/test.txt` | 24 indoor ERP panoramas, 512 x 1024, exact range GT, seed 0 |
| NYC street panoramas | `data/nyc_dap/test.txt` | 75 real outdoor panoramas evaluated with MiDaS DPT-Hybrid |
| Structured3D | `../../structured3d/structured3d/test.txt` relative to `Lokesh/` | 200 scenes in DA360 Study 01 |
| PanoX | `../../panox/panox/test.txt` relative to `Lokesh/` | 200 panoramas across eight environments in Studies 02, 04 and 05 |
| Holo360D | `data/holo360d/` when provided | Current local training-scene subset is only for loader/mask smoke testing; no held-out test evaluation is reported |

Datasets and model weights are not generally stored in Git. `weights/` and `data/` are git-ignored. Obtain gated datasets from their owners and keep credentials out of notebooks and configuration files.

## Installation and core runs

Use the project's Python environment and install:

```bash
pip install -r requirements.txt
```

The MiDaS DPT-Hybrid checkpoint is expected at `weights/dpt_hybrid_384.pt`; the Swin2-Tiny checkpoint is expected at `weights/dpt_swin2_tiny_256.pt`.

Generate the synthetic set and run the core experiment from `Lokesh/`:

```bash
python -m datasets.synthetic --out data/synthetic --n 24 --seed 0
python run_experiment.py --config configs/default.yaml
python run_experiment.py --config configs/midas_swin2_tiny.yaml
python run_experiment.py --config configs/midas_nyc_dap.yaml
```

The core runner supports geometry checks, baseline and correction inference, latitude profiles, content-vs-latitude controls, resolution and timing studies, and qualitative comparisons. To regenerate the aggregate Markdown tables from the saved result folders:

```bash
python scripts/make_results_tables.py \
  results/midas_dpt_hybrid_synthetic \
  results/midas_swin2_tiny_synthetic \
  results/midas_dpt_hybrid_nyc
```

The generated table is `results/RESULT_TABLES.md`. The cross-domain comparison is `results/synthetic_vs_nyc_comparison.md`; the narrative for the core work is `RESULTS.md`.

## Follow-up studies

Eight studies/evaluations are isolated under [`followup_experiments/`](followup_experiments/README.md). They keep separate configs, runners, logs, timestamped outputs, and summaries.

| Study | Research question | Evidence status |
|---|---|---|
| 01 - Scale-only protocol | Does DA360 scale-only disparity alignment differ from affine fitting? | 200-scene Structured3D run saved |
| 02 - Domain-conditioned gate | Does a PanoX threshold transfer under leave-one-environment-out calibration? | 200 scenes / eight environments; all folds select baseline |
| 03 - PanDA-inspired student | Can a compact student preserve DA360 teacher quality? | 50-scene held-out evaluation saved; student is weaker and checkpoint is missing locally |
| 04 - 20-view 360MonoDepth-style | Does full-sphere icosahedral inference help over two-pole tangent views? | 200-scene PanoX run saved |
| 05 - FOV/resolution sweep | How do tangent-view FOV and resolution affect polar error? | 200-scene PanoX run saved; Holo360D test validation pending |
| 06 - Structure-at-the-poles gate | Can image-level pole structure decide when correction is appropriate? | Design and code only; not run |
| 07 - Real NYC 20-view transfer | Does full-sphere 20-view inference transfer to real NYC data and beat two-pole tangent directly? | 182-frame manifest generated; all 364 referenced files and three RGB/range samples preflight-checked; GPU run pending |
| 08 - Paired PanoX significance audit | Is the Experiment 04 20-view-vs-two-pole result directly supported? | Reanalysis completed; direct 95% intervals include zero under both alignments |

The selected run IDs, result tables, confidence intervals, caveats, and generated figures are compiled in [`followup_experiments/RESULTS.md`](followup_experiments/RESULTS.md). The Experiment 08 direct paired PanoX audit and Experiment 07 NYC transfer guide/results are documented separately under their respective folders. Earlier timestamped runs are preserved. The selected outputs are not overwritten by new runs.

For Kaggle setup and execution details, see [`followup_experiments/README.md`](followup_experiments/README.md) and the `kaggle_two_t4_runner.ipynb` notebook. DA360-dependent runs require the official DA360 implementation and checkpoint to be mounted separately. Do not silently substitute MiDaS for DA360.

## Evaluation and interpretation rules

- Report `align-all` and `align-equatorial` for affine relative-depth models; they answer different questions.
- Use the same validity masks for paired comparisons. Invalid depth is excluded rather than interpolated into ground truth.
- Treat PanoX environment groups as the independent units for cross-environment bootstrap analysis; 200 adjacent panoramas are not 200 independent environments.
- The saved Experiment 04/05 bootstrap intervals compare a method/configuration with baseline. They do not establish pairwise significance between alternatives.
- Report inference calls and runtime alongside accuracy. Full-sphere methods can be materially more expensive.
- Do not describe the MiDaS NYC evaluation as a DAP-model evaluation, and do not present the Holo360D loader smoke test as held-out benchmark performance.

## Tests

From `Lokesh/`:

```bash
python -m pytest -q tests
```

The current local validation snapshot passed 33 tests. The Holo360D loader-specific smoke test is also available as:

```bash
python -m followup_experiments.tests.smoke_holo360d_loader
```

## Licensing and attribution

See `LICENSE` and the licenses of third-party model repositories and datasets. The vendored MiDaS code and model weights retain their respective upstream terms; gated datasets must be obtained under their own access and usage agreements.