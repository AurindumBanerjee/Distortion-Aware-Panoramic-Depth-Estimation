"""Shared experiment machinery: config loading, seeding, the method plan, the evaluation loop."""
from __future__ import annotations

import copy
import json
import os
import platform
import random
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import yaml

from datasets.panorama import PanoramaDataset
from evaluation.evaluation import Evaluator
from evaluation.metrics import error_maps
from inference.pipeline import DistortionAwareInference, MethodConfig
from models.depth_model import build_model


# ----------------------------------------------------------------------------
# Config / reproducibility
# ----------------------------------------------------------------------------

def load_config(path: str, overrides: Optional[List[str]] = None) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    for o in overrides or []:  # key.sub=value (YAML-parsed value)
        k, v = o.split("=", 1)
        d = cfg
        ks = k.split(".")
        for kk in ks[:-1]:
            d = d.setdefault(kk, {})
        d[ks[-1]] = yaml.safe_load(v)
    return cfg


def seed_everything(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass


def environment_info() -> dict:
    return {"python": sys.version.split()[0], "torch": torch.__version__, "platform": platform.platform(),
            "cuda": torch.cuda.is_available(), "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cpu_threads": torch.get_num_threads(), "time": time.strftime("%Y-%m-%d %H:%M:%S")}


def peak_rss_mb() -> float:
    try:
        import resource  # Unix only
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except ImportError:  # Windows: peak working set
        import psutil
        return psutil.Process().memory_info().peak_wset / (1024.0 * 1024.0)


# ----------------------------------------------------------------------------
# Method plan
# ----------------------------------------------------------------------------

MAIN_TAGS = ("E2_tangent", "E3_rotation", "E4_hybrid", "E10_acgf", "E11_mono360")

def default_rotset_name(cfg: dict) -> str:
    inf = cfg["inference"]
    for name, rs in cfg["experiments"].get("rotation_sets", {}).items():
        if [list(map(float, r)) for r in rs] == [list(map(float, r)) for r in inf["rotation_angles"]]:
            return name
    return "default"


def _mc(method, inf, thr=None, views=None, rotset=None, fusion=None, merge=None, extra_tag="", seam=None):
    thr = inf["polar_threshold"] if thr is None else thr
    views = inf["views_per_pole"] if views is None else views
    rs_name, rs = rotset if rotset is not None else (inf.get("_rotset_name", "default"), None)
    rs = rs if rs is not None else inf["rotation_angles"]
    fusion = fusion or inf["fusion_method"]
    merge = merge or inf["merge"]
    parts = [method, f"t{int(thr)}"]
    if method in ("tangent", "hybrid"):
        parts.append(f"v{views}")
    if method in ("rotation", "hybrid"):
        parts.append(rs_name)
    parts += [fusion, merge]
    seam = inf.get("seam_width", 20.0) if seam is None else seam
    if seam != inf.get("seam_width", 20.0):
        extra_tag += f"|seam{int(seam)}"
    return MethodConfig(method=method, lat_threshold=thr, views_per_pole=views, tangent_size=inf["tangent_size"],
                        rotations=[list(map(float, r)) for r in rs], merge=merge, fusion=fusion, band=inf["band"],
                        power=inf["power"], align=inf["align"], seam_width=seam, range_guard=inf.get("range_guard", False),
                        name="|".join(parts) + extra_tag)


# ACGF ablations: name suffix -> overrides of the configured ACGF defaults
ACGF_ABLATIONS = {
    "nogate": dict(acgf_gate=False),
    "value": dict(acgf_domain="value"),
    "law": dict(acgf_law="on"),
    "screen-base": dict(acgf_screen="baseline"),
    "GG": dict(acgf_views=[["gnomonic", 110.0, 0.0], ["gnomonic", 110.0, 45.0]]),
    "SS": dict(acgf_views=[["stereo", 180.0, 0.0], ["stereo", 180.0, 45.0]]),
    "S150": dict(acgf_views=[["stereo", 150.0, 0.0], ["gnomonic", 110.0, 45.0]]),
    "+rot": dict(acgf_rotations=[[0.0, 90.0, 0.0], [0.0, -90.0, 0.0]]),
}


def _acgf(inf, name="acgf", **over):
    a = dict(inf.get("acgf", {}))
    kw = dict(acgf_views=[list(v) for v in a.get("views", [["stereo", 180.0, 0.0], ["gnomonic", 110.0, 45.0]])],
              acgf_screen=a.get("screen", "value"), acgf_lambda_cap=a.get("lambda_cap", 5.0),
              acgf_lambda_edge=a.get("lambda_edge", 50.0), acgf_gate_sigma=a.get("gate_sigma", 3.0),
              acgf_irls=a.get("irls", 1), acgf_law=a.get("law", "off"))
    kw.update(over)
    return MethodConfig(method="acgf", lat_threshold=inf["polar_threshold"], tangent_size=inf["tangent_size"],
                        band=inf["band"], name=name, **kw)


def build_plan(cfg: dict) -> List[Tuple[List[str], MethodConfig]]:
    """All (tags, MethodConfig) to run on every image. Identical configs are run once and carry all tags."""
    inf, ex = dict(cfg["inference"]), cfg["experiments"]
    inf["_rotset_name"] = default_rotset_name(cfg)
    plan: Dict[str, Tuple[List[str], MethodConfig]] = {}

    def add(tag, mc: MethodConfig):
        if mc.name in plan:
            plan[mc.name][0].append(tag)
        else:
            plan[mc.name] = ([tag], mc)

    add("E1_baseline", MethodConfig("baseline", name="baseline"))
    add("E2_tangent", _mc("tangent", inf))
    add("E3_rotation", _mc("rotation", inf))
    add("E4_hybrid", _mc("hybrid", inf))
    for thr in ex["thresholds"]:
        for m in ("tangent", "rotation", "hybrid"):
            add("E5_threshold", _mc(m, inf, thr=thr))
    for v in ex["views_per_pole"]:
        add("E6_views", _mc("tangent", inf, views=v))
        add("E6_views", _mc("hybrid", inf, views=v))
    for f in ex["fusions"]:
        for m in ("tangent", "rotation", "hybrid"):
            add("E7_fusion", _mc(m, inf, fusion=f))
    for mg in ex["merge_modes"]:
        add("E7_merge", _mc("rotation", inf, rotset=("pitch90_x4", ex["rotation_sets"]["pitch90_x4"]), merge=mg))
        add("E7_merge", _mc("hybrid", inf, merge=mg))
    for m in ("rotation", "hybrid"):
        add("E7_seam", _mc(m, inf))
        add("E7_seam", _mc(m, inf, seam=0.0))
    # control for the hybrid: tangent views + yaw-only rotations (extra passes that do NOT move the poles)
    if "yaw_only_x3" in ex["rotation_sets"]:
        add("E4_hybrid_control", _mc("hybrid", inf, rotset=("yaw_only_x3", ex["rotation_sets"]["yaw_only_x3"])))
        add("E4_hybrid_control", _mc("hybrid", inf))
    for name, rs in ex["rotation_sets"].items():
        add("E3_rotation_sets", _mc("rotation", inf, rotset=(name, rs)))
        add("E3_rotation_sets", _mc("rotation", inf, rotset=(name, rs), fusion="confidence"))
    # Anchored Conformal Gradient Fusion (E10) and the 360MonoDepth-style baseline (E11)
    add("E10_acgf", _acgf(inf))
    for suffix, over in ACGF_ABLATIONS.items():
        add("E10_acgf_ablation", _acgf(inf, f"acgf|{suffix}", **over))
    for thr in ex["thresholds"]:
        add("E10_acgf_threshold", _acgf(dict(inf, polar_threshold=thr), f"acgf|t{int(thr)}"))
    if ex.get("mono360", False):
        add("E11_mono360", MethodConfig(method="mono360", tangent_size=inf["tangent_size"], name="mono360"))
    # name the default rotation set consistently
    out = []
    for name, (tags, mc) in plan.items():
        out.append((tags, mc))
    return out


def resolve_eval_align(cfg: dict, model) -> str:
    ea = cfg["evaluation"]["eval_align"]
    if ea != "auto":
        return ea
    if model.spec.space == "disparity":
        return "affine"
    return {"metric": "none", "scale": "median", "affine": "median"}[model.spec.scale]


def make_model(cfg: dict):
    model = build_model(dict(cfg["model"]))
    tmodel = build_model(dict(cfg["tangent_model"])) if cfg.get("tangent_model") else None
    return model, tmodel


def make_dataset(cfg: dict, height=None, width=None, limit=None) -> PanoramaDataset:
    d = cfg["dataset"]
    return PanoramaDataset(d["root"], d["list"], height or d["height"], width or d["width"], name=d["name"],
                           limit=limit if limit is not None else d.get("limit"),
                           depth_scale=d.get("depth_scale"), max_depth=d.get("max_depth"),
                           min_depth=d.get("min_depth"))


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------

def run_plan(cfg: dict, plan, model, tmodel, dataset, out_dir: str, tag_prefix: str = "", qualitative: int = 0,
             heatmap_methods: Optional[List[str]] = None, log=print) -> Dict[str, Evaluator]:
    """Runs every method of the plan on every image; returns one Evaluator per alignment region."""
    os.makedirs(out_dir, exist_ok=True)
    ev_cfg = cfg["evaluation"]
    ea = resolve_eval_align(cfg, model)
    evaluators = {r: Evaluator(model.spec.space, ea, ev_cfg["bands"], ev_cfg["bad_threshold"], ev_cfg["profile_bin"],
                               ev_cfg.get("max_depth", 100.0), align_region=r) for r in ev_cfg["align_regions"]}
    dai = DistortionAwareInference(model, tmodel, batch_size=cfg["inference"]["batch_size"])
    heat = {}
    heat_n = {}
    tag_of = {mc.name: tags for tags, mc in plan}
    qdir = os.path.join(out_dir, "predictions")
    for i, s in enumerate(dataset):
        t0 = time.time()
        for tags, mc in plan:
            res = dai.run(s.rgb, s.id, mc)
            info = {k: res[k] for k in ("runtime_s", "model_time_s", "post_time_s", "model_calls", "extra_model_calls",
                                        "peak_mem_mb", "n_tangent_views", "n_rotations")}
            info.update({"tags": ";".join(tag_prefix + t for t in tags), "family": mc.method,
                         "lat_threshold": mc.lat_threshold, "fusion": mc.fusion, "merge": mc.merge,
                         "views_per_pole": mc.views_per_pole, "n_rot": len(mc.rotations),
                         "height": s.rgb.shape[0], "width": s.rgb.shape[1]})
            for r, ev in evaluators.items():
                depth = ev.add(s.id, mc.name, res["pred"], s.depth, s.valid, info)
                if r == "all" and heatmap_methods and mc.name in heatmap_methods:
                    e = error_maps(depth, np.nan_to_num(s.depth, nan=1.0), s.valid)["abs_rel"]
                    heat.setdefault(mc.name, np.zeros_like(e))
                    heat_n.setdefault(mc.name, np.zeros_like(e))
                    heat[mc.name] += np.nan_to_num(e)
                    heat_n[mc.name] += np.isfinite(e)
                if r == "all" and i < qualitative and (mc.name == "baseline" or set(tags) & set(MAIN_TAGS)):
                    os.makedirs(qdir, exist_ok=True)
                    np.savez_compressed(os.path.join(qdir, f"{s.id}__{mc.name.replace('|', '_')}.npz"),
                                        pred_metric=depth.astype(np.float32), pred_native=res["pred"].astype(np.float32))
        dai.clear_cache()
        log(f"[{i + 1}/{len(dataset)}] {s.id}: {len(plan)} methods in {time.time() - t0:.1f}s "
            f"(peak RSS {peak_rss_mb():.0f} MB)")
    for name in heat:
        np.save(os.path.join(out_dir, f"heatmap__{name.replace('|', '_')}.npy"), heat[name] / np.maximum(heat_n[name], 1))
    for r, ev in evaluators.items():
        ev.frame().to_csv(os.path.join(out_dir, f"rows_align-{r}.csv"), index=False)
        np.savez_compressed(os.path.join(out_dir, f"profiles_align-{r}.npz"), centres=ev.profile_centres,
                            **{k.replace("|", "_"): np.stack(v) for k, v in ev.profiles.items()})
    return evaluators


# ----------------------------------------------------------------------------
# Reporting helpers
# ----------------------------------------------------------------------------

BANDS = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90"]


def method_table(df: pd.DataFrame, methods: List[str], weighting: str = "pixel",
                 metrics=("abs_rel", "sq_rel", "rmse", "rmse_log", "mae", "medae", "d1", "d2", "d3", "pct_bad")):
    """Global ('all') metrics + polar (|lat|>=60) AbsRel + runtime for a list of methods."""
    d = df[(df.weighting == weighting) & (df.method.isin(methods))]
    g = d[d.band == "all"].groupby("method", sort=False)[list(metrics)].mean()
    for b in BANDS:
        g[f"abs_rel_{b}"] = d[d.band == b].groupby("method", sort=False)["abs_rel"].mean()
    polar = d[d.band.isin(["60-75", "75-90"])]
    # pixel-count-weighted polar AbsRel per image, then mean over images
    pp = polar.groupby(["method", "image"]).apply(lambda x: np.average(x.abs_rel, weights=x.n), include_groups=False)
    g["abs_rel_polar_60_90"] = pp.groupby("method").mean()
    rt = d[d.band == "all"].groupby("method", sort=False)[["runtime_s", "model_calls"]].mean()
    g = g.join(rt)
    base_rt = rt.loc["baseline", "runtime_s"] if "baseline" in rt.index else np.nan
    g["runtime_ratio"] = g["runtime_s"] / base_rt
    return g.reindex(methods)


def improvement_vs_baseline(df: pd.DataFrame, method: str, metric="abs_rel", weighting="pixel"):
    from evaluation.evaluation import improvement_table
    hib = metric.startswith("d") and metric[1:].isdigit()
    return improvement_table(df, "baseline", method, metric, weighting, higher_is_better=hib)


def write_markdown_table(df: pd.DataFrame, path: str, floatfmt=".4f"):
    with open(path, "w") as f:
        f.write(df.to_markdown(floatfmt=floatfmt))
