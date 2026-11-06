# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 07:47:30`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1174**, Global AbsRel = **0.1338**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1338** | 0.3771 | 4.0925 | 0.2929 | 87.35% | 97.18% | 98.47% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1840 | 6.8128 | 80.4% | Stable |
| Low Latitude | 15-30° | 0.1188 | 3.6784 | 90.5% | Stable |
| Mid Latitude | 30-45° | 0.1391 | 3.2803 | 87.2% | Stable |
| High Latitude | 45-60° | 0.1202 | 1.7753 | 88.0% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1147** | 0.5969 | 90.1% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1201** | 0.5668 | 93.4% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _x5p5_da2
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  split: all
  width: 512
evaluation:
  log_dir: logs_panox_x5p5_da2
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_panox_x5p5_da2
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
