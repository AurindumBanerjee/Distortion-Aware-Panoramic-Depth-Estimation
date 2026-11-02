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


def gradient_domain_polar_fuse(
    d_erp: np.ndarray,
    d_tangent: np.ndarray,
    weight_map: np.ndarray,
    phi_deg_map: np.ndarray,
    phi_threshold: float = 45.0,
    blend_margin: float = 10.0,
    solver_mode: str = "sor"
) -> np.ndarray:
    """Fuses ERP base depth and polar tangent depth in the gradient domain.
    
    Args:
        d_erp: Baseline panoramic depth/disparity [H, W]
        d_tangent: Backprojected tangent depth/disparity [H, W]
        weight_map: Distortion/confidence weight in [0, 1] [H, W]
        phi_deg_map: Absolute latitude in degrees [0, 90] [H, W]
        phi_threshold: Onset latitude for polar correction (e.g. 45.0 deg)
        blend_margin: Transition ramp margin in degrees
        solver_mode: 'sor' (Dirichlet boundary) or 'fft'
        
    Returns:
        fused_depth: Seamless gradient-fused depth map [H, W]
    """
    # 1. Compute smooth transition alpha mask w(phi) in [0, 1]
    # w = 0 below (phi_threshold - margin), w = 1 above (phi_threshold + margin)
    phi_min = max(0.0, phi_threshold - blend_margin)
    phi_max = min(90.0, phi_threshold + blend_margin)
    
    raw_alpha = (phi_deg_map - phi_min) / max(phi_max - phi_min, 1e-4)
    alpha = np.clip(raw_alpha, 0.0, 1.0)
    # Cosine easing: 0.5 * (1 - cos(pi * alpha))
    alpha = 0.5 * (1.0 - np.cos(np.pi * alpha))
    
    # Modulate alpha by tangent validity and weight
    valid_tangent = np.isfinite(d_tangent) & (d_tangent > 0)
    alpha = alpha * valid_tangent.astype(np.float32)

    # 2. Compute individual gradient vector fields
    gx_erp, gy_erp = compute_gradients(d_erp)
    
    # Safe tangent gradients (fill invalid with erp gradients)
    d_tan_safe = np.where(valid_tangent, d_tangent, d_erp)
    gx_tan, gy_tan = compute_gradients(d_tan_safe)

    # 3. Blend gradient fields: G = (1 - alpha) * grad_ERP + alpha * grad_Tangent
    gx_fused = (1.0 - alpha) * gx_erp + alpha * gx_tan
    gy_fused = (1.0 - alpha) * gy_erp + alpha * gy_tan

    # 4. Compute target divergence field
    div_g = compute_divergence(gx_fused, gy_fused)

    # 5. Solve Poisson equation
    if solver_mode == "fft":
        # Fast FFT based solution
        sol_raw = solve_poisson_fft(div_g)
        # Shift DC component to match equator mean
        equator_mask = phi_deg_map < 30.0
        dc_offset = np.mean(d_erp[equator_mask]) - np.mean(sol_raw[equator_mask])
        fused = sol_raw + dc_offset
        # Hard anchor equatorial zone to exact ERP
        fused = np.where(alpha < 1e-3, d_erp, fused)
    else:
        # Fixed boundary where alpha == 0 (equatorial zone preserved perfectly)
        fixed_mask = (alpha < 1e-3)
        fused = solve_poisson_multigrid(
            base=d_erp,
            div_g=div_g,
            mask_fixed=fixed_mask,
            max_iters=100,
            tol=1e-4
        )

    # Safety clipping to ensure strictly positive depths
    min_val = max(1e-3, np.percentile(d_erp[np.isfinite(d_erp) & (d_erp > 0)], 0.5) * 0.5)
    fused = np.clip(fused, min_val, 1e4)
    return fused
