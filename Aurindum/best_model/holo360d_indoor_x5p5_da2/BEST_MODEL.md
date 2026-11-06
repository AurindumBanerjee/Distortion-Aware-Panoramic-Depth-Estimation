# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 08:37:34`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1448**, Global AbsRel = **0.1111**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1111** | 0.0419 | 0.3147 | 0.1575 | 93.58% | 98.95% | 99.64% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.0961 | 0.3949 | 95.7% | Stable |
| Low Latitude | 15-30° | 0.1018 | 0.3431 | 95.4% | Stable |
| Mid Latitude | 30-45° | 0.1030 | 0.2610 | 95.2% | Stable |
| High Latitude | 45-60° | 0.1092 | 0.1996 | 95.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1265** | 0.1968 | 92.8% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1631** | 0.2409 | 87.7% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor_x5p5_da2
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
evaluation:
  log_dir: logs_holo360d_indoor_x5p5_da2
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor_x5p5_da2
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
  gate_lat: null
  min_weight: 1.0
  passes:
  - pitch: 45
    scale: 1.0
  - pitch: -45
    scale: 1.0
  - pitch: 90
    scale: 1.0
  - pitch: -90
    scale: 1.0
  reanchor: auto
  weight_power: 0
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
