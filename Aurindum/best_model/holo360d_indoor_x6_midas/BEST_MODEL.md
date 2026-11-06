# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 00:43:53`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.2277**, Global AbsRel = **0.2851**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2851** | 0.2853 | 0.9068 | 0.4011 | 46.01% | 76.32% | 89.91% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3549 | 1.3380 | 31.2% | Stable |
| Low Latitude | 15-30° | 0.3146 | 1.0815 | 38.2% | Stable |
| Mid Latitude | 30-45° | 0.2787 | 0.7510 | 42.5% | Stable |
| High Latitude | 45-60° | 0.2648 | 0.5854 | 44.6% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.2562** | 0.5422 | 54.8% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1992** | 0.4544 | 78.4% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _indoor_x6_midas
data:
  dataset: holo360d
  height: 256
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 512
evaluation:
  log_dir: logs_holo360d_indoor_x6_midas
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_holo360d_indoor_x6_midas
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
  - pitch: 0
    scale: 0.5
  - pitch: 0
    scale: 2.0
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
