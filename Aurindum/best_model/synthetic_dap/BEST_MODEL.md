# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 14:44:02`  
> **Winning Method:** **Gradient-Domain Polar Fusion**  
> **Key Highlights:** Polar AbsRel = **0.1911**, Global AbsRel = **0.1712**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1712** | 0.0651 | 0.3738 | 0.2036 | 77.08% | 99.93% | 99.99% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1435 | 0.4494 | 94.1% | Stable |
| Low Latitude | 15-30° | 0.1475 | 0.4119 | 91.1% | Stable |
| Mid Latitude | 30-45° | 0.1618 | 0.3689 | 84.1% | Stable |
| High Latitude | 45-60° | 0.1758 | 0.3544 | 71.6% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1975** | 0.3358 | 62.6% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1846** | 0.3067 | 63.6% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
alignment:
  anchor_max_lat: 60.0
  mad_threshold: 2.5
benchmark_suffix: _dap
blending:
  blend_margin: 10.0
  mode: gradient_poisson
  poisson_solver: sparse
  texture_gate_mode: erp
  texture_tau: 0.0
evaluation:
  height: 512
  log_dir: logs_dap
  max_depth: 50.0
  min_depth: 0.05
  num_scenes: 24
  output_dir: outputs_dap
  protocols:
  - none
  - align-all
  width: 1024
method_name: Gradient-Domain Polar Fusion (DAP)
model:
  device: auto
  name: dap
  repo: third_party/DAP
  scale: metric
  space: depth
  weights: weights/dap/model.pth
polar_source: auto
tangent:
  fov_deg: 90.0
  num_tangent_views: 2
  phi_threshold: 45.0
  resolution: 384
```

## 3. Qualitative Predictions
Sample output files saved in `sample_predictions/`:
- `sample_rgb.png`: Input equirectangular panorama
- `sample_gt_depth.png`: Ground truth Euclidean depth
- `sample_best_pred.png`: Colorized prediction from current best model
- `sample_error_heatmap.png`: Pixel-wise absolute relative error heatmap
- `comparison_overview.png`: Side-by-side composite visual overview
