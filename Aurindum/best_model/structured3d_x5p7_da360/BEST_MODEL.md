# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 04:46:44`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.0107**, Global AbsRel = **0.0147**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.0147** | 0.0024 | 0.0587 | 0.0342 | 99.77% | 99.95% | 99.99% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.0214 | 0.0920 | 99.5% | Stable |
| Low Latitude | 15-30° | 0.0178 | 0.0731 | 99.6% | Stable |
| Mid Latitude | 30-45° | 0.0132 | 0.0423 | 99.9% | Stable |
| High Latitude | 45-60° | 0.0112 | 0.0277 | 100.0% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0111** | 0.0215 | 100.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.0102** | 0.0190 | 100.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _x5p7_da360
data:
  dataset: structured3d
  height: 256
  list: test.txt
  max_scenes: null
  root: data/structured3d
  split: eval
  width: 512
evaluation:
  log_dir: logs_x5p7_da360
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_x5p7_da360
  protocols:
  - align-all
  - align-equatorial
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  fov_deg: 90.0
  phi_threshold: 45.0
  planar_prior:
    agree_tol: 0.5
    blend_margin: 10.0
    cap_from: 40.0
    inlier_tol: 0.05
    max_tilt_deg: 20.0
    min_inlier: 0.6
    phi_threshold: 60.0
    ring:
    - 40.0
    - 60.0
  polar_source: rotated_erp
  resolution: 384
  shift_model: cos
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark
mobius_tta:
  anchor_max_lat: 30.0
  consensus: false
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
  reanchor_scope: identity
  sync_max_lat: 45.0
  weight_power: 0
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
