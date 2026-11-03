# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 16:20:21`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1810**, Global AbsRel = **0.1960**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1960** | 0.5697 | 4.1777 | 0.3340 | 71.12% | 94.08% | 98.73% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2512 | 6.2524 | 55.6% | Stable |
| Low Latitude | 15-30° | 0.1933 | 3.7484 | 68.2% | Stable |
| Mid Latitude | 30-45° | 0.1812 | 3.2295 | 73.9% | Stable |
| High Latitude | 45-60° | 0.1824 | 1.8270 | 77.5% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1889** | 0.8990 | 74.7% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1730** | 0.6409 | 71.4% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap
data:
  dataset: panox
  height: 512
  list: test.txt
  max_scenes: null
  root: data/panox
  width: 1024
evaluation:
  log_dir: logs_dap_panox
  max_depth: 100.0
  min_depth: 0.1
  output_dir: outputs_dap_panox
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
