# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 00:27:31`  
> **Winning Method:** **Gradient-Domain Polar Fusion**  
> **Key Highlights:** Polar AbsRel = **0.9964**, Global AbsRel = **1.1440**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **1.1440** | 11.7789 | 4.1146 | 1.1437 | 14.09% | 27.26% | 41.05% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.8410 | 3.6377 | 7.2% | Stable |
| Low Latitude | 15-30° | 0.9831 | 4.4302 | 9.5% | Stable |
| Mid Latitude | 30-45° | 1.8120 | 6.7323 | 9.5% | Stable |
| High Latitude | 45-60° | 1.2522 | 3.4518 | 19.3% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.9438** | 1.9253 | 15.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **1.0490** | 1.8325 | 23.7% | 🎯 Target Corrected |

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
  num_scenes: 2
  output_dir: outputs
  width: 512
method_name: Gradient-Domain Polar Fusion
model:
  device: cpu
  name: midas_dpt_hybrid
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
