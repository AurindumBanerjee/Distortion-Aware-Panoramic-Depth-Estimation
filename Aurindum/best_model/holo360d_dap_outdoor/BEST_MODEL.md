# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:30:56`  
> **Winning Method:** **Structured3D: Tangent_Spatial**  
> **Key Highlights:** Polar AbsRel = **0.2419**, Global AbsRel = **0.3213**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.3213** | 6.4574 | 9.3785 | 0.3992 | 64.37% | 84.24% | 92.07% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2879 | 10.0860 | 54.7% | Stable |
| Low Latitude | 15-30° | 0.3064 | 10.3905 | 63.6% | Stable |
| Mid Latitude | 30-45° | 0.3385 | 9.5797 | 70.8% | Stable |
| High Latitude | 45-60° | 0.2837 | 7.3159 | 66.8% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.2271** | 7.5650 | 70.1% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.2566** | 2.4840 | 55.8% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_outdoor
data:
  dataset: holo360d
  height: 512
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  width: 1024
evaluation:
  log_dir: logs_dap_holo360d_outdoor
  max_depth: 100.0
  min_depth: 0.1
  output_dir: outputs_dap_holo360d_outdoor
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
  - pitch: 90.0
    scale: 1.0
  - pitch: -90.0
    scale: 1.0
  - pitch: 0.0
    scale: 1.6
  - pitch: 0.0
    scale: 0.625
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
