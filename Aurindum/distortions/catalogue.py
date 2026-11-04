"""Realistic capture degradations of 360-degree panoramas, each with a physical cause, and candidate inference-time
mitigations. Used by scripts/distortion_gallery.py (exploratory study, before/after comparisons).

Conventions
-----------
* A distortion maps a clean ERP RGB image to the degraded image a camera would deliver, plus a context dict.
* A geometric distortion (tilt) also moves pixels: `to_original(pred, ctx)` brings a prediction made in the degraded
  frame back onto the original grid, so every method is scored against the SAME ground truth. Photometric distortions
  leave the geometry unchanged (identity).
* A mitigation receives (model, degraded rgb, ctx) and returns a prediction IN THE DEGRADED FRAME (scored after
  `to_original`). `ctx` may carry knowledge a real system would have (e.g. the IMU tilt for the 'oracle' re-levelling,
  the occlusion mask, which every 360 camera knows). Mitigations that use such knowledge are labelled 'known ...'.
* `region(H, W, ctx)` is the region where the degradation acts (scored separately), or None.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np

from geometry.erp_projection import rotate_erp
from geometry.spherical import erp_lonlat_grid, latitude_map, rotation_from_ypr


def _lat_lon_deg(H, W):
    lon, lat = erp_lonlat_grid(H, W)
    return np.degrees(lat.numpy()), np.degrees(lon.numpy())


def _rot_img(img: np.ndarray, R: np.ndarray) -> np.ndarray:
    out = np.asarray(rotate_erp(img.astype(np.float32), R))
    return np.clip(np.rint(out), 0, 255).astype(np.uint8) if img.dtype == np.uint8 else out


def _rot_pred(pred: np.ndarray, R: np.ndarray) -> np.ndarray:
    return np.asarray(rotate_erp(np.asarray(pred, dtype=np.float64), R), dtype=np.float64)


def rotation_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Smallest rotation Q with Q a = b (unit vectors), Rodrigues formula."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = float(a @ b)
    if np.linalg.norm(v) < 1e-12:
        if c > 0:
            return np.eye(3)
        p = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 0, 1.0])  # 180 deg about any axis normal to a
        p = p - (p @ a) * a
        p /= np.linalg.norm(p)
        return 2 * np.outer(p, p) - np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


# ------------------------------------------------------------------------------------------------------------------
# distortions
# ------------------------------------------------------------------------------------------------------------------

@dataclass
class Distortion:
    key: str
    title: str
    cause: str
    apply: Callable[[np.ndarray, Dict], Tuple[np.ndarray, Dict]]
    to_original: Callable[[np.ndarray, Dict], np.ndarray] = lambda p, ctx: p
    region: Optional[Callable[[int, int, Dict], np.ndarray]] = None
    mitigations: List[str] = field(default_factory=list)


def tilt_apply(rgb, ctx):
    R = rotation_from_ypr(pitch_deg=ctx.get("pitch", 12.0), roll_deg=ctx.get("roll", 8.0))
    return _rot_img(rgb, R), {**ctx, "R": R}


def tilt_to_original(pred, ctx):
    # degraded image = I(R d): the prediction for degraded-frame direction e belongs to original direction R e
    return _rot_pred(pred, ctx["R"].T)


def occlusion_mask(H, W, ctx):
    lat, _ = _lat_lon_deg(H, W)
    m = np.zeros((H, W), bool)
    if ctx.get("nadir_from") is not None:
        m |= lat < -ctx["nadir_from"]
    if ctx.get("zenith_from") is not None:
        m |= lat > ctx["zenith_from"]
    return m


def nadir_apply(rgb, ctx):
    ctx = {**ctx, "nadir_from": ctx.get("nadir_from", 62.0)}
    out = rgb.copy()
    out[occlusion_mask(*rgb.shape[:2], ctx)] = ctx.get("fill", (48, 48, 52))  # tripod / logo patch
    return out, ctx


def vfov_apply(rgb, ctx):
    ctx = {**ctx, "nadir_from": ctx.get("half_vfov", 50.0), "zenith_from": ctx.get("half_vfov", 50.0)}
    out = rgb.copy()
    out[occlusion_mask(*rgb.shape[:2], ctx)] = 0  # phone / cylindrical panorama: nothing captured above / below
    return out, ctx


def seam_weight(H, W, feather_deg=2.0):
    """1 on the front lens hemisphere (|lon| < 90), 0 on the back one, linear feather across the two stitch lines."""
    _, lon = _lat_lon_deg(H, W)
    d = 90.0 - np.abs(lon)  # > 0 inside the front hemisphere
    return np.clip(0.5 + d / (2 * feather_deg), 0.0, 1.0)


def seam_apply(rgb, ctx):
    gain = np.array(ctx.get("gain", (1.35, 1.30, 1.18)), dtype=np.float32)  # front lens brighter and warmer
    w = seam_weight(*rgb.shape[:2])[..., None]
    out = rgb.astype(np.float32) * (1 + w * (gain - 1))
    return np.clip(np.rint(out), 0, 255).astype(np.uint8), {**ctx, "gain": gain}


def yawblur_apply(rgb, ctx):
    L = int(ctx.get("length_px", 9))  # yaw rotation during the exposure = the same arc for every pixel of a row
    k = np.zeros(rgb.shape[1], np.float32)
    k[:L] = 1.0 / L
    k = np.roll(k, -(L // 2))
    F = np.fft.rfft(rgb.astype(np.float32), axis=1) * np.fft.rfft(k)[None, :, None]
    out = np.fft.irfft(F, n=rgb.shape[1], axis=1)  # circular in longitude: exactly what a yaw shake does to an ERP
    return np.clip(np.rint(out), 0, 255).astype(np.uint8), {**ctx, "kernel": k}


def noise_apply(rgb, ctx):
    rng = np.random.default_rng(ctx.get("seed", 0))
    x = rgb.astype(np.float32) / 255.0
    peak = ctx.get("photons", 60.0)  # shot noise (low light) + read noise
    x = rng.poisson(np.clip(x, 0, 1) * peak) / peak + rng.normal(0, ctx.get("read", 0.03), x.shape)
    return np.clip(np.rint(x * 255), 0, 255).astype(np.uint8), ctx


def jpeg_apply(rgb, ctx):
    ok, buf = cv2.imencode(".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, int(ctx.get("q", 8))])
    return cv2.cvtColor(cv2.imdecode(buf, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB), ctx


def lowres_apply(rgb, ctx):
    f = int(ctx.get("factor", 4))
    H, W = rgb.shape[:2]
    small = cv2.resize(rgb, (W // f, H // f), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC), ctx


def _lens_angle_deg(H, W):
    """Angle (deg) of every ERP ray from the optical axis of the lens that images it in a dual-fisheye camera
    (front lens looks along +z and covers |lon| < 90, back lens along -z)."""
    from geometry.spherical import erp_to_sphere
    z = erp_to_sphere(H, W).numpy()[..., 2]
    return np.degrees(np.arccos(np.clip(np.abs(z), 0.0, 1.0)))


def _parallax_view(rgb, depth, baseline, d_stitch, sign, iters=4):
    """Image the clean scene through ONE lens of a dual-fisheye rig and stitch it as the software does.

    Lens centre c = sign * (0, 0, baseline / 2). The stitcher assumes every point lies on a sphere of radius d_stitch
    around the rig centre, so a scene point P = r d (true direction d, range r from the rig centre) seen by the lens
    along u = (P - c)/|P - c| is placed where that ray meets the stitching sphere: d' = normalise(c + t u), |c + t u| = d_stitch. Points at r = d_stitch are
    exact; nearer points are displaced away from the lens axis, farther ones towards it. The output is the image the
    stitcher writes, I_out(d') = I(d): solved backwards for every output pixel d' by fixed-point iteration on d.
    """
    from geometry.erp_projection import sample_erp
    from geometry.spherical import erp_to_sphere, sphere_to_erp
    H, W = depth.shape
    c = np.array([0.0, 0.0, sign * baseline / 2.0])
    dp = erp_to_sphere(H, W).numpy()  # output directions d'
    d = dp.copy()
    for _ in range(iters):
        u_, v_ = sphere_to_erp(d, H, W)
        r = np.asarray(sample_erp(depth.astype(np.float64), u_, v_, mode="bilinear"))
        P = d * r[..., None]
        uvec = P - c
        uvec /= np.linalg.norm(uvec, axis=-1, keepdims=True)
        # intersection of the lens ray c + t u (t > 0) with the stitching sphere |x| = d_stitch around the rig centre
        cu = uvec @ c
        t = -cu + np.sqrt(np.maximum(cu ** 2 - c @ c + d_stitch ** 2, 0.0))
        f = c + t[..., None] * uvec
        f /= np.linalg.norm(f, axis=-1, keepdims=True)
        d = d + (dp - f)  # move the source direction by the residual of its forward mapping
        d /= np.linalg.norm(d, axis=-1, keepdims=True)
    u_, v_ = sphere_to_erp(d, H, W)
    out = np.asarray(sample_erp(rgb.astype(np.float32), u_, v_, mode="bilinear"))
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def parallax_apply(rgb, ctx):
    """Dual-fisheye stitching with a lens baseline: each hemisphere comes from its own lens (parallax displaced), and
    a band of +-blend_deg around the two stitch lines blends both lenses (double images / tears of near objects)."""
    depth = np.asarray(ctx["depth"], dtype=np.float64)
    b, D0 = ctx.get("baseline", 0.05), ctx.get("d_stitch", 2.0)
    front = _parallax_view(rgb, depth, b, D0, +1)
    back = _parallax_view(rgb, depth, b, D0, -1)
    w = seam_weight(*rgb.shape[:2], feather_deg=ctx.get("blend_deg", 5.0))[..., None]
    out = w * front.astype(np.float32) + (1 - w) * back.astype(np.float32)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8), {**ctx, "seam_band": ctx.get("blend_deg", 5.0)}


def seam_band_mask(H, W, ctx):
    _, lon = _lat_lon_deg(H, W)
    return np.abs(np.abs(lon) - 90.0) <= ctx.get("seam_band", 5.0) + 3.0


def vignette_apply(rgb, ctx):
    """Residual fisheye vignetting: brightness falls with the angle from each lens axis (towards the stitch lines,
    90 deg off-axis); the stitcher's correction profile is imperfect, so a falloff to `edge` remains at the seams."""
    th = _lens_angle_deg(*rgb.shape[:2])
    v = 1.0 - (1.0 - ctx.get("edge", 0.45)) * (th / 90.0) ** ctx.get("power", 2.0)
    out = rgb.astype(np.float32) * v[..., None]
    return np.clip(np.rint(out), 0, 255).astype(np.uint8), {**ctx, "vignette": v}


# ------------------------------------------------------------------------------------------------------------------
# mitigations (return a prediction in the DEGRADED frame)
# ------------------------------------------------------------------------------------------------------------------

def _pred(model, rgb):
    return np.asarray(model.predict(rgb, kind="erp"), dtype=np.float64)


def m_none(model, rgb_d, ctx):
    return _pred(model, rgb_d)


def releveled(model, rgb_d, Q):
    """Run the model on the degraded panorama rotated by Q (I_l(d) = I_d(Q d)), then return to the degraded frame."""
    return _rot_pred(_pred(model, _rot_img(rgb_d, Q)), Q.T)


def m_relevel_known(model, rgb_d, ctx):
    """Known tilt (camera IMU / gravity sensor): rotate the panorama upright before inference."""
    return releveled(model, rgb_d, ctx["R"].T)


def estimate_down(model, pred_d, space: str, max_dev_deg: float = 45.0) -> Optional[np.ndarray]:
    """Gravity direction in the degraded frame from the model's OWN prediction: normals of the floor plane (nadir ring)
    and of the ceiling plane (zenith ring), fitted robustly (planar_prior.fit_polar_planes), inlier-weighted.

    Measured limitation (real MiDaS, 8 Structured3D frames tilted by 12 deg pitch + 8 deg roll): the estimate is off by
    ~12 deg, about the whole tilt, because the model predicts the floor as if the image were level (its upright prior
    shapes the prediction itself). A joint floor + ceiling fit with a shared disparity offset (removing the c_y / beta
    trade-off of each ring) does not change this (11.3 vs 11.9 deg). A tilt cue independent of the model (vanishing
    lines, IMU) is needed; this estimator is kept as the model-only baseline."""
    from planar_prior import fit_polar_planes
    _, infos = fit_polar_planes(pred_d, space, ring=(35.0, 65.0), min_inlier=0.0, max_tilt_deg=90.0, agree_tol=1e9)
    acc = np.zeros(3)
    for info in infos:
        if "c" not in info:
            continue
        c = np.asarray(info["c"], float)
        n = c / max(np.linalg.norm(c), 1e-12)
        acc += (n if info["pole"] == "floor" else -n) * max(info.get("inlier_share", 0.0), 1e-3)
    if np.linalg.norm(acc) < 1e-9:
        return None
    acc = acc / np.linalg.norm(acc)
    # plausibility: a handheld / tripod panorama is within a few tens of degrees of level, so an estimate more than
    # max_dev_deg from the image's own 'down' is a failed plane fit (seen on real MiDaS output: a flipped normal, 158 deg),
    # and re-levelling with it would turn the panorama upside down. Refuse it; the caller then leaves the image as is.
    if np.degrees(np.arccos(np.clip(acc[1], -1.0, 1.0))) > max_dev_deg:
        return None
    return acc


def m_relevel_self(model, rgb_d, ctx, iters: int = 2):
    """No sensor: estimate 'down' from the floor / ceiling planes of the model's own prediction, re-level, repeat."""
    from polar_views import fusion_space
    space = "disparity" if fusion_space(model) == "disparity" else "depth"
    Q = np.eye(3)
    pred = _pred(model, rgb_d)
    y = np.array([0.0, 1.0, 0.0])
    for _ in range(iters):
        # `pred` is the prediction for the image I_l(d) = I_d(Q d) (Q = identity in the first round). Its estimated
        # 'down' n (in that frame) is the degraded-frame direction Q n; the new levelling rotation must map y to it:
        # Q_new y = Q n  <=>  Q_new = Q @ rotation_between(y, n)
        down = estimate_down(model, pred, space)
        if down is None:
            break
        Q = Q @ rotation_between(y, down)
        pred = _pred(model, _rot_img(rgb_d, Q))
    ctx["Q_est"] = Q
    return _rot_pred(pred, Q.T)


def _inpaint_erp(rgb, mask, radius=5):
    return cv2.inpaint(rgb, mask.astype(np.uint8) * 255, radius, cv2.INPAINT_TELEA)


def m_inpaint_erp(model, rgb_d, ctx):
    """Known occlusion mask: inpaint the masked region on the ERP grid, then predict."""
    return _pred(model, _inpaint_erp(rgb_d, occlusion_mask(*rgb_d.shape[:2], ctx)))


def _inpaint_tangent(rgb, mask, fov=130.0, size=384):
    """Inpaint each occluded polar cap in a gnomonic (tangent-plane) view centred on the pole, where the cap is a
    round, undistorted disk instead of a stretched band, then project the fill back onto the ERP grid."""
    from geometry.tangent_plane import erp_to_tangent, generate_tangent_plane, tangent_to_erp
    H, W = rgb.shape[:2]
    out = rgb.copy()
    lat = latitude_map(H, W)
    for sign in (+1, -1):
        cap = mask & (np.sign(lat) == sign)
        if not cap.any():
            continue
        plane = generate_tangent_plane(0.0, 90.0 * sign, fov, size)
        t_rgb = np.clip(np.rint(np.asarray(erp_to_tangent(rgb.astype(np.float32), plane))), 0, 255).astype(np.uint8)
        t_m = np.asarray(erp_to_tangent(cap.astype(np.float32), plane, mode="nearest")) > 0.5
        t_fill = cv2.inpaint(t_rgb, t_m.astype(np.uint8) * 255, 7, cv2.INPAINT_TELEA)
        back = tangent_to_erp(t_fill.astype(np.float32), plane, H, W)
        use = cap & back.valid
        out[use] = np.clip(np.rint(np.asarray(back.values)[use]), 0, 255).astype(np.uint8)
        rest = cap & ~back.valid  # outside the tangent view (should not happen for fov >= 2 * cap size)
        if rest.any():
            out = _inpaint_erp(out, rest)
    return out


def m_inpaint_tangent(model, rgb_d, ctx):
    return _pred(model, _inpaint_tangent(rgb_d, occlusion_mask(*rgb_d.shape[:2], ctx)))


def m_plane_fill(model, rgb_d, ctx):
    """Tangent inpainting, then the occluded caps are replaced by the floor / ceiling plane fitted to the model's own
    prediction on the visible ring next to them, fused in the gradient domain (no seam). Falls back to the inpainted
    prediction where no plane is accepted."""
    from planar_prior import fit_polar_planes
    from polar_views import fuse_polar, fusion_space, to_fusion
    H, W = rgb_d.shape[:2]
    mask = occlusion_mask(H, W, ctx)
    pred = _pred(model, _inpaint_tangent(rgb_d, mask))
    lat = latitude_map(H, W)
    fs = fusion_space(model)
    space = "disparity" if fs == "disparity" else "depth"
    out = pred
    for sign, key in ((-1, "nadir_from"), (1, "zenith_from")):
        edge = ctx.get(key)
        if edge is None:
            continue
        # plane fitted on the visible ring next to the occluded cap; its gradients are used from `edge - 4` deg
        # (visible floor / ceiling) through the whole cap, so the level is pinned on VISIBLE pixels, not at the mask
        # boundary where the inpainted prediction may jump (that jump would otherwise offset the whole cap)
        ring = (max(edge - 25.0, 15.0), edge - 2.0)
        plane, _ = fit_polar_planes(out, space, ring=ring, cap_from=edge - 4.0, min_inlier=0.5, max_tilt_deg=20.0,
                                    agree_tol=1e9)
        hemi = (np.sign(lat) == sign) & (np.abs(lat) >= edge - 4.0)
        plane = np.where(hemi, plane, np.nan)
        if not np.isfinite(plane).any():
            continue
        # ramp [edge - 8, edge - 4] has no plane values -> pinned; alpha = 1 from edge - 4 on
        out = fuse_polar(out, to_fusion(plane, fs), fs, np.where(np.sign(lat) == sign, np.abs(lat), 0.0),
                         mode="gradient_poisson", phi_threshold=edge - 6.0, blend_margin=2.0)
    return out


def m_gain_match(model, rgb_d, ctx, band_deg=4.0):
    """Estimate the per-channel gain between the two lenses from thin bands on both sides of the two stitch lines
    (blind: no knowledge of the gain), divide it out on the front hemisphere with the same feather, predict."""
    H, W = rgb_d.shape[:2]
    _, lon = _lat_lon_deg(H, W)
    x = rgb_d.astype(np.float32)
    lat = latitude_map(H, W)
    keep = np.abs(lat) < 60
    inner = keep & (np.abs(np.abs(lon) - 90.0) < band_deg) & (np.abs(lon) < 90.0 - 2.5)
    outer = keep & (np.abs(np.abs(lon) - 90.0) < band_deg) & (np.abs(lon) > 90.0 + 2.5)
    g = np.array([np.median(x[..., c][inner]) / max(np.median(x[..., c][outer]), 1e-3) for c in range(3)], np.float32)
    ctx["gain_est"] = g
    w = seam_weight(H, W)[..., None]
    out = x / (1 + w * (g - 1))
    return _pred(model, np.clip(np.rint(out), 0, 255).astype(np.uint8))


def m_wiener(model, rgb_d, ctx, snr=0.01):
    """Known yaw-shake kernel (camera gyro): Wiener deconvolution along each ERP row (circular, exact model)."""
    K = np.fft.rfft(ctx["kernel"])[None, :, None]
    F = np.fft.rfft(rgb_d.astype(np.float32), axis=1)
    out = np.fft.irfft(F * np.conj(K) / (np.abs(K) ** 2 + snr), n=rgb_d.shape[1], axis=1)
    return _pred(model, np.clip(np.rint(out), 0, 255).astype(np.uint8))


def m_seam_inpaint(model, rgb_d, ctx):
    """Known stitch geometry: inpaint the blend band around the two stitch lines (where the double images are), then
    predict. Needs no depth and no image of the clean scene."""
    H, W = rgb_d.shape[:2]
    _, lon = _lat_lon_deg(H, W)
    band = np.abs(np.abs(lon) - 90.0) <= ctx.get("seam_band", 5.0)
    return _pred(model, _inpaint_erp(rgb_d, band, radius=3))


def m_flatfield(model, rgb_d, ctx, nbins=18):
    """Blind flat-field: estimate the brightness profile against the lens-axis angle as the median luminance per angle
    bin (scene content averages out over a whole panorama), fit a smooth even polynomial, divide it out, predict."""
    H, W = rgb_d.shape[:2]
    th = _lens_angle_deg(H, W)
    lum = rgb_d.astype(np.float32).mean(-1)
    edges = np.linspace(0, 90, nbins + 1)
    cen = 0.5 * (edges[:-1] + edges[1:])
    med = np.array([np.median(lum[(th >= a) & (th < b)]) for a, b in zip(edges[:-1], edges[1:])])
    ok = np.isfinite(med) & (med > 1)
    A = np.stack([np.ones(ok.sum()), (cen[ok] / 90) ** 2, (cen[ok] / 90) ** 4], -1)
    coef, *_ = np.linalg.lstsq(A, med[ok], rcond=None)
    prof = coef[0] + coef[1] * (th / 90) ** 2 + coef[2] * (th / 90) ** 4
    gain = np.clip(coef[0] / np.maximum(prof, 1e-3), 1.0, 4.0)  # only brighten, never darken
    ctx["flatfield_gain_edge"] = float(np.median(gain[th > 85]))
    out = rgb_d.astype(np.float32) * gain[..., None]
    return _pred(model, np.clip(np.rint(out), 0, 255).astype(np.uint8))


def m_denoise(model, rgb_d, ctx):
    return _pred(model, cv2.fastNlMeansDenoisingColored(rgb_d, None, 10, 10, 7, 21))


def m_bilateral(model, rgb_d, ctx):
    return _pred(model, cv2.bilateralFilter(rgb_d, 7, 40, 5))


MITIGATIONS: Dict[str, Tuple[str, Callable]] = {
    "none": ("no mitigation", m_none),
    "relevel_known": ("re-level, known tilt (IMU)", m_relevel_known),
    "relevel_self": ("re-level, tilt estimated from the predicted floor / ceiling", m_relevel_self),
    "inpaint_erp": ("inpaint on the ERP grid", m_inpaint_erp),
    "inpaint_tangent": ("inpaint in a polar tangent view", m_inpaint_tangent),
    "plane_fill": ("tangent inpaint + floor / ceiling plane fill", m_plane_fill),
    "gain_match": ("blind lens-gain matching across the stitch lines", m_gain_match),
    "wiener": ("Wiener deconvolution, known yaw kernel (gyro)", m_wiener),
    "denoise": ("non-local-means denoising", m_denoise),
    "seam_inpaint": ("inpaint the stitch blend band (known seam geometry)", m_seam_inpaint),
    "flatfield": ("blind flat-field from the brightness-vs-lens-angle profile", m_flatfield),
    "bilateral": ("bilateral smoothing (deblocking)", m_bilateral),
}

CATALOGUE: List[Distortion] = [
    Distortion("tilt", "Camera tilt (12 deg pitch, 8 deg roll)",
               "Handheld or monopod capture, tripod on a slope, robot / drone platforms: the panorama is not levelled to "
               "gravity, so floors and ceilings no longer sit at the poles and the horizon is a wave.",
               tilt_apply, tilt_to_original, None, ["relevel_known", "relevel_self"]),
    Distortion("nadir", "Tripod / operator occlusion at the nadir (below -62 deg)",
               "Every tripod-mounted 360 camera sees its own mount and often the operator; vendors paint a logo or a black "
               "disk over it. The floor under the camera is then unknown to the model.",
               nadir_apply, region=occlusion_mask, mitigations=["inpaint_erp", "inpaint_tangent", "plane_fill"]),
    Distortion("vfov", "Limited vertical field of view (only +-50 deg captured)",
               "Phone 'panorama' modes and cylindrical rigs capture a band around the horizon; the caps are black.",
               vfov_apply, region=occlusion_mask, mitigations=["inpaint_erp", "inpaint_tangent", "plane_fill"]),
    Distortion("seam", "Exposure / white-balance mismatch between the two lenses",
               "Dual-fisheye cameras meter each lens separately; facing a window, one hemisphere is brighter and warmer and "
               "the stitch lines (longitude +-90 deg) show a step.",
               seam_apply, mitigations=["gain_match"]),
    Distortion("parallax", "Stitching parallax of a dual-lens rig (5 cm baseline)",
               "The two fisheye lenses sit a few centimetres apart; the stitcher assumes all points are about 2 m away, "
               "so nearer objects are displaced differently in each lens and tear or double at the stitch lines "
               "(longitude +-90 deg), worst for furniture and people close to the camera.",
               parallax_apply, region=seam_band_mask, mitigations=["seam_inpaint"]),
    Distortion("vignette", "Residual fisheye vignetting (seams 55% darker)",
               "Fisheye lenses lose light towards the edge of their field (the stitch lines); vendor flat-field profiles are "
               "approximate, so a darkening band remains along the seams, strongest in cheap cameras and at high ISO.",
               vignette_apply, mitigations=["flatfield"]),
    Distortion("yawblur", "Camera shake during exposure (yaw, 9 px)",
               "Handheld capture in dim light: a small rotation about the vertical axis during the exposure smears every "
               "row by the same longitude arc.",
               yawblur_apply, mitigations=["wiener"]),
    Distortion("noise", "Low-light sensor noise",
               "Indoor scenes at night or in dim rooms: shot noise plus read noise at high ISO.",
               noise_apply, mitigations=["denoise"]),
    Distortion("jpeg", "Heavy JPEG compression (quality 8)",
               "Streaming 360 video, web / social uploads and storage-limited capture.",
               jpeg_apply, mitigations=["bilateral"]),
    Distortion("lowres", "Low resolution (4x down-sampled)",
               "Thumbnails, low-bit-rate streams, cheap cameras.",
               lowres_apply, mitigations=[]),
]
