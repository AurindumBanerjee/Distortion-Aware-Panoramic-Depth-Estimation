"""Test-Time Möbius Augmentation (Möbius-TTA) Ensembling.

Each pass applies a conformal Möbius map (rotation pitch + stereographic dilation) to the
panorama, runs the frozen model, maps the prediction back, re-anchors it to the identity
pass and fuses all passes with distortion weights.

Fixes over v1:
  * passes can rotate (pitch = +/-90) so the poles are actually seen at the equator;
  * fusion weights use the latitude at which each ORIGINAL pixel was seen in the warped
    frame (v1 used a warped-frame map on the original grid);
  * equatorial re-anchoring: an affine-invariant model (MiDaS) returns each pass with its
    own unknown (s, t). Every non-identity pass is affinely fitted to the identity pass on
    pixels that are low-latitude in BOTH frames before fusion.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from geometry.spherical import latitude_map
from mobius_transform import unwarp_depth_mobius, warp_erp_mobius

logger = logging.getLogger("MobiusTTA")

PassSpec = Union[float, Dict[str, float]]


def _parse_pass(p: PassSpec) -> Tuple[float, float]:
    if isinstance(p, dict):
        return float(p.get("pitch", 0.0)), float(p.get("scale", 1.0))
    return 0.0, float(p)


def _robust_fit(x: np.ndarray, y: np.ndarray, mode: str, iters: int = 3, k: float = 2.5) -> Tuple[float, float]:
    """y ~ a*x + b (mode 'affine') or y ~ a*x (mode 'scale') with MAD trimming."""
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 50:
        return 1.0, 0.0
    x, y = x[m], y[m]
    keep = np.ones_like(x, dtype=bool)
    a, b = 1.0, 0.0
    for _ in range(iters):
        xi, yi = x[keep], y[keep]
        if len(xi) < 50:
            break
        if mode == "scale":
            a, b = float((xi * yi).sum() / max((xi * xi).sum(), 1e-12)), 0.0
        else:
            A = np.stack([xi, np.ones_like(xi)], -1)
            (a, b), *_ = np.linalg.lstsq(A, yi, rcond=None)
            a, b = float(a), float(b)
        r = np.abs(y - (a * x + b))
        med = np.median(r)
        mad = np.median(np.abs(r - med)) + 1e-12
        keep = r < med + k * 1.4826 * mad
    if not np.isfinite(a) or a <= 0:
        return 1.0, 0.0
    return a, b


class MobiusTTAEnsemble:
    def __init__(
        self,
        model,
        scales: Optional[Sequence[float]] = None,
        fusion_mode: str = "distortion_weighted",
        passes: Optional[Sequence[PassSpec]] = None,
        reanchor: str = "auto",
        anchor_max_lat: float = 30.0,
        weight_power: float = 2.0,
        min_weight: float = 0.02,
    ):
        """
        Args:
            model: DepthModelWrapper
            scales: legacy list of pure dilation factors (1.0 = identity). Ignored if `passes` given.
            passes: list of {pitch: deg, scale: lambda} (or bare floats = pure dilations).
                    The identity pass is always added first if missing.
            fusion_mode: 'distortion_weighted' | 'median' | 'mean'
            reanchor: 'affine' | 'scale' | 'none' | 'auto' (affine for affine-invariant
                      disparity models, scale for relative depth, none for metric models)
            anchor_max_lat: anchor pixels must have |lat| below this in both frames
            weight_power: w = cos(lat_seen)^p
        """
        self.model = model
        specs = list(passes) if passes is not None else list(scales if scales is not None else [1.0])
        parsed = [_parse_pass(p) for p in specs]
        if not any(abs(pt) < 1e-6 and abs(sc - 1.0) < 1e-6 for pt, sc in parsed):
            parsed.insert(0, (0.0, 1.0))
        parsed.sort(key=lambda ps: not (abs(ps[0]) < 1e-6 and abs(ps[1] - 1.0) < 1e-6))  # identity first
        self.passes = parsed
        self.scales = [sc for _, sc in parsed]  # backwards compatibility (logging)
        self.fusion_mode = fusion_mode
        self.anchor_max_lat = anchor_max_lat
        self.weight_power = weight_power
        self.min_weight = min_weight
        if reanchor == "auto":
            spec = getattr(model, "spec", None)
            space = getattr(model, "space", getattr(spec, "space", "depth"))
            scale = getattr(model, "scale", getattr(spec, "scale", "metric"))
            reanchor = "affine" if space == "disparity" else ("none" if scale == "metric" else "scale")
        self.reanchor = reanchor

    def predict(self, rgb_erp: np.ndarray, identity_pred: Optional[np.ndarray] = None
                ) -> Tuple[np.ndarray, List[Dict[str, np.ndarray]]]:
        """Run all passes and fuse. `identity_pred` may be passed to reuse a baseline forward pass."""
        H, W = rgb_erp.shape[:2]
        lat0 = np.abs(latitude_map(H, W))
        preds, weights, diags = [], [], []
        ref = None

        for pitch, scale in self.passes:
            is_id = abs(pitch) < 1e-6 and abs(scale - 1.0) < 1e-6
            if is_id:
                unwarped = identity_pred if identity_pred is not None else self.model.predict(rgb_erp, kind="erp")
                unwarped = unwarped.astype(np.float64)
                lat_seen = lat0
                ref = unwarped
                a, b = 1.0, 0.0
            else:
                warped_rgb, lat_seen = warp_erp_mobius(rgb_erp, scale_factor=scale, pitch_deg=pitch)
                pred_w = self.model.predict(warped_rgb, kind="erp")
                unwarped = unwarp_depth_mobius(pred_w, scale_factor=scale, pitch_deg=pitch)
                a, b = 1.0, 0.0
                if self.reanchor != "none" and ref is not None:
                    anchor = (lat0 < self.anchor_max_lat) & (lat_seen < self.anchor_max_lat)
                    if anchor.sum() < 200:  # e.g. pitch 90: overlap of the two equators is small
                        score = np.maximum(lat0, lat_seen)
                        anchor = score <= np.percentile(score, 10.0)
                    a, b = _robust_fit(unwarped[anchor], ref[anchor], self.reanchor)
                    unwarped = a * unwarped + b

            w = np.clip(np.cos(np.deg2rad(lat_seen)) ** self.weight_power, self.min_weight, 1.0)
            valid = np.isfinite(unwarped) & (unwarped > 0)
            w = np.where(valid, w, 0.0)
            preds.append(np.where(valid, unwarped, np.nan))
            weights.append(w)
            diags.append({"pitch": pitch, "scale": scale, "anchor_a": a, "anchor_b": b,
                          "unwarped_pred": unwarped, "weight": w})
            logger.debug(f"pass pitch={pitch:+.0f} scale={scale:.3f}: anchor a={a:.4f} b={b:.4f}")

        P = np.stack(preds, 0)
        Wt = np.stack(weights, 0)
        if self.fusion_mode == "median":
            fused = np.nanmedian(P, axis=0)
        elif self.fusion_mode == "mean":
            fused = np.nanmean(P, axis=0)
        else:
            sw = Wt.sum(0)
            fused = np.where(sw > 1e-8, np.nansum(np.nan_to_num(P) * Wt, 0) / np.maximum(sw, 1e-8), np.nan)
        bad = ~np.isfinite(fused)
        if bad.any():
            fused[bad] = preds[0][bad]
        return fused, diags
