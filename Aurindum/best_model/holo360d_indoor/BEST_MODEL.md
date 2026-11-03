# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:02:07`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.2190**, Global AbsRel = **0.2950**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2950** | 0.2488 | 0.8093 | 0.4335 | 45.45% | 76.10% | 88.02% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3526 | 1.1405 | 32.9% | Stable |
| Low Latitude | 15-30° | 0.3213 | 0.9114 | 37.5% | Stable |
| Mid Latitude | 30-45° | 0.3131 | 0.7415 | 37.6% | Stable |
| High Latitude | 45-60° | 0.2884 | 0.5698 | 41.1% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.2675** | 0.5168 | 57.6% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1705** | 0.3966 | 84.9% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  width: 512
evaluation:
  log_dir: logs_holo360d_indoor
  max_depth: 10.0
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor
  protocols:
  - align-all
  - align-equatorial
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  fov_deg: 90.0
  phi_threshold: 45.0
  polar_source: auto
  resolution: 384
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark
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
  name: dpt_hybrid_384
  scale: affine
  space: disparity
```

## 3. Qualitative Predictions
Sample output files saved in `sample_predictions/`:
- `sample_rgb.png`: Input equirectangular panorama
- `sample_gt_depth.png`: Ground truth Euclidean depth
- `sample_best_pred.png`: Colorized prediction from current best model
- `sample_error_heatmap.png`: Pixel-wise absolute relative error heatmap
- `comparison_overview.png`: Side-by-side composite visual overview
