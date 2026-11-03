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
    if mode == "logscale":  # metric depth: pure multiplicative scale, robust median of the log ratio
        m &= (x > 0) & (y > 0)
        if m.sum() < 50:
            return 1.0, 0.0
        return float(np.exp(np.median(np.log(y[m]) - np.log(x[m])))), 0.0
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


PRESETS: Dict[str, List[Dict[str, float]]] = {
    # The ablation (results/ABLATION_*) attributes the whole Structured3D/MiDaS gain to the two pole-recentring
    # rotations; the dilations add nothing on S3 and hurt PanoX under align-equatorial.
    "rotation_only": [{"pitch": 90.0, "scale": 1.0}, {"pitch": -90.0, "scale": 1.0}],
    "dilation_only": [{"pitch": 0.0, "scale": 1.6}, {"pitch": 0.0, "scale": 0.625}],
    "full": [{"pitch": 90.0, "scale": 1.0}, {"pitch": -90.0, "scale": 1.0},
             {"pitch": 0.0, "scale": 1.6}, {"pitch": 0.0, "scale": 0.625}],
}


def fit_quality(x: np.ndarray, y: np.ndarray, a: float, b: float, mode: str) -> float:
    """Scale-free residual of the anchor fit: median |fit - ref| / median |ref - median(ref)|.

    ~0: the pass reproduces the identity pass on the overlap (after a global affine / scale);
    ~1 or more: the fit explains little of the structure there, so the pass is not trustworthy.
    The overlap is seen at low distortion in BOTH frames, which makes it a free validation set.
    """
    m = np.isfinite(x) & np.isfinite(y)
    if mode == "logscale":
        m &= (x > 0) & (y > 0)
        if m.sum() < 50:
            return float("nan")
        fx, ty = np.log(a * x[m]), np.log(y[m])
    else:
        if m.sum() < 50:
            return float("nan")
        fx, ty = a * x[m] + b, y[m]
    spread = np.median(np.abs(ty - np.median(ty)))
    return float(np.median(np.abs(fx - ty)) / max(spread, 1e-6))


def guard_weight(res: float, a: float, tau: float, a_max: float) -> float:
    """Reliability in [0, 1] of one rotated pass: Gaussian in the fit residual, 0 for implausible scales."""
    if not np.isfinite(res):
        return 1.0
    if a > a_max or a < 1.0 / a_max:
        return 0.0
    return float(np.exp(-(res / max(tau, 1e-6)) ** 2))


def joint_reanchor(raw: Sequence[np.ndarray], seen: Sequence[np.ndarray], mode: str, max_lat: float = 45.0,
                   max_px_per_pair: int = 20000, iters: int = 2, k: float = 2.5) -> List[Tuple[float, float]]:
    """Pass synchronisation: solve every pass's re-anchor jointly (pass 0 = identity, fixed to a=1, b=0).

    affine / scale:  min sum_{i<j} sum_px w * (a_i P_i + b_i - a_j P_j - b_j)^2   (b = 0 for 'scale')
    logscale:        min sum_{i<j} sum_px w * (x_i + log P_i - x_j - log P_j)^2,  a_i = exp(x_i)
    over pixels seen below `max_lat` in BOTH views, w = cos^2(lat_i) cos^2(lat_j); MAD trimming between iterations.
    A pass whose solution is not usable (a <= 0, no overlap) gets (1, 0).
    """
    n = len(raw)
    has_b = mode == "affine"
    npar = (n - 1) * (2 if has_b else 1)
    rng = np.random.default_rng(0)
    blocks = []  # (i, j, Pi, Pj, w)
    for i in range(n):
        for j in range(i + 1, n):
            m = (seen[i] < max_lat) & (seen[j] < max_lat) & np.isfinite(raw[i]) & np.isfinite(raw[j])
            if mode == "logscale":
                m &= (raw[i] > 0) & (raw[j] > 0)
            idx = np.flatnonzero(m)
            if idx.size < 50:
                continue
            if idx.size > max_px_per_pair:
                idx = rng.choice(idx, max_px_per_pair, replace=False)
            w = (np.cos(np.deg2rad(seen[i].ravel()[idx])) * np.cos(np.deg2rad(seen[j].ravel()[idx]))) ** 2
            blocks.append((i, j, raw[i].ravel()[idx], raw[j].ravel()[idx], w))
    if not blocks:
        return [(1.0, 0.0)] * n

    def col(p, which):  # column of parameter (pass p, 0 = a/x, 1 = b) ; pass 0 is fixed
        return None if p == 0 else (p - 1) * (2 if has_b else 1) + which

    rows_A, rows_y, rows_w = [], [], []
    for i, j, Pi, Pj, w in blocks:
        L = len(w)
        A = np.zeros((L, npar))
        y = np.zeros(L)
        for p, P, sgn in ((i, Pi, 1.0), (j, Pj, -1.0)):
            v = np.log(P) if mode == "logscale" else P
            if mode == "logscale":
                c = col(p, 0)
                if c is not None:
                    A[:, c] += sgn
                y -= sgn * v  # x_i - x_j = log P_j - log P_i
            else:
                c = col(p, 0)
                if c is None:
                    y -= sgn * v  # fixed a = 1 for the identity
                else:
                    A[:, c] += sgn * v
                if has_b and col(p, 1) is not None:
                    A[:, col(p, 1)] += sgn
        rows_A.append(A)
        rows_y.append(y)
        rows_w.append(w)
    A, y, w = np.concatenate(rows_A), np.concatenate(rows_y), np.concatenate(rows_w)
    keep = np.ones(len(y), bool)
    sol = np.zeros(npar)
    for _ in range(iters):
        sw = np.sqrt(w[keep])
        sol, *_ = np.linalg.lstsq(A[keep] * sw[:, None], y[keep] * sw, rcond=None)
        r = np.abs(A @ sol - y)
        med = np.median(r)
        mad = np.median(np.abs(r - med)) + 1e-12
        keep = r < med + k * 1.4826 * mad
    out = [(1.0, 0.0)]
    for p in range(1, n):
        if mode == "logscale":
            a, b = float(np.exp(sol[col(p, 0)])), 0.0
        else:
            a = float(sol[col(p, 0)])
            b = float(sol[col(p, 1)]) if has_b else 0.0
        out.append((a, b) if np.isfinite(a) and a > 0 and np.isfinite(b) else (1.0, 0.0))
    return out


def consensus_weights(preds: Sequence[np.ndarray], weights: Sequence[np.ndarray], k: float = 2.5) -> List[np.ndarray]:
    """Down-weight, per pixel, passes far from the per-pixel median of all aligned passes (robust sigma global)."""
    P = np.stack(preds, 0)
    med = np.nanmedian(P, axis=0)
    dev = np.abs(P - med[None])
    d = dev[np.isfinite(dev)]
    if d.size == 0:
        return list(weights)
    sigma = 1.4826 * np.median(d) + 1e-12
    f = np.exp(-(np.nan_to_num(dev, nan=np.inf) / (k * sigma)) ** 2)
    return [w * f[i] for i, w in enumerate(weights)]


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
        gate_lat: Optional[Sequence[float]] = None,
        preset: Optional[str] = None,
        fit_guard: Optional[Dict[str, float]] = None,
        reanchor_scope: str = "identity",
        sync_max_lat: float = 45.0,
        consensus: bool = False,
        consensus_k: float = 2.5,
    ):
        """
        Args:
            model: DepthModelWrapper
            scales: legacy list of pure dilation factors (1.0 = identity). Ignored if `passes` given.
            passes: list of {pitch: deg, scale: lambda} (or bare floats = pure dilations).
                    The identity pass is always added first if missing.
            fusion_mode: 'distortion_weighted' | 'median' | 'mean'
            reanchor: 'affine' | 'scale' | 'logscale' | 'none' | 'auto' (affine for affine-invariant
                      disparity models, scale for relative depth, logscale for metric models)
            gate_lat: [lo, hi] in degrees or None. Non-identity passes only contribute where the ORIGINAL
                      pixel has |lat| > lo (smooth ramp to full weight at hi); below lo the output equals the
                      identity pass exactly. Protects the equator from out-of-distribution (rotated / strongly
                      dilated) passes, which the first full run showed to be catastrophic for DAP and outdoor scenes.
            preset: 'rotation_only' | 'dilation_only' | 'full' (overrides `passes` when given)
            fit_guard: {tau, a_max} or None. Self-validating TTA: every non-identity pass is weighted by how
                       well it reproduces the identity pass on the equatorial overlap (see fit_quality). A pass
                       whose fit is poor, or whose re-anchor scale is implausible (outside [1/a_max, a_max]),
                       is faded out, so that image falls back to the identity prediction. Needs no ground truth.
            reanchor_scope: 'identity' (default: each pass fitted to the identity pass on the equatorial overlap) |
                       'joint' (pass synchronisation: all passes' (a, b) solved together over EVERY pairwise overlap
                       where both views see the pixel below sync_max_lat; the identity stays fixed). The two
                       pole-recentring passes see BOTH poles near their equator, so they constrain each other at the
                       poles, where the identity-only fit has no data.
            consensus: per-pixel robust fusion: a pass that disagrees with the per-pixel median of the aligned
                       passes by more than ~consensus_k robust sigmas is down-weighted (label-free outlier rejection).
            anchor_max_lat: anchor pixels must have |lat| below this in both frames
            weight_power: w = cos(lat_seen)^p
        """
        self.model = model
        if preset:  # a named preset overrides any `passes` list (so --set mobius_tta.preset=... works on every config)
            if preset not in PRESETS:
                raise ValueError(f"unknown preset {preset!r}; choose from {sorted(PRESETS)}")
            passes = PRESETS[preset]
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
            reanchor = "affine" if space == "disparity" else ("logscale" if scale == "metric" else "scale")
        self.reanchor = reanchor
        self.gate_lat = None if gate_lat in (None, [], ()) else (float(gate_lat[0]), float(gate_lat[1]))
        if reanchor_scope not in ("identity", "joint"):
            raise ValueError(f"unknown reanchor_scope {reanchor_scope!r} (identity | joint)")
        self.reanchor_scope = reanchor_scope
        self.sync_max_lat = float(sync_max_lat)
        self.consensus = bool(consensus)
        self.consensus_k = float(consensus_k)
        self.fit_guard = None if not fit_guard else {"tau": float(fit_guard.get("tau", 0.5)),
                                                     "a_max": float(fit_guard.get("a_max", 4.0))}

    def predict(self, rgb_erp: np.ndarray, identity_pred: Optional[np.ndarray] = None
                ) -> Tuple[np.ndarray, List[Dict[str, np.ndarray]]]:
        """Run all passes and fuse. `identity_pred` may be passed to reuse a baseline forward pass."""
        H, W = rgb_erp.shape[:2]
        lat0 = np.abs(latitude_map(H, W))

        # 1. forward passes, brought back to the original grid (raw, not yet re-anchored)
        raw, seen, is_ids = [], [], []
        for pitch, scale in self.passes:
            is_id = abs(pitch) < 1e-6 and abs(scale - 1.0) < 1e-6
            if is_id:
                u = identity_pred if identity_pred is not None else self.model.predict(rgb_erp, kind="erp")
                u, ls = np.asarray(u, dtype=np.float64), lat0
            else:
                warped_rgb, ls = warp_erp_mobius(rgb_erp, scale_factor=scale, pitch_deg=pitch)
                u = unwarp_depth_mobius(self.model.predict(warped_rgb, kind="erp"), scale_factor=scale, pitch_deg=pitch)
            raw.append(u)
            seen.append(ls)
            is_ids.append(is_id)
        ref = raw[0]

        # 2. re-anchoring: each pass to the identity on the equatorial overlap (default), or all passes jointly
        fits = [(1.0, 0.0)] * len(raw)
        if self.reanchor != "none" and self.reanchor_scope == "joint" and len(raw) > 1:
            fits = joint_reanchor(raw, seen, self.reanchor, max_lat=self.sync_max_lat)

        preds, weights, diags = [], [], []
        for k, ((pitch, scale), unwarped, lat_seen, is_id) in enumerate(zip(self.passes, raw, seen, is_ids)):
            a, b = 1.0, 0.0
            res, n_anchor = float("nan"), 0
            if not is_id and self.reanchor != "none":
                anchor = (lat0 < self.anchor_max_lat) & (lat_seen < self.anchor_max_lat)
                if anchor.sum() < 200:  # e.g. pitch 90: overlap of the two equators is small
                    score = np.maximum(lat0, lat_seen)
                    anchor = score <= np.percentile(score, 10.0)
                if self.reanchor_scope == "joint":
                    a, b = fits[k]
                else:
                    a, b = _robust_fit(unwarped[anchor], ref[anchor], self.reanchor)
                res = fit_quality(unwarped[anchor], ref[anchor], a, b, self.reanchor)
                n_anchor = int(anchor.sum())
                unwarped = a * unwarped + b

            w = np.clip(np.cos(np.deg2rad(lat_seen)) ** self.weight_power, self.min_weight, 1.0)
            g = 1.0
            if self.fit_guard is not None and not is_id:
                g = guard_weight(res, a, self.fit_guard["tau"], self.fit_guard["a_max"])
                w = w * g
            if self.gate_lat is not None and not is_id:
                lo, hi = self.gate_lat
                t = np.clip((lat0 - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
                w = w * (0.5 * (1.0 - np.cos(np.pi * t)))  # 0 below lo, 1 above hi (cosine ramp)
            valid = np.isfinite(unwarped) & (unwarped > 0)
            w = np.where(valid, w, 0.0)
            preds.append(np.where(valid, unwarped, np.nan))
            weights.append(w)
            diags.append({"pitch": pitch, "scale": scale, "anchor_a": a, "anchor_b": b,
                          "anchor_res": (float("nan") if is_id else res), "anchor_n": (0 if is_id else n_anchor),
                          "guard_w": g, "unwarped_pred": unwarped, "weight": w})
            logger.debug(f"pass pitch={pitch:+.0f} scale={scale:.3f}: anchor a={a:.4f} b={b:.4f}")

        if self.consensus and len(preds) > 2:
            weights = consensus_weights(preds, weights, k=self.consensus_k)
            for d, w in zip(diags, weights):
                d["weight"] = w
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


def yaw_shift_ensemble(model, rgb_erp: np.ndarray, n_passes: int, identity_pred: Optional[np.ndarray] = None,
                       reanchor: str = "affine", anchor_max_lat: float = 30.0) -> np.ndarray:
    """Compute-matched control for Möbius-TTA: the same number of forward passes, but each pass
    only shifts longitude (a pixel roll), which leaves every pixel's latitude and ERP distortion
    unchanged. Passes are re-anchored to the identity pass and averaged.

    If Möbius-TTA beats this, the gain comes from showing the poles at low distortion, not from
    plain test-time averaging.
    """
    H, W = rgb_erp.shape[:2]
    lat0 = np.abs(latitude_map(H, W))
    anchor = lat0 < anchor_max_lat
    ref = (identity_pred if identity_pred is not None else model.predict(rgb_erp, kind="erp")).astype(np.float64)
    preds = [ref]
    for k in range(1, max(1, n_passes)):
        shift = int(round(k * W / n_passes))
        p = np.roll(model.predict(np.roll(rgb_erp, shift, axis=1), kind="erp").astype(np.float64), -shift, axis=1)
        if reanchor != "none":
            a, b = _robust_fit(p[anchor], ref[anchor], reanchor)
            p = a * p + b
        preds.append(p)
    return np.nanmean(np.stack(preds, 0), axis=0)
