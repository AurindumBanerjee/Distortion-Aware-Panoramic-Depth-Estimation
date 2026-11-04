# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 18:04:03`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.1165**, Global AbsRel = **0.1307**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1307** | 0.3726 | 4.0950 | 0.2964 | 88.33% | 97.10% | 98.47% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1920 | 6.7918 | 79.4% | Stable |
| Low Latitude | 15-30° | 0.1302 | 3.6801 | 88.4% | Stable |
| Mid Latitude | 30-45° | 0.1454 | 3.2690 | 85.3% | Stable |
| High Latitude | 45-60° | 0.1285 | 1.7455 | 88.6% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1120** | 0.6288 | 91.3% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1209** | 0.6256 | 93.4% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _r3wonly_da2
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
  log_dir: logs_panox_r3wonly_da2
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_panox_r3wonly_da2
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
