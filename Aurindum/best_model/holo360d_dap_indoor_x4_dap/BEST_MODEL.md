# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-06 02:42:19`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.1306**, Global AbsRel = **0.1383**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.1383** | 0.0651 | 0.3990 | 0.1890 | 83.65% | 98.45% | 99.67% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.1382 | 0.5453 | 83.5% | Stable |
| Low Latitude | 15-30° | 0.1450 | 0.4875 | 82.7% | Stable |
| Mid Latitude | 30-45° | 0.1386 | 0.3727 | 82.2% | Stable |
| High Latitude | 45-60° | 0.1275 | 0.2694 | 87.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.1222** | 0.2278 | 88.7% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.1390** | 0.2282 | 91.3% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_indoor_x4_dap
data:
  dataset: holo360d
  height: 512
  list: indoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 1024
evaluation:
  log_dir: logs_dap_holo360d_indoor_x4_dap
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_dap_holo360d_indoor_x4_dap
  protocols:
  - none
  - align-all
method1:
  anchor_max_lat: 60.0
  blend_margin: 10.0
  fov_deg: 90.0
  phi_threshold: 45.0
  polar_source: auto
  resolution: 384
  texture_gate_mode: erp
  texture_tau: 0.0
method_name: Structured3D Real Foundation Benchmark (DAP)
mobius_tta:
  anchor_max_lat: 30.0
  fusion_mode: distortion_weighted
  gate_lat: null
  min_weight: 1.0
  passes:
  - pitch: 90.0
    scale: 1.0
  - pitch: -90.0
    scale: 1.0
  - pitch: 0.0
    scale: 1.6
  - pitch: 0.0
    scale: 0.625
  preset: rotation_only
  reanchor: auto
  weight_power: 0
model:
  device: auto
  name: dap
  repo: third_party/DAP
  scale: metric
  space: depth
  weights: weights/dap/model.pth
```

## 3. Qualitative Predictions
Sample output files saved in `sample_predictions/`:
- `sample_rgb.png`: Input equirectangular panorama
- `sample_gt_depth.png`: Ground truth Euclidean depth
- `sample_best_pred.png`: Colorized prediction from current best model
- `sample_error_heatmap.png`: Pixel-wise absolute relative error heatmap
- `comparison_overview.png`: Side-by-side composite visual overview
