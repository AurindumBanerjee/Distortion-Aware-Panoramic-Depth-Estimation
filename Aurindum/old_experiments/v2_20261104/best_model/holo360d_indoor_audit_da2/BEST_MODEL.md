# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 03:18:37`  
> **Winning Method:** **Structured3D: Method1_PlanarPrior**  
> **Key Highlights:** Polar AbsRel = **0.1417**, Global AbsRel = **0.1180**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1180** | 0.0445 | 0.3296 | 0.1646 | 90.55% | 98.87% | 99.62% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1011 | 0.4371 | 94.0% | Stable |
| Low Latitude | 15-30° | 0.1075 | 0.3635 | 92.8% | Stable |
| Mid Latitude | 30-45° | 0.1138 | 0.2740 | 92.3% | Stable |
| High Latitude | 45-60° | 0.1166 | 0.2169 | 92.4% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1260** | 0.2124 | 90.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1574** | 0.2461 | 86.9% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor_audit_da2
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  width: 512
evaluation:
  log_dir: logs_holo360d_indoor_audit_da2
  max_depth: 10.0
  methods:
  - Method1_PlanarPrior
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor_audit_da2
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
  shift_model: cos
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
  preset: rotation_only
  reanchor: auto
model:
  device: auto
  name: da2
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
