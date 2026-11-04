# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 02:49:21`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.0796**, Global AbsRel = **0.1373**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1373** | 2.4385 | 6.7263 | 0.2293 | 85.25% | 93.80% | 97.51% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1956 | 8.7453 | 69.5% | Stable |
| Low Latitude | 15-30° | 0.1386 | 6.7630 | 83.6% | Stable |
| Mid Latitude | 30-45° | 0.1134 | 4.9732 | 89.6% | Stable |
| High Latitude | 45-60° | 0.0757 | 2.6034 | 94.8% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0730** | 0.7847 | 97.2% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.0861** | 0.2533 | 92.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _outdoor_audit_da360
data:
  dataset: holo360d
  height: 256
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  width: 512
evaluation:
  log_dir: logs_holo360d_outdoor_audit_da360
  max_depth: 100.0
  methods:
  - Method1_PlanarPrior
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_holo360d_outdoor_audit_da360
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
  name: da360
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
