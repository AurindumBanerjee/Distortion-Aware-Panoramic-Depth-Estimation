# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 01:08:05`  
> **Winning Method:** **Structured3D: Tangent_Spatial**  
> **Key Highlights:** Polar AbsRel = **0.1278**, Global AbsRel = **0.1824**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1824** | 1.2495 | 5.5274 | 0.3075 | 73.22% | 89.72% | 96.38% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3520 | 12.1548 | 39.6% | Stable |
| Low Latitude | 15-30° | 0.2173 | 5.5131 | 66.9% | Stable |
| Mid Latitude | 30-45° | 0.1587 | 2.6591 | 82.1% | Stable |
| High Latitude | 45-60° | 0.1399 | 1.2833 | 84.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1234** | 0.6152 | 82.1% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1323** | 0.4314 | 92.9% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _m1cos
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox_m1cos
  max_depth: 100.0
  methods:
  - Tangent_Spatial
  - Method1_GradientFusion
  min_depth: 0.1
  output_dir: outputs_panox_m1cos
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
