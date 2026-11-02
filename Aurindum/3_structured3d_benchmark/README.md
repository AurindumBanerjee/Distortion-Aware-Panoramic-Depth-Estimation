# Method 3: Structured3D Real-World Foundation Benchmark

**Inspired by:**
- *Depth Any Panoramas (DAP)* (CVPR 2026 / Dec 2025, [arXiv:2512.16913](https://arxiv.org/abs/2512.16913))
- *Depth Anything in 360° (DA360)* (Dec 2025, [arXiv:2512.22819](https://arxiv.org/abs/2512.22819))

---

## 1. Overview
Prior evaluation in this repository was constrained to synthetic toy scenes. This benchmark suite extracts and evaluates real panoramic imagery from `Structured3D_panorama_15.zip`.

It conducts an apples-to-apples comparison of four paradigms on identical real scenes:
1. **Baseline ERP:** Direct standard inference with black-box depth foundation model.
2. **Tangent-Plane Fusion:** Perspective tangent inference with spatial cosine ramping.
3. **Method 1 (Gradient-Domain Polar Fusion):** Poisson gradient-domain blending + shift-decoupled disparity alignment.
4. **Method 2 (Möbius-TTA Ensembling):** Conformal test-time Riemannian sphere dilation and distortion-weighted fusion.

---

## 2. Independent Execution

To run the comparative benchmark:
```bash
cd d:\MyStuff\College\.7thSemester\CV\Project\Distortion-Aware-Panoramic-Depth-Estimation\Aurindum\3_structured3d_benchmark

# Run benchmark on 5 real Structured3D scenes
python run.py --max_scenes 5
```

Outputs:
- **`data/curated_scenes/`**: Extracted high-resolution RGB rawlight and 16-bit PNG depth pairs.
- **`logs/method3_benchmark.log`**: Complete execution and per-scene metrics trace.
- **`outputs/benchmark_summary.json`**: Full hierarchical metrics per latitude band.
- **`outputs/benchmark_table.csv`**: Publication-ready comparison spreadsheet.
- **`../best_model/`**: Automatically updated with the winning method and qualitative depth predictions!
