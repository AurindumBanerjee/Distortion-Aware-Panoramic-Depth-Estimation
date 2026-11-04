# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:32:31`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1805**, Global AbsRel = **0.2302**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2302** | 0.1607 | 0.5773 | 0.2838 | 60.76% | 90.87% | 97.82% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3132 | 0.9308 | 51.8% | Stable |
| Low Latitude | 15-30° | 0.2568 | 0.6401 | 60.0% | Stable |
| Mid Latitude | 30-45° | 0.1957 | 0.4391 | 60.2% | Stable |
| High Latitude | 45-60° | 0.1653 | 0.3260 | 65.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1768** | 0.3083 | 65.5% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1842** | 0.2777 | 57.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _abl_midas_s3_rot_on
data:
  dataset: structured3d
  height: 256
  list: test.txt
  max_scenes: 60
  root: data/structured3d
  width: 512
evaluation:
  log_dir: logs_abl_midas_s3_rot_on
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_abl_midas_s3_rot_on
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
