# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 00:32:48`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.2320**, Global AbsRel = **0.2830**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2830** | 0.2664 | 0.8960 | 0.4019 | 46.62% | 76.53% | 90.03% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3498 | 1.2883 | 32.2% | Stable |
| Low Latitude | 15-30° | 0.3091 | 1.0530 | 38.9% | Stable |
| Mid Latitude | 30-45° | 0.2793 | 0.7459 | 43.9% | Stable |
| High Latitude | 45-60° | 0.2658 | 0.5834 | 45.3% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.2593** | 0.5440 | 55.5% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.2046** | 0.4512 | 78.1% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor_x5p5_midas
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
evaluation:
  log_dir: logs_holo360d_indoor_x5p5_midas
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor_x5p5_midas
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
