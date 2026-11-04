# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 14:28:00`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1586**, Global AbsRel = **0.1947**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1947** | 0.1041 | 0.4339 | 0.2473 | 68.19% | 95.03% | 98.95% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2761 | 0.5967 | 59.9% | Stable |
| Low Latitude | 15-30° | 0.2028 | 0.4649 | 68.0% | Stable |
| Mid Latitude | 30-45° | 0.1615 | 0.3477 | 71.9% | Stable |
| High Latitude | 45-60° | 0.1555 | 0.3104 | 69.6% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1549** | 0.2652 | 72.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1622** | 0.2579 | 74.6% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
data:
  dataset: structured3d
  height: 256
  list: test.txt
  max_scenes: null
  root: data/structured3d
  width: 512
evaluation:
  log_dir: logs
  max_depth: 10.0
  min_depth: 0.1
  output_dir: outputs
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
