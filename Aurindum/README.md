# Distortion-Aware Panoramic Depth Estimation

B23CS1006, CV coursework, IIT Jodhpur. Final report: [`Final_Report.pdf`](Final_Report.pdf) (source in `Report/draft/`).

## What this repository does

Monocular depth models are applied to 360 degree panoramas stored as equirectangular projections (ERP), whose rows are stretched by 1/cos(latitude) towards the poles. The repository tests whether that stretching explains the larger polar error, and what does.

All models are used as released; nothing is trained.

1. **Measurement.** Sweeps (rotation, dilation, flip) move the same content to different latitudes while the ground truth stays fixed. The polar deficit is mostly not a projection effect.
2. **Inference-time methods.** Gradient-domain polar fusion and Mobius test-time augmentation are evaluated with a compute-matched control. They help the perspective-trained MiDaS and do not help the panoramic models.
3. **Capture faults and correction.** Ten realistic capture faults (tilt, blocked nadir, limited vertical field of view, seam, parallax, vignetting, yaw blur, noise, JPEG, low resolution) are simulated, each with a model-agnostic fix. A correction front end detects faults and applies, per model, the fix chosen leave-one-dataset-out on held-out data, or none.

## Models and data

| | |
|---|---|
| Models (frozen) | MiDaS DPT-Hybrid, DAP, DA360, DA2 |
| Core datasets | Structured3D, PanoX, Holo360D indoor, Holo360D outdoor |
| External datasets (never used for any choice) | Stanford2D3D, NYC street panoramas |
| Metrics | AbsRel (whole, polar, affected region), median relative change, share of frames improved or worse, recovery, cluster-robust bootstrap intervals |

Datasets and model weights are not in the repository (`data/` and `weights/` are git-ignored, as are the third-party model repositories `third_party/DAP`, `third_party/DA2` and `third_party/DA360`; only the vendored `third_party/midas_repo` is tracked). Alignment: DAP in raw metres; MiDaS and DA360 with an affine fit; DA2 with least squares (headline) and a median fit (reported alongside).

## Layout

```text
Final_Report.pdf              compiled report
Report/draft/                 report source (main.tex), figures, style files
configs/                      model and dataset configs
models/  datasets/            frozen-model wrappers, dataset loaders
geometry/  inference/         ERP geometry, projections, rotation and tangent views
distortions/                  capture-fault catalogue and the correction front end
evaluation/                   metrics, alignment protocols, bootstrap, sweeps analysis
1_gradient_polar_fusion/      gradient-domain polar fusion (library code)
2_mobius_tta_ensembling/      Mobius test-time augmentation (library code)
3_structured3d_benchmark/     benchmark runner and configs
best_model/                   tracker used by the benchmark runners
experiments/  visualization/  experiment helpers, plotting
scripts/                      studies, sweeps, policy learning, analyses, final run script
tests/                        automated tests
results/                      result tables, JSON, figures
logs/                         submission run logs
```

## Data preparation

Each dataset is placed under `data/<name>/` and gets a split list (`test.txt`) from a script in `scripts/`. The datasets themselves must be obtained from their owners; Stanford2D3D, Structured3D and Holo360D need a licence form.

| dataset | folder | how the list is built |
|---|---|---|
| Structured3D | `data/structured3d/` | `python scripts/make_structured3d_subset.py` reads the panorama zips directly and writes the subset (`rgb/`, `depth/`, `test.txt`) |
| PanoX | `data/panox/` | `python scripts/download_panox.py --split test --out data/panox`, then `python scripts/make_panox_list.py --root data/panox` (prints the depth unit of the first file; the `panox` preset converts centimetres to metres) |
| Holo360D | `data/holo360d/` | `python scripts/make_holo360d_list.py --root data/holo360d` writes `test.txt`, `indoor.txt` and `outdoor.txt` (mesh depth only) |
| Stanford2D3D | `data/stanford2d3d/` | `python scripts/make_stanford_list.py --root data/stanford2d3d --areas area_5a area_5b --out test_area5.txt` |
| NYC street panoramas | `data/nyc_dap/` | copy or link the RGB folder to `rgb/` and the distance folder to `depth/`, then `python scripts/make_nyc_list.py --root data/nyc_dap` |

The configs in `configs/` name the preset and list file used for each dataset. The core sets (Structured3D, PanoX, Holo360D indoor, Holo360D outdoor) are the first four rows; Stanford2D3D and NYC are external and never used to choose anything.

## Running

```bash
bash scripts/run_submission.sh start     # detached, writes logs/submission_<timestamp>.log
bash scripts/run_submission.sh status
bash scripts/run_submission.sh stop
bash scripts/run_submission.sh run       # foreground; DRY=1 prints the commands only
```

Default stages (`STAGES="da2both diag strict analysis"`): DA2 median-fit runs, nadir+JPEG diagnosis, stricter selection rules on the external sets, and CPU analysis and figure generation. The optional `study100` stage repeats the capture-fault studies with 100 frames.

Main entry points in `scripts/`: `distortion_sweep.py` (sweeps), `distortion_study.py` (fault studies), `calibrate_correction.py` and `run_correction.py` (policy learning and end-to-end correction), `threshold_sweep.py`, `nadir_jpeg_diagnosis.py`, `da2_protocol_report.py`, `policy_stability.py`, `make_figures.py`, `make_submission_figures.py`, `check_submission.py`. The `make_*_list.py` scripts and `download_panox.py` prepare the data (see above).

## Tests

```bash
pytest -q                          # 134 tests
python scripts/check_submission.py # confirms the expected result files exist
```

## Results

`results/` holds per-model and per-dataset JSON (`study_*`, `sweep_*`, `correction_*`), the learned policy (`correction_policy.json`), analysis outputs in `results/diag/`, `results/threshold_sweep/`, `results/policy_stability/`, and the figures used in the report in `results/figures/`.

## Licence

See `LICENSE`.
