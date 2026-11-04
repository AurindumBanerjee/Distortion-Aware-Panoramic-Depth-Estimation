# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-04 16:40:09`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.2401**, Global AbsRel = **0.2725**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2725** | 5.6582 | 8.9865 | 0.3608 | 68.37% | 87.44% | 94.74% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.2854 | 9.3332 | 55.5% | Stable |
| Low Latitude | 15-30° | 0.2883 | 10.2825 | 62.3% | Stable |
| Mid Latitude | 30-45° | 0.2905 | 9.2221 | 69.0% | Stable |
| High Latitude | 45-60° | 0.2378 | 6.3571 | 78.9% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.2271** | 4.3332 | 79.3% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.2530** | 0.5689 | 57.1% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _dap_outdoor_r3gonly_dap
data:
  dataset: holo360d
  height: 512
  list: outdoor.txt
  max_scenes: null
  root: data/holo360d
  split: all
  width: 1024
distortion_curve: results/sweep_dap_s3_calib.json
evaluation:
  log_dir: logs_dap_holo360d_outdoor_r3gonly_dap
  max_depth: 100.0
  methods:
  - Method2_MobiusTTA
  min_depth: 0.1
  output_dir: outputs_dap_holo360d_outdoor_r3gonly_dap
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
  curve_gate: true
  fusion_mode: distortion_weighted
  gate_lat:
  - 30
  - 55
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
