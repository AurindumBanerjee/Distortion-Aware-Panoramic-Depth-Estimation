# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 01:11:28`  
> **Winning Method:** **Structured3D: Method1_GradientFusion**  
> **Key Highlights:** Polar AbsRel = **0.1295**, Global AbsRel = **0.2099**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2099** | 1.8286 | 7.7792 | 0.3036 | 73.61% | 92.15% | 96.77% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3646 | 15.7696 | 42.8% | Stable |
| Low Latitude | 15-30° | 0.2416 | 6.6796 | 67.6% | Stable |
| Mid Latitude | 30-45° | 0.1497 | 2.3442 | 80.9% | Stable |
| High Latitude | 45-60° | 0.1304 | 1.0986 | 83.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1091** | 0.5289 | 91.1% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1498** | 0.4438 | 81.2% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _m1rot
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox_m1rot
  max_depth: 100.0
  methods:
  - Tangent_Spatial
  - Method1_GradientFusion
  min_depth: 0.1
  output_dir: outputs_panox_m1rot
  protocols:
  - align-all
  - align-equatorial
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  fov_deg: 90.0
  phi_threshold: 45.0
  polar_source: rotated_erp
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
