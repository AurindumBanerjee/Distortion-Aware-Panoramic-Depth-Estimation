# Method 2: Test-Time Möbius Augmentation & Equator-to-Pole Ensembling

**Inspired by:**
- *PanDA: Towards Panoramic Depth Anything with Unlabeled Panoramas and Möbius Spatial Augmentation* (CVPR 2025, [arXiv:2406.13378](https://arxiv.org/abs/2406.13378))

---

## 1. Mathematical Formulation

### The Problem
Rigid $SO(3)$ pitch rotation ($\pm 90^\circ$) places poles on the equator, but creates artificial boundaries and completely disrupts standard horizontal orientation priors (causing sky/floor misclassification).

### The Solution: Conformal Möbius Transformations
The unit sphere $S^2$ is parameterized as the extended complex Riemann sphere $\bar{\mathbb{C}}$. Points $(\theta, \phi)$ map via stereographic projection:
$$\zeta = e^{i\theta} \tan\left(\frac{\pi}{4} + \frac{\phi}{2}\right)$$

Conformal dilation is applied as:
$$f(\zeta) = \lambda \cdot \zeta \quad (\lambda > 0)$$
- When $\lambda = 1.6$, the southern high-distortion polar cap is smoothly pulled up into the equatorial band.
- When $\lambda = 0.625$, the northern high-distortion polar cap is pulled down into the equatorial band.

Because Möbius transformations are **strictly conformal** (angle-preserving), local textures and surface normals remain undistorted.

### Test-Time Ensembling
For each input panorama:
1. Generate multiple conformal passes ($\lambda \in \{1.0, 1.6, 0.625\}$).
2. Forward through the black-box depth model in ERP mode.
3. Conformal inverse unwarp each prediction back to the original ERP coordinate space.
4. Fuse predictions with an effective latitude prior:
$$w_i(u, v) = \cos(\phi_{\text{effective}}(u, v))^2$$

---

## 2. Independent Execution

To execute this method independently:
```bash
cd Aurindum/2_mobius_tta_ensembling

# Run with default config
python run.py

# Run with custom parameters
python run.py --num_scenes 8 --fusion_mode distortion_weighted
```

Outputs:
- **`logs/method2_mobius.log`**: Complete execution log and band-by-band error tracking.
- **`outputs/metrics_summary.json`**: Performance metrics JSON.
- **`../best_model/`**: Automatically updated if this run achieves a new best polar AbsRel!


## Rotation-only preset and self-validating pass guard (added 3 Nov 2026)
* `mobius_tta.preset: rotation_only` keeps only the pitch +/-90 passes (the ablation shows the S3/MiDaS gain comes entirely
  from them; dilation adds nothing there and hurts PanoX under align-equatorial). A preset overrides `passes`.
* `mobius_tta.fit_guard: {tau: 0.5, a_max: 4.0}` weights every rotated pass by `exp(-(res/tau)^2)` where `res` is the scale-free
  residual of its equatorial re-anchor fit (`fit_quality`) and drops it if the fitted scale is outside [1/a_max, a_max].
  The overlap seen at low distortion in both frames is a free, label-free validation set; a pass that cannot reproduce the
  identity pass there is not trusted at the pole either (to be confirmed by `scripts/diagnose_reanchor.py`).
  Default is off, so earlier results are reproduced bit for bit.
* `scripts/diagnose_reanchor.py` reports, per rotated pass, the intrinsic gain (oracle polar fit), the realised gain
  (label-free re-anchor) and the anchor loss, plus the AUC of each label-free signal for predicting harm.
