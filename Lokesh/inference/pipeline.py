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
from .fusion import confidence_fusion, fuse_with_baseline, merge_views
from .rotation_inference import predict_rotated_raw, unrotate_predictions
from .tangent_inference import predict_tangent_raw, reproject_tangent_predictions


@dataclass
class MethodConfig:
    method: str = "baseline"  # baseline | tangent | rotation | hybrid
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
