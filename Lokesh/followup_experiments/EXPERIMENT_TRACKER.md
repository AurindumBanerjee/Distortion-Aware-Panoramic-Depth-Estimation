# Follow-up Experiments Tracker & Audit Ledger

This document tracks the five follow-up experiments designed to evaluate panoramic depth estimation under distortion, scale protocols, rotation gating, and multi-view fusion on Kaggle 2x Tesla T4 GPUs.

---

## 1. Experiment Overview & Architecture Matrix

| ID | Name | Model | Dataset | Input Modality | Core Question / Hypothesis | Execution Script | Primary Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Scale-Only Protocol** | DA360 Large | Structured3D | Full ERP | Does scale-only alignment ($s \cdot d$) reveal distortion that affine shift ($a \cdot d + b$) conceals? | `01_scale_only_protocol/run_gpu.sh` | `REPORT.md`, `per_scene.csv`, `summary.json` |
| **02** | **Domain-Conditioned Gate** | DA360 Large | PanoX | ERP + Rotations | Can latitude rotation gates ($\theta \in [30^\circ..70^\circ]$) be calibrated via Leave-One-Environment-Out (LOEO)? | `02_domain_conditioned_gate/run_gpu.sh` | `REPORT.md`, `folds.json`, `summary.json` |
| **03** | **Student Fine-Tuning** | Student U-Net (Teacher: DA360) | PanoX | ERP | Can a student model trained on teacher pseudo-disparity with patch-normalization learn polar correction without GT? | `03_panda_style_finetuning/run_gpu.sh` | `best.pt`, `history.csv`, `training_summary.json` |
| **04** | **360MonoDepth 20-View** | MiDaS DPT-Hybrid | PanoX | Tangent (20 views vs 2 poles) | Does 20-view icosahedral L-BFGS alignment outperform analytical 2-pole polar tangent correction? | `04_mono360_20view/run_gpu.sh` | `REPORT.md`, `per_scene.csv`, `summary.json` |
| **05** | **FOV $\times$ Resolution Sweep** | MiDaS DPT-Hybrid | PanoX | Tangent views | How do tangent FOV ($70^\circ..130^\circ$) and resolution ($256..512$) trade off polar accuracy and latency? | `05_fov_resolution_sweep/run_gpu.sh` | `REPORT.md`, `summary.json` |

---

## 2. Infrastructure & Environment Specifications

- **Compute:** Kaggle Cloud Kernel (Linux x86_64 Ubuntu container).
- **Accelerators:** 2x NVIDIA Tesla T4 GPUs (16 GB GDDR6 VRAM each, 32 GB total).
- **Client:** VS Code on Windows connected to Kaggle via remote Jupyter Kernel Provider.
- **Python Runtime:** Python 3.10 / 3.11 (`/opt/conda/bin/python`), PyTorch with CUDA 12/13.
- **Mounted Kaggle Datasets:**
  - `lokeshmotwani213/structured3d-panoramic-depth` (322 MB, synthetic indoor).
  - `lokeshmotwani213/panox-panoramic-depth` (1.41 GB, realistic multi-environment, 32-bit float OpenEXR depth).
  - `lokeshmotwani213/lokesh-code` (v4, pure Unix LF line endings, automated workspace patcher).
- **Pretrained Weights:**
  - `DA360_large.pth` (~1.34 GB, Hugging Face Hub `hljiang/DA360`).
  - `dpt_hybrid_384.pt` (~470 MB, MiDaS v3 release).

---

## 3. Pilot Benchmark Results (`LIMIT = 16`)

On November 5, 2026, the complete sequential suite (`RUN = "all"`, `LIMIT = 16`) was executed end-to-end with **0 failures**:

```
================================================================
Experiment all execution log:
  01_scale_only_protocol:     Completed in 52s (16 scenes)
  02_domain_conditioned_gate: Completed in 2m 42s (16 scenes, 6 gate thresholds)
  04_mono360_20view:          Completed in 3m 16s (16 scenes, 20-view L-BFGS)
  05_fov_resolution_sweep:    Completed in 3m 08s (16 scenes, 12 configurations)
Finished with failed stages: 0
================================================================
```

### Key Scientific Findings from Pilot Run:

1. **Polar Tangent Correction is FOV-Driven, Not Resolution-Driven (Experiment 05):**
   - High-latitude ($75^\circ$–$90^\circ$) polar error drops from **0.3328 (baseline ERP)** down to **0.1800 (130° FOV, 512 size)**, representing a **~46% error reduction**.
   - Comparing resolutions at $130^\circ$ FOV:
     - $256 \times 256$: AbsRel = $0.1870$
     - $384 \times 384$: AbsRel = $0.1804$
     - $512 \times 512$: AbsRel = $0.1800$
   - **Conclusion:** Expanding perspective FOV to capture surrounding context is vastly more impactful than increasing pixel resolution.

2. **Computational Efficiency of 2-Pole vs 20-View (Experiment 04):**
   - 20-view icosahedral L-BFGS solve takes **$\sim 10$ seconds per scene** and requires **20 neural network forward passes**.
   - 2-pole polar tangent inference takes **$\sim 0.3$ seconds** (3 network passes) and analytical cosine blending.
   - The trade-off between dense multi-view optimization and lightweight polar stitching is clearly quantified.

3. **Scale vs Affine Sensitivity (Experiment 01):**
   - Established baseline cluster-bootstrapped confidence intervals (2,000 resamples) across equatorial ($0^\circ$–$45^\circ$) and polar ($60^\circ$–$90^\circ$) latitude bands.

---

## 4. Pending / Next Steps

### Step 1: Run Experiment 03 (Two-GPU Student Training)
- **Why Pending:** Student training is opt-in because it optimizes a neural network over multiple epochs on both T4 GPUs.
- **How to Run:**
  1. In Cell 2 of `kaggle_two_t4_runner.ipynb`, set:
     ```python
     RUN = "03"
     LIMIT = None
     ```
  2. Run Cell 2 (verifies both T4 GPUs: `CUDA_VISIBLE_DEVICES=0,1`).
  3. Run Cell 4 (launches `03_panda_style_finetuning/train.py`).
  4. Once training finishes and `best.pt` is generated, run **Cell 6 (`student-eval`)** to evaluate the student against ground truth.

### Step 2: Run Full-Scale Benchmark (`LIMIT = None`)
- **Full Scale Setup:**
  1. In Cell 2 of `kaggle_two_t4_runner.ipynb`, set:
     ```python
     RUN = "all"
     LIMIT = None  # Process all 200 scenes across all 8 environments
     ```
  2. Run Cell 2, then run Cell 4.
  3. Expected total runtime: $\sim 35$–$45$ minutes.
  4. When finished, run Cell 8 to view the full-scale cross-environment statistical tables.
