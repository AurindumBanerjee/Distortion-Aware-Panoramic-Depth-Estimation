# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 17:59:34`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1159**, Global AbsRel = **0.1322**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1322** | 0.3781 | 4.0928 | 0.2941 | 86.58% | 97.19% | 98.49% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1834 | 6.8073 | 80.4% | Stable |
| Low Latitude | 15-30° | 0.1185 | 3.6784 | 90.6% | Stable |
| Mid Latitude | 30-45° | 0.1367 | 3.2799 | 87.0% | Stable |
| High Latitude | 45-60° | 0.1226 | 1.7517 | 87.5% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1133** | 0.5947 | 88.9% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1184** | 0.5736 | 93.7% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _r3_da2
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  split: all
  width: 512
distortion_curve: results/sweep_da2_s3_calib.json
evaluation:
  log_dir: logs_panox_r3_da2
  max_depth: 100.0
  methods:
  - Tangent_Spatial
  - Method1_GradientFusion
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_panox_r3_da2
  protocols:
  - align-all
  - align-equatorial
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  curve_gate: true
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
  curve_gate: true
  curve_weights: true
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
