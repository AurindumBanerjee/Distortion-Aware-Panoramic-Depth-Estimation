# Experiment 05 cross-dataset validation: Holo360D indoor

## Status

Prepared but **not yet executed**. The currently connected Windows workspace has no Holo360D files or attached CUDA device. Do not report this as a completed experiment until the runner writes a timestamped output directory and the validation report.

## Question

Does the FOV trend observed with MiDaS on PanoX transfer to real Holo360D indoor panoramas?

## Controlled protocol

- Frozen model: MiDaS DPT-Hybrid 384, same checkpoint as Experiment 05.
- Dataset: Holo360D **test split, indoor scenes only**.
- Input ERP: 512 x 1024.
- Tangent FOV: 70, 90, 110 and 130 degrees.
- Tangent resolution: fixed at 256 x 256. FOV is the only swept inference variable.
- Fixed settings: threshold 45 degrees, one view per pole, cosine fusion, 20-degree blend band, power 2, affine disparity alignment.
- Report both align-all and align-equatorial; evaluate all, 60-75 and 75-90 degree bands.
- Use the third-column Holo mask (pixel > 127 = valid) in addition to finite/range-valid mesh depth.
- Report paired uncertainty by independent scene cluster, not by treating adjacent frames as independent samples.

The fixed 256 resolution matches the 256 configuration from the original Experiment 05 sweep, allowing a direct comparison to its FOV70 and FOV130 results without confounding FOV with resolution.

## Data preparation

Download only the official Holo360D **test** split, not the training scenes. Extract the indoor scene archives so that the directory passed as `HOLO360D_ROOT` directly contains scene folders and the generated `indoor.txt` list. Each scene must have:

`<Scene>/<Scene>/{rgb,mask,depth/mesh_depth}`

The upstream list builder is `Aurindum/scripts/make_holo360d_list.py`. From the repository's `Aurindum` directory:

```bash
python scripts/make_holo360d_list.py --root /absolute/path/to/Holo360D/test
```

This writes `indoor.txt` at the supplied root. The list must contain three columns: RGB path, mesh-depth EXR path, mask path. Do not use a list containing training scenes for this held-out validation.

## Run

From the `Lokesh` directory, with a CUDA-enabled environment and the MiDaS checkpoint available at `weights/dpt_hybrid_384.pt`:

```bash
export OPENCV_IO_ENABLE_OPENEXR=1
export HOLO360D_ROOT=/absolute/path/to/Holo360D/test
python followup_experiments/05_fov_resolution_sweep/run.py \
  --config followup_experiments/05_fov_resolution_sweep/config_holo360d_indoor.yaml
```

The run writes to a new folder under `followup_experiments/05_fov_resolution_sweep/outputs_holo360d_indoor/`; it does not overwrite the PanoX outputs.

After it finishes, run the cluster analysis (replace the path with the newly created `run_YYYYMMDD_HHMMSS` directory):

```bash
python followup_experiments/05_fov_resolution_sweep/summarize_holo360d_fov.py \
  --run-dir followup_experiments/05_fov_resolution_sweep/outputs_holo360d_indoor/run_YYYYMMDD_HHMMSS
```

This writes `HOLO360D_VALIDATION.md` and `HOLO360D_VALIDATION.json` into the run directory. It reports paired cluster-bootstrap CIs both against the uncorrected baseline and against FOV70.

## Decision rule

Call the PanoX FOV finding externally supported only if wider FOV produces a positive 75-90 degree gain over FOV70 and its cluster-bootstrap CI excludes zero under **both** alignment protocols, while global performance does not materially regress. Report the number of independent scene clusters. If 110 degrees beats 130 degrees, report that as a dataset-dependent optimum rather than claiming that wider is always better.

## Important limitation

The public Holo360D test tree is large (the repository lists the complete test split at roughly 463 GB). Use the team's existing extracted test subset if available. A one-scene smoke test can validate the data pipeline, but one scene cluster is not sufficient for a generalization claim.
