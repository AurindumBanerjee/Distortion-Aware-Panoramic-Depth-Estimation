"""DistortionAwareInference: the model-agnostic orchestration layer.

    DepthModelWrapper  (frozen, black box: predict(image, kind))
            |
    DistortionAwareInference.run(rgb, method_cfg)
            |-- baseline ERP pass
            |-- polar tangent views      (tangent_inference)
            |-- rotated-sphere passes    (rotation_inference)
            |-- alignment to baseline on trusted pixels (no GT)
            |-- merge views + fuse with baseline (fusion)
            v
       final ERP depth (fusion space of the model) + bookkeeping

Raw model outputs are cached per (image, view) so that ablations sharing views (e.g. the
fusion-strategy sweep) do not re-run the model. Runtime is still accounted correctly: each
cached entry stores the time and peak memory of the forward pass that produced it, and a
method's runtime is the sum over the views it uses plus its own (measured) fusion time.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import torch

from geometry.tangent_plane import TangentPlane, polar_tangent_layout
from models.depth_model import DepthModelWrapper

from .baseline import ViewPrediction
from .conformal_fusion import DEFAULT_VIEWS, ACGFParams, RotatedView, acgf_fuse, pole_views, predict_views_raw
from .fusion import confidence_fusion, fuse_with_baseline, merge_views
from .mono360 import icosahedron_planes, mono360_fuse
from .rotation_inference import predict_rotated_raw, unrotate_predictions
from .tangent_inference import predict_tangent_raw, reproject_tangent_predictions


@dataclass
class MethodConfig:
    method: str = "baseline"  # baseline | tangent | rotation | hybrid | acgf | mono360
    lat_threshold: float = 45.0
    views_per_pole: int = 1
    tangent_fov: Optional[float] = None
    tangent_size: int = 384
    rotations: List[List[float]] = field(default_factory=lambda: [[0.0, 90.0, 0.0]])
    merge: str = "prior"  # prior | mean | median
    fusion: str = "cosine"  # hard | linear | sigmoid | cosine | polynomial | confidence
    band: float = 20.0
    power: float = 2.0
    prior_power: float = 2.0
    align: str = "auto"  # auto | none | scale | affine
    tangent_geometry: Optional[str] = None  # override the model's declared pinhole geometry
    sigma_agree: float = 0.10
    sigma_local: float = 0.05
    seam_width: float = 20.0  # deg; 0 disables the ERP-seam prior
    # Plausibility guard for tangent / rotation / hybrid views: aligned values outside
    # [0.5 * p1, 2 * p99] of the baseline (fusion space) are invalid instead of being fused.
    range_guard: bool = False
    # ACGF (inference/conformal_fusion.py)
    acgf_views: List[List[Any]] = field(default_factory=lambda: [list(v) for v in DEFAULT_VIEWS])
    acgf_domain: str = "gradient"  # gradient | value
    acgf_screen: str = "value"  # value | baseline
    acgf_rotations: List[List[float]] = field(default_factory=list)  # extra pitch-rotated ERP views (ablation)
    acgf_gate: bool = True
    acgf_law: str = "auto"  # auto | on | off  (stereographic magnification correction)
    acgf_lambda_cap: float = 5.0
    acgf_lambda_edge: float = 50.0
    acgf_gate_sigma: float = 3.0
    acgf_irls: int = 1
    # 360MonoDepth-style baseline (inference/mono360.py)
    mono360_padding: float = 0.3
    name: Optional[str] = None

    def label(self) -> str:
        if self.name:
            return self.name
        if self.method == "baseline":
            return "baseline"
        s = f"{self.method}_t{int(self.lat_threshold)}_{self.fusion}"
        if self.method in ("tangent", "hybrid"):
            s += f"_v{self.views_per_pole}"
        if self.method in ("rotation", "hybrid"):
            s += f"_r{len(self.rotations)}"
        return s


def _key(*parts) -> str:
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


class DistortionAwareInference:
    def __init__(self, model: DepthModelWrapper, tangent_model: Optional[DepthModelWrapper] = None,
                 batch_size: int = 4, use_cache: bool = True):
        self.model = model
        self.tangent_model = tangent_model or model
        self.batch_size = batch_size
        self.use_cache = use_cache
        self.cache: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------ raw model calls (cached)
    def _timed(self, key: Optional[str], fn, n_calls: int):
        if key is not None and self.use_cache and key in self.cache:
            return self.cache[key]
        dev = self.model.device
        if dev.type == "cuda":
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        out = fn()
        if dev.type == "cuda":
            torch.cuda.synchronize()
        entry = {"out": out, "time": time.perf_counter() - t0, "calls": n_calls,
                 "peak_mem_mb": (torch.cuda.max_memory_allocated() / 2 ** 20) if dev.type == "cuda" else float("nan")}
        if key is not None and self.use_cache:
            self.cache[key] = entry
        return entry

    def baseline_raw(self, rgb, image_id):
        k = _key("base", self.model.name, image_id, rgb.shape)
        return self._timed(k, lambda: self.model.predict(rgb, kind="erp").astype(np.float64), 1)

    def tangent_raw(self, rgb, image_id, plane: TangentPlane):
        k = _key("tan", self.tangent_model.name, image_id, rgb.shape, plane.to_dict())
        return self._timed(k, lambda: predict_tangent_raw(self.tangent_model, rgb, [plane], self.batch_size)[0], 1)

    def tangent_raw_batch(self, rgb, image_id, planes: Sequence[TangentPlane]):
        """Batched computation of all uncached planes; time is split evenly per view."""
        keys = [_key("tan", self.tangent_model.name, image_id, rgb.shape, p.to_dict()) for p in planes]
        todo = [i for i, k in enumerate(keys) if not (self.use_cache and k in self.cache)]
        if todo:
            entry = self._timed(None,
                                lambda: predict_tangent_raw(self.tangent_model, rgb, [planes[i] for i in todo],
                                                            self.batch_size), len(todo))
            for j, i in enumerate(todo):
                self.cache[keys[i]] = {"out": entry["out"][j], "time": entry["time"] / len(todo), "calls": 1,
                                       "peak_mem_mb": entry["peak_mem_mb"]}
        return [self.cache[k] for k in keys]

    def rotated_raw_batch(self, rgb, image_id, angles):
        keys = [_key("rot", self.model.name, image_id, rgb.shape, list(a)) for a in angles]
        todo = [i for i, k in enumerate(keys) if not (self.use_cache and k in self.cache)]
        if todo:
            entry = self._timed(None,
                                lambda: predict_rotated_raw(self.model, rgb, [angles[i] for i in todo],
                                                            batch_size=max(1, self.batch_size // 2)), len(todo))
            for j, i in enumerate(todo):
                self.cache[keys[i]] = {"out": entry["out"][j], "time": entry["time"] / len(todo), "calls": 1,
                                       "peak_mem_mb": entry["peak_mem_mb"]}
        return [self.cache[k] for k in keys]

    def views_raw_batch(self, rgb, image_id, views):
        """Pole views of any projection (stereographic / gnomonic), batched and cached like tangent views."""
        keys = [_key("view", self.tangent_model.name, image_id, rgb.shape, type(v).__name__, v.to_dict())
                for v in views]
        todo = [i for i, k in enumerate(keys) if not (self.use_cache and k in self.cache)]
        if todo:
            entry = self._timed(None, lambda: predict_views_raw(self.tangent_model, rgb, [views[i] for i in todo],
                                                                self.batch_size), len(todo))
            for j, i in enumerate(todo):
                self.cache[keys[i]] = {"out": entry["out"][j], "time": entry["time"] / len(todo), "calls": 1,
                                       "peak_mem_mb": entry["peak_mem_mb"]}
        return [self.cache[k] for k in keys]

    def clear_cache(self, image_id=None):
        self.cache.clear()

    # ------------------------------------------------------------------ main entry
    def resolve_align(self, cfg: MethodConfig) -> str:
        if cfg.align != "auto":
            return cfg.align
        return {"metric": "none", "scale": "scale", "affine": "affine"}[self.model.spec.scale]

    def planes_for(self, cfg: MethodConfig) -> List[TangentPlane]:
        return polar_tangent_layout(cfg.lat_threshold, views_per_pole=cfg.views_per_pole, fov_deg=cfg.tangent_fov,
                                    size=cfg.tangent_size)

    def run(self, rgb: np.ndarray, image_id: str, cfg: MethodConfig, return_views: bool = False) -> Dict[str, Any]:
        H, W = rgb.shape[:2]
        b = self.baseline_raw(rgb, image_id)
        from geometry.spherical import latitude_map
        from geometry.spherical import erp_lonlat_grid
        base = ViewPrediction("baseline", b["out"], np.isfinite(b["out"]), latitude_map(H, W),
                              view_lon=np.degrees(erp_lonlat_grid(H, W)[0].numpy()))
        if cfg.method in ("acgf", "mono360"):
            return self._run_view_method(rgb, image_id, cfg, b, return_views)
        used = [b]
        views: List[ViewPrediction] = []
        align = self.resolve_align(cfg)
        planes: List[TangentPlane] = []
        t_post = 0.0
        if cfg.method in ("tangent", "hybrid"):
            planes = self.planes_for(cfg)
            entries = self.tangent_raw_batch(rgb, image_id, planes)
            used += entries
            t0 = time.perf_counter()
            tangent_align = align
            if self.tangent_model is not self.model and align == "none":
                tangent_align = "scale"  # different model -> at least match scale
            views += reproject_tangent_predictions([e["out"] for e in entries], planes, self.tangent_model, base,
                                                   cfg.lat_threshold, tangent_align,
                                                   geometry_override=cfg.tangent_geometry)
            t_post += time.perf_counter() - t0
        if cfg.method in ("rotation", "hybrid"):
            entries = self.rotated_raw_batch(rgb, image_id, cfg.rotations)
            used += entries
            t0 = time.perf_counter()
            views += unrotate_predictions([e["out"] for e in entries], cfg.rotations, self.model, base,
                                          cfg.lat_threshold, align, seam_width=cfg.seam_width)
            t_post += time.perf_counter() - t0

        if cfg.range_guard and views:
            views = [_guard_view(v, base.values) for v in views]
        t0 = time.perf_counter()
        extra: Dict[str, Any] = {}
        if cfg.method == "baseline" or not views:
            final = base.values.copy()
            corr, corr_valid = None, None
        elif cfg.fusion == "confidence":
            final, extra = confidence_fusion(base, views, cfg.prior_power, cfg.sigma_agree, cfg.sigma_local,
                                             seam_width=cfg.seam_width)
            corr, corr_valid, _ = merge_views(views, cfg.merge, cfg.prior_power, seam_width=cfg.seam_width)
        else:
            corr, corr_valid, _ = merge_views(views, cfg.merge, cfg.prior_power, seam_width=cfg.seam_width)
            final = fuse_with_baseline(base, corr, corr_valid, cfg.fusion, cfg.lat_threshold, cfg.band, cfg.power)
        t_post += time.perf_counter() - t0

        res = {
            "pred": final, "baseline": base.values, "corrected": corr, "corrected_valid": corr_valid,
            "label": cfg.label(),
            "runtime_s": sum(e["time"] for e in used) + t_post,
            "model_time_s": sum(e["time"] for e in used),
            "post_time_s": t_post,
            "model_calls": int(sum(e["calls"] for e in used)),
            "extra_model_calls": int(sum(e["calls"] for e in used)) - 1,
            "peak_mem_mb": float(np.nanmax([e["peak_mem_mb"] for e in used])) if self.model.device.type == "cuda" else float("nan"),
            "align": align, "n_tangent_views": len(planes),
            "n_rotations": len(cfg.rotations) if cfg.method in ("rotation", "hybrid") else 0,
            "align_info": [v.meta.get("align") for v in views],
        }
        if return_views:
            res["views"] = views
            res["planes"] = planes
            res.update(extra)
        return res

    def _run_view_method(self, rgb, image_id, cfg: MethodConfig, b, return_views: bool) -> Dict[str, Any]:
        """ACGF and the 360MonoDepth-style baseline: extra pinhole / stereographic views, own fusion."""
        H, W = rgb.shape[:2]
        if cfg.method == "acgf":
            pv = pole_views(cfg.acgf_views, cfg.tangent_size)
            entries = self.views_raw_batch(rgb, image_id, [v for _, v in pv])
            if cfg.acgf_rotations:  # optional pitch-rotated ERP passes (shared cache with rotation / hybrid)
                rot = self.rotated_raw_batch(rgb, image_id, cfg.acgf_rotations)
                for ang, e in zip(cfg.acgf_rotations, rot):
                    rv = RotatedView(tuple(float(a) for a in ang), cfg.seam_width)
                    pv += [(1, rv), (-1, rv)]
                    entries += [e, dict(e, time=0.0, calls=0)]  # one pass serves both hemispheres
            law = cfg.acgf_law == "on" or (cfg.acgf_law == "auto" and self.tangent_model.appearance_scale_law)
            params = ACGFParams(lat_threshold=cfg.lat_threshold, band=cfg.band, prior_power=cfg.prior_power,
                                domain=cfg.acgf_domain, screen=cfg.acgf_screen, gate=cfg.acgf_gate, lambda_cap=cfg.acgf_lambda_cap,
                                lambda_edge=cfg.acgf_lambda_edge, gate_sigma_deg=cfg.acgf_gate_sigma,
                                irls_iters=cfg.acgf_irls)
            t0 = time.perf_counter()
            final, extra = acgf_fuse(b["out"], [e["out"] for e in entries], pv, self.tangent_model, params, law,
                                     perspective_geometry=cfg.tangent_geometry)
            used, n_views = [b] + entries, len(pv)
        else:
            if self.tangent_model.spec.space != "disparity":
                raise ValueError("mono360 is defined for disparity models only")
            planes = icosahedron_planes(cfg.tangent_size, cfg.mono360_padding)
            entries = self.tangent_raw_batch(rgb, image_id, planes)
            t0 = time.perf_counter()
            final, extra = mono360_fuse([e["out"] for e in entries], planes, H, W,
                                        cfg.tangent_geometry or self.tangent_model.geometry("perspective"))
            used, n_views = entries, len(planes)  # the method does not use the ERP pass
        t_post = time.perf_counter() - t0
        calls = int(sum(e["calls"] for e in used))
        res = {
            "pred": final, "baseline": b["out"], "corrected": None, "corrected_valid": None, "label": cfg.label(),
            "runtime_s": sum(e["time"] for e in used) + t_post, "model_time_s": sum(e["time"] for e in used),
            "post_time_s": t_post, "model_calls": calls, "extra_model_calls": calls - 1,
            "peak_mem_mb": float(np.nanmax([e["peak_mem_mb"] for e in used])) if self.model.device.type == "cuda" else float("nan"),
            "align": "gradient" if cfg.method == "acgf" else "deformable", "n_tangent_views": n_views, "n_rotations": 0,
            "align_info": extra.get("view_info", []),
        }
        if return_views:
            res.update(extra)
        return res


def _guard_view(v: ViewPrediction, base: np.ndarray, g0: float = 0.5, g1: float = 2.0) -> ViewPrediction:
    """Invalidate aligned view values outside the baseline's plausible range (see MethodConfig.range_guard)."""
    fin = np.isfinite(base)
    lo, hi = g0 * np.percentile(base[fin], 1), g1 * np.percentile(base[fin], 99)
    ok = v.valid & np.isfinite(v.values) & (v.values > lo) & (v.values < hi)
    v.meta["guard_rejected"] = int((v.valid & ~ok).sum())
    return ViewPrediction(v.source, np.where(ok, v.values, np.nan), ok, v.view_lat, v.meta, v.cos_axis, v.view_lon)
