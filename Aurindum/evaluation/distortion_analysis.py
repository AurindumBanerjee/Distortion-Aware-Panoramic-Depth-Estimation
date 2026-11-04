"""Part A of the round-3 checklist: how ERP distortion affects a depth model as a function of latitude.

Two measurements, both model-agnostic (only `model.predict` is called):

1. Latitude profile (descriptive, A1): plain ERP prediction, aligned to GT with a protocol, AbsRel per |latitude|
   bin. Mixes distortion, content (the caps are mostly floor / ceiling) and the alignment protocol.

2. Distortion sweep (causal, A2): the panorama is rotated by pitch theta, predicted, and the prediction rotated back,
   for several theta. Every ORIGINAL pixel is then predicted while being seen at several different latitudes, with its
   content unchanged. Per pixel, the error when seen at latitude L is compared with the error of the SAME pixel when
   seen closest to the equator:
       dE(L) = mean over pixels seen at L of [ e(pixel, L) - e(pixel, L_min(pixel)) ]
   which isolates the effect of distortion from the effect of content. With pitches -90..90 in 30 deg steps every
   pixel is seen below 15 deg latitude in at least one pass (rotation about the x axis moves the (y, z) angle of a
   direction in 30 deg steps, so one pass is within 15 deg of the equator).

   Two error estimators per pass:
     'global' : the pass is aligned to GT once over all common pixels (as the benchmark does)
     'local'  : the pass is aligned to GT separately inside each seen-latitude bin (oracle): only the SHAPE error
                remains, the alignment protocol is taken out of the curve
   Use 'global' for decisions (onset, gate, weights). 'local' is a sensitivity estimator only: re-fitting the alignment
   per bin lets the CONTENT mix of each bin leak into dE (on a synthetic model whose error depends only on content,
   'global' correctly finds no distortion effect while 'local' reports a spurious onset).
   A resampling floor (GT rotated there and back, i.e. a perfect model) is reported per bin, because rotating
   images and predictions costs interpolation error near depth edges that must not be read as distortion.

Conventions: rotate_erp gives I_rot(d) = I(R d); an original pixel with direction o is seen in the rotated frame at
R^T o (geometry.erp_projection.rotated_latitude), and the prediction is brought back with rotate_erp(pred, R^T).
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional, Sequence

import numpy as np

from evaluation.protocol import align_to_gt, group_of, model_space
from geometry.erp_projection import rotate_erp, rotated_latitude
from geometry.spherical import latitude_map, rotation_from_ypr

DEFAULT_PITCHES = (-90.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0)
REF_MAX_LAT = 15.0


# ----------------------------------------------------------------------------------------------------------------
# Calibration / evaluation split (by cluster, deterministic, order independent)
# ----------------------------------------------------------------------------------------------------------------

def split_of(scene_id: str) -> str:
    """'calib' or 'eval' for a scene, decided by a hash of its CLUSTER (house / environment / scene), so that all frames
    of one house land on the same side and the assignment never depends on list order or subset size."""
    g = group_of(scene_id)
    return "calib" if int(hashlib.md5(g.encode("utf-8")).hexdigest(), 16) % 2 == 0 else "eval"


def in_split(scene_id: str, part: Optional[str]) -> bool:
    return part in (None, "", "all") or split_of(scene_id) == part


# ----------------------------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------------------------

def bin_edges(bin_deg: float) -> np.ndarray:
    return np.arange(0.0, 90.0 + 1e-9, bin_deg)


def _bin_index(lat_abs: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.clip(np.digitize(lat_abs, edges) - 1, 0, len(edges) - 2)


def _abs_rel(pred: np.ndarray, gt: np.ndarray) -> np.ndarray:
    return np.abs(pred - gt) / gt


def _align_local(pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, model, min_depth: float, max_depth: float
                 ) -> np.ndarray:
    """Alignment fitted on `mask` only (affine for disparity models, median scale for depth models)."""
    space, scale = model_space(model)
    if not (space == "depth" and scale == "metric") and mask.sum() >= 50:
        return align_to_gt(pred, gt, mask, model, protocol="align-all", min_depth=min_depth, max_depth=max_depth)
    if space == "depth" and mask.sum() >= 50:  # metric model: a local median scale (the 'none' protocol has no fit)
        ok = mask & np.isfinite(pred) & (pred > 0)
        s = np.median(gt[ok]) / np.median(pred[ok]) if ok.sum() >= 50 else 1.0
        return np.clip(np.where(np.isfinite(pred), pred * s, max_depth), min_depth, max_depth)
    return np.full_like(gt, np.nan)


def headline_protocol(model) -> str:
    space, scale = model_space(model)
    return "none" if (space == "depth" and scale == "metric") else "align-all"


# ----------------------------------------------------------------------------------------------------------------
# A1: latitude profile of the plain ERP prediction
# ----------------------------------------------------------------------------------------------------------------

def frame_profile(pred: np.ndarray, gt: np.ndarray, valid: np.ndarray, model, protocols: Sequence[str],
                  bin_deg: float = 2.5, min_depth: float = 0.1, max_depth: float = 10.0) -> Dict[str, Dict]:
    """{protocol: {'mean': [n_bins] mean AbsRel per |lat| bin (NaN if empty), 'n': [n_bins]}} for one frame."""
    H, W = gt.shape
    edges = bin_edges(bin_deg)
    idx = _bin_index(np.abs(latitude_map(H, W)), edges)
    nb = len(edges) - 1
    out = {}
    for proto in protocols:
        al = align_to_gt(pred, gt, valid, model, protocol=proto, min_depth=min_depth, max_depth=max_depth)
        m = valid & np.isfinite(al) & (gt > 0)
        e = _abs_rel(al[m], gt[m])
        s = np.bincount(idx[m], weights=e, minlength=nb)
        c = np.bincount(idx[m], minlength=nb).astype(float)
        out[proto] = {"mean": np.where(c > 0, s / np.maximum(c, 1), np.nan).tolist(), "n": c.tolist()}
    return out


# ----------------------------------------------------------------------------------------------------------------
# A2: distortion sweep for one frame
# ----------------------------------------------------------------------------------------------------------------

def sweep_frame(model, rgb: np.ndarray, gt: np.ndarray, valid: np.ndarray,
                pitches: Sequence[float] = DEFAULT_PITCHES, bin_deg: float = 5.0,
                min_depth: float = 0.1, max_depth: float = 10.0, identity_pred: Optional[np.ndarray] = None,
                planar_mask: Optional[np.ndarray] = None) -> Dict:
    """Per seen-latitude bin statistics of one frame (see module docstring).

    Returns None if fewer than 500 pixels are valid in every pass, else a dict of per-bin lists (n_bins = 90 / bin_deg):
      n                     pixel-pass samples in the bin
      e_global, e_local     mean AbsRel of the samples (global / local alignment)
      de_global, de_local   mean content-paired excess error dE (same pixels, vs their lowest-latitude pass)
      ref_global, ref_local mean reference error of the same samples (denominator of the error ratio)
      floor                 mean AbsRel of the GT round trip (resampling floor), same samples
      and, if planar_mask is given, de_global_planar / de_global_nonplanar / n_planar / n_nonplanar (content split, A4)
    """
    H, W = gt.shape
    edges = bin_edges(bin_deg)
    nb = len(edges) - 1
    preds, seens, floors = [], [], []
    gt_f = np.where(valid, gt, np.nan).astype(np.float64)
    for th in pitches:
        if abs(th) < 1e-9:
            p = identity_pred if identity_pred is not None else model.predict(rgb, kind="erp")
            preds.append(np.asarray(p, dtype=np.float64))
            seens.append(np.abs(latitude_map(H, W)))
            floors.append(gt_f.copy())
            continue
        R = rotation_from_ypr(pitch_deg=th)
        rgb_rot = np.clip(np.rint(np.asarray(rotate_erp(rgb.astype(np.float32), R))), 0, 255).astype(np.uint8)
        p_rot = np.asarray(model.predict(rgb_rot, kind="erp"), dtype=np.float64)
        preds.append(np.asarray(rotate_erp(p_rot, R.T), dtype=np.float64))
        seens.append(np.abs(rotated_latitude(H, W, R)))
        # perfect model: GT carried into the rotated frame and back (two bilinear resamplings, as for the prediction:
        # one on the input image, one on the output)
        g_rot = np.asarray(rotate_erp(gt_f, R), dtype=np.float64)
        floors.append(np.asarray(rotate_erp(g_rot, R.T), dtype=np.float64))

    # common pixel set: valid GT and a finite, positive prediction in EVERY pass (same content in every bin)
    common = valid & (gt > 0)
    for p in preds:
        common &= np.isfinite(p) & (p > 0)
    K = len(pitches)
    res = {k: np.zeros(nb) for k in ("n", "e_global", "e_local", "de_global", "de_local", "ref_global", "ref_local",
                                     "floor", "n_floor")}
    if planar_mask is not None:
        for k in ("de_global_planar", "de_global_nonplanar", "n_planar", "n_nonplanar"):
            res[k] = np.zeros(nb)
    if common.sum() < 500:
        return None  # too few pixels valid in every pass: the caller skips this frame

    E_g = np.full((K, int(common.sum())), np.nan)
    E_l = np.full_like(E_g, np.nan)
    L = np.zeros_like(E_g)
    F = np.full_like(E_g, np.nan)
    g_c = gt[common]
    for k, (p, s, fl) in enumerate(zip(preds, seens, floors)):
        a_g = align_to_gt(p, gt, common, model, protocol=("align-all" if headline_protocol(model) == "align-all" else "none"),
                          min_depth=min_depth, max_depth=max_depth)
        E_g[k] = _abs_rel(a_g[common], g_c)
        bi = _bin_index(s, edges)
        a_l = np.full_like(gt, np.nan, dtype=np.float64)
        for b in range(nb):
            mb = common & (bi == b)
            if mb.sum() >= 200:
                al = _align_local(p, gt, mb, model, min_depth, max_depth)
                a_l[mb] = al[mb]
        E_l[k] = _abs_rel(a_l[common], g_c)
        L[k] = s[common]
        F[k] = _abs_rel(np.clip(fl[common], min_depth, max_depth), g_c)
    ref_k = np.argmin(L, axis=0)  # pass in which each pixel is seen closest to the equator
    cols = np.arange(L.shape[1])
    ref_g, ref_l = E_g[ref_k, cols], E_l[ref_k, cols]
    planar_c = planar_mask[common] if planar_mask is not None else None
    for k in range(K):
        bi = _bin_index(L[k], edges)
        for name, E, ref in (("global", E_g[k], ref_g), ("local", E_l[k], ref_l)):
            ok = np.isfinite(E) & np.isfinite(ref)
            res[f"e_{name}"] += np.bincount(bi[ok], weights=E[ok], minlength=nb)
            res[f"de_{name}"] += np.bincount(bi[ok], weights=(E - ref)[ok], minlength=nb)
            res[f"ref_{name}"] += np.bincount(bi[ok], weights=ref[ok], minlength=nb)
            if name == "global":
                res["n"] += np.bincount(bi[ok], minlength=nb)
                if planar_c is not None:
                    for lab, sel in (("planar", planar_c), ("nonplanar", ~planar_c)):
                        o2 = ok & sel
                        res[f"de_global_{lab}"] += np.bincount(bi[o2], weights=(E - ref)[o2], minlength=nb)
                        res[f"n_{lab}"] += np.bincount(bi[o2], minlength=nb)
        okf = np.isfinite(F[k])
        res["floor"] += np.bincount(bi[okf], weights=F[k][okf], minlength=nb)
        res["n_floor"] += np.bincount(bi[okf], minlength=nb)
    # note: e_local / de_local use the same count as global up to bins with < 200 pixels in a pass (then NaN, skipped);
    # keep a separate count for them
    n_loc = np.zeros(nb)
    for k in range(K):
        bi = _bin_index(L[k], edges)
        ok = np.isfinite(E_l[k]) & np.isfinite(ref_l)
        n_loc += np.bincount(bi[ok], minlength=nb)
    out = {"n": res["n"].tolist(), "n_local": n_loc.tolist(), "n_floor": res["n_floor"].tolist()}
    for k in ("e_global", "de_global", "ref_global"):
        out[k] = np.where(res["n"] > 0, res[k] / np.maximum(res["n"], 1), np.nan).tolist()
    for k in ("e_local", "de_local", "ref_local"):
        out[k] = np.where(n_loc > 0, res[k] / np.maximum(n_loc, 1), np.nan).tolist()
    out["floor"] = np.where(res["n_floor"] > 0, res["floor"] / np.maximum(res["n_floor"], 1), np.nan).tolist()
    if planar_c is not None:
        for lab in ("planar", "nonplanar"):
            n = res[f"n_{lab}"]
            out[f"n_{lab}"] = n.tolist()
            out[f"de_global_{lab}"] = np.where(n > 0, res[f"de_global_{lab}"] / np.maximum(n, 1), np.nan).tolist()
    return out


# ----------------------------------------------------------------------------------------------------------------
# aggregation over frames: cluster-robust mean curve, CI and onset
# ----------------------------------------------------------------------------------------------------------------

def cluster_curve(values: np.ndarray, groups: Sequence[str], n_boot: int = 2000, seed: int = 0) -> Dict:
    """values: (n_frames, n_bins) with NaN for empty bins. Frames are averaged within clusters first, then the mean
    over clusters is bootstrapped over clusters. Returns mean, ci_lo, ci_hi, n_clusters per bin."""
    v = np.asarray(values, dtype=float)
    g = np.array([str(x) for x in groups])
    uniq = sorted(set(g))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        C = np.stack([np.nanmean(v[g == u], axis=0) if np.isfinite(v[g == u]).any() else np.full(v.shape[1], np.nan)
                      for u in uniq])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(uniq), (n_boot, len(uniq)))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mean = np.nanmean(C, axis=0)
        boots = np.nanmean(C[idx], axis=1)
        lo, hi = np.nanpercentile(boots, 2.5, axis=0), np.nanpercentile(boots, 97.5, axis=0)
    ncl = np.isfinite(C).sum(0)
    return {"mean": mean.tolist(), "ci_lo": lo.tolist(), "ci_hi": hi.tolist(), "n_clusters": ncl.tolist()}


def onset_from_curve(centres: Sequence[float], ci_lo: Sequence[float], ref: Optional[Sequence[float]] = None,
                     rel_min: float = 0.10, min_lat: float = REF_MAX_LAT,
                     min_clusters: Optional[Sequence[int]] = None, need: int = 2) -> Optional[float]:
    """Lower edge of the first bin (centre >= min_lat) such that this and the next need-1 bins all have a cluster-CI
    lower bound of the excess error dE above rel_min * ref (the same samples' error when seen near the equator), i.e. a
    practically relevant AND significant distortion effect. None if there is no such run.

    rel_min matters: rotating images and predictions costs a little interpolation error everywhere, which is
    'significant' with enough pixels but is not a distortion effect a correction should act on (validated on a
    content-only synthetic model, tests/test_distortion_analysis.py)."""
    c = np.asarray(centres, float)
    lo = np.asarray(ci_lo, float)
    thr = rel_min * np.asarray(ref, float) if ref is not None else np.zeros_like(lo)
    ok = np.isfinite(lo) & np.isfinite(thr) & (lo > thr)
    if min_clusters is not None:
        ok &= np.asarray(min_clusters) >= 3
    half = (c[1] - c[0]) / 2.0 if len(c) > 1 else 0.0
    for j in range(len(c)):
        if c[j] < min_lat:
            continue
        if j + need <= len(c) and ok[j:j + need].all():
            return float(c[j] - half)
    return None


def summarize_sweep(frames: List[Dict], ids: Sequence[str], bin_deg: float, n_boot: int = 2000,
                    rel_min: float = 0.10) -> Dict:
    """Aggregate sweep_frame outputs into curves with cluster CIs, onset latitudes and the error-ratio curve."""
    groups = [group_of(i) for i in ids]
    edges = bin_edges(bin_deg)
    centres = (0.5 * (edges[:-1] + edges[1:])).tolist()
    out = {"centres": centres, "bin_deg": bin_deg, "n_frames": len(frames), "n_clusters": len(set(groups)),
           "rel_min": rel_min}
    keys = [k for k in ("e_global", "e_local", "de_global", "de_local", "floor", "ref_global", "ref_local",
                        "de_global_planar", "de_global_nonplanar") if k in frames[0]]
    for k in keys:
        out[k] = cluster_curve(np.array([f[k] for f in frames], float), groups, n_boot=n_boot)
    for est in ("global", "local"):
        cur = out[f"de_{est}"]
        out[f"onset_{est}"] = onset_from_curve(centres, cur["ci_lo"], ref=out[f"ref_{est}"]["mean"], rel_min=rel_min,
                                               min_clusters=cur["n_clusters"])
        # error ratio rho(L) = E(L) / E_ref of the same samples (>= 1 means worse than when seen at the equator)
        e, r = np.array(out[f"e_{est}"]["mean"]), np.array(out[f"ref_{est}"]["mean"])
        with np.errstate(invalid="ignore", divide="ignore"):
            out[f"ratio_{est}"] = np.where(r > 0, e / r, np.nan).tolist()
    return out


# ----------------------------------------------------------------------------------------------------------------
# Part B: using a measured curve at inference time
# ----------------------------------------------------------------------------------------------------------------

def load_curve(path: str, estimator: str = "global") -> Dict:
    """{'centres', 'ratio', 'onset'} from a sweep summary JSON (results/sweep_<model>_<dataset>_<split>.json)."""
    with open(path) as f:
        s = json.load(f)
    s = s.get("summary", s)
    return {"centres": s["centres"], "ratio": s[f"ratio_{estimator}"], "onset": s[f"onset_{estimator}"],
            "source": path, "estimator": estimator}


def curve_ratio(curve: Dict, lat_seen_abs: np.ndarray) -> np.ndarray:
    """Expected error ratio rho(L) at each pixel's seen latitude (linear interpolation, >= 1, NaN bins filled)."""
    c = np.asarray(curve["centres"], float)
    r = np.asarray(curve["ratio"], float)
    ok = np.isfinite(r)
    if not ok.any():
        return np.ones_like(lat_seen_abs, dtype=float)
    r = np.interp(c, c[ok], r[ok])
    return np.maximum(np.interp(lat_seen_abs, c, r), 1.0)


def curve_gate_range(curve: Dict, width: float = 15.0) -> Optional[tuple]:
    """(lo, hi) of the correction ramp derived from the measured onset, or None if the model shows no distortion
    effect (then no correction may be applied)."""
    if curve.get("onset") is None:
        return None
    lo = float(curve["onset"])
    return lo, min(lo + width, 89.0)
