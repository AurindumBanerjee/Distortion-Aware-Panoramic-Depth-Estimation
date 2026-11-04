# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:53:59`  
> **Winning Method:** **Structured3D: Control_YawEnsemble**  
> **Key Highlights:** Polar AbsRel = **0.1437**, Global AbsRel = **0.1837**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1837** | 0.6448 | 4.8815 | 0.3280 | 74.00% | 88.83% | 96.36% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3293 | 11.8721 | 41.5% | Stable |
| Low Latitude | 15-30° | 0.1941 | 4.3737 | 68.0% | Stable |
| Mid Latitude | 30-45° | 0.1817 | 2.4416 | 77.3% | Stable |
| High Latitude | 45-60° | 0.1673 | 2.2040 | 82.2% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1349** | 0.7874 | 81.9% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1524** | 0.6205 | 69.7% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _abl_midas_panox_rot_on
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: 60
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox_abl_midas_panox_rot_on
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_panox_abl_midas_panox_rot_on
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
