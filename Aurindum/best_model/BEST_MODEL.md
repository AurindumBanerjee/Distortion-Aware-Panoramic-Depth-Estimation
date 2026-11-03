# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 01:04:32`  
> **Winning Method:** **Gradient-Domain Polar Fusion**  
> **Key Highlights:** Polar AbsRel = **0.3672**, Global AbsRel = **0.2639**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2639** | 0.2650 | 0.6682 | 0.3695 | 51.51% | 78.10% | 90.32% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1741 | 0.6649 | 74.9% | Stable |
| Low Latitude | 15-30° | 0.1584 | 0.5990 | 75.7% | Stable |
| Mid Latitude | 30-45° | 0.2062 | 0.5857 | 61.8% | Stable |
| High Latitude | 45-60° | 0.3101 | 0.6749 | 41.6% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.3675** | 0.6837 | 31.6% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.3669** | 0.6252 | 23.3% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
alignment:
  anchor_max_lat: 35.0
  mad_threshold: 2.5
blending:
  blend_margin: 10.0
  mode: gradient_poisson
  poisson_solver: sor
evaluation:
  align_protocol: align-equatorial
  height: 256
  log_dir: logs
  num_scenes: 24
  output_dir: outputs
  width: 512
method_name: Gradient-Domain Polar Fusion
model:
  device: auto
  name: dpt_hybrid_384
  scale: affine
  space: disparity
tangent:
  fov_deg: 90.0
  num_tangent_views: 2
  phi_threshold: 45.0
  resolution: 384
```

## 3. Qualitative Predictions
Sample output files saved in `sample_predictions/`:
- `sample_rgb.png`: Input equirectangular panorama
- `sample_gt_depth.png`: Ground truth Euclidean depth
- `sample_best_pred.png`: Colorized prediction from current best model
- `sample_error_heatmap.png`: Pixel-wise absolute relative error heatmap
- `comparison_overview.png`: Side-by-side composite visual overview
