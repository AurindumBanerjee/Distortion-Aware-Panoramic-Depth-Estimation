# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 00:52:23`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1619**, Global AbsRel = **0.2038**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2038** | 0.1085 | 0.4400 | 0.2548 | 66.92% | 93.61% | 98.98% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2965 | 0.5899 | 54.4% | Stable |
| Low Latitude | 15-30° | 0.2276 | 0.4644 | 62.0% | Stable |
| Mid Latitude | 30-45° | 0.1692 | 0.3580 | 69.2% | Stable |
| High Latitude | 45-60° | 0.1602 | 0.3162 | 69.6% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1577** | 0.2714 | 71.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1660** | 0.2562 | 74.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _rotguard
data:
  dataset: structured3d
  height: 256
  list: test.txt
  max_scenes: null
  root: data/structured3d
  width: 512
evaluation:
  log_dir: logs_rotguard
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_rotguard
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
  polar_source: auto
  resolution: 384
  shift_model: cos
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark
mobius_tta:
  anchor_max_lat: 30.0
  consensus: false
  fit_guard:
    a_max: 4.0
    tau: 0.5
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
  reanchor_scope: identity
  sync_max_lat: 45.0
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
