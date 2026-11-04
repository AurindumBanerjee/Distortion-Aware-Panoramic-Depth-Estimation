# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 01:29:35`  
> **Winning Method:** **Structured3D: Tangent_Spatial**  
> **Key Highlights:** Polar AbsRel = **0.1731**, Global AbsRel = **0.2958**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2958** | 2.8441 | 10.0373 | 0.4708 | 51.71% | 74.97% | 84.48% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3861 | 13.4409 | 30.0% | Stable |
| Low Latitude | 15-30° | 0.3093 | 9.1791 | 45.2% | Stable |
| Mid Latitude | 30-45° | 0.2670 | 5.5112 | 54.9% | Stable |
| High Latitude | 45-60° | 0.2450 | 2.8138 | 66.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1622** | 1.8818 | 78.8% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1840** | 0.5264 | 62.8% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _outdoor_m1cos
data:
  dataset: holo360d
  height: 256
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  width: 512
evaluation:
  log_dir: logs_holo360d_outdoor_m1cos
  max_depth: 100.0
  methods:
  - Tangent_Spatial
  - Method1_GradientFusion
  min_depth: 0.1
  output_dir: outputs_holo360d_outdoor_m1cos
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
