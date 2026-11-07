"""Capture-aware correction: one inference-time front end for ANY panoramic depth model (model.predict(rgb, kind="erp")).

Given a panorama and whatever capture metadata is available, it decides which fixes to run and runs them:

  fault                         cue                                     candidate fixes (distortions/catalogue.py)
  ----------------------------  --------------------------------------  ------------------------------------------
  camera tilt                   gravity rotation from the IMU (meta)    re-level before inference
  missing caps (tripod / logo,  detected from the image (constant       ERP inpaint, tangent inpaint, plane fill
  limited vertical FOV)         polar rows) or a mask in meta
  camera shake                  yaw kernel from the gyro (meta)         Wiener deconvolution
  exposure seam, vignetting,    flagged in meta                         gain match, flat-field, seam inpaint,
  parallax, noise, JPEG                                                  denoise, bilateral

Which fix (or none) is used for a fault is NOT hand-picked per model: it comes from a policy learned on held-out data
by scripts/calibrate_correction.py (leave-one-dataset-out), which keeps "none" unless a fix beats it. A fix that hurts
a model (e.g. inpainting for DA360) is therefore switched off for that model automatically.

The model is frozen and only called through predict(); the output is always the depth for the INPUT image's grid.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from distortions.catalogue import MITIGATIONS, occlusion_mask

# faults whose cue has to come from metadata (they cannot be detected reliably from the image alone)
META_FAULTS = ("tilt", "yawblur", "seam", "parallax", "vignette", "noise", "jpeg")
CAP_FAULTS = ("nadir", "vfov")
# fallback policy when no calibration file exists: only the fixes that were positive for every model in the study
DEFAULT_POLICY = {"tilt": "relevel_known", "yawblur": "wiener"}


@dataclass
class CaptureMeta:
    """What the capture device or pipeline may know. All fields optional.

    R:       3x3 rotation such that the captured image is I_level(R d) (the catalogue's convention); an IMU gives it.
    kernel:  1D yaw-shake kernel along a row (length W), from the gyro.
    flags:   other known faults, e.g. {"jpeg", "noise", "seam"} (from file metadata / ISO / camera model).
    caps:    {"nadir_from": deg, "zenith_from": deg} if the occluded caps are known; otherwise detected."""
    R: Optional[np.ndarray] = None
    kernel: Optional[np.ndarray] = None
    flags: set = field(default_factory=set)
    caps: Optional[Dict[str, Optional[float]]] = None


def detect_caps(rgb: np.ndarray, tols: Tuple[float, ...] = (3.0, 14.0), min_deg: float = 10.0, band_deg: float = 2.8,
                share: float = 0.9, edge_pct: float = 95.0, wobble_deg: float = 2.0) -> Dict[str, Optional[float]]:
    """Find occluded polar caps: a region around a pole filled with one colour (a tripod / logo patch, or the black band
    of a limited-FOV capture) whose edge is a circle of constant latitude.

    For every column, L_j = number of pixels from the pole that stay within `tol` grey levels (every channel) of the
    pole colour, for a tight (3: an uncompressed patch; a dark patch next to a dark floor still separates) and a loose
    tolerance (14: JPEG quality 8 moves flat pixels by up to ~10 levels). A cap is accepted if
      (a) the median run spans at least min_deg of latitude: rendered panoramas have 1-2 flat rows at the pole (one 3D
          point stretched over the row), real patches and band captures span 15-40 deg; and
      (b) its edge is a constant latitude: at least `share` of the columns end within `band_deg` degrees of the median
          (an ANGLE, not rows: the real Stanford2D3D caps wobble by 2.8 deg between columns at every resolution, which
          a 4-row band passed at 256 x 512 and failed at 512 x 1024).
    (b) is what separates a pasted patch from a real uniform ceiling or floor: Structured3D renders noiseless white
    ceilings that are flat over 25 deg, but a room's ceiling edge in ERP is a wave (the walls), not a circle.

    Returns {"nadir_from": a, "zenith_from": b} in the convention of catalogue.occlusion_mask (cap = |lat| > value),
    None for a pole without a cap; the edge is the `edge_pct` percentile of the per-column run lengths, so that
    the mask covers the black pixels of (almost) every column instead of leaving a black ring where the edge wobbles. A cap whose colour matches the
    scene right outside it is missed (prediction then runs uncorrected); sensor noise ON the patch also defeats it,
    but patches are added after capture, so in practice only compression touches them."""
    H = rgb.shape[0]
    x = rgb.astype(np.int16)
    deg = 180.0 / H
    min_rows = max(2, int(np.ceil(min_deg / deg)))
    band_rows = max(2, int(np.ceil(band_deg / deg)))

    def run(block, tol):  # block: (rows from the pole outwards, W, 3)
        c = np.median(block[0], axis=0)
        near = np.abs(block - c).max(axis=-1) <= tol                     # (rows, W)
        L = np.where(near.all(axis=0), near.shape[0], np.argmin(near, axis=0))  # first non-matching row per column
        med = int(np.median(L))
        if med < min_rows or med >= H // 2:
            return 0
        if np.mean(np.abs(L - med) <= band_rows) < share:
            return 0
        # cover the wobbling edge (Stanford: p95 - median ~ 1.4 deg) but never extend further than `wobble_deg` past the
        # median: a loose tolerance can run on into a dark floor in a few columns
        return int(min(np.ceil(np.percentile(L, edge_pct)), med + np.ceil(wobble_deg / deg)))

    # every tolerance that yields a constant-latitude edge is a valid reading; the largest is used (JPEG ringing makes
    # the tight one stop a few rows short, while a loose one that runs into a same-coloured floor fails test (b))
    best = lambda blk: max(run(blk, t) for t in tols)
    k_top = best(x[: H // 2])
    k_bot = best(x[::-1][: H // 2])
    return {"zenith_from": 90.0 - k_top * deg if k_top else None,
            "nadir_from": 90.0 - k_bot * deg if k_bot else None}


JPEG_EDGE_MARGIN_DEG = 1.5


def grow_caps(caps: Dict[str, Optional[float]], deg: float) -> Dict[str, Optional[float]]:
    """Enlarge detected caps by `deg` toward the equator (cap = |lat| > value, so the value goes down)."""
    return {k: (None if v is None else max(float(v) - deg, 0.0)) for k, v in caps.items()}


def cap_fault(caps: Dict[str, Optional[float]]) -> Optional[str]:
    """Which policy entry applies: both caps missing -> 'vfov' (band capture), only the bottom -> 'nadir'."""
    if caps.get("nadir_from") is not None and caps.get("zenith_from") is not None:
        return "vfov"
    if caps.get("nadir_from") is not None:
        return "nadir"
    if caps.get("zenith_from") is not None:
        return "vfov"  # a top-only cap behaves like the band case (nothing above), closest calibrated fault
    return None


def load_policy(path: Optional[str], model_key: Optional[str]) -> Dict[str, str]:
    """Policy for one model from results/correction_policy.json ({model_key: {fault: fix}}); the default otherwise."""
    if path and Path(path).is_file() and model_key:
        allp = json.loads(Path(path).read_text())
        if model_key in allp:
            return dict(allp[model_key])
    return dict(DEFAULT_POLICY)


def correct(model, rgb: np.ndarray, meta: Optional[CaptureMeta] = None, policy: Optional[Dict[str, str]] = None,
            detect: bool = True, order: str = "photometric_first") -> Tuple[np.ndarray, List[str]]:
    """Depth for `rgb` (on its own grid) with the capture-aware fixes the policy allows. Returns (prediction, log).

    Order: a known tilt is handled first and alone (re-levelling rotates the caps away from the poles, so the cap
    fixes, which assume polar caps in the capture frame, are not combined with it); then photometric fixes (one, the
    first flagged fault that has a fix in the policy); then missing caps. Each step only changes the image or the
    inference, never the model."""
    meta = meta or CaptureMeta()
    policy = DEFAULT_POLICY if policy is None else policy
    log: List[str] = []
    fix = lambda key: MITIGATIONS[key][1]

    if meta.R is not None and policy.get("tilt", "none") != "none":
        log.append(f"tilt: {policy['tilt']}")
        return fix(policy["tilt"])(model, rgb, {"R": np.asarray(meta.R, float)}), log

    ctx: Dict = {}
    img = rgb
    photometric = [(f, policy.get(f, "none")) for f in ("yawblur", "seam", "vignette", "noise", "jpeg", "parallax")
                   if (f in meta.flags or (f == "yawblur" and meta.kernel is not None))]
    photometric = [(f, k) for f, k in photometric if k != "none"]

    caps = meta.caps if meta.caps is not None else (detect_caps(rgb) if detect else {})
    if meta.caps is None and "jpeg" in meta.flags:
        caps = grow_caps(caps, JPEG_EDGE_MARGIN_DEG)   # block ringing shortens the detected run by 0.7-1.4 deg (Stanford, q8)
    cf = cap_fault(caps) if caps else None
    cap_fix = policy.get(cf, "none") if cf else "none"

    if photometric:
        f, k = photometric[0]
        if f == "yawblur":
            ctx["kernel"] = meta.kernel
        log.append(f"{f}: {k}")
        if cap_fix == "none":
            return fix(k)(model, img, ctx), log
        # a photometric fix and a cap fix both wanted: apply the photometric one to the IMAGE only (the catalogue fixes
        # end in a prediction, so the cleaned image is produced through a capturing model stub)
        if order == "cap_first" and cf is not None:
            # fill the caps BEFORE the smoothing, so that it never blurs the patch edge into the visible scene
            from distortions.catalogue import _inpaint_tangent
            img = _inpaint_tangent(img, occlusion_mask(img.shape[0], img.shape[1], caps))
        img = _image_after(k, img, ctx)

    if cf is not None:
        log.append(f"{cf} (caps {caps}): {cap_fix}")
        if cap_fix != "none":
            return fix(cap_fix)(model, img, dict(caps)), log
    return np.asarray(model.predict(img, kind="erp"), dtype=np.float64), log or ["no fault detected"]


class _Capture:
    """Model stub that records the image a catalogue fix would feed to the model."""
    name = "capture"

    def __init__(self, H, W):
        self.shape = (H, W)
        self.seen = None

    def predict(self, rgb, kind="erp"):
        self.seen = rgb
        return np.zeros(self.shape, np.float32)


def _image_after(key: str, rgb: np.ndarray, ctx: Dict) -> np.ndarray:
    stub = _Capture(*rgb.shape[:2])
    MITIGATIONS[key][1](stub, rgb, dict(ctx))
    return stub.seen if stub.seen is not None else rgb


def cap_mask(rgb_shape, caps) -> np.ndarray:
    return occlusion_mask(rgb_shape[0], rgb_shape[1], caps or {})
