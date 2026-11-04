# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 01:57:55`  
> **Winning Method:** **Structured3D: Method1_PlanarPrior**  
> **Key Highlights:** Polar AbsRel = **0.2115**, Global AbsRel = **0.2870**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2870** | 5.6665 | 8.9864 | 0.3619 | 67.90% | 87.44% | 94.74% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2854 | 9.3332 | 55.5% | Stable |
| Low Latitude | 15-30° | 0.2883 | 10.2825 | 62.3% | Stable |
| Mid Latitude | 30-45° | 0.2905 | 9.2221 | 69.0% | Stable |
| High Latitude | 45-60° | 0.2234 | 6.3627 | 79.5% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1853** | 4.3332 | 84.2% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.2377** | 0.5689 | 60.4% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_outdoor_planar
data:
  dataset: holo360d
  height: 512
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  width: 1024
evaluation:
  log_dir: logs_dap_holo360d_outdoor_planar
  max_depth: 100.0
  methods:
  - Method1_PlanarPrior
  min_depth: 0.1
  output_dir: outputs_dap_holo360d_outdoor_planar
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
