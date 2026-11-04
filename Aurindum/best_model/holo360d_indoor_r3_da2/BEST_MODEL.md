# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 18:11:50`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1435**, Global AbsRel = **0.1131**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1131** | 0.0437 | 0.3159 | 0.1586 | 93.11% | 98.95% | 99.62% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.0959 | 0.4035 | 95.6% | Stable |
| Low Latitude | 15-30° | 0.1005 | 0.3466 | 95.1% | Stable |
| Mid Latitude | 30-45° | 0.1057 | 0.2644 | 95.1% | Stable |
| High Latitude | 45-60° | 0.1111 | 0.2021 | 96.1% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1240** | 0.1934 | 92.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1630** | 0.2422 | 87.1% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor_r3_da2
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
distortion_curve: results/sweep_da2_s3_calib.json
evaluation:
  log_dir: logs_holo360d_indoor_r3_da2
  max_depth: 10.0
  methods:
  - Tangent_Spatial
  - Method1_GradientFusion
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor_r3_da2
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
