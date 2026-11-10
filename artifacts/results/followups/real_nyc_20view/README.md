File: Distortion-Aware-Panoramic-Depth-Estimation/artifacts/results/followups/real_nyc_20view/README.md






# Experiment 07 — Real NYC transfer of full-sphere inference

## Research question

Does the existing 20-view icosahedral inference method outperform the simpler two-pole tangent correction on real outdoor panoramas, or is its PanoX polar-band advantage specific to rendered scenes?

This is a locked transfer evaluation, not another hyperparameter sweep. It compares three frozen-MiDaS inference paths on exactly the same images and ground truth:

1. Baseline ERP inference (one view).
2. Two-pole tangent correction (the existing Experiment 04 comparator).
3. 20-view icosahedral tangent inference with the existing overlap alignment and fusion implementation.

No parameter is selected using the 182 evaluation panoramas.

## Dataset and sampling

The workspace contains 1,908 paired NYC RGB panoramas and range maps in DAP_selected/:

- nyc_raw_images_panorama/panorama_<id>.png
- nyc_distance_panorama_npy/erp_distance_<id>.npy

The earlier Lokesh NYC run used the first 75 IDs (0–74). This study deliberately excludes those IDs. It takes IDs at offsets 4 and 14 from each complete 20-ID block starting at 80, producing 182 frames across 91 assumed clusters. The deterministic manifest is committed under artifacts/results/followups/real_nyc_20view/manifests/.

The 20-consecutive-ID grouping is an assumed dependence block, not a verified route or capture-session ID. The cluster bootstrap uses these 91 blocks rather than treating all 182 frames as independent. State this limitation in any report.

## Locked evaluation protocol

- Model: frozen MiDaS DPT-Hybrid 384.
- ERP evaluation grid: 512 x 1024; tangent views: 384 x 384.
- 20-view parameters: padding 0.3, 50 LBFGS iterations, 20,000 max overlap samples, sample fraction 0.02.
- Two-pole parameters: 45-degree threshold, one tangent view per pole, cosine fusion, affine alignment to the ERP baseline.
- Dataset validity: NYC DAP range maps, 0.5–1000 m.
- Protocols: align-all and align-equatorial.
- Primary endpoint: 75–90 degree AbsRel. Secondary endpoints: 60–75 degree and whole-panorama AbsRel.
- Statistics: paired scene-level comparison, aggregated inside 20-ID clusters, 10,000 cluster-bootstrap replicates.

Positive gain means the candidate has lower AbsRel than the reference. The key comparison is 20_view_vs_two_pole; comparisons against baseline alone do not establish that 20-view is better than two-pole tangent.

## Setup and execution

Run commands from the repository root.

### 1. Verify the data and generate the deterministic manifest

In the existing Windows workspace, the generator finds ../../DAP_selected by default:

    python experiments/followups/real_nyc_20view/scripts/create_manifest.py

Expected output: 1,908 paired IDs, 182 selected frames, 91 assumed clusters. The manifest and metadata use relative sample paths and do not hard-code your local Windows root. It writes:

- artifacts/results/followups/real_nyc_20view/manifests/nyc_holdout_182.txt
- artifacts/results/followups/real_nyc_20view/manifests/nyc_holdout_182.metadata.json

The metadata contains sample IDs and the manifest SHA256. If you move the data, pass --dap-root or set DAP_SELECTED_ROOT. The folder supplied as the root must directly contain the two NYC directories above.

### 2. Run the no-GPU PanoX statistical audit first

This is Experiment 08 and should be done before using the GPU:

    python experiments/followups/paired_panox_analysis/analyze_panox.py

It re-analyses the saved Experiment 04 per-scene CSV and calculates the direct paired 20-view-vs-two-pole cluster-bootstrap interval. It uses all 200 scenes and the eight PanoX environments. It performs no new model inference.

### 3. Make the code available to Kaggle

The Kaggle environment must use a repository revision containing these files. Git publication is a separate, deliberate step; do not use this guide to auto-commit or push. The repository's output sync helper only copies files and has Git operations disabled.

### 4. Mount data and model weights in Kaggle

Attach the NYC dataset so the mounted root contains:

- nyc_raw_images_panorama/
- nyc_distance_panorama_npy/

Attach the existing dpt_hybrid_384.pt checkpoint as a Kaggle Dataset as well. Do not upload model weights to Git.

In a Kaggle notebook, after cloning the repository and changing into its Lokesh/ directory, set the paths. Adjust the dataset folder names to the actual names shown in /kaggle/input/:

In a Python notebook cell, set persistent kernel environment variables (replace the two dataset slugs with the names shown in Kaggle's Input pane):

    import os
    os.environ["DAP_SELECTED_ROOT"] = "/kaggle/input/dap-selected"
    os.environ["MIDAS_WEIGHTS"] = "/kaggle/input/midas-weights/dpt_hybrid_384.pt"

Then run the manifest/preflight commands in a later cell:

    !python experiments/followups/real_nyc_20view/scripts/create_manifest.py --dap-root "$DAP_SELECTED_ROOT"

The manifest contains relative paths under DAP_SELECTED_ROOT, so it is portable between the local workspace and Kaggle as long as those two subdirectory names are preserved.

Before the pilot, run the dedicated preflight:

    !python experiments/followups/real_nyc_20view/scripts/preflight.py

It verifies the checkpoint, manifest, all 364 referenced files, CUDA availability, and decodes sample RGB/range pairs. On a CPU-only local machine with no PyTorch installed, use `--skip-cuda` for the path and data check only.

Verify the GPU and Python imports before running:

    !python -c "import torch, numpy, cv2, scipy, yaml, timm; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"

The Kaggle image already supplies CUDA-enabled PyTorch in the normal GPU runtime. Do not blindly run `pip install -r requirements.txt`, because that file includes torch/torchvision and can replace the working CUDA stack. Only install a missing helper dependency, for example:

    !pip install timm==0.6.13 scipy opencv-python-headless pyyaml

Do not reinstall torch unless the Kaggle runtime itself is broken. The .npy maps are read directly by the project loader.

### 5. Run a small pilot before the complete evaluation

The pilot retains complete two-frame clusters. Sixteen frames means eight clusters, which is the minimum accepted by the bootstrap code:

    !bash experiments/followups/real_nyc_20view/run_gpu.sh --limit 16

Check that all 16 images load, CUDA is used, and the report and CSV are created. The pilot's confidence intervals are diagnostic only and must not be quoted as final evidence.

### 6. Run the full locked evaluation

    !bash experiments/followups/real_nyc_20view/run_gpu.sh

The launcher uses one visible CUDA device by default. The current runner is not multi-GPU distributed; selecting two T4 devices does not automatically split the work. Progress is printed every five panoramas. Do not change the FOV, padding, number of views, fusion, fit protocol, or sample after seeing test scores.

The run produces a fresh timestamped directory under outputs/ with:

- per_scene.csv: each scene, cluster, protocol, method, latitude band and metric.
- summary.json: environment, config, sample IDs, bootstrap intervals and runtime.
- REPORT.md: formatted tables and interpretation guardrails.

The shell log is saved under logs/. Existing runs are never overwritten.

## Decision rule and how to interpret it

For the primary 75–90 degree endpoint:

- If the direct 20-view-vs-two-pole 95% interval is entirely above zero, the 20-view method has a supported polar-band advantage on this NYC subset.
- If it is entirely below zero, two-pole tangent is better on this subset.
- If it includes zero, the experiment does not establish a difference; prefer the simpler, lower-call method unless a pre-declared secondary result justifies the extra compute.

Always read this beside whole-panorama error and measured runtime. A polar win that damages overall depth or costs much more per image is not automatically a better practical method.

## Reproducibility and guardrails

- The code records the manifest SHA256 and selected panorama IDs.
- The baseline, two-pole and 20-view predictions are evaluated on identical samples and masks.
- The inference settings are copied from Experiment 04; no NYC-specific tuning is performed.
- align-all and align-equatorial are both evaluation alignments fitted using ground truth. They are reported separately and must not be described as inference-time calibration.
- The 182 frames are disjoint from the earlier first-75 NYC subset, but this is still the same underlying dataset, not an independent dataset release.
- The assumed 20-ID clusters may not correspond to actual routes. Do not overstate the confidence interval as route-level generalisation.
- A pilot is not a substitute for the full 182-frame run.