# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 00:15:32`  
> **Winning Method:** **Structured3D: Method2_MobiusTTA**  
> **Key Highlights:** Polar AbsRel = **0.1389**, Global AbsRel = **0.2496**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2496** | 2.5724 | 9.6302 | 0.3749 | 61.25% | 84.43% | 93.60% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.5036 | 18.4739 | 26.6% | Stable |
| Low Latitude | 15-30° | 0.3328 | 9.3462 | 45.4% | Stable |
| Mid Latitude | 30-45° | 0.2143 | 3.8321 | 63.9% | Stable |
| High Latitude | 45-60° | 0.1738 | 1.2880 | 74.0% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1393** | 0.6288 | 83.2% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1385** | 0.4309 | 76.5% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _x5p5_midas
data:
  dataset: panox
  height: 256
  list: test.txt
  max_scenes: null
  root: data/panox
  split: all
  width: 512
evaluation:
  log_dir: logs_panox_x5p5_midas
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_panox_x5p5_midas
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
  shift_model: cos
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark
mobius_tta:
  anchor_max_lat: 30.0
  fusion_mode: distortion_weighted
  gate_lat: null
  min_weight: 1.0
  passes:
  - pitch: 45
    scale: 1.0
  - pitch: -45
    scale: 1.0
  - pitch: 90
    scale: 1.0
  - pitch: -90
    scale: 1.0
  reanchor: auto
  weight_power: 0
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
