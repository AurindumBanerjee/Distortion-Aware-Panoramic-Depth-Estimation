# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:54:50`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1505**, Global AbsRel = **0.1942**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1942** | 0.6727 | 4.8747 | 0.3452 | 72.17% | 87.63% | 95.63% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3464 | 12.0325 | 37.8% | Stable |
| Low Latitude | 15-30° | 0.2121 | 4.3318 | 64.5% | Stable |
| Mid Latitude | 30-45° | 0.1974 | 2.4575 | 74.5% | Stable |
| High Latitude | 45-60° | 0.1783 | 2.0909 | 83.5% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1537** | 0.8302 | 75.8% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1473** | 0.6989 | 69.1% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _abl_midas_panox_dil_off
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: 60
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox_abl_midas_panox_dil_off
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_panox_abl_midas_panox_dil_off
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
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark
mobius_tta:
  anchor_max_lat: 30.0
  fusion_mode: distortion_weighted
  gate_lat: null
  passes:
  - pitch: 0
    scale: 1.6
  - pitch: 0
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
