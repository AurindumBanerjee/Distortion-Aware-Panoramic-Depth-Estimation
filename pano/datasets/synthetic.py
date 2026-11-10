"""Procedural indoor panoramas with *exact* ground-truth range, rendered by analytic ray casting.

Why: the public panoramic depth benchmarks (Stanford2D3D, Matterport3D, Structured3D)
need signed access agreements, so this generator provides a fully reproducible test bed
whose ground truth is exact (no sensor holes, no stitching errors). It is NOT a
substitute for real data: textures come from scikit-image's bundled photos plus
procedural patterns and shading is a simple Lambertian model with hard shadows.

Scene model (camera at the origin, OpenCV axes x right, y down, z forward):
  * an axis-aligned room box (floor at y = +cam_height, ceiling above);
  * furniture boxes standing on the floor (optionally yawed);
  * ceiling fixtures (lamps / beams) hanging from the ceiling;
  * thin wall panels (posters, shelves) on the walls.
The poles of the panorama therefore see the floor and the ceiling, as in real indoor data.

Ground truth: Euclidean range (metres) along each ERP pixel-centre ray.
RGB: rendered with 2x2 supersampling for anti-aliasing.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from typing import List, Tuple

import cv2
import numpy as np

from pano.geometry.spherical import erp_lonlat_grid, lonlat_to_xyz


# ----------------------------------------------------------------------------
# Textures
# ----------------------------------------------------------------------------

def _texture_bank(seed: int = 0) -> List[np.ndarray]:
    """Float RGB textures in [0,1]. Photos from skimage if available + rich procedural patterns."""
    import warnings

    rng = np.random.default_rng(seed)
    bank = []
    try:
        import skimage.data as sd
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for name in ["brick", "grass", "gravel", "moon", "camera", "coins", "page", "text"]:
                g = getattr(sd, name)().astype(np.float32) / 255.0
                bank.append(np.repeat(g[..., None], 3, -1))
            for name in ["coffee", "chelsea", "astronaut", "rocket", "immunohistochemistry", "hubble_deep_field"]:
                bank.append(getattr(sd, name)()[..., :3].astype(np.float32) / 255.0)
    except Exception:
        # Fallback to procedural patterns if scikit-image is not installed
        n = 256
        yy, xx = np.mgrid[0:n, 0:n] / n
        for freq in [4, 8, 16, 32]:
            grid = ((np.floor(xx * freq) + np.floor(yy * freq)) % 2) * 0.4 + 0.3
            bank.append(np.repeat(grid[..., None], 3, -1).astype(np.float32))
        for col in [(0.8, 0.7, 0.6), (0.3, 0.5, 0.7), (0.7, 0.3, 0.3), (0.5, 0.5, 0.5)]:
            grad = (xx * 0.5 + yy * 0.5)[..., None] * np.array(col, dtype=np.float32)
            bank.append(grad.astype(np.float32))

    # procedural: wood, tiles, checker, smooth noise
    n = 256
    yy, xx = np.mgrid[0:n, 0:n] / n
    wood = 0.5 + 0.5 * np.sin(2 * np.pi * (12 * xx + 0.6 * np.sin(2 * np.pi * 3 * yy)))
    bank.append(np.stack([0.55 + 0.25 * wood, 0.35 + 0.18 * wood, 0.2 + 0.1 * wood], -1).astype(np.float32))
    tiles = ((np.floor(xx * 8) + np.floor(yy * 8)) % 2) * 0.35 + 0.5
    grout = ((xx * 8) % 1 < 0.06) | ((yy * 8) % 1 < 0.06)
    tiles = np.where(grout, 0.25, tiles)
    bank.append(np.repeat(tiles[..., None], 3, -1).astype(np.float32))
    noise = cv2.GaussianBlur(rng.random((n, n)).astype(np.float32), (0, 0), 6)
    noise = (noise - noise.min()) / (np.ptp(noise) + 1e-6)
    bank.append(np.repeat((0.4 + 0.5 * noise)[..., None], 3, -1).astype(np.float32))
    return bank


def _sample_texture(tex: np.ndarray, s: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Bilinear, tiled texture lookup. s, t in texture-repeat units."""
    h, w = tex.shape[:2]
    x = (s % 1.0) * w - 0.5
    y = (t % 1.0) * h - 0.5
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    fx = (x - x0)[..., None].astype(np.float32)
    fy = (y - y0)[..., None].astype(np.float32)
    x0 %= w
    y0 %= h
    x1 = (x0 + 1) % w
    y1 = (y0 + 1) % h
    return ((tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx) * (1 - fy)
            + (tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx) * fy)


# ----------------------------------------------------------------------------
# Scene description
# ----------------------------------------------------------------------------

@dataclass
class Box:
    lo: np.ndarray  # (3,) min corner in the box frame
    hi: np.ndarray  # (3,) max corner
    yaw: float = 0.0  # rotation about the vertical (y) axis around the box centre
    tex: int = 0
    tint: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    tex_scale: float = 1.0

    @property
    def centre(self):
        return 0.5 * (self.lo + self.hi)


@dataclass
class Scene:
    room_lo: np.ndarray
    room_hi: np.ndarray
    room_tex: List[int]  # per face: -x, +x, -y(ceiling), +y(floor), -z, +z
    room_tint: List[Tuple[float, float, float]]
    room_tex_scale: List[float]
    boxes: List[Box] = field(default_factory=list)
    lights: List[np.ndarray] = field(default_factory=list)

    def to_dict(self):
        return {
            "room_lo": self.room_lo.tolist(), "room_hi": self.room_hi.tolist(), "room_tex": self.room_tex,
            "boxes": [dict(lo=b.lo.tolist(), hi=b.hi.tolist(), yaw=b.yaw, tex=b.tex) for b in self.boxes],
            "lights": [l.tolist() for l in self.lights],
        }


def random_scene(rng: np.random.Generator, n_tex: int) -> Scene:
    W = rng.uniform(3.0, 9.0)
    D = rng.uniform(3.0, 9.0)
    Hroom = rng.uniform(2.5, 3.6)
    cam_h = rng.uniform(1.0, 1.7)
    cx = rng.uniform(-0.3, 0.3) * W
    cz = rng.uniform(-0.3, 0.3) * D
    lo = np.array([-W / 2 - cx, -(Hroom - cam_h), -D / 2 - cz])
    hi = np.array([W / 2 - cx, cam_h, D / 2 - cz])
    room_tex = [int(rng.integers(n_tex)) for _ in range(6)]
    room_tint = [tuple(rng.uniform(0.6, 1.0, 3)) for _ in range(6)]
    room_scale = [float(rng.uniform(0.6, 2.0)) for _ in range(6)]
    boxes: List[Box] = []

    def free_xz(margin=0.6):
        for _ in range(50):
            x = rng.uniform(lo[0] + 0.2, hi[0] - 0.2)
            z = rng.uniform(lo[2] + 0.2, hi[2] - 0.2)
            if x * x + z * z > margin ** 2:  # keep the camera outside furniture
                return x, z
        return lo[0] + 0.3, lo[2] + 0.3

    # floor furniture
    for _ in range(int(rng.integers(3, 9))):
        sx, sz = rng.uniform(0.3, 1.6, 2)
        sy = rng.uniform(0.3, 1.9)
        x, z = free_xz(0.4 + 0.75 * max(sx, sz))
        b_lo = np.array([x - sx / 2, hi[1] - sy, z - sz / 2])
        b_hi = np.array([x + sx / 2, hi[1], z + sz / 2])
        boxes.append(Box(b_lo, b_hi, yaw=float(rng.uniform(-0.6, 0.6)), tex=int(rng.integers(n_tex)),
                         tint=tuple(rng.uniform(0.5, 1.0, 3)), tex_scale=float(rng.uniform(0.5, 1.5))))
    # rugs (very thin floor boxes) -> texture on the south pole
    for _ in range(int(rng.integers(0, 3))):
        sx, sz = rng.uniform(1.0, 2.5, 2)
        x, z = rng.uniform(-1, 1, 2)
        boxes.append(Box(np.array([x - sx / 2, hi[1] - 0.02, z - sz / 2]), np.array([x + sx / 2, hi[1], z + sz / 2]),
                         yaw=float(rng.uniform(-0.8, 0.8)), tex=int(rng.integers(n_tex)),
                         tint=tuple(rng.uniform(0.5, 1.0, 3))))
    # ceiling fixtures / beams -> structure near the north pole
    for _ in range(int(rng.integers(1, 5))):
        if rng.random() < 0.5:  # beam spanning the room
            t = rng.uniform(0.15, 0.35)
            dpt = rng.uniform(0.15, 0.4)
            z = rng.uniform(lo[2] + 0.5, hi[2] - 0.5)
            b_lo = np.array([lo[0], lo[1], z - t / 2])
            b_hi = np.array([hi[0], lo[1] + dpt, z + t / 2])
            yaw = 0.0
        else:  # lamp
            s = rng.uniform(0.2, 0.7)
            dpt = rng.uniform(0.2, 0.7)
            x, z = rng.uniform(-1.5, 1.5, 2)
            b_lo = np.array([x - s / 2, lo[1], z - s / 2])
            b_hi = np.array([x + s / 2, lo[1] + dpt, z + s / 2])
            yaw = float(rng.uniform(-0.8, 0.8))
        boxes.append(Box(b_lo, b_hi, yaw=yaw, tex=int(rng.integers(n_tex)), tint=tuple(rng.uniform(0.5, 1.0, 3))))
    # wall panels (posters / shelves)
    for _ in range(int(rng.integers(2, 6))):
        axis = int(rng.integers(2)) * 2  # 0 (x walls) or 2 (z walls)
        side = int(rng.integers(2))
        wpos = (lo if side == 0 else hi)[axis]
        th = rng.uniform(0.03, 0.35)
        a, b = rng.uniform(0.5, 1.5), rng.uniform(0.4, 1.2)
        other = 2 - axis
        c_o = rng.uniform(lo[other] + a, hi[other] - a) if hi[other] - lo[other] > 2 * a else 0.0
        c_y = rng.uniform(lo[1] + 0.3, hi[1] - 1.0)
        b_lo, b_hi = np.zeros(3), np.zeros(3)
        b_lo[axis], b_hi[axis] = (wpos, wpos + th) if side == 0 else (wpos - th, wpos)
        b_lo[other], b_hi[other] = c_o - a / 2, c_o + a / 2
        b_lo[1], b_hi[1] = c_y - b / 2, c_y + b / 2
        boxes.append(Box(b_lo, b_hi, tex=int(rng.integers(n_tex)), tint=tuple(rng.uniform(0.6, 1.0, 3))))
    lights = [np.array([rng.uniform(lo[0] + 0.5, hi[0] - 0.5), lo[1] + 0.05, rng.uniform(lo[2] + 0.5, hi[2] - 0.5)])
              for _ in range(int(rng.integers(1, 3)))]
    return Scene(lo, hi, room_tex, room_tint, room_scale, boxes, lights)


# ----------------------------------------------------------------------------
# Ray casting
# ----------------------------------------------------------------------------

def _rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _ray_box(o: np.ndarray, d: np.ndarray, box: Box):
    """Slab test. o: (3,) or (N,3), d: (N,3). Returns t (N,) (inf if miss) and hit normal (N,3) in world frame."""
    Rb = _rot_y(box.yaw)
    c = box.centre
    o_l = (o - c) @ Rb  # world -> box frame (R^T x in row form)
    d_l = d @ Rb
    lo, hi = box.lo - c, box.hi - c
    with np.errstate(divide="ignore", invalid="ignore"):
        inv = 1.0 / d_l
        t1 = (lo - o_l) * inv
        t2 = (hi - o_l) * inv
    tmin = np.minimum(t1, t2)
    tmax = np.maximum(t1, t2)
    tmin = np.nan_to_num(tmin, nan=-np.inf)
    tmax = np.nan_to_num(tmax, nan=np.inf)
    t_enter = tmin.max(-1)
    t_exit = tmax.min(-1)
    hit = (t_enter <= t_exit) & (t_enter > 1e-6)
    t = np.where(hit, t_enter, np.inf)
    ax = tmin.argmax(-1)
    n_l = np.zeros_like(d_l)
    n_l[np.arange(len(ax)), ax] = -np.sign(d_l[np.arange(len(ax)), ax])
    n = n_l @ Rb.T
    return t, n


def _ray_room(o: np.ndarray, d: np.ndarray, scene: Scene):
    """Exit distance from inside the room box. Returns t (N,), face index (N,), normal (N,3)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        t_hi = (scene.room_hi - o) / d
        t_lo = (scene.room_lo - o) / d
    t_axis = np.where(d > 0, t_hi, t_lo)
    t_axis = np.where(np.isfinite(t_axis) & (t_axis > 0), t_axis, np.inf)
    ax = t_axis.argmin(-1)
    t = t_axis[np.arange(len(ax)), ax]
    pos = d[np.arange(len(ax)), ax] > 0
    face = ax * 2 + pos.astype(int)  # 0:-x 1:+x 2:-y(ceil) 3:+y(floor) 4:-z 5:+z
    n = np.zeros_like(d)
    n[np.arange(len(ax)), ax] = np.where(pos, -1.0, 1.0)
    return t, face, n


def cast(scene: Scene, d: np.ndarray, o: np.ndarray = None):
    """Cast rays d (N,3) from o. Returns range t, surface id (room faces 0..5, boxes 6..), normal, hit point."""
    if o is None:
        o = np.zeros(3)
    t, sid, n = _ray_room(o, d, scene)
    for k, b in enumerate(scene.boxes):
        tb, nb = _ray_box(o, d, b)
        closer = tb < t
        t = np.where(closer, tb, t)
        sid = np.where(closer, 6 + k, sid)
        n = np.where(closer[:, None], nb, n)
    p = o + d * t[:, None]
    return t, sid, n, p


def shade(scene: Scene, bank: List[np.ndarray], d, t, sid, n, p, shadows: bool = True) -> np.ndarray:
    N = len(t)
    albedo = np.zeros((N, 3), np.float32)
    # planar UVs: choose the two axes orthogonal to the dominant normal axis
    for s in np.unique(sid):
        m = sid == s
        if s < 6:
            tex, tint, sc = scene.room_tex[s], scene.room_tint[s], scene.room_tex_scale[s]
            pl = p[m]
        else:
            b = scene.boxes[s - 6]
            tex, tint, sc = b.tex, b.tint, b.tex_scale
            pl = (p[m] - b.centre) @ _rot_y(b.yaw)
        nax = np.abs(n[m] @ (_rot_y(scene.boxes[s - 6].yaw) if s >= 6 else np.eye(3))).argmax(-1)
        uvs = np.zeros((m.sum(), 2))
        for a in range(3):
            mm = nax == a
            others = [i for i in range(3) if i != a]
            uvs[mm] = pl[mm][:, others]
        img = _sample_texture(bank[tex], (uvs[:, 0] / sc)[None], (uvs[:, 1] / sc)[None])[0]
        albedo[m] = img * np.asarray(tint, np.float32)
    light = np.full(N, 0.30, np.float32)  # ambient
    for L in scene.lights:
        v = L - p
        dist = np.linalg.norm(v, axis=-1)
        l = v / dist[:, None]
        lam = np.clip((n * l).sum(-1), 0, None)
        vis = np.ones(N, bool)
        if shadows:
            o2 = p + n * 1e-3
            for b in scene.boxes:
                tb, _ = _ray_box_batch_origin(o2, l, b)
                vis &= ~(tb < dist - 1e-3)
        light += (1.1 * lam * vis / (1.0 + 0.04 * dist ** 2)).astype(np.float32)
    # slight distance fog so far surfaces are not identical to near ones
    rgb = albedo * light[:, None]
    return np.clip(rgb, 0, 1)


def _ray_box_batch_origin(o, d, box):
    return _ray_box(o, d, box)


def render_erp(scene: Scene, bank, height: int, width: int, ss: int = 2, chunk: int = 1 << 17):
    """Render RGB (uint8, HxWx3, ss x ss supersampled) and exact GT range (float32, HxW) at pixel centres."""
    def _render(h, w, need_rgb=True):
        lon, lat = erp_lonlat_grid(h, w)
        d = lonlat_to_xyz(lon.numpy(), lat.numpy()).reshape(-1, 3)
        T = np.empty(len(d), np.float32)
        RGB = np.empty((len(d), 3), np.float32) if need_rgb else None
        for s in range(0, len(d), chunk):
            dd = d[s:s + chunk]
            t, sid, n, p = cast(scene, dd)
            T[s:s + chunk] = t
            if need_rgb:
                RGB[s:s + chunk] = shade(scene, bank, dd, t, sid, n, p)
        return T.reshape(h, w), (RGB.reshape(h, w, 3) if need_rgb else None)

    depth, _ = _render(height, width, need_rgb=False)
    _, rgb_hi = _render(height * ss, width * ss)
    rgb = cv2.resize(rgb_hi, (width, height), interpolation=cv2.INTER_AREA)
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), depth


def render_perspective(scene: Scene, bank, dirs: np.ndarray):
    """Render RGB + range for arbitrary ray directions (h,w,3) -- used to validate tangent projection."""
    h, w = dirs.shape[:2]
    d = dirs.reshape(-1, 3)
    t, sid, n, p = cast(scene, d)
    rgb = shade(scene, bank, d, t, sid, n, p)
    return (np.clip(rgb.reshape(h, w, 3), 0, 1) * 255 + 0.5).astype(np.uint8), t.reshape(h, w)


def generate_dataset(out_dir: str, n: int = 24, height: int = 512, width: int = 1024, seed: int = 0,
                     ss: int = 2) -> List[dict]:
    """Write rgb/*.png, depth/*.npy (float32 metres), scenes.json and a fixed split list."""
    os.makedirs(os.path.join(out_dir, "rgb"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "depth"), exist_ok=True)
    bank = _texture_bank(seed)
    rng = np.random.default_rng(seed)
    meta = []
    for i in range(n):
        scene = random_scene(rng, len(bank))
        rgb, depth = render_erp(scene, bank, height, width, ss=ss)
        name = f"scene_{i:04d}"
        cv2.imwrite(os.path.join(out_dir, "rgb", name + ".png"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        np.save(os.path.join(out_dir, "depth", name + ".npy"), depth.astype(np.float32))
        meta.append({"name": name, "scene": scene.to_dict()})
        print(f"[synthetic] {name}: range {depth.min():.2f}-{depth.max():.2f} m")
    with open(os.path.join(out_dir, "scenes.json"), "w") as f:
        json.dump({"seed": seed, "height": height, "width": width, "scenes": meta}, f)
    with open(os.path.join(out_dir, "test.txt"), "w") as f:
        for m in meta:
            f.write(f"rgb/{m['name']}.png depth/{m['name']}.npy\n")
    return meta


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/synthetic")
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--height", type=int, default=512)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    generate_dataset(a.out, a.n, a.height, a.width, a.seed)
