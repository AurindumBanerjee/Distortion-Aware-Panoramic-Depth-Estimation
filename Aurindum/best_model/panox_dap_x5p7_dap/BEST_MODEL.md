# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 02:08:55`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.1854**, Global AbsRel = **0.2006**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2006** | 0.5748 | 4.1857 | 0.3364 | 70.18% | 93.66% | 98.71% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2504 | 6.4372 | 54.8% | Stable |
| Low Latitude | 15-30° | 0.1970 | 3.7638 | 66.5% | Stable |
| Mid Latitude | 30-45° | 0.1835 | 3.2757 | 72.8% | Stable |
| High Latitude | 45-60° | 0.1871 | 1.8323 | 76.1% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1941** | 0.9146 | 74.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1766** | 0.6270 | 70.6% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_x5p7_dap
data:
  dataset: panox
  height: 512
  list: test.txt
  max_scenes: null
  root: data/panox
  split: all
  width: 1024
evaluation:
  log_dir: logs_dap_panox_x5p7_dap
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_dap_panox_x5p7_dap
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
  gate_lat: null
  min_weight: 1.0
  passes:
  - pitch: 30
    scale: 1.0
  - pitch: -30
    scale: 1.0
  - pitch: 60
    scale: 1.0
  - pitch: -60
    scale: 1.0
  - pitch: 90
    scale: 1.0
  - pitch: -90
    scale: 1.0
  reanchor: auto
  weight_power: 0
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
