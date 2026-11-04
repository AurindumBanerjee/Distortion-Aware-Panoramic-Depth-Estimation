# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 18:24:50`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.5752**, Global AbsRel = **0.5434**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.5434** | 2.6188 | 6.7623 | 0.7879 | 3.68% | 8.87% | 25.39% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.5160 | 9.0304 | 9.2% | Stable |
| Low Latitude | 15-30° | 0.5415 | 6.6944 | 2.8% | Stable |
| Mid Latitude | 30-45° | 0.5436 | 5.1119 | 0.6% | Stable |
| High Latitude | 45-60° | 0.5540 | 3.9280 | 0.1% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.5511** | 2.3779 | 0.0% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.5993** | 1.3709 | 0.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _outdoor_r3gonly_da2
data:
  dataset: holo360d
  height: 256
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
distortion_curve: results/sweep_da2_s3_calib.json
evaluation:
  log_dir: logs_holo360d_outdoor_r3gonly_da2
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_holo360d_outdoor_r3gonly_da2
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
  curve_gate: true
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
