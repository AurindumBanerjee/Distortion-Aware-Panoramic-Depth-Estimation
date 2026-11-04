# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 17:19:44`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1050**, Global AbsRel = **0.1412**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1412** | 1.5356 | 6.8181 | 0.2635 | 80.36% | 91.14% | 96.64% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2168 | 9.1993 | 66.2% | Stable |
| Low Latitude | 15-30° | 0.1464 | 5.8702 | 79.5% | Stable |
| Mid Latitude | 30-45° | 0.1210 | 4.4834 | 88.5% | Stable |
| High Latitude | 45-60° | 0.0956 | 2.6045 | 94.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0738** | 0.6981 | 97.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1362** | 0.3630 | 79.9% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _outdoor_r3wonly_da360
data:
  dataset: holo360d
  height: 256
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
distortion_curve: results/sweep_da360_s3_calib.json
evaluation:
  log_dir: logs_holo360d_outdoor_r3wonly_da360
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_holo360d_outdoor_r3wonly_da360
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
