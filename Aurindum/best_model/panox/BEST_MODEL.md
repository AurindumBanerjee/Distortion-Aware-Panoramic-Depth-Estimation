# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 14:33:38`  
> **Winning Method:** **Structured3D: Tangent_Spatial**  
> **Key Highlights:** Polar AbsRel = **0.1057**, Global AbsRel = **0.1894**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1894** | 1.3147 | 6.9485 | 0.2872 | 74.90% | 92.09% | 96.86% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3491 | 13.3955 | 42.1% | Stable |
| Low Latitude | 15-30° | 0.1920 | 5.5542 | 71.6% | Stable |
| Mid Latitude | 30-45° | 0.1328 | 2.3745 | 84.0% | Stable |
| High Latitude | 45-60° | 0.1456 | 1.4076 | 77.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.0959** | 0.5505 | 94.9% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1155** | 0.3653 | 100.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  width: 512
evaluation:
  log_dir: logs_panox
  max_depth: 100.0
  min_depth: 0.1
  output_dir: outputs_panox
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
