"""Experiments 5-9: thresholds, number of tangent views, fusion strategies, resolution, runtime."""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd

from pano.inference.pipeline import DistortionAwareInference
from pano.visualization.visualize import plot_latitude_profiles, plot_runtime_tradeoff

from .common import method_table, write_markdown_table

COLS = ["abs_rel", "rmse", "d1", "abs_rel_0-15", "abs_rel_30-45", "abs_rel_45-60", "abs_rel_60-75", "abs_rel_75-90",
        "abs_rel_polar_60_90", "model_calls", "runtime_ratio"]


def _select(df, tag):
    return [m for m in df.method.unique() if any(t.endswith(tag) for t in
                                                 df[df.method == m].tags.iloc[0].split(";"))]


def ablation_tables(df, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    out = {}
    for tag in ["E5_threshold", "E6_views", "E7_fusion", "E7_merge", "E7_seam", "E3_rotation_sets", "E4_hybrid_control"]:
        ms = ["baseline"] + sorted(_select(df, tag))
        tab = method_table(df, ms)
        tab.insert(0, "experiment", tag)
        out[tag] = tab
        write_markdown_table(tab[[c for c in COLS if c in tab]], os.path.join(out_dir, f"{tag}.md"))
    allt = pd.concat(out.values())
    allt.to_csv(os.path.join(out_dir, "..", "ablation.csv"))
    return out


def profile_plots(evaluator, out_dir, groups: dict, tag="align-all"):
    """groups: title -> list of method names (first = baseline)."""
    c = evaluator.profile_centres
    for title, ms in groups.items():
        prof = {m: np.stack(evaluator.profiles[m]) for m in ms if m in evaluator.profiles}
        if len(prof) < 2:
            continue
        short = {m: m.replace("|prior", "").replace("|", " ") for m in prof}
        plot_latitude_profiles(c, {short[m]: v for m, v in prof.items()},
                               os.path.join(out_dir, f"profile_{title}_{tag}.png"),
                               title=f"AbsRel vs |latitude|: {title} ({tag})")


def runtime_tradeoff(df, out_dir):
    tab = method_table(df, list(df.method.unique()))
    tab = tab.reset_index().rename(columns={"index": "method"})
    tab["family"] = tab["method"].str.split("|").str[0]
    tab["polar_abs_rel"] = tab["abs_rel_polar_60_90"]
    tab["annotate"] = tab["method"].isin(["baseline"]) | tab["method"].str.contains(r"\|t45\|.*cosine\|prior$")
    tab.to_csv(os.path.join(out_dir, "runtime_vs_accuracy.csv"), index=False)
    plot_runtime_tradeoff(tab, os.path.join(out_dir, "runtime_vs_accuracy.png"))
    return tab


def cold_timing(model, tmodel, dataset, plan_items, n_images: int, out_dir: str, log=print):
    """Uncached wall-clock timing: every method recomputes all of its model passes."""
    rows = []
    for i, s in enumerate(dataset):
        if i >= n_images:
            break
        for tags, mc in plan_items:
            dai = DistortionAwareInference(model, tmodel, use_cache=False)
            model.reset_counters()
            import torch
            if model.device.type == "cuda":
                torch.cuda.reset_peak_memory_stats()
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            res = dai.run(s.rgb, s.id, mc)
            if model.device.type == "cuda":
                torch.cuda.synchronize()
            rows.append({"image": s.id, "method": mc.name, "wall_s": time.perf_counter() - t0,
                         "model_calls": res["model_calls"], "model_time_s": res["model_time_s"],
                         "post_time_s": res["post_time_s"],
                         "peak_gpu_mem_mb": (torch.cuda.max_memory_allocated() / 2 ** 20)
                         if model.device.type == "cuda" else float("nan")})
        log(f"[timing] {s.id}")
    df = pd.DataFrame(rows)
    g = df.groupby("method", sort=False).mean(numeric_only=True)
    g["overhead_x"] = g["wall_s"] / g.loc["baseline", "wall_s"]
    g.to_csv(os.path.join(out_dir, "runtime_cold.csv"))
    write_markdown_table(g, os.path.join(out_dir, "runtime_cold.md"), floatfmt=".3f")
    return g
