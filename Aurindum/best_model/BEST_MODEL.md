# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 00:50:12`  
> **Winning Method:** **Mobius TTA Ensembling**  
> **Key Highlights:** Polar AbsRel = **0.6286**, Global AbsRel = **0.7088**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.7088** | 1.3661 | 2.0426 | 1.4596 | 3.04% | 5.31% | 8.29% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.7655 | 3.2144 | 1.1% | Stable |
| Low Latitude | 15-30° | 0.7945 | 2.8165 | 0.4% | Stable |
| Mid Latitude | 30-45° | 0.7502 | 1.7841 | 1.2% | Stable |
| High Latitude | 45-60° | 0.6843 | 1.2705 | 5.1% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.6432** | 1.0222 | 6.4% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.6139** | 0.9184 | 3.9% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
evaluation:
  align_protocol: align-equatorial
  height: 256
  log_dir: logs
  num_scenes: 2
  output_dir: outputs
  width: 512
method_name: Mobius TTA Ensembling
mobius_tta:
  fusion_mode: distortion_weighted
  scales:
  - 1.0
  - 1.6
  - 0.625
model:
  device: cpu
  name: midas_dpt_hybrid
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
