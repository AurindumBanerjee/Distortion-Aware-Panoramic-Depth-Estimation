# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:55:39`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1509**, Global AbsRel = **0.1913**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1913** | 0.6612 | 4.8667 | 0.3394 | 72.63% | 87.79% | 95.75% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3351 | 11.9530 | 39.0% | Stable |
| Low Latitude | 15-30° | 0.2015 | 4.3030 | 65.7% | Stable |
| Mid Latitude | 30-45° | 0.2009 | 2.4744 | 77.3% | Stable |
| High Latitude | 45-60° | 0.1775 | 2.1038 | 83.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1543** | 0.8301 | 75.9% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1475** | 0.6983 | 69.8% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _abl_midas_panox_dil_on
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: 60
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox_abl_midas_panox_dil_on
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_panox_abl_midas_panox_dil_on
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
  gate_lat:
  - 30
  - 55
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
