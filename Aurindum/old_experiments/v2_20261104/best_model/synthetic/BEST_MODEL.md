# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 14:20:19`  
> **Winning Method:** **Mobius TTA Ensembling**  
> **Key Highlights:** Polar AbsRel = **0.1722**, Global AbsRel = **0.1655**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1655** | 0.1013 | 0.5420 | 0.2062 | 69.26% | 97.19% | 99.91% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2077 | 0.8180 | 61.4% | Stable |
| Low Latitude | 15-30° | 0.1802 | 0.7549 | 59.4% | Stable |
| Mid Latitude | 30-45° | 0.1377 | 0.3964 | 74.8% | Stable |
| High Latitude | 45-60° | 0.1281 | 0.2928 | 84.2% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1212** | 0.2588 | 87.3% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.2233** | 0.4087 | 57.5% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
evaluation:
  height: 256
  log_dir: logs
  max_depth: 50.0
  min_depth: 0.05
  num_scenes: 24
  output_dir: outputs
  protocols:
  - align-all
  - align-equatorial
  width: 512
method_name: Mobius TTA Ensembling
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
