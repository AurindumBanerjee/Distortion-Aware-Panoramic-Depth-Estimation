"""Gradient-Domain (Poisson) Polar Fusion for Panoramic Depth.

Inspired by 360MonoDepth (CVPR 2022, arXiv:2111.15669).
Instead of simple spatial alpha blending (which blurs structural edges across the polar boundary),
this module fuses the depth gradient fields and solves the Poisson equation:

    div(grad D) = div(G)

where G(u, v) = (1 - w) * grad D_ERP + w * grad D_tangent.
The solution maintains high-frequency structural edges from the tangent view while seamlessly
matching the low-frequency scale and continuity of the equatorial ERP baseline.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger("GradientPolarFusion")


def compute_gradients(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Computes spatial gradients (dI/dx, dI/dy) with circular boundary in x (longitude)."""
    # Horizontal gradient (central differences, periodic boundary in longitude)
    gx = (np.roll(image, -1, axis=1) - np.roll(image, 1, axis=1)) / 2.0
    
    # Vertical gradient (forward/backward at poles, central difference inside)
    gy = np.zeros_like(image)
    gy[1:-1, :] = (image[2:, :] - image[:-2, :]) / 2.0
    gy[0, :] = image[1, :] - image[0, :]
    gy[-1, :] = image[-1, :] - image[-2, :]
    
    return gx, gy


def compute_divergence(gx: np.ndarray, gy: np.ndarray) -> np.ndarray:
    """Computes divergence of a 2D vector field div(G) = dGx/dx + dGy/dy with periodic x."""
    # dGx/dx (central difference, periodic x)
    dgx = (np.roll(gx, -1, axis=1) - np.roll(gx, 1, axis=1)) / 2.0
    
    # dGy/dy (boundary aware in y)
    dgy = np.zeros_like(gy)
    dgy[1:-1, :] = (gy[2:, :] - gy[:-2, :]) / 2.0
    dgy[0, :] = gy[1, :] - gy[0, :]
    dgy[-1, :] = gy[-1, :] - gy[-2, :]
    
    return dgx + dgy


def solve_poisson_fft(div_g: np.ndarray) -> np.ndarray:
    """Fast Poisson solver on full image using 2D FFT with periodic x and cosine y."""
    H, W = div_g.shape
    # Frequencies
    kx = 2.0 * np.pi * np.fft.fftfreq(W)
    ky = 2.0 * np.pi * np.fft.fftfreq(H)
    KX, KY = np.meshgrid(kx, ky)
    denom = 2.0 * (np.cos(KX) - 1.0) + 2.0 * (np.cos(KY) - 1.0)
    denom[0, 0] = 1.0  # avoid division by zero at DC component

    div_fft = np.fft.fft2(div_g)
    sol_fft = div_fft / denom
    sol_fft[0, 0] = 0.0  # Zero DC offset

    sol = np.real(np.fft.ifft2(sol_fft))
    return sol


def solve_poisson_multigrid(
    base: np.ndarray,
    div_g: np.ndarray,
    mask_fixed: np.ndarray,
    max_iters: int = 150,
    tol: float = 1e-4,
    omega: float = 1.6
) -> np.ndarray:
    """Solves Poisson equation with Dirichlet boundary condition on mask_fixed using SOR.
    
    Delta D = div_g, with D(x, y) = base(x, y) where mask_fixed is True.
    """
    sol = base.copy()
    mask_free = ~mask_fixed

    if not np.any(mask_free):
        return sol

    # Successive Over-Relaxation (SOR) with red-black Gauss-Seidel for speed
    H, W = base.shape
    r_idx, c_idx = np.indices((H, W))
    red_mask = ((r_idx + c_idx) % 2 == 0) & mask_free
    black_mask = ((r_idx + c_idx) % 2 == 1) & mask_free

    for it in range(max_iters):
        prev_sol = sol.copy()

        # Update Red points
        up = np.roll(sol, -1, axis=0)
        down = np.roll(sol, 1, axis=0)
        left = np.roll(sol, 1, axis=1)
        right = np.roll(sol, -1, axis=1)

        laplacian_neighbors = 0.25 * (up + down + left + right - div_g)
        sol[red_mask] = (1 - omega) * sol[red_mask] + omega * laplacian_neighbors[red_mask]

        # Update Black points
        up = np.roll(sol, -1, axis=0)
        down = np.roll(sol, 1, axis=0)
        left = np.roll(sol, 1, axis=1)
        right = np.roll(sol, -1, axis=1)

        laplacian_neighbors = 0.25 * (up + down + left + right - div_g)
        sol[black_mask] = (1 - omega) * sol[black_mask] + omega * laplacian_neighbors[black_mask]

        # Check convergence
        max_diff = np.max(np.abs(sol[mask_free] - prev_sol[mask_free]))
        if max_diff < tol:
            logger.debug(f"Poisson solver converged in {it+1} iterations (diff={max_diff:.2e}).")
            break

    return sol


def _edge_gradients(img: np.ndarray):
    """Forward-difference gradients on the ERP grid.

    gx[i, j] = img[i, (j+1) % W] - img[i, j]   (longitude is periodic)
    gy[i, j] = img[i+1, j]       - img[i, j]   (i < H-1; no edge across a pole)
    NaNs propagate, so an edge is invalid if either endpoint is.
    """
    gx = np.roll(img, -1, axis=1) - img
    gy = img[1:, :] - img[:-1, :]
    return gx, gy


def _texture_gate(rgb: np.ndarray, tau: float, H: int, W: int):
    """Soft gate in [0, 1] per edge: ~0 where the RGB gradient is below tau (textureless)."""
    g = rgb.astype(np.float64)
    if g.max() > 1.5:
        g = g / 255.0
    if g.ndim == 3:
        g = g.mean(-1)
    if g.shape != (H, W):
        import cv2
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_AREA)
    tx, ty = _edge_gradients(g)
    soft = max(0.25 * tau, 1e-6)
    sig = lambda t: 1.0 / (1.0 + np.exp(-(np.abs(t) - tau) / soft))
    return sig(tx), sig(ty)


def solve_screened_poisson_sparse(
    base: np.ndarray,
    gx: np.ndarray,
    gy: np.ndarray,
    fixed: np.ndarray,
    cg_threshold: int = 300_000,
) -> np.ndarray:
    """Least-squares integration of a gradient field with Dirichlet constraints.

    Solves  min_D  sum_edges (D_q - D_p - g_pq)^2   s.t.  D = base on `fixed`
    on the ERP grid graph (periodic in longitude, Neumann at the poles: there is no
    edge between the north-pole row and the south-pole row). The discrete operator is
    exactly consistent with `_edge_gradients`, so integrating the gradients of an image
    reproduces that image (unlike the previous central-difference / 5-point mismatch).
    Uses a sparse direct solve (or CG for very large systems): exact, no iteration cap.
    """
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla

    H, W = base.shape
    N = H * W
    idx = np.arange(N).reshape(H, W)

    p_h, q_h = idx.ravel(), np.roll(idx, -1, axis=1).ravel()
    p_v, q_v = idx[:-1].ravel(), idx[1:].ravel()
    p = np.concatenate([p_h, p_v])
    q = np.concatenate([q_h, q_v])
    g = np.concatenate([gx.ravel(), gy.ravel()])
    E = len(g)
    rows = np.concatenate([np.arange(E), np.arange(E)])
    cols = np.concatenate([q, p])
    vals = np.concatenate([np.ones(E), -np.ones(E)])
    A = sp.csr_matrix((vals, (rows, cols)), shape=(E, N))

    fixed_f = fixed.ravel()
    free = ~fixed_f
    if not free.any():
        return base.copy()
    A_f = A[:, free]
    A_c = A[:, fixed_f]
    rhs_e = g - A_c @ base.ravel()[fixed_f]
    M = (A_f.T @ A_f).tocsc()
    b = A_f.T @ rhs_e
    if not fixed_f.any():  # pure Neumann problem: pin the mean with a tiny regulariser
        M = M + 1e-8 * sp.identity(M.shape[0], format="csc")
    if M.shape[0] <= cg_threshold:
        x = spla.spsolve(M, b)
    else:
        diag = M.diagonal()
        pre = spla.LinearOperator(M.shape, matvec=lambda v: v / diag)
        x, info = spla.cg(M, b, x0=base.ravel()[free], M=pre, maxiter=5000, rtol=1e-8)
        if info != 0:
            logger.warning(f"CG did not fully converge (info={info}).")
    out = base.ravel().copy()
    out[free] = x
    return out.reshape(H, W)


def gradient_domain_polar_fuse(
    d_erp: np.ndarray,
    d_tangent: np.ndarray,
    weight_map: np.ndarray,
    phi_deg_map: np.ndarray,
    phi_threshold: float = 45.0,
    blend_margin: float = 10.0,
    solver_mode: str = "sparse",
    rgb: Optional[np.ndarray] = None,
    texture_tau: float = 0.0,
    texture_gate_mode: str = "erp",
) -> np.ndarray:
    """Fuses ERP base disparity and aligned polar tangent disparity in the gradient domain.

    Both inputs MUST be in the same space (ERP disparity); see shift_alignment.

    G = (1 - alpha) * grad D_ERP + alpha * grad D_tan, alpha = cosine ramp in |phi| around
    phi_threshold (x weight_map, x tangent validity). D is fixed to D_ERP wherever alpha == 0,
    and the rest is the least-squares integral of G (solve_screened_poisson_sparse).

    Texture gating (texture_tau > 0): tangent gradients on textureless pixels (|grad I| < tau,
    image in [0, 1]) are distrusted.
      texture_gate_mode='erp'  -> use the ERP gradient there instead (alpha *= gate)
      texture_gate_mode='zero' -> G_tan *= gate (flattens textureless regions; the
                                  formulation from the project notes; can bend planar ceilings)
    """
    H, W = d_erp.shape
    phi_min = max(0.0, phi_threshold - blend_margin)
    phi_max = min(90.0, phi_threshold + blend_margin)
    alpha = np.clip((phi_deg_map - phi_min) / max(phi_max - phi_min, 1e-4), 0.0, 1.0)
    alpha = 0.5 * (1.0 - np.cos(np.pi * alpha))
    valid_tangent = np.isfinite(d_tangent) & (d_tangent > 0)
    alpha = alpha * valid_tangent * np.clip(np.nan_to_num(weight_map, nan=0.0), 0.0, 1.0)

    gx_e, gy_e = _edge_gradients(d_erp)
    gx_t, gy_t = _edge_gradients(np.where(valid_tangent, d_tangent, np.nan))
    # edge weight = mean of endpoint alphas; invalid tangent edges fall back to ERP
    ax = 0.5 * (alpha + np.roll(alpha, -1, axis=1))
    ay = 0.5 * (alpha[1:] + alpha[:-1])
    ax = np.where(np.isfinite(gx_t), ax, 0.0)
    ay = np.where(np.isfinite(gy_t), ay, 0.0)
    gx_t = np.nan_to_num(gx_t)
    gy_t = np.nan_to_num(gy_t)

    if texture_tau > 0 and rgb is not None:
        tgx, tgy = _texture_gate(rgb, texture_tau, H, W)
        if texture_gate_mode == "zero":
            gx_t, gy_t = gx_t * tgx, gy_t * tgy
        else:
            ax, ay = ax * tgx, ay * tgy

    gx = (1.0 - ax) * gx_e + ax * gx_t
    gy = (1.0 - ay) * gy_e + ay * gy_t

    fixed = alpha < 1e-3
    if solver_mode == "fft":
        logger.warning("solver_mode='fft' is deprecated (ignores the Dirichlet anchor); using 'sparse'.")
    fused = solve_screened_poisson_sparse(d_erp, gx, gy, fixed)

    pos = d_erp[np.isfinite(d_erp) & (d_erp > 0)]
    min_val = max(1e-6, 0.5 * np.percentile(pos, 0.5)) if pos.size else 1e-6
    return np.clip(fused, min_val, None)
