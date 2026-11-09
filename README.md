# Distortion-Aware Panoramic Depth Estimation

CV coursework, IIT Jodhpur.

| Author | Roll number | Folder |
|---|---|---|
| Aurindum Banerjee | B23CS1006 | [`Aurindum/`](Aurindum/) |
| Harshita Vachhani | B23EE1026 | [`Harshita/`](Harshita/) |
| Lokesh Motwani | B23CS1033 | [`Lokesh/`](Lokesh/) |

The project asks whether the stretching of equirectangular (ERP) panoramas explains the larger polar error of monocular depth models, and what does. All models are used as released; nothing is trained in the final study.

## Where the final report and results are

- **Final report:** [`Aurindum/Final_Report.pdf`](Aurindum/Final_Report.pdf), source in [`Aurindum/Report/draft/`](Aurindum/Report/draft/).
- **Code, tests, results and how to run them:** [`Aurindum/README.md`](Aurindum/README.md). The final study covers four frozen models (MiDaS DPT-Hybrid, DAP, DA360, DA2) on six datasets (Structured3D, PanoX, Holo360D indoor and outdoor, and the external Stanford2D3D and NYC panoramas), with sweeps, capture-fault studies and a correction front end.
- **Reproducing:** from `Aurindum/`, `pytest -q` runs the 134 tests and `bash scripts/run_submission.sh start` runs the final experiments (details in `Aurindum/README.md`).

## The three folders

Each folder is a self-contained copy of the code base with that author's experiments and results.

| Folder | Contents |
|---|---|
| [`Aurindum/`](Aurindum/) | The final study: cross-model benchmark and measurement sweeps, the capture-fault catalogue with a fix per fault, the correction front end with a leave-one-dataset-out policy, the external Stanford2D3D and NYC checks, the report and the submission scripts. |
| [`Harshita/`](Harshita/) | Inference-time projection corrections (tangent planes, rotated spheres) with MiDaS DPT-Hybrid and Swin2-Tiny on procedurally rendered indoor panoramas, with Holo360D and Structured3D runs; see its `README.md` and `RESULTS.md`. |
| [`Lokesh/`](Lokesh/) | Follow-up experiments in `followup_experiments/`: scale-only alignment, a domain-conditioned gate, PanDA-style fine-tuning, 20-view tangent inference, an FOV and resolution sweep and a structure-at-poles gate; see its `README.md` and `RESULTS.md`. |

Datasets and model weights are not in the repository.
