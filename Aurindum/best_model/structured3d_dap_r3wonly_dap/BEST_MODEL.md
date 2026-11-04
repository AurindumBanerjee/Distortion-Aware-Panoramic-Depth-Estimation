# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 16:05:51`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.0268**, Global AbsRel = **0.0339**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.0339** | 0.0043 | 0.0797 | 0.0530 | 99.61% | 99.92% | 99.99% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.0419 | 0.1190 | 99.2% | Stable |
| Low Latitude | 15-30° | 0.0399 | 0.0979 | 99.4% | Stable |
| Mid Latitude | 30-45° | 0.0341 | 0.0693 | 99.7% | Stable |
| High Latitude | 45-60° | 0.0325 | 0.0574 | 99.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0286** | 0.0465 | 100.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.0250** | 0.0385 | 100.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_r3wonly_dap
data:
  dataset: structured3d
  height: 512
  list: test.txt
  max_scenes: null
  root: data/structured3d
  split: eval
  width: 1024
distortion_curve: results/sweep_dap_s3_calib.json
evaluation:
  log_dir: logs_dap_r3wonly_dap
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_dap_r3wonly_dap
  protocols:
  - none
  - align-all
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  fov_deg: 90.0
  phi_threshold: 45.0
  polar_source: auto
  resolution: 384
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark (DAP)
mobius_tta:
  anchor_max_lat: 30.0
  curve_weights: true
  fusion_mode: distortion_weighted
  gate_lat:
  - 30
  - 55
  passes:
  - pitch: 90.0
    scale: 1.0
  - pitch: -90.0
    scale: 1.0
  - pitch: 0.0
    scale: 1.6
  - pitch: 0.0
    scale: 0.625
  preset: rotation_only
  reanchor: auto
model:
  device: auto
  name: dap
  repo: third_party/DAP
  scale: metric
  space: depth
  weights: weights/dap/model.pth
```

## 3. Qualitative Predictions
Sample output files saved in `sample_predictions/`:
- `sample_rgb.png`: Input equirectangular panorama
- `sample_gt_depth.png`: Ground truth Euclidean depth
- `sample_best_pred.png`: Colorized prediction from current best model
- `sample_error_heatmap.png`: Pixel-wise absolute relative error heatmap
- `comparison_overview.png`: Side-by-side composite visual overview
