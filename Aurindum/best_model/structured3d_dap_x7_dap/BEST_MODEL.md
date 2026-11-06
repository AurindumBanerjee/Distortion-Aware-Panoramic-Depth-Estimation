# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 01:32:22`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.0261**, Global AbsRel = **0.0343**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.0343** | 0.0042 | 0.0790 | 0.0530 | 99.64% | 99.93% | 99.99% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.0412 | 0.1168 | 99.3% | Stable |
| Low Latitude | 15-30° | 0.0390 | 0.1024 | 99.4% | Stable |
| Mid Latitude | 30-45° | 0.0345 | 0.0685 | 99.8% | Stable |
| High Latitude | 45-60° | 0.0316 | 0.0550 | 99.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0284** | 0.0463 | 100.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.0237** | 0.0375 | 100.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_x7_dap
data:
  dataset: structured3d
  height: 512
  list: test.txt
  max_scenes: null
  root: data/structured3d
  split: eval
  width: 1024
distortion_curve: results/sweep_dilation_dap_s3_calib.json
evaluation:
  log_dir: logs_dap_x7_dap
  max_depth: 10.0
  methods:
  - Tangent_Spatial
  - Method1_GradientFusion
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_dap_x7_dap
  protocols:
  - none
  - align-all
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  curve_gate: true
  fov_deg: 90.0
  phi_threshold: 45.0
  polar_source: auto
  resolution: 384
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark (DAP)
mobius_tta:
  anchor_max_lat: 30.0
  curve_gate: true
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
