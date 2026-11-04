# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 22:03:03`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1034**, Global AbsRel = **0.1209**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1209** | 0.5272 | 4.6627 | 0.2191 | 90.15% | 96.82% | 98.84% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1850 | 6.7777 | 75.4% | Stable |
| Low Latitude | 15-30° | 0.1357 | 3.9003 | 88.3% | Stable |
| Mid Latitude | 30-45° | 0.1194 | 3.2668 | 92.7% | Stable |
| High Latitude | 45-60° | 0.1178 | 3.1593 | 95.4% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1164** | 0.8820 | 99.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.0903** | 0.3411 | 100.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_abl_dap_panox_rot_on
data:
  dataset: panox
  height: 512
  list: test.txt
  max_scenes: 60
  root: data/panox
  width: 1024
evaluation:
  log_dir: logs_dap_panox_abl_dap_panox_rot_on
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_dap_panox_abl_dap_panox_rot_on
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
  fusion_mode: distortion_weighted
  gate_lat:
  - 30
  - 55
  passes:
  - pitch: 90
    scale: 1.0
  - pitch: -90
    scale: 1.0
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
