# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:31:44`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1725**, Global AbsRel = **0.2108**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2108** | 0.1323 | 0.5006 | 0.2622 | 64.44% | 91.80% | 98.59% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2840 | 0.8188 | 54.4% | Stable |
| Low Latitude | 15-30° | 0.2212 | 0.6074 | 59.8% | Stable |
| Mid Latitude | 30-45° | 0.1779 | 0.4148 | 65.9% | Stable |
| High Latitude | 45-60° | 0.1551 | 0.3020 | 71.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1641** | 0.2789 | 70.5% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1810** | 0.2852 | 63.1% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _abl_midas_s3_rot_off
data:
  dataset: structured3d
  height: 256
  list: test.txt
  max_scenes: 60
  root: data/structured3d
  width: 512
evaluation:
  log_dir: logs_abl_midas_s3_rot_off
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_abl_midas_s3_rot_off
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
  - pitch: 90
    scale: 1.0
  - pitch: -90
    scale: 1.0
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
