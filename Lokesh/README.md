# Distortion-Aware Panoramic Depth Estimation

This repository holds model-agnostic, **inference-time** corrections for latitude-dependent
equirectangular (ERP) distortion in panoramic depth estimation. The depth model stays a
**frozen black box**: no retraining and no architectural changes. The corrections run extra
inference passes on alternative spherical projections (tangent planes or rotated spheres) and fuse
the results with the baseline.

> **Status, read first.** The panoramic foundation model this project targets is **DAP**
> (*Depth Any Panoramas*, Lin et al., CVPR 2026). Its wrapper is in `models/depth_model.py` and its
> configs are in `configs/dap_*.yaml`. The development environment had **no GPU and no access to
> Hugging Face, Google Drive or the gated datasets**, so DAP and the real benchmarks could not be run
> here. All numbers in `results/` come from **MiDaS DPT-Hybrid and MiDaS Swin2-Tiny**, whose weights
> are on GitHub releases. These are *perspective* relative-depth models. They were evaluated on
> **procedurally rendered indoor panoramas with exact ground truth** (`datasets/synthetic.py`). Treat
> those results as a validated, end-to-end exercise of the framework and as evidence about *these*
> models. They are not evidence about DAP. The DAP experiments are one command away
> (see [Running DAP](#running-dap-the-target-experiment)).

---

## 1. Motivation

An ERP image maps longitude/latitude (θ, φ) linearly to pixel columns and rows. A pixel row at
latitude φ samples a circle of circumference 2π cos φ with the same number of pixels as the
equator, so it is horizontally stretched by **1/cos φ**: ×1.41 at 45°, ×2 at 60°, ×3.9 at 75° and
∞ at the poles. The pixel solid angle shrinks as cos φ. Depth networks learn local appearance
statistics, so the polar rows are a different input distribution even for models trained on ERP.

**Hypothesis.** ERP distortion causes a latitude-dependent degradation of panoramic depth.
Targeted inference on less-distorted projections of the affected regions can correct it without
touching the model.

## 2. Mathematical formulation

**Conventions** (`geometry/spherical.py`, tested). Camera axes: x right, y down, z forward. ERP pixel
centre (u, v) ↦ θ = 2π(u+½)/W − π, φ = π/2 − π(v+½)/H. The unit ray is
d = (cos φ sin θ, −sin φ, cos φ cos θ).

**Seam and pole-aware sampling** (`geometry/erp_projection.py`). Before interpolation the ERP is
padded circularly in longitude and *across the poles*: row −k equals row k−1 shifted by W/2. This
makes bilinear and bicubic sampling correct across the 180° seam and at φ = ±90°.

**Tangent plane / gnomonic view** (`geometry/tangent_plane.py`) at centre c = d(θc, φc), with FOV α
and N×N pixels:
f = (N/2)/tan(α/2), principal point N/2 − ½, R = [right | down | forward]. Here
right = (cos θc, 0, −sin θc), which never degenerates, even at the poles. A tangent pixel (i, j) has
ray R·((j−c)/f, (i−c)/f, 1).

* ERP → tangent: backward-warp each tangent ray into the ERP using seam/pole-aware sampling.
* Tangent → ERP: backward-warp each ERP ray into the tangent image. Pixels with z ≤ 0 or outside
  the frame are invalid.
* **Depth semantics.** Pinhole models predict planar depth z, while ERP ground truth is range
  r = z·√(1+x²+y²) = z / cos∠(ray, axis). Skipping this conversion introduces errors of up to 42% at
  the corners of a 90° view. The test suite measures this explicitly.
* For affine-invariant *disparity* models (MiDaS), a view's output is d = s/z + t, so the inverse
  range is 1/r = cos·(d − t)/s. A view is aligned to the baseline disparity b with the 3-parameter fit
  b ≈ A·(cos·d) + B·cos + C. No ground truth is used.

**Sphere rotation** (`rotate_erp`). I_rot(d) = I(R d) is a true SO(3) resampling, not a pixel
roll. Exception: pure yaw, which the tests confirm is an exact column shift. Range is invariant
under rotations about the camera centre. A pitch of +90° maps *both* poles onto the equator (north
to the front, south to the back).

**Fusion** (`inference/fusion.py`). Every correction view *v* gives a prediction P_v on the ERP grid
and a per-pixel "distortion coordinate" λ_v. λ_v is the latitude inside the rotated ERP the model
saw, or the off-axis angle inside the pinhole view.
1. Views are merged into D_corr = Σ w_v P_v / Σ w_v with w_v = cos(λ_v)^p (`prior`), or with
   `mean` or `median`.
2. D_corr is fused with the baseline:
   * **hard**: D = D_corr where |φ| > φ_t, otherwise D_ERP
   * **soft**: D = (1 − w(φ)) D_ERP + w(φ) D_corr. w is `linear`, `cosine` (raised cosine), `sigmoid`
     or `polynomial`, ramping over φ_t ± 10°.
   * **confidence (heuristic)**: none of the models used here outputs uncertainty, so per-pixel
     confidence is *derived* as c_i = cos(λ_i)^p · exp(−(log x_i − log median_j x_j)² / 2σ²) ·
     exp(−localstd(log x_i/x_base)/σ_l). These are the latitude prior, multi-view agreement and
     local consistency terms. The result is D = Σ c_i x_i / Σ c_i over the baseline and all views.
     The heuristic is documented as such and was not tuned on the test data (σ = 0.10, σ_l = 0.05).

**Inference-time alignment uses no ground truth.** Views are aligned to the *baseline* on "anchor"
pixels that are trusted in both frames: |φ| < φ_t in the original panorama, and low distortion in the
view (|λ| < φ_t, or inside 85% of the tangent half-width). Fits are robust least squares with MAD
outlier rejection.

## 3. Architecture

```
DepthModelWrapper.predict(image, kind='erp'|'perspective')     <- the only model interface
        |
DistortionAwareInference.run(rgb, MethodConfig)                inference/pipeline.py
   |-- baseline ERP pass                                       inference/baseline.py
   |-- polar tangent views  (selective, |phi| > threshold)     inference/tangent_inference.py
   |-- rotated-sphere passes                                   inference/rotation_inference.py
   |-- robust alignment to the baseline (no GT)                inference/alignment.py
   |-- merge views + fuse with baseline                        inference/fusion.py
   v
final ERP depth  (+ runtime, #model calls, peak memory)
```

Swapping the model means writing one `DepthModelWrapper` subclass that declares what its numbers
mean (`space`: depth/disparity, `scale`: metric/scale/affine, `geometry`: range/planar for ERP and
pinhole inputs). Provided wrappers:

| wrapper | model | role |
|---|---|---|
| `DAPWrapper` | DAP, Depth Any Panoramas (ERP-native, metric range/100 m, 512×1024) | **target model** |
| `MiDaSWrapper` | MiDaS DPT-Hybrid / Swin2-Tiny (perspective, affine disparity) | runnable here; generalisation |
| `DepthAnythingV2Wrapper` | DAv2 metric-indoor (perspective, z in metres), via `transformers` | optional tangent-view model |
| `EncodedDepthOracle` | decodes depth from pixels and adds latitude-dependent noise | **pipeline test only** |

### Why DAP

DAP is the most recent openly released *panoramic* depth foundation model. It is ERP-native, trained
on large-scale panoramic data, and evaluated zero-shot on Stanford2D3D and Matterport3D. Facts used
by the wrapper come from its code: `test/infer.py`, `test/eval.py`, `networks/dap.py`,
`config/infer.yaml` and `datasets/stanford2d3d.py`.
* Input is ERP RGB at 512×1024 in [0,1]. `eval.py` applies ImageNet normalisation but `infer.py` does
  not, so this is exposed as `imagenet_normalize` (default: the eval protocol).
* Output `pred_depth` is **Euclidean range / 100 m**, clipped to [0,1]. A `pred_mask` head flags
  sky / > 100 m pixels, which the wrapper returns as NaN.
* The model has no built-in handling of arbitrary rotations or crops. Its behaviour on
  pinhole tangent images is out of distribution and not documented, so the DAP config aligns tangent
  views to the baseline in *scale*. `configs/dap_dav2_tangent.yaml` uses Depth Anything V2 (a
  pinhole model) for the tangent views instead.

PanDA, DA360 and Depth Anywhere are alternative ERP models. Plugging one in takes about 30 lines
modelled on `DAPWrapper`.

## 4. Repository structure

```
configs/            default.yaml (MiDaS, synthetic), midas_swin2_tiny.yaml, dap_stanford2d3d.yaml,
                    dap_matterport3d.yaml, dap_dav2_tangent.yaml
models/             depth_model.py      (wrapper interface + DAP / MiDaS / DAv2 / oracle)
geometry/           spherical.py, erp_projection.py, tangent_plane.py, validation.py
inference/          baseline.py, tangent_inference.py, rotation_inference.py, alignment.py, fusion.py, pipeline.py
evaluation/         metrics.py, latitude_analysis.py, evaluation.py
visualization/      visualize.py
datasets/           panorama.py (Stanford2D3D / Matterport3D / Structured3D / .npy), synthetic.py (renderer)
experiments/        common.py, baseline.py (E1 + content control), tangent_plane.py (E2),
                    rotation_ensemble.py (E3/E4), ablation.py (E5-E9)
notebooks/          01_baseline, 02_latitude_analysis, 03_tangent_projection, 04_results (end-to-end)
tests/              geometry, scene-level projection, oracle pipeline, DAP wrapper plumbing
third_party/        vendored MiDaS code (MIT); DAP is cloned here by the user
run_experiment.py   single entry point
```

## 5. Installation

```bash
pip install -r requirements.txt
# MiDaS weights (GitHub releases)
mkdir -p weights
curl -L -o weights/dpt_hybrid_384.pt     https://github.com/isl-org/MiDaS/releases/download/v3/dpt_hybrid_384.pt
curl -L -o weights/dpt_swin2_tiny_256.pt https://github.com/isl-org/MiDaS/releases/download/v3_1/dpt_swin2_tiny_256.pt
pytest -q tests/        # geometry + pipeline tests (about 1 min on CPU)
```

## 6. Dataset preparation

* **Synthetic (default, reproducible):** `python -m datasets.synthetic --out data/synthetic --n 24 --seed 0`.
  This renders 24 ERP panoramas at 512×1024 (2×2 supersampled RGB) with exact range ground truth, in
  about 1 min each on CPU.
* **Stanford2D3D** (request access): place the release under `data/stanford2d3d`, then run
  `python scripts/make_stanford_list.py --root data/stanford2d3d --areas area_5a area_5b`
  (standard test split; depth png/512; 65535 = invalid).
* **Matterport3D** (ERP release used by UniFuse/BiFuse; depth png/4000): write `data/matterport3d/test.txt`
  with `rgb_path depth_path` lines.

Invalid GT (NaN, ≤ min_depth, > max_depth, sensor holes) is excluded from every metric. GT is never
interpolated: resizing and rotation use nearest-neighbour sampling with validity masks.

## 7. Running the experiments

```bash
python run_experiment.py --config configs/default.yaml           # all stages, MiDaS DPT-Hybrid (~2.5 h on 2 CPU cores)
python run_experiment.py --config configs/midas_swin2_tiny.yaml  # second model
python run_experiment.py --config configs/default.yaml --stages reports   # re-make tables/plots from saved rows
python run_experiment.py --config configs/default.yaml --set dataset.limit=4 inference.polar_threshold=60
```

Stages run in this order: `geometry` (a gate: experiments refuse to run if projection errors exceed
tolerance), `main` (every method in the plan on every image, sharing a cache of model outputs),
`reports`, `control` (content-vs-latitude), `resolution`, `timing` (uncached wall-clock) and
`qualitative`.

### Running DAP (the target experiment)

```bash
git clone https://github.com/Insta360-Research-Team/DAP third_party/DAP
pip install -r third_party/DAP/requirements.txt
huggingface-cli download Insta360-Research/DAP-weights --local-dir weights/dap   # -> weights/dap/model.pth
python run_experiment.py --config configs/dap_stanford2d3d.yaml
python run_experiment.py --config configs/dap_matterport3d.yaml
python run_experiment.py --config configs/dap_dav2_tangent.yaml    # DAv2 for tangent views
```

DAP is metric, so evaluation uses no GT alignment (`eval_align: none`). Add
`--set evaluation.eval_align=median` for the scale-aligned protocol. `tests/test_dap_wrapper.py`
checks the wrapper against DAP's output contract with a stand-in network.

## 8. Evaluation protocol

* Metrics are AbsRel, SqRel, RMSE, RMSElog, MAE, MedAE, δ1/δ2/δ3, error variance and % pixels with
  AbsRel > 0.10. They are computed globally and per |latitude| band (0–15, 15–30, …, 75–90). Each is
  given pixel-weighted (standard) and solid-angle-weighted (cos φ).
* **GT alignment of relative models** (MiDaS: affine in disparity) is fitted once per image and
  method, on all valid pixels (`align-all`, standard). It is *never* fitted per band, so polar errors
  cannot be hidden by a local re-fit. The global fit couples the bands: changing the poles shifts the
  fit everywhere. A second protocol (`align-equatorial`) therefore fits only on |φ| < 30°, which every
  method leaves (almost) unchanged. Both are reported.
* Improvement = (E_baseline − E_corrected)/E_baseline × 100, per band. It is reported with a paired
  per-image bootstrap 95% CI, a Wilcoxon signed-rank p-value and the number of images improved.
* Everything is seeded and the split is fixed (first N lines of the list file). The resolved config,
  environment, method plan and log are saved with each run.

## 9. Results

See **[RESULTS.md](RESULTS.md)** for the research summary (problem, method, setup, results,
limitations and future work), written from the CSVs in `results/`.

## 10. Expected outputs

```
results/<run>/
  geometry_validation.json            projection error report (gate)
  rows_align-{all,equatorial}.csv     every image x method x band x weighting (+ runtime, #calls)
  profiles_align-*.npz                per-image error-vs-|latitude| curves
  report_align-*/                     baseline.csv, tangent_plane.csv, rotation.csv, hybrid.csv, ablation.csv,
                                      *_improvement.{csv,md}, main_comparison.md, latitude_bands_*.csv, onset_*.json,
                                      profile_*.png, heatmap_*.png, runtime_vs_accuracy.png, ablations/*.md
  latitude_control/                   content-vs-latitude control (csv + png)
  resolution.{csv,md}, runtime_cold.{csv,md}
  qualitative/                        8-panel comparisons + tangent-view pipeline figures
```
 
## 11. Follow-up studies (November 2026)

Five additional experiments are maintained separately in [followup_experiments/README.md](followup_experiments/README.md).
They do not replace or rewrite the existing E1–E11 pipeline above.

| Study | Purpose |
|---|---|
| 01 — scale-only protocol | DA360 scale-only disparity evaluation vs affine-fit sensitivity |
| 02 — domain-conditioned gate | PanoX leave-one-environment-out calibration of the rotation gate |
| 03 — PanDA-inspired distillation | Frozen DA360 pseudo-label teacher and compact student training |
| 04 — 20-view 360MonoDepth-style | Full-sphere icosahedral tangent baseline vs two-pole tangent correction |
| 05 — FOV/resolution sweep | Tangent-view FOV × output-resolution sensitivity |

Each study has its own `config.yaml`, `run.py`, GPU launcher, logs and timestamped `outputs/` folder.
The Kaggle entrypoint is `followup_experiments/kaggle_two_t4_runner.ipynb`; it is designed for a
two-T4 Kaggle kernel. DA360-dependent studies require the official DA360 repository and checkpoint
to be mounted separately. GPU runs are not considered complete until the Kaggle notebook has executed
and written its result reports.
