"""Model-agnostic, ground-truth-free gate deciding whether a polar correction
should be applied at all, per pole, per image.

Motivated by experiment 02's finding that gating on latitude threshold or on
environment identity does not transfer (LOEO always selected "baseline"; the
oracle upper bound was worse than baseline for 2/8 held-out environments
while clearly better for 3/8). The hypothesis tested here is that what
predicts whether correction helps is not *where* on the sphere you are, but
whether the polar cap actually contains real, correctable geometric
structure in *this* image -- see README.md for the full rationale, tying
this to Harshita's capture-artifact benchmark (tilt, tripod occlusion,
missing top/bottom coverage, compression).

Pure-numpy (+scipy.ndimage for connected components), no model/GT dependency,
so this can run on any backbone's raw RGB + disparity/depth output before
alignment.

Sanity-tested against synthetic clean/artifact scenes in HANDOFF.md's test
session: the first cut of the tripod heuristic (area-fraction only) scored
0.76/1.0 on a CLEAN synthetic indoor cap with no injected artifact -- smooth
ordinary geometry (floors, walls) naturally has locally-flat patches. Adding
a connectedness + bottom-edge-contact requirement (a real tripod is one
compact blob entering from the frame edge, not scattered flat pixels) fixed
this: 0/15 false positives on repeated clean synthetic scenes, while still
flagging all four injected artifacts (tripod, missing coverage, flat sky,
compression) correctly. Still: this was validated on synthetic data only.
Calibrate thresholds (see calibrate_thresholds()) and spot-check against real
PanoX/Structured3D scenes -- especially ones with large nearby flat surfaces
(close-up walls, tabletops) -- before trusting it on a full run.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import numpy as np
from scipy import ndimage

# ---- thresholds -----------------------------------------------------------
# These are starting points, not fitted values. Calibrate on a small held-out
# slice (same spirit as experiment 02's minimum_calibration_gain) before
# trusting should_correct() for a real run; see calibrate_thresholds().
TRIPOD_VARIANCE_PCTL = 15        # cap pixels below this disparity-variance percentile -> flat
TRIPOD_AREA_FRAC = 0.08          # min fraction of the cap the blob must cover to flag
TRIPOD_NEAR_DEPTH_FRAC = 0.25    # "near camera" = disparity in top 25% of the cap's own range
TRIPOD_MIN_COMPACTNESS = 0.6     # largest connected flat+near component must hold this fraction
                                  # of ALL flagged pixels -- rejects scattered/diffuse flat regions
TRIPOD_TOUCHES_EDGE = True       # south-cap blob must touch the bottom frame-edge row (how a
                                  # physical tripod actually enters the shot)
MISSING_COVERAGE_FRAC = 0.05     # fraction of invalid/degenerate pixels in the cap to flag
FLAT_SKY_GRADIENT_PCTL = 10      # cap mean |gradient| below this percentile (vs whole image) -> flat
FLAT_SKY_TEXTURE_STD = 0.02      # RGB std (0-1 scale) below this -> likely featureless sky/ceiling
BLOCKINESS_RATIO = 1.8           # 8x8-grid edge energy vs interior energy ratio -> compressed


@dataclass
class CapScores:
    tripod_occlusion_score: float
    missing_coverage_score: float
    flat_sky_score: float
    compression_blockiness_score: float

    def as_dict(self) -> dict:
        return asdict(self)


def _cap_slice(height: int, lat_lo: float, lat_hi: float, pole: str) -> slice:
    """Equirectangular row slice for a latitude band, pole in {'north','south'}."""
    # row 0 = +90 (north pole), row height-1 = -90 (south pole), equirect convention
    # (confirmed against geometry/spherical.py:erp_lonlat_grid / latitude_map)
    top_frac = (90.0 - lat_hi) / 180.0
    bot_frac = (90.0 - lat_lo) / 180.0
    r0, r1 = int(round(top_frac * height)), int(round(bot_frac * height))
    if pole == "south":
        r0, r1 = height - r1, height - r0
    return slice(max(r0, 0), min(r1, height))


def _tripod_occlusion(disp_cap: np.ndarray, valid_cap: np.ndarray) -> float:
    """Flags a COMPACT, CONNECTED blob of flat+near pixels touching the bottom
    frame edge -- the actual signature of a tripod head intruding into frame,
    as opposed to an ordinary flat-ish nearby surface (floor, wall, table top)
    which is locally flat but spatially diffuse, not a single near-edge blob.
    A naive area-fraction-only version of this check false-positives heavily
    on smooth indoor geometry (see module docstring); requiring connectedness
    and bottom-edge contact removes that failure mode.
    """
    d = disp_cap[valid_cap]
    if d.size < 64:
        return 0.0
    lo, hi = np.percentile(d, [1, 99])
    rng = max(hi - lo, 1e-8)
    near_thr = hi - TRIPOD_NEAR_DEPTH_FRAC * rng
    # local variance via small-window std on the full cap (cheap box filter)
    k = 9
    pad = k // 2
    padded = np.pad(disp_cap, pad, mode="edge")
    win_std = np.zeros_like(disp_cap, dtype=np.float64)
    for dy in range(k):
        for dx in range(k):
            win_std += (padded[dy:dy + disp_cap.shape[0], dx:dx + disp_cap.shape[1]] - disp_cap) ** 2
    win_std = np.sqrt(win_std / (k * k))
    flat_thr = np.percentile(win_std[valid_cap], TRIPOD_VARIANCE_PCTL)
    near_mask = disp_cap >= near_thr
    flat_near = (win_std <= flat_thr) & valid_cap & near_mask
    total_flagged = int(flat_near.sum())
    if total_flagged == 0:
        return 0.0
    labels, n = ndimage.label(flat_near)
    if n == 0:
        return 0.0
    sizes = ndimage.sum(flat_near, labels, index=range(1, n + 1))
    largest_idx = int(np.argmax(sizes)) + 1
    largest_size = float(sizes[largest_idx - 1])
    compactness = largest_size / total_flagged
    if compactness < TRIPOD_MIN_COMPACTNESS:
        return 0.0  # flat+near pixels are scattered -> ordinary geometry, not a blob
    if TRIPOD_TOUCHES_EDGE:
        bottom_row = labels[-1, :]
        if not np.any(bottom_row == largest_idx):
            return 0.0  # a real tripod enters from the bottom frame edge
    frac = largest_size / float(valid_cap.sum())
    return min(frac / TRIPOD_AREA_FRAC, 1.0)


def _missing_coverage(valid_cap: np.ndarray) -> float:
    frac_invalid = 1.0 - float(valid_cap.mean())
    return min(frac_invalid / MISSING_COVERAGE_FRAC, 1.0)


def _flat_sky(rgb_cap: np.ndarray, disp_cap: np.ndarray, valid_cap: np.ndarray,
              disp_gradient_ref: float) -> float:
    if valid_cap.sum() < 64:
        return 0.0
    gy, gx = np.gradient(disp_cap.astype(np.float64))
    grad_mag = np.sqrt(gy ** 2 + gx ** 2)[valid_cap]
    cap_grad = float(np.mean(grad_mag))
    low_gradient = cap_grad <= max(disp_gradient_ref, 1e-8) * (FLAT_SKY_GRADIENT_PCTL / 100.0)
    rgb_std = float(np.std(rgb_cap[valid_cap]))
    low_texture = rgb_std <= FLAT_SKY_TEXTURE_STD
    if low_gradient and low_texture:
        return 1.0
    if low_gradient or low_texture:
        return 0.5
    return 0.0


def _compression_blockiness(rgb_cap: np.ndarray) -> float:
    if rgb_cap.ndim == 3:
        gray = rgb_cap.mean(axis=-1)
    else:
        gray = rgb_cap
    if min(gray.shape) < 16:
        return 0.0
    dy = np.abs(np.diff(gray, axis=0))
    dx = np.abs(np.diff(gray, axis=1))
    rows = np.arange(dy.shape[0])
    cols = np.arange(dx.shape[1])
    on_block_edge_y = (rows % 8 == 7)
    on_block_edge_x = (cols % 8 == 7)
    edge_energy = float(dy[on_block_edge_y].mean()) + float(dx[:, on_block_edge_x].mean())
    interior_energy = float(dy[~on_block_edge_y].mean()) + float(dx[:, ~on_block_edge_x].mean())
    ratio = edge_energy / max(interior_energy, 1e-8)
    return float(np.clip((ratio - 1.0) / (BLOCKINESS_RATIO - 1.0), 0.0, 1.0))


def compute_cap_scores(rgb: np.ndarray, disparity: np.ndarray, valid: np.ndarray | None = None,
                       lat_lo: float = 75.0, lat_hi: float = 90.0) -> dict[str, "CapScores"]:
    """rgb: (H,W,3) float in [0,1]. disparity: (H,W) model-space disparity (higher = nearer).
    valid: optional (H,W) bool mask of pixels with real captured content.
    Returns {'north': CapScores, 'south': CapScores}.
    """
    h, w = disparity.shape[:2]
    if valid is None:
        valid = np.isfinite(disparity)
    gy, gx = np.gradient(disparity.astype(np.float64))
    whole_grad_ref = float(np.mean(np.sqrt(gy[valid] ** 2 + gx[valid] ** 2))) if valid.any() else 1.0

    out = {}
    for pole in ("north", "south"):
        sl = _cap_slice(h, lat_lo, lat_hi, pole)
        rgb_cap, disp_cap, valid_cap = rgb[sl], disparity[sl], valid[sl]
        out[pole] = CapScores(
            tripod_occlusion_score=_tripod_occlusion(disp_cap, valid_cap) if pole == "south" else 0.0,
            missing_coverage_score=_missing_coverage(valid_cap),
            flat_sky_score=_flat_sky(rgb_cap, disp_cap, valid_cap, whole_grad_ref),
            compression_blockiness_score=_compression_blockiness(rgb_cap),
        )
    return out


def should_correct(scores: "CapScores") -> bool:
    """Decide whether a tangent-plane / rotation-ensemble correction should be
    applied to this cap. Correction is skipped when there is nothing real to
    correct (flat_sky, missing_coverage) and when it would correct the wrong
    thing (tripod_occlusion -- that needs inpainting/masking, not a tangent
    realignment). Compression alone does not block correction, but is logged
    since it predicts correction will be noisier (route to wider-FOV patches
    per experiment 05's finding, not to skip entirely).
    """
    s = scores
    if s.flat_sky_score >= 0.5:
        return False
    if s.missing_coverage_score >= 1.0:
        return False
    if s.tripod_occlusion_score >= 1.0:
        return False
    return True


def calibrate_thresholds(calibration_records: list[dict]) -> dict:
    """Placeholder for the calibration step referenced in the README: given a
    small held-out slice of (cap_scores, baseline_absrel, corrected_absrel)
    records, sweep the module-level thresholds and report which setting
    maximizes agreement between should_correct() and the sign of the actual
    gain. Left unimplemented here -- wire up once run_gate_eval.py has
    produced a first batch of scored, evaluated scenes to calibrate against.
    """
    raise NotImplementedError(
        "Calibrate thresholds against a first run_gate_eval.py pass before trusting "
        "should_correct() on held-out data; see README.md 'What would make this a real result'."
    )
