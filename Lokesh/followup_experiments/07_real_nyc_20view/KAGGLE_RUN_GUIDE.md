# Experiment 07 execution checklist (Kaggle T4)

This guide is separate from the method description in 07_real_nyc_20view/README.md.

## Before opening Kaggle

1. Confirm the new files are in your working tree.
2. From the repository root, stage only the experiment, manifest, audit, and index files:

       git add Lokesh/README.md Lokesh/followup_experiments/README.md Lokesh/followup_experiments/RESULTS.md Lokesh/followup_experiments/07_real_nyc_20view Lokesh/followup_experiments/08_paired_panox_analysis

3. Commit and push the branch you use for Kaggle:

       git commit -m "Add real NYC 20-view transfer experiment"
       git push origin main

   If the branch is not main, push that branch and use its name below. Do not add the model checkpoint, data, or other generated large files to Git.

## Kaggle notebook setup

Use a GPU notebook with a T4 accelerator. Two T4s are not required; the Experiment 07 launcher currently uses one visible CUDA device and is not distributed across multiple GPUs.

Clone or update the repository in /kaggle/working:

    %cd /kaggle/working
    !git clone --depth 1 --branch main https://github.com/AurindumBanerjee/Distortion-Aware-Panoramic-Depth-Estimation.git

If the repository is already cloned, use !git pull from the correct branch instead.

Attach the NYC dataset and MiDaS weights as Kaggle Input datasets. The NYC input root must contain both folders:

- nyc_raw_images_panorama/
- nyc_distance_panorama_npy/

Set paths using the actual Kaggle slugs shown in the Input panel:

    %cd /kaggle/working/Distortion-Aware-Panoramic-Depth-Estimation/Lokesh
    import os
    os.environ["DAP_SELECTED_ROOT"] = "/kaggle/input/dap-selected"
    os.environ["MIDAS_WEIGHTS"] = "/kaggle/input/midas-weights/dpt_hybrid_384.pt"

Verify GPU and imports:

    !python -c "import torch, numpy, cv2, scipy, yaml, timm; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"

A standard Kaggle GPU image already has CUDA-enabled PyTorch. Do not blindly install requirements.txt: it includes torch/torchvision and can replace the working CUDA installation. Install only missing helper dependencies, e.g.:

    !pip install timm==0.6.13 scipy opencv-python-headless pyyaml

## Generate / verify the manifest

    !python followup_experiments/07_real_nyc_20view/scripts/create_manifest.py --dap-root "$DAP_SELECTED_ROOT"

Expected: 1,908 paired source IDs, 182 selected frames, 91 assumed blocks. The manifest and metadata are stored under followup_experiments/07_real_nyc_20view/manifests/.

The sample IDs exclude 0–74, which were used by Lokesh's earlier NYC evaluation. Keep the generated manifest unchanged for the main run. Do not choose a new sample after looking at experiment results.

## Pilot, then full run

First run a small pilot containing 16 frames (eight complete assumed blocks):

    !bash followup_experiments/07_real_nyc_20view/run_gpu.sh --limit 16

Confirm that:
- CUDA is available.
- All 16 frames load.
- The run finishes and writes REPORT.md, summary.json, and per_scene.csv.
- Runtime and memory are reasonable.

Then run the locked full evaluation:

    !bash followup_experiments/07_real_nyc_20view/run_gpu.sh

It evaluates all 182 images under align-all and align-equatorial and compares baseline, two-pole tangent, and 20-view inference. It creates a timestamped output directory and a log file. Existing outputs are not overwritten.

Download or save the output folder from /kaggle/working before closing the notebook.

## What not to change

Do not change the tangent FOV/size, 20-view padding, overlap solver, polar threshold, fusion, sample, or alignment protocols after inspecting this evaluation. That would turn the held-out set into tuning data.

## Decision rule

Read the 20_view_vs_two_pole paired cluster-bootstrap interval for the primary 75–90° AbsRel endpoint:

- Entirely above zero: evidence that 20-view has lower polar error on this NYC subset.
- Entirely below zero: evidence that two-pole tangent has lower polar error.
- Includes zero: no established direct difference; prefer the simpler method unless a pre-declared secondary endpoint justifies the added cost.

Always consider whole-panorama error and measured runtime alongside polar error.

## Statistical limitation

The runner groups panorama IDs into contiguous 20-ID blocks. This is an explicit dependence assumption, not a verified route or capture-session identifier. Report the result as held-out-frame transfer within this NYC collection, not independent route-level validation or a new dataset benchmark.
