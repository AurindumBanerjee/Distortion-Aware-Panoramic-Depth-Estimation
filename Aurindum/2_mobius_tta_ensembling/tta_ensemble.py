"""Test-Time Möbius Augmentation (Möbius-TTA) Ensembling.

Applies multiple conformal transformations to shift polar latitude bands into
equatorial low-distortion regions during test-time inference, and ensembles the unwarped
predictions using latitude distortion weights.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import numpy as np

from geometry.spherical import latitude_map
from mobius_transform import unwarp_depth_mobius, warp_erp_mobius

logger = logging.getLogger("MobiusTTA")


class MobiusTTAEnsemble:
    def __init__(
        self,
        model,
        scales: List[float] = (1.0, 1.5, 0.67),
        fusion_mode: str = "distortion_weighted"
    ):
        """
        Args:
            model: DepthModelWrapper instance
            scales: Dilation factors (1.0 is identity, >1.0 compresses south pole, <1.0 compresses north pole)
            fusion_mode: 'distortion_weighted', 'median', or 'mean'
        """
        self.model = model
        self.scales = list(scales)
        self.fusion_mode = fusion_mode

    def predict(
        self,
        rgb_erp: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict[str, np.ndarray]]]:
        """Runs multi-pass Möbius TTA inference and fuses predictions.
        
        Returns:
            fused_depth: Ensembled depth map on the original ERP grid [H, W]
            pass_diagnostics: Diagnostic details for each TTA pass
        """
        H, W = rgb_erp.shape[:2]
        unwarped_predictions = []
        weights = []
        pass_diagnostics = []

        for scale in self.scales:
            logger.debug(f"Executing Möbius TTA pass with scale lambda={scale:.3f}...")
            
            if abs(scale - 1.0) < 1e-4:
                # Identity pass
                pred = self.model.predict(rgb_erp, kind="erp")
                unwarped = pred
                lat_deg = np.abs(latitude_map(H, W))
            else:
                # 1. Conformal forward warp
                warped_rgb, effective_lat = warp_erp_mobius(rgb_erp, scale_factor=scale)
                
                # 2. Model inference on warped image
                pred_warped = self.model.predict(warped_rgb, kind="erp")
                
                # 3. Conformal inverse unwarp
                unwarped = unwarp_depth_mobius(pred_warped, scale_factor=scale)
                lat_deg = effective_lat

            # Weight calculation: based on the latitude the model actually processed
            # cos(phi)^2 prior: equatorial content receives weight ~1, polar content ~0
            w = np.cos(np.deg2rad(lat_deg)) ** 2
            w = np.clip(w, 0.05, 1.0)
            
            # Mask out invalid predictions
            valid = np.isfinite(unwarped) & (unwarped > 0)
            w = np.where(valid, w, 0.0)

            unwarped_predictions.append(unwarped)
            weights.append(w)
            pass_diagnostics.append({
                "scale": scale,
                "unwarped_pred": unwarped,
                "weight": w
            })

        # --- Fusion ---
        preds_stack = np.stack(unwarped_predictions, axis=0)
        weights_stack = np.stack(weights, axis=0)

        if self.fusion_mode == "median":
            fused = np.nanmedian(preds_stack, axis=0)
        elif self.fusion_mode == "mean":
            fused = np.nanmean(preds_stack, axis=0)
        else:  # distortion_weighted
            sum_w = np.sum(weights_stack, axis=0)
            sum_w_safe = np.where(sum_w > 1e-6, sum_w, 1.0)
            fused = np.sum(preds_stack * weights_stack, axis=0) / sum_w_safe

        # Fallback for any NaN pixels
        nan_mask = ~np.isfinite(fused)
        if np.any(nan_mask):
            fused[nan_mask] = unwarped_predictions[0][nan_mask]

        return fused, pass_diagnostics
