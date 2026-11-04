# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 01:34:33`  
> **Winning Method:** **Structured3D: Method1_PlanarPrior**  
> **Key Highlights:** Polar AbsRel = **0.1474**, Global AbsRel = **0.1897**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1897** | 0.7677 | 4.8683 | 0.3079 | 73.11% | 88.85% | 96.09% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3310 | 11.5924 | 40.2% | Stable |
| Low Latitude | 15-30° | 0.2161 | 4.6605 | 66.8% | Stable |
| Mid Latitude | 30-45° | 0.1646 | 2.2842 | 83.0% | Stable |
| High Latitude | 45-60° | 0.1376 | 1.0107 | 86.3% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1449** | 0.5888 | 86.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1499** | 0.4369 | 89.9% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _planar
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox_planar
  max_depth: 100.0
  methods:
  - Method1_PlanarPrior
  min_depth: 0.1
  output_dir: outputs_panox_planar
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
