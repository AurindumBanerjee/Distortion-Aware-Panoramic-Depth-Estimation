# Lokesh — Follow-up Experiments

Five follow-up studies are isolated under this directory. They use the same experiment hygiene as Aurindum:
each study has its own config, standalone runner, GPU launcher, logs, timestamped output folder, per-scene
metrics, summary JSON, and Markdown report. Shared model/data/protocol helpers live in shared/.

Nothing under Aurindum/ or the existing Lokesh pipeline was modified. This bundle adds one isolated DA360
wrapper and a 360MonoDepth-style comparison implementation under followup_experiments/shared/.

## Studies

| ID | Folder | Question | Default model/data |
|---|---|---|---|
| 01 | 01_scale_only_protocol | How much do DA360 polar metrics change when scale-only disparity alignment is used instead of a more permissive affine fit? | DA360 / Structured3D |
| 02 | 02_domain_conditioned_gate | Does a distortion gate calibrated on other environments transfer to a held-out PanoX environment? | DA360 / PanoX, leave-one-environment-out |
| 03 | 03_panda_style_finetuning | Can a compact student learn teacher pseudo-disparity with spherical yaw/reflection consistency and patch-normalized loss? | Frozen DA360 teacher / unlabeled PanoX RGB |
| 04 | 04_mono360_20view | Does a full-sphere 20-view icosahedral pipeline beat the existing two-pole tangent correction? | MiDaS DPT-Hybrid / PanoX |
| 05 | 05_fov_resolution_sweep | How sensitive is tangent correction to the view FOV and pixel resolution? | MiDaS DPT-Hybrid / PanoX |

### Important research-scope notes

- 01: DA360 is described as scale-invariant disparity. Scale-only fitting is the preferred headline protocol; affine fitting is retained as a sensitivity analysis. Structured3D is in-domain for DA360, so do not describe this as zero-shot cross-domain evaluation.
- 02: PanoX is split by environment, not by individual frame. Every fold selects the threshold on all other environments and evaluates it on the held-out one. The per-environment oracle is diagnostic only, never a deployable method.
- 03: This is a PanDA-inspired prototype, not a reproduction of the PanDA paper. It uses a small U-Net student, teacher pseudo-disparity, yaw-roll/reflection augmentations, and a patch-normalized consistency objective. train.py does not open the GT depth files. GT is used only by evaluate.py on held-out environment groups.
- 04: The 20-view implementation follows the icosahedral tangent-view / deformable overlap alignment / frustum blending recipe, but is not claimed as a byte-for-byte reproduction. It is defined for disparity models.
- 05: This is a DAC-motivated FOV/resolution sensitivity experiment using MiDaS tangent views. It does not load or reproduce the DAC model.

## Workspace paths and prerequisites

The connected workspace currently has the following layout:

- PanoX: ../../panox/panox relative to Lokesh/
- Structured3D: ../../structured3d/structured3d relative to Lokesh/
- MiDaS DPT-Hybrid weights: Lokesh/weights/dpt_hybrid_384.pt

The default configs use those paths. For Kaggle, point the variables below at your mounted Kaggle datasets:

    export PANOX_ROOT=/kaggle/input/<your-panox-dataset>/panox
    export STRUCTURED3D_ROOT=/kaggle/input/<your-structured3d-dataset>/structured3d
    export DA360_REPO=/kaggle/working/DA360
    export DA360_WEIGHTS=/kaggle/input/<your-da360-weights>/DA360_large.pth
    export MIDAS_WEIGHTS=/kaggle/input/<your-midas-weights>/dpt_hybrid_384.pt

DA360 requirements: official DA360 repository and checkpoint must be present at those paths. This workspace did not contain the DA360 repository or checkpoint when these files were prepared. Do not silently substitute MiDaS for DA360.

PanoX list: the configured root must contain test.txt with RGB/depth relative paths. Structured3D root must contain test.txt (or change the config to test_s3250.txt). For PanoX, the existing file list has eight environment clusters; keep all clusters in Experiment 02.

PanoX depths are float32 EXR files. If `cv2.imread` cannot decode them in Kaggle, install the optional fallback with `pip install -r followup_experiments/requirements-kaggle.txt`. The Lokesh dataset loader now tries the `OpenEXR` Python reader after OpenCV fails.

## Running

From Lokesh/ on Linux/Kaggle:

    # Individual studies
    bash followup_experiments/01_scale_only_protocol/run_gpu.sh
    bash followup_experiments/02_domain_conditioned_gate/run_gpu.sh
    bash followup_experiments/04_mono360_20view/run_gpu.sh
    bash followup_experiments/05_fov_resolution_sweep/run_gpu.sh

    # Student fine-tuning uses both T4s
    CUDA_VISIBLE_DEVICES=0,1 bash followup_experiments/03_panda_style_finetuning/run_gpu.sh

    # Optional GT evaluation on held-out validation environments
    bash followup_experiments/03_panda_style_finetuning/evaluate_gpu.sh \
      followup_experiments/03_panda_style_finetuning/outputs/run_<timestamp>/best.pt

    # Run 01, 02, 04, 05 sequentially. Add RUN_FINETUNE=1 for the longer student stage.
    bash followup_experiments/run_all.sh
    RUN_FINETUNE=1 bash followup_experiments/run_all.sh

    # Override a data path / reduce a pilot run without editing YAML
    bash followup_experiments/01_scale_only_protocol/run_gpu.sh --limit 32
    bash followup_experiments/04_mono360_20view/run_gpu.sh --limit 16
    bash followup_experiments/05_fov_resolution_sweep/run_gpu.sh --limit 32

Experiment 02 intentionally uses all PanoX environments for LOEO; avoid --limit unless the selected subset
still includes at least three complete environment clusters.

## Result layout

Each run creates a fresh folder under that study's outputs/run_<timestamp>/ containing:

- logs/run.log (or train.log via the shell launcher)
- config_environment.json / summary.json with environment, model, split, and protocol metadata
- per_scene.csv and/or JSON per-scene records
- REPORT.md with the headline comparison

No old run is archived or overwritten. Re-running creates another timestamped folder. The output helper refuses
to reuse a non-empty run path unless explicitly overridden.

## Kaggle setup — step by step

### 1. Publish the experiment commit

The new work is committed locally. Push it from the repository root so Kaggle can clone it:

    git push origin main

The current experiment commit must be visible on GitHub before running the clone command below.

### 2. Upload the datasets to Kaggle

The two dataset archives are outside Git in the parent workspace:

- `panox.zip` (PanoX RGB + EXR distances)
- `structured3d.zip` (Structured3D RGB + depth)

Create private Kaggle Datasets for these files, or upload the extracted folders instead. Add both datasets to the Notebook's **Input** panel. If you upload the zip files, the setup cell can extract them into writable `/kaggle/working` and find the inner folder containing `test.txt`.

The resolved PanoX folder must contain `test.txt` and the nested RGB/distance paths. The resolved Structured3D folder must contain `test.txt` and its RGB/depth folders.

### 3. Configure the Kaggle session

In Notebook **Settings / Session options**:

- Accelerator: **GPU T4 x2**
- Internet: **On**

Changing the accelerator can restart the session. After the restart, run the notebook cells from the beginning. Kaggle exposes accelerator, Internet and attached data sources in the notebook settings/input UI. See the [Kaggle Notebook guide](https://www.kaggle.com/docs/notebooks).

### 4. Clone this repository into the Kaggle working directory

In a cell in your current Kaggle Jupyter session:

    %cd /kaggle/working
    !git clone --depth 1 --branch main https://github.com/AurindumBanerjee/Distortion-Aware-Panoramic-Depth-Estimation.git

Then open:

    /kaggle/working/Distortion-Aware-Panoramic-Depth-Estimation/Lokesh/followup_experiments/kaggle_two_t4_runner.ipynb

If the repository requires GitHub authentication, use a Kaggle Secret / credential helper rather than embedding a personal access token in the notebook. The notebook can also be uploaded/imported directly after downloading it from the repository.

### 5. Set the Kaggle Input paths

In the runner notebook's setup cell, edit `DATA_PATHS` so each root points to the attached Kaggle Input dataset folder. The default placeholders are:

    PANOX_ROOT=/kaggle/input/panox
    STRUCTURED3D_ROOT=/kaggle/input/structured3d

Replace `panox` and `structured3d` with the actual Kaggle dataset slugs shown in the Input pane. You can point the variables at the zip-containing dataset directory or the extracted data root; the cell searches for `test.txt` and can extract a zip into `/kaggle/working`.

### 6. Run the setup cell

Choose the experiment at the top of the setup cell:

    RUN = '01'
    LIMIT = 16

Run the first setup cell. It will:

- confirm CUDA and list the two T4 GPUs;
- install helper libraries without replacing Kaggle's CUDA-enabled PyTorch;
- resolve / extract the selected dataset roots;
- clone the official [DA360 implementation](https://github.com/antigravity-tech/DA360) and download `DA360_large.pth` from [Hugging Face](https://huggingface.co/hljiang/DA360) only for runs 01/02/03;
- download MiDaS DPT-Hybrid weights only for runs 04/05.

The DA360 large checkpoint is about 1.34 GB. Keep Internet enabled during this first setup/download. The wrapper expects the DA360 checkout to contain `checkpoint.py` and the `networks/` package; the setup cell checks this before continuing.

### 7. Run one experiment at a time

After setup succeeds, run the **Choose the study / Launch** cell. Suggested order:

| Run | What it checks | Pilot recommendation |
|---|---|---|
| `01` | DA360 on Structured3D, scale-only vs affine evaluation | Start with `LIMIT=16`; later set `LIMIT=None` |
| `02` | PanoX leave-one-environment-out distortion gate | Set `LIMIT=None`; all PanoX environment groups must be present |
| `04` | 20-view icosahedral pipeline vs two-pole tangent baseline | Start with `LIMIT=2`; this is inference-heavy |
| `05` | Four FOVs × three tangent resolutions | Start with `LIMIT=2`; then scale up |
| `03` | DA360 teacher → student pseudo-label training | Set `RUN='03'`; uses both T4s |

For Experiment 03, the training cell creates `best.pt`. Then set that checkpoint path in the final evaluation cell and run it. Evaluation defaults to the held-out PanoX environment groups; it does not score on the training environments.

To run all inference experiments sequentially, set `RUN='all'`. To include the much longer student training stage too, set `RUN_FINETUNE_IN_ALL=True`. I recommend running 01 and 02 first, checking their reports, and only then spending GPU time on 04/05/03.

### 8. Find and save the results

Each study writes into its own timestamped folder under:

    Lokesh/followup_experiments/<study>/outputs/run_<timestamp>/

Look for `REPORT.md`, `summary.json`, `per_scene.csv`, and logs. Kaggle saves files generated in `/kaggle/working` as notebook output (subject to its output-storage limit); download or save important result folders before ending the session.

## Statistics and caveats

Per-scene metrics use the shared evaluation code and identical validity masks. Experiments 01/02/04/05 report
latitude bands; comparisons use paired scenes and, where applicable, environment-cluster bootstrap. Do not
interpret a small number of PanoX environments as hundreds of independent samples: the environment is the
independent unit for cross-domain gate calibration.

These scripts have not been run on the Kaggle T4 session yet. Syntax and smoke checks are performed separately;
GPU outputs should be treated as pending until the Kaggle notebook executes them successfully.