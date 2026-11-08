# Method 1: Gradient-Domain Polar Fusion & Shift-Decoupled Alignment

**Inspired by:**
- *360MonoDepth: High-Resolution 360° Monocular Depth Estimation* (CVPR 2022, [arXiv:2111.15669](https://arxiv.org/abs/2111.15669))
- *DA360: Towards Scale Invariance in the Wild* (Dec 2025, [arXiv:2512.22819](https://arxiv.org/abs/2512.22819))

---

## 1. Mathematical Formulation

### The Problem
When blending a polar tangent view $D_{\text{tangent}}$ with the base ERP depth $D_{\text{ERP}}$, spatial alpha blending:
$$D_{\text{fused}}(u, v) = (1 - w(\phi)) D_{\text{ERP}}(u, v) + w(\phi) D_{\text{tangent}}(u, v)$$
causes blurring, double-edge ghosting, and step-discontinuities across high-contrast edges (such as ceiling lights, corners, or floor objects) at the latitude boundary $|\phi| \approx 45^\circ$.

### The Solution: Gradient-Domain (Poisson) Blending
Instead of blending values directly, this method fuses the **spatial depth gradient fields**:
$$\mathbf{G}(u, v) = (1 - w(\phi)) \nabla D_{\text{ERP}}(u, v) + w(\phi) \nabla D_{\text{tangent}}(u, v)$$

The reconstructed depth map $D^*$ is obtained by solving the Poisson equation:
$$\Delta D^* = \text{div}(\mathbf{G})$$
subject to Dirichlet boundary conditions on the equatorial baseline ($D^*(u, v) = D_{\text{ERP}}(u, v)$ for $|\phi| < \phi_{\text{threshold}} - \Delta$).

### Shift-Decoupled Disparity Alignment
Perspective foundation models output affine disparity:
$$d = s \cdot \frac{1}{z} + t$$
where $t$ is an unknown per-view additive shift. Converting directly to Euclidean range $r = \frac{1}{\cos(\text{ray}) \cdot d}$ causes severe non-linear scale drift when $t \neq 0$.
The parameters $(s, t)$ are fitted exclusively on high-confidence equatorial anchor pixels ($|\phi| < 35^\circ$) using iteratively reweighted least squares with MAD outlier rejection before backprojection.

---

## 2. Independent Execution

To execute this method independently:
```bash
cd Aurindum/1_gradient_polar_fusion

# Run with default config
python run.py

# Run with custom parameters
python run.py --num_scenes 8 --blend_mode gradient_poisson
```

Outputs:
- **`logs/method1_gradient.log`**: Detailed execution trace and scene-by-scene metrics.
- **`outputs/metrics_summary.json`**: Global and per-latitude band performance metrics.
- **`../best_model/`**: Automatically updated if this run establishes a new state-of-the-art polar AbsRel score.
