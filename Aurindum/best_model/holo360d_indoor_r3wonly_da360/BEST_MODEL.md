# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 17:13:12`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.0477**, Global AbsRel = **0.0608**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.0608** | 0.0279 | 0.3247 | 0.1082 | 96.15% | 98.99% | 99.68% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.0746 | 0.4762 | 94.8% | Stable |
| Low Latitude | 15-30° | 0.0670 | 0.3653 | 96.1% | Stable |
| Mid Latitude | 30-45° | 0.0566 | 0.2418 | 97.4% | Stable |
| High Latitude | 45-60° | 0.0493 | 0.1602 | 98.4% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0458** | 0.1302 | 98.5% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.0497** | 0.1725 | 96.6% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor_r3wonly_da360
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
distortion_curve: results/sweep_da360_s3_calib.json
evaluation:
  log_dir: logs_holo360d_indoor_r3wonly_da360
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor_r3wonly_da360
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
