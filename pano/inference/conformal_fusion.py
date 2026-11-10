"""Anchored Conformal Gradient Fusion (ACGF): inference-time polar correction in the gradient domain.

Three parts, each aimed at a failure of the value-domain tangent / rotation / hybrid methods
(see README section "ACGF"):

1. Conformal pole views. Each polar cap is seen by
     * a 180 deg *stereographic* view (geometry/stereographic.py). It is conformal, so the model
       sees the whole polar hemisphere with its surrounding walls (context), magnified at most
       2x and never sheared, with the camera looking straight up / down (gravity unchanged), and
     * a gnomonic (pinhole) view with a different in-plane orientation, whose errors are
       expected to be different (used by the gate).
   The stereographic magnification k = sec^2(alpha/2) is known in closed form; a learned model
   is assumed to see magnified content k times closer (Depth Any Camera's scaling law), which is
   undone per pixel ("law"; ablation `nolaw`).

2. Nuisance-free fusion in the gradient domain. Only finite differences of each view enter the
   solution, in the log of the model's fusion space (log range for depth models, log of
   baseline-space disparity for disparity models):
     * metric / scale depth models: d log(range) does not depend on the unknown scale, so views
       need NO alignment at all;
     * affine disparity models: differences cancel the additive constant, so per view only
       (A, B) in  d b ~ A d(m P) + B d(m)  are fitted, on anchor edges, by robust least squares
       (m = cos(off-axis) for pinhole views, 1/k for stereographic views).
   The fused log-depth u solves a screened Poisson problem on the sphere over the polar caps,

       min_u  sum_e omega_e c_e (du_e - t_e)^2  +  sum_p a_p lambda_p (u_p - u_base,p)^2,

   with the spherical metric (omega_e: edge weights of the Dirichlet energy on the ERP grid,
   a_p: pixel solid angle), Dirichlet boundary u = u_base at |lat| < threshold - band/2 (the
   equator is untouched by construction), a screening weight lambda_p that is strong near the
   boundary and weak inside the cap, and IRLS (Cauchy) re-weighting c_e of inconsistent edges.
   The output is exp(u): positive by construction.

3. A "do no harm" gate. Per pixel, from local (blurred) edge statistics:
       sigma_n^2 = 1/2 E[(dv - dv')^2]          view noise (two views of the same pole disagree)
       e_b^2     = max(E[(dv - db)^2] - sigma_n^2, 0)   baseline error not explained by view noise
       gamma     = e_b^2 / (e_b^2 + sigma_n^2 / n_views)
   gamma is the Wiener weight of the view consensus against the baseline: the target edge
   difference is t = gamma * mean_views + (1 - gamma) * d_base. If the views agree with each
   other but not with the baseline, the baseline is corrected; if they disagree with each other
   as much as with the baseline, the baseline is kept. Caveat: views of the same model can share
   errors, which makes sigma_n^2 an underestimate (the gate is then too permissive).

No ground truth is used anywhere.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from pano.geometry.erp_projection import rotate_erp, rotated_lonlat
from pano.geometry.spherical import latitude_map, rotation_from_ypr
from pano.geometry.stereographic import StereoView, erp_to_stereo, generate_stereo_view, stereo_to_erp
from pano.geometry.tangent_plane import TangentPlane, erp_to_tangent, generate_tangent_plane, tangent_to_erp
from pano.models.depth_model import DepthModelWrapper

from .alignment import robust_lstsq
from .fusion import latitude_weight

DEFAULT_VIEWS = (("stereo", 180.0, 0.0), ("gnomonic", 110.0, 45.0))


# ----------------------------------------------------------------------------
# Pole views
# ----------------------------------------------------------------------------

def pole_views(specs: Sequence[Sequence], size: int, poles=(1, -1)) -> List[Tuple[int, object]]:
    """(pole_sign, view) for every spec [kind, fov_deg, lon_deg] and pole. `lon` rotates the view
    about the polar axis (different pixel grid and image orientation, same centre)."""
    out = []
    for s in poles:
        for kind, fov, lon in specs:
            if kind == "stereo":
                out.append((s, generate_stereo_view(float(lon), s * 90.0, float(fov), size)))
            elif kind == "gnomonic":
                out.append((s, generate_tangent_plane(float(lon), s * 90.0, float(fov), size)))
            else:
                raise ValueError(f"unknown view kind {kind}")
    return out


@dataclass
class RotatedView:
    """A pitch-rotated ERP pass (rotation_inference), used as an extra ACGF view of one hemisphere."""
    ypr: Tuple[float, float, float]
    seam_width: float = 20.0

    def to_dict(self):
        return {"kind": "rotation", "ypr": list(self.ypr)}


def render_view(rgb: np.ndarray, view) -> np.ndarray:
    f = erp_to_stereo if isinstance(view, StereoView) else erp_to_tangent
    return np.clip(f(rgb.astype(np.float32), view, mode="bilinear") + 0.5, 0, 255).astype(np.uint8)


def predict_views_raw(model: DepthModelWrapper, rgb: np.ndarray, views: Sequence, batch_size: int = 4):
    """Model outputs on the rendered views (view pixel grid, model-native units)."""
    out: List[Optional[np.ndarray]] = [None] * len(views)
    by_size: Dict[int, List[int]] = {}
    for k, v in enumerate(views):
        by_size.setdefault(v.size, []).append(k)
    for _, idx in by_size.items():
        preds = model.predict_batch([render_view(rgb, views[k]) for k in idx], kind="perspective",
                                    batch_size=batch_size)
        for k, p in zip(idx, preds):
            out[k] = p
    return out


@dataclass
class ErpView:
    """One pole view on the ERP grid, converted to the work space u = log(fusion-space value)."""
    name: str
    pole: int
    u: np.ndarray  # (H, W), NaN where invalid
    valid: np.ndarray
    distortion: np.ndarray  # deg; prior = cos(distortion)^p (off-axis angle; alpha/2 for stereographic)
    info: Dict = field(default_factory=dict)


def _view_on_erp(raw: np.ndarray, view, H: int, W: int, perspective_geometry: str, law: bool):
    """Resample a view prediction onto the ERP. Returns (P, valid, m, distortion_deg, anchor_ok).

    m is the per-pixel multiplier that turns the model output into a quantity proportional to
    inverse range (disparity: q ~ m * (P - t)) or range (depth: r ~ P / m)."""
    mask = np.isfinite(raw)
    src = np.nan_to_num(raw, nan=0.0).astype(np.float64)
    if isinstance(view, RotatedView):  # ERP input: same semantics as the baseline, no multiplier
        R = rotation_from_ypr(*view.ypr)
        back, valid = rotate_erp(src, R.T, mode="bilinear", mask=mask)
        vlon, vlat = rotated_lonlat(H, W, R)
        valid = valid & (np.abs(vlon) < 180.0 - view.seam_width)  # drop the rotated panorama's seam
        return back, valid, np.ones((H, W)), np.abs(vlat), valid
    if isinstance(view, StereoView):
        r = stereo_to_erp(src, view, H, W, mode="bilinear", mask=mask)
        m = 1.0 / r.magnification if law else np.ones((H, W))
        return r.values, r.valid, m, r.alpha_deg / 2.0, r.valid
    r = tangent_to_erp(src, view, H, W, mode="bilinear", mask=mask)
    m = r.cos_axis if perspective_geometry == "planar" else np.ones((H, W))
    alpha = np.degrees(np.arccos(np.clip(r.cos_axis, 0, 1)))
    return r.values, r.valid, m, alpha, r.valid & (r.radial < 0.85)


# ----------------------------------------------------------------------------
# Edges on the ERP grid
# ----------------------------------------------------------------------------

def edge_diffs(u: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Horizontal (wrapping in longitude) and vertical finite differences: (H, W) and (H-1, W)."""
    return np.roll(u, -1, axis=1) - u, u[1:] - u[:-1]


def edge_valid(valid: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    return valid & np.roll(valid, -1, axis=1), valid[1:] & valid[:-1]


def edge_mean(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    return 0.5 * (x + np.roll(x, -1, axis=1)), 0.5 * (x[1:] + x[:-1])


def edges_to_pixels(eh: np.ndarray, ev: np.ndarray, mh: np.ndarray, mv: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Average of the edge values touching each pixel (only valid edges). Returns (sum, count)."""
    num = np.zeros(eh.shape)
    cnt = np.zeros(eh.shape)
    h = np.where(mh, eh, 0.0)
    num += h + np.roll(h, 1, axis=1)
    cnt += mh + np.roll(mh, 1, axis=1)
    v = np.where(mv, ev, 0.0)
    num[:-1] += v
    num[1:] += v
    cnt[:-1] += mv
    cnt[1:] += mv
    return num, cnt


def blur_wrap(x: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian blur with wrap-around in longitude and reflection at the poles."""
    if sigma <= 0:
        return x
    p = int(math.ceil(3 * sigma))
    xp = np.concatenate([x[:, -p:], x, x[:, :p]], axis=1).astype(np.float64)
    return cv2.GaussianBlur(xp, (0, 0), sigma, borderType=cv2.BORDER_REFLECT)[:, p:-p]


def sphere_edge_weights(H: int, W: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Dirichlet-energy edge weights and pixel solid angles of the ERP grid on the unit sphere.

    integral |grad u|^2 dA  ~  sum_h (dlat / (cos lat dlon)) du_h^2 + sum_v (cos lat_{i+1/2} dlon / dlat) du_v^2
    """
    dlat, dlon = math.pi / H, 2 * math.pi / W
    lat = np.radians(latitude_map(H, W)[:, :1])
    lat_half = (lat[1:] + lat[:-1]) / 2
    wh = np.broadcast_to(dlat / (np.cos(lat) * dlon), (H, W))
    wv = np.broadcast_to(np.cos(lat_half) * dlon / dlat, (H - 1, W))
    area = np.broadcast_to(np.cos(lat) * dlon * dlat, (H, W))
    return wh, wv, area


# ----------------------------------------------------------------------------
# Conversion of a view to the work space (the only place model semantics enter)
# ----------------------------------------------------------------------------

def _fit_on_edges(feats: List[np.ndarray], target: np.ndarray, anchor: np.ndarray, max_edges: int = 60000):
    """Robust LSQ  d target ~ sum_i coef_i d feat_i  over anchor edges (both endpoints anchors)."""
    th, tv = edge_diffs(target)
    ah, av = edge_valid(anchor)
    cols_h = [edge_diffs(f)[0][ah] for f in feats]
    cols_v = [edge_diffs(f)[1][av] for f in feats]
    A = np.stack([np.concatenate([h, v]) for h, v in zip(cols_h, cols_v)], -1)
    y = np.concatenate([th[ah], tv[av]])
    ok = np.isfinite(A).all(1) & np.isfinite(y)
    A, y = A[ok], y[ok]
    if len(y) > max_edges:  # deterministic subsample
        sel = np.linspace(0, len(y) - 1, max_edges).astype(int)
        A, y = A[sel], y[sel]
    if len(y) < 50:
        return None, len(y)
    coef, inl = robust_lstsq(A, y)
    return coef, len(y)


def convert_view(P, valid, m, anchor, base, space: str, scale: str, lo: float, hi: float) -> Tuple[np.ndarray, Dict]:
    """Model output P (on the ERP grid) -> X in the baseline's fusion space (up to what gradients ignore).

    depth, metric/scale : X = c * P / m         (c = median ratio on anchors; irrelevant for gradients)
    depth, affine       : X = A * P / m + C     (A fitted on anchor edges, C by median on anchors)
    disparity           : X = A * m P + B * m + C   (A, B on anchor edges; C by median on anchors)
    X outside the baseline's plausible range [lo, hi] is marked invalid (never clamped).
    """
    info: Dict = {"n_anchor": int(anchor.sum())}
    a = anchor & valid & np.isfinite(base)
    if space == "depth":
        F1 = np.where(valid, P / np.maximum(m, 1e-9), np.nan)
        if scale in ("metric", "scale"):
            r = np.log(base[a]) - np.log(np.clip(F1[a], 1e-12, None)) if a.sum() else np.array([0.0])
            c = float(np.exp(np.median(r)))
            X = c * F1
            info["coef"] = [c]
        else:
            coef, n = _fit_on_edges([F1], base, a)
            info["n_fit_edges"] = n
            if coef is None or coef[0] <= 0:
                info["rejected"] = "fit"
                return np.full_like(base, np.nan), info
            C = float(np.median(base[a] - coef[0] * F1[a]))
            X = coef[0] * F1 + C
            info["coef"] = [float(coef[0]), C]
    else:
        F1 = np.where(valid, m * P, np.nan)
        F2 = np.where(valid, m, np.nan)
        feats = [F1, F2] if np.nanstd(F2[a]) > 1e-4 else [F1]
        coef, n = _fit_on_edges(feats, base, a)
        info["n_fit_edges"] = n
        if coef is None or coef[0] <= 0:
            info["rejected"] = "fit"
            return np.full_like(base, np.nan), info
        B = float(coef[1]) if len(coef) > 1 else 0.0
        lin = coef[0] * F1 + B * F2
        C = float(np.median(base[a] - lin[a]))
        X = lin + C
        info["coef"] = [float(coef[0]), B, C]
    plausible = valid & np.isfinite(X) & (X > lo) & (X < hi)
    info["plausible_frac"] = float(plausible.sum() / max(valid.sum(), 1))
    return np.where(plausible, X, np.nan), info


# ----------------------------------------------------------------------------
# Gate
# ----------------------------------------------------------------------------

def consensus_gate(base_u: np.ndarray, views: List[ErpView], prior_power: float, sigma_px: float,
                   eps: float = 1e-12) -> Tuple[np.ndarray, Dict]:
    """Per-pixel Wiener weight gamma in [0, 1] of the view consensus against the baseline (module doc)."""
    H, W = base_u.shape
    bh, bv = edge_diffs(base_u)
    bmh, bmv = edge_valid(np.isfinite(base_u))
    dh, dv, mh, mv, wh, wv = [], [], [], [], [], []
    for v in views:
        h, vv = edge_diffs(v.u)
        eh, ev = edge_valid(v.valid)
        ph, pv = edge_mean(np.cos(np.radians(np.clip(v.distortion, 0, 90))) ** prior_power)
        dh.append(h); dv.append(vv); mh.append(eh); mv.append(ev); wh.append(np.where(eh, ph, 0)); wv.append(np.where(ev, pv, 0))
    # view vs baseline
    num_h = sum(w * np.where(m, (d - bh) ** 2, 0) for d, m, w in zip(dh, mh, wh))
    num_v = sum(w * np.where(m, (d - bv) ** 2, 0) for d, m, w in zip(dv, mv, wv))
    den_h, den_v = sum(wh), sum(wv)
    s, c = edges_to_pixels(np.where(bmh & (den_h > 0), num_h / np.maximum(den_h, 1e-12), 0),
                           np.where(bmv & (den_v > 0), num_v / np.maximum(den_v, 1e-12), 0),
                           bmh & (den_h > 0), bmv & (den_v > 0))
    e_vb = blur_wrap(s, sigma_px) / np.maximum(blur_wrap(c, sigma_px), 1e-9)
    # view vs view (pairs)
    pnum_h = np.zeros((H, W)); pden_h = np.zeros((H, W))
    pnum_v = np.zeros((H - 1, W)); pden_v = np.zeros((H - 1, W))
    for a in range(len(views)):
        for b in range(a + 1, len(views)):
            if not (views[a].valid & views[b].valid).any():  # disjoint views add exact zeros: skip (20 ico views)
                continue
            w = wh[a] * wh[b]
            pnum_h += w * np.where(mh[a] & mh[b], (dh[a] - dh[b]) ** 2, 0); pden_h += w
            w = wv[a] * wv[b]
            pnum_v += w * np.where(mv[a] & mv[b], (dv[a] - dv[b]) ** 2, 0); pden_v += w
    s, c = edges_to_pixels(np.where(pden_h > 0, pnum_h / np.maximum(pden_h, 1e-12), 0),
                           np.where(pden_v > 0, pnum_v / np.maximum(pden_v, 1e-12), 0), pden_h > 0, pden_v > 0)
    cb = blur_wrap(c, sigma_px)
    e_vv = blur_wrap(s, sigma_px) / np.maximum(cb, 1e-9)
    has_pairs = cb > 1e-3
    fallback = float(np.median(e_vv[has_pairs])) if has_pairs.any() else 0.0
    sig_n = 0.5 * np.where(has_pairs, e_vv, fallback)
    n_eff = blur_wrap(sum(v.valid.astype(float) for v in views), sigma_px)
    e_b = np.maximum(e_vb - sig_n, 0.0)
    gamma = e_b / (e_b + sig_n / np.maximum(n_eff, 1.0) + eps)
    gamma = np.where(n_eff > 0.5, np.clip(gamma, 0, 1), 0.0)
    return gamma, {"view_noise": sig_n, "baseline_excess": e_b, "n_eff": n_eff}


# ----------------------------------------------------------------------------
# Screened Poisson solve on the sphere
# ----------------------------------------------------------------------------

def screened_poisson(u0: np.ndarray, th: np.ndarray, tv: np.ndarray, mth: np.ndarray, mtv: np.ndarray,
                     unknown: np.ndarray, lam: np.ndarray, irls_iters: int = 1) -> Tuple[np.ndarray, Dict]:
    """min_u sum_e omega_e c_e (du_e - t_e)^2 + sum_p area_p lam_p (u_p - u0_p)^2 over `unknown` pixels;
    all other pixels are fixed to u0. Targets t (th: (H, W) horizontal, tv: (H-1, W) vertical) are used
    where mth / mtv. c_e: Cauchy IRLS weights (1 on the first solve)."""
    H, W = u0.shape
    wh, wv, area = sphere_edge_weights(H, W)
    idx = -np.ones((H, W), np.int64)
    n = int(unknown.sum())
    idx[unknown] = np.arange(n)
    fixed_ok = np.isfinite(u0)
    # edge list: (p, q, omega, target)
    P_h = np.arange(H * W).reshape(H, W)
    Q_h = np.roll(P_h, -1, axis=1)
    P_v, Q_v = P_h[:-1], P_h[1:]
    p = np.concatenate([P_h.ravel(), P_v.ravel()])
    q = np.concatenate([Q_h.ravel(), Q_v.ravel()])
    om = np.concatenate([np.ascontiguousarray(wh).ravel(), np.ascontiguousarray(wv).ravel()])
    t = np.concatenate([th.ravel(), tv.ravel()])
    mt = np.concatenate([mth.ravel(), mtv.ravel()])
    flat_unk = unknown.ravel()
    flat_fix = fixed_ok.ravel() & ~flat_unk
    u0f = u0.ravel()
    use = mt & np.isfinite(t) & (flat_unk[p] | flat_unk[q]) & (flat_unk[p] | flat_fix[p]) & (flat_unk[q] | flat_fix[q])
    p, q, om, t = p[use], q[use], om[use], t[use]
    ip, iq = idx.ravel()[p], idx.ravel()[q]
    # residual r_e = u_q - u_p - t_e = (D u)_e - b_e, with fixed endpoints moved into b
    m = len(p)
    rows = np.concatenate([np.arange(m)[iq >= 0], np.arange(m)[ip >= 0]])
    cols = np.concatenate([iq[iq >= 0], ip[ip >= 0]])
    vals = np.concatenate([np.ones((iq >= 0).sum()), -np.ones((ip >= 0).sum())])
    D = sp.csr_matrix((vals, (rows, cols)), shape=(m, n))
    b = t - np.where(iq < 0, u0f[q], 0.0) + np.where(ip < 0, u0f[p], 0.0)
    a_l = (np.ascontiguousarray(area).ravel() * np.ascontiguousarray(lam).ravel())[flat_unk]
    u0u = u0f[flat_unk]
    screen_ok = np.isfinite(u0u)
    a_l = np.where(screen_ok, a_l, 0.0)
    u0u = np.where(screen_ok, u0u, 0.0)
    c = np.ones(m)
    info: Dict = {"n_unknown": n, "n_edges": m}
    sol = u0u
    t0 = time.perf_counter()
    for it in range(irls_iters + 1):
        Wd = sp.diags(om * c)
        A = (D.T @ Wd @ D + sp.diags(a_l + 1e-12)).tocsc()
        rhs = D.T @ (om * c * b) + a_l * u0u
        sol = spla.spsolve(A, rhs, permc_spec="MMD_AT_PLUS_A")  # symmetric ordering: ~1.5x faster than COLAMD here
        if it < irls_iters:
            r = D @ sol - b
            mad = np.median(np.abs(r - np.median(r))) * 1.4826 + 1e-12
            c = 1.0 / (1.0 + (r / (2.5 * mad)) ** 2)
    info["solve_s"] = time.perf_counter() - t0
    out = u0.copy()
    out[unknown] = sol
    return out, info


# ----------------------------------------------------------------------------
# Main entry
# ----------------------------------------------------------------------------

@dataclass
class ACGFParams:
    lat_threshold: float = 45.0
    band: float = 20.0
    prior_power: float = 2.0
    domain: str = "gradient"  # gradient | value (ablation: value-domain blending of the same views)
    screen: str = "value"  # value | baseline: what the screening term pulls towards inside the cap
    gate: bool = True
    lambda_cap: float = 5.0  # rad^-2: pull towards the screening target inside the cap
    lambda_edge: float = 50.0  # rad^-2: extra pull near the cap boundary (fades with the latitude ramp)
    gate_sigma_deg: float = 3.0  # blur of the gate statistics, in degrees of latitude
    irls_iters: int = 1
    # v2 options (after the real-data diagnosis, RESULTS.md section 10):
    work: str = "log"  # log | linear | auto (auto = linear for disparity models, log for depth models)
    gate_mode: str = "edge"  # edge: gamma mixes view/baseline differences per edge | value: gamma blends solved values
    guard: Tuple[float, float] = (0.5, 2.0)  # plausible X range: [g0 * p1(base), g1 * p99(base)]
    # acgf|ico options (RESULTS.md section 12):
    scope: str = "polar"  # polar: solve the caps |lat| > threshold - band/2, rest = baseline | sphere: solve everywhere,
                          # lambda_cap everywhere, no fixed boundary (the gate alone protects the equator)


@dataclass
class ViewProducts:
    """What the solve and the gate consume, from any number of views on the ERP grid (2 pole views per pole for
    v2, ~3 icosahedral views per pixel for acgf|ico). Edge arrays: horizontal (H, W), vertical (H-1, W)."""
    gamma: np.ndarray  # per-pixel gate weight in [0, 1]
    view_noise: np.ndarray  # sigma_n^2: per-pixel across-view variance of edge differences (work-space units^2)
    n_eff: np.ndarray  # per-pixel (blurred) number of views
    u_v: np.ndarray  # per-pixel prior-weighted mean of the views (v_bar), NaN where no view
    t_h: np.ndarray  # per-edge consensus t_e: prior-weighted mean of the views' differences (0 where no view)
    t_v: np.ndarray
    w_h: np.ndarray  # per-edge summed prior weight (0 = no view on that edge)
    w_v: np.ndarray
    n_views: int


def view_products(u_b: np.ndarray, ev: List[ErpView], params: ACGFParams, sigma_px: float) -> ViewProducts:
    """Gate statistics, value consensus and edge consensus of a set of views (work space, ERP grid)."""
    H, W = u_b.shape
    if params.gate:
        gamma, gi = consensus_gate(u_b, ev, params.prior_power, sigma_px)
    else:
        gamma, gi = np.ones((H, W)), {}
    # value consensus of the views (prior-weighted mean of u)
    num = np.zeros((H, W)); den = np.zeros((H, W))
    for v in ev:
        w = np.where(v.valid, np.cos(np.radians(np.clip(v.distortion, 0, 90))) ** params.prior_power, 0.0)
        num += w * np.nan_to_num(v.u); den += w
    u_v = np.where(den > 0, num / np.maximum(den, 1e-12), np.nan)
    # edge consensus: prior-weighted mean of the view differences
    nh = np.zeros((H, W)); dh = np.zeros((H, W)); nv = np.zeros((H - 1, W)); dv = np.zeros((H - 1, W))
    for v in ev:
        h, vv = edge_diffs(v.u)
        mh, mv = edge_valid(v.valid)
        ph, pv = edge_mean(np.cos(np.radians(np.clip(v.distortion, 0, 90))) ** params.prior_power)
        nh += np.where(mh, ph * h, 0); dh += np.where(mh, ph, 0)
        nv += np.where(mv, pv * vv, 0); dv += np.where(mv, pv, 0)
    nan = np.full((H, W), np.nan)
    return ViewProducts(gamma, gi.get("view_noise", nan), gi.get("n_eff", nan), u_v,
                        np.where(dh > 0, nh / np.maximum(dh, 1e-12), 0), np.where(dv > 0, nv / np.maximum(dv, 1e-12), 0),
                        dh, dv, len(ev))


def fuse_products(base: np.ndarray, u_b: np.ndarray, prod: ViewProducts, params: ACGFParams, inv,
                  extra: Dict, t0: float) -> Tuple[np.ndarray, Dict]:
    """Screened Poisson solve over the caps (scope polar) or the whole sphere (scope sphere), then the gate."""
    H, W = base.shape
    lat = latitude_map(H, W)
    fin = np.isfinite(base) & (base > 0)
    sigma_px = params.gate_sigma_deg / 180.0 * H
    gamma = prod.gamma
    if params.scope == "polar":
        w_lat = latitude_weight(np.abs(lat), "cosine", params.lat_threshold, params.band)
    elif params.scope == "sphere":
        w_lat = np.ones((H, W))
    else:
        raise ValueError(f"unknown ACGF scope {params.scope}")

    # gated value consensus, latitude-blended with the baseline
    u_v = prod.u_v
    g = np.where(np.isfinite(u_v), w_lat * gamma, 0.0)
    u_val = np.where(np.isfinite(u_v), (1 - g) * u_b + g * np.nan_to_num(u_v), u_b)
    if params.domain == "value":
        extra.update({"gamma": gamma, "post_s": time.perf_counter() - t0})
        return np.where(fin & (g > 0), inv(u_val), base), extra

    # targets: gamma * consensus of view differences + (1 - gamma) * baseline difference
    bh, bv = edge_diffs(u_b)
    bmh, bmv = edge_valid(fin)
    dh, dv = prod.w_h, prod.w_v
    gh, gv = edge_mean(gamma if params.gate_mode == "edge" else np.ones((H, W)))
    gh = np.where(dh > 0, gh, 0.0); gv = np.where(dv > 0, gv, 0.0)
    th = gh * prod.t_h + (1 - gh) * np.where(bmh, bh, 0)
    tv = gv * prod.t_v + (1 - gv) * np.where(bmv, bv, 0)
    mth = bmh | (dh > 0)
    mtv = bmv | (dv > 0)
    if params.scope == "polar":
        unknown = (np.abs(lat) > params.lat_threshold - params.band / 2) & fin
    else:
        unknown = fin.copy()
    lam = params.lambda_cap + params.lambda_edge * (1.0 - w_lat)
    # screening target: the baseline ("baseline") or the gated value consensus ("value"); both equal
    # the baseline on the fixed boundary, where w_lat = 0
    u0 = u_val if params.screen == "value" else u_b
    u, si = screened_poisson(u0, th, tv, mth, mtv, unknown, lam, params.irls_iters)
    extra.update({"gamma": gamma, "post_s": time.perf_counter() - t0, **si})
    out = base.copy()
    if params.gate_mode == "value":  # gate the solved correction instead of mixing gradient sources
        gs = blur_wrap(gamma, sigma_px)
        u = u_b + gs * (u - u_b)
    out[unknown] = inv(u[unknown])  # fixed pixels keep the baseline bit-for-bit
    return out, extra


def _work_transforms(base: np.ndarray, params: ACGFParams, space: str):
    """Work space: log (scale-free gradients, positive output) or linear (bounded jumps where the model predicts
    near-zero disparity, e.g. sky; log turns those into huge steps that the gradient solve spreads)."""
    fin = np.isfinite(base) & (base > 0)
    work = params.work if params.work != "auto" else ("linear" if space == "disparity" else "log")
    fwd = (lambda x: np.log(x)) if work == "log" else (lambda x: x)
    inv = (lambda x: np.exp(x)) if work == "log" else (lambda x: np.maximum(x, float(base[fin].min())))
    u_b = np.where(fin, fwd(np.where(fin, base, 1.0)), np.nan)
    lo = params.guard[0] * float(np.percentile(base[fin], 1))
    hi = params.guard[1] * float(np.percentile(base[fin], 99))
    return fin, fwd, inv, u_b, lo, hi


def acgf_fuse(base: np.ndarray, raw_views: List[np.ndarray], views: List[Tuple[int, object]], model: DepthModelWrapper,
              params: ACGFParams, law: bool, perspective_geometry: Optional[str] = None) -> Tuple[np.ndarray, Dict]:
    """Fuse pole-view predictions with the baseline ERP prediction (fusion space in, fusion space out)."""
    H, W = base.shape
    lat = latitude_map(H, W)
    geom = perspective_geometry or model.geometry("perspective")
    space, scale = model.spec.space, model.spec.scale
    fin, fwd, inv, u_b, lo, hi = _work_transforms(base, params, space)
    t0 = time.perf_counter()
    ev: List[ErpView] = []
    for (pole, view), raw in zip(views, raw_views):
        P, valid, m, dist, anchor_ok = _view_on_erp(raw, view, H, W, geom, law)
        anchor = anchor_ok & valid & fin & (np.abs(lat) < params.lat_threshold) & (np.sign(lat) == pole)
        if isinstance(view, RotatedView):  # an ERP view is trusted where it is near its own equator
            anchor &= dist < params.lat_threshold
        X, info = convert_view(P, valid, m, anchor, np.where(fin, base, np.nan), space, scale, lo, hi)
        ok = np.isfinite(X) & (X > 0) & (pole * lat > 0)
        info["kind"] = view.to_dict().get("kind", "gnomonic")
        ev.append(ErpView(f"{info['kind']}_{'N' if pole > 0 else 'S'}", pole,
                          np.where(ok, fwd(np.where(ok, X, 1.0)), np.nan), ok, dist, info))
    ev = [v for v in ev if v.valid.any()]
    extra: Dict = {"view_info": [v.info for v in ev]}
    if not ev:
        extra["acgf_fallback"] = "no valid views"
        return base.copy(), extra

    prod = view_products(u_b, ev, params, params.gate_sigma_deg / 180.0 * H)
    return fuse_products(base, u_b, prod, params, inv, extra, t0)


# ----------------------------------------------------------------------------
# acgf|ico: the 20 icosahedral views of 360MonoDepth as ACGF input
# ----------------------------------------------------------------------------

def ico_erp_views(base: np.ndarray, raw_views: List[np.ndarray], planes: Sequence[TangentPlane],
                  model: DepthModelWrapper, params: ACGFParams, align: str = "affine",
                  perspective_geometry: Optional[str] = None, grid: Optional[Dict] = None,
                  affine_cache: Optional[Dict] = None) -> Tuple[List[ErpView], Dict]:
    """Icosahedral pinhole views -> ErpViews in the work space, each aligned to the ERP BASELINE (not to each other).

    affine_cache: a dict shared by calls on the same image and settings; the affine step is stored there and reused
    (the grid variants all start from it).

    Anchors: pixels the baseline is trusted on (|lat| < threshold) inside the inner 85% of the view.
      align='affine': ACGF's robust pinhole fit  X = A*cos*P + B*cos + C  (convert_view), range guard.
      align='grid'  : the affine X, then mono360's deformable per-view (scale, offset) grids fitted to the baseline
                      on the anchors (mono360.anchored_grid_align), range guard again.
    """
    H, W = base.shape
    lat = latitude_map(H, W)
    geom = perspective_geometry or model.geometry("perspective")
    fin, fwd, inv, u_b, lo, hi = _work_transforms(base, params, model.spec.space)
    base_nan = np.where(fin, base, np.nan)
    reused = affine_cache is not None and "affine" in affine_cache
    if reused:
        Xs, dists, anchors, infos = (list(x) for x in affine_cache["affine"])
    else:
        ta = time.perf_counter()
        Xs, dists, anchors, infos = [], [], [], []
        for plane, raw in zip(planes, raw_views):
            P, valid, m, dist, anchor_ok = _view_on_erp(raw, plane, H, W, geom, law=False)
            anchor = anchor_ok & valid & fin & (np.abs(lat) < params.lat_threshold)
            X, info = convert_view(P, valid, m, anchor, base_nan, model.spec.space, model.spec.scale, lo, hi)
            info["kind"] = "ico"
            Xs.append(X); dists.append(dist); anchors.append(anchor); infos.append(info)
        if affine_cache is not None:
            affine_cache["affine"] = (tuple(Xs), tuple(dists), tuple(anchors), tuple(infos))
            affine_cache["affine_s"] = time.perf_counter() - ta
    # time of the affine step even when it was reused, so that every variant's runtime is as if it ran alone
    extra: Dict = {"affine_reused_s": affine_cache["affine_s"] if reused else 0.0}
    if align == "grid":
        from .mono360 import anchored_grid_align
        g = dict(grid or {})
        Xs, extra = anchored_grid_align(Xs, anchors, list(planes), base_nan, **g)
        Xs = [np.where(np.isfinite(X) & (X > lo) & (X < hi), X, np.nan) for X in Xs]
    elif align != "affine":
        raise ValueError(f"unknown ico alignment {align}")
    ev = []
    for k, (X, dist, info) in enumerate(zip(Xs, dists, infos)):
        ok = np.isfinite(X) & (X > 0)
        ev.append(ErpView(f"ico{k:02d}", 0, np.where(ok, fwd(np.where(ok, X, 1.0)), np.nan), ok, dist, info))
    return [v for v in ev if v.valid.any()], extra


def ico_view_products(base: np.ndarray, raw_views: List[np.ndarray], planes: Sequence[TangentPlane],
                      model: DepthModelWrapper, params: ACGFParams, align: str = "affine",
                      perspective_geometry: Optional[str] = None, grid: Optional[Dict] = None,
                      affine_cache: Optional[Dict] = None) -> Tuple[ViewProducts, Dict]:
    """Input adapter: icosahedral views (raw model outputs + planes) -> the ViewProducts ACGF's gate and solve consume
    (edge consensus t_e, per-pixel v_bar, sigma_n^2, n). Independent of the fusion scope, so it can be shared by the
    polar and sphere variants of one image."""
    t0 = time.perf_counter()
    ev, extra = ico_erp_views(base, raw_views, planes, model, params, align, perspective_geometry, grid, affine_cache)
    _, _, _, u_b, _, _ = _work_transforms(base, params, model.spec.space)
    if not ev:
        return None, {"view_info": [], "acgf_fallback": "no valid views", "products_s": time.perf_counter() - t0}
    prod = view_products(u_b, ev, params, params.gate_sigma_deg / 180.0 * base.shape[0])
    extra.update({"view_info": [v.info for v in ev],
                  "products_s": time.perf_counter() - t0 + extra.get("affine_reused_s", 0.0)})
    return prod, extra


def acgf_fuse_ico(base: np.ndarray, prod: Optional[ViewProducts], params: ACGFParams,
                  model: DepthModelWrapper, extra: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
    """acgf|ico: ACGF's gate and screened Poisson solve on the products of the icosahedral views."""
    extra = dict(extra or {})
    if prod is None:
        return base.copy(), extra
    _, _, inv, u_b, _, _ = _work_transforms(base, params, model.spec.space)
    return fuse_products(base, u_b, prod, params, inv, extra, time.perf_counter())
