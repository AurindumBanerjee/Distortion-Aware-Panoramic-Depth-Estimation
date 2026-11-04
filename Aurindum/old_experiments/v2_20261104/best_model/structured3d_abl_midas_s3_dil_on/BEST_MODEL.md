# 🏆 Best Model & Method Registry

> **Last Updated:** `2026-11-03 21:33:58`  
> **Winning Method:** **Structured3D: Baseline**  
> **Key Highlights:** Polar AbsRel = **0.2163**, Global AbsRel = **0.2591**

---

## 1. Quantitative Performance

### Global Metrics (Full Sphere)
| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Score** | **0.2591** | 0.1539 | 0.5287 | 0.3368 | 48.97% | 83.45% | 96.39% |

### Per-Latitude Band Breakdown (|φ|)
| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |
|:--- |:---:|:---:|:---:|:---:|:---:|
| Equatorial | 0-15° | 0.3654 | 0.6531 | 42.2% | Stable |
| Low Latitude | 15-30° | 0.3266 | 0.5895 | 50.4% | Stable |
| Mid Latitude | 30-45° | 0.2441 | 0.4404 | 51.1% | Stable |
| High Latitude | 45-60° | 0.2074 | 0.3824 | 58.7% | 🎯 Target Corrected |
| Severe Polar | 60-75° | **0.2063** | 0.3542 | 53.2% | 🎯 Target Corrected |
| Extreme Polar | 75-90° | **0.2263** | 0.3750 | 50.0% | 🎯 Target Corrected |

---

## 2. Configuration
```yaml
benchmark_suffix: _abl_midas_s3_dil_on
data:
  dataset: structured3d
  height: 256
  list: test.txt
  max_scenes: 60
  root: data/structured3d
  width: 512
evaluation:
  log_dir: logs_abl_midas_s3_dil_on
  max_depth: 10.0
  methods:
  - Method2_MobiusTTA
  - Control_YawEnsemble
  min_depth: 0.1
  output_dir: outputs_abl_midas_s3_dil_on
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
  - pitch: 0
    scale: 1.6
  - pitch: 0
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
