"""Experiment 2: ERP + selective polar tangent-plane correction (report + tangent visualisations)."""
from __future__ import annotations

import os

import numpy as np

from geometry.tangent_plane import tangent_to_erp
from inference.pipeline import DistortionAwareInference, MethodConfig
from inference.tangent_inference import render_tangent_images
from visualization.visualize import tangent_panel

from .common import improvement_vs_baseline, method_table, write_markdown_table


def report(df, out_dir, method_name: str, csv_path: str):
    os.makedirs(out_dir, exist_ok=True)
    tab = method_table(df, ["baseline", method_name])
    imp = improvement_vs_baseline(df, method_name)
    imp_area = improvement_vs_baseline(df, method_name, weighting="area")
    tab.to_csv(csv_path)
    imp.to_csv(csv_path.replace(".csv", "_improvement.csv"), index=False)
    imp_area.to_csv(csv_path.replace(".csv", "_improvement_area.csv"), index=False)
    write_markdown_table(imp, csv_path.replace(".csv", "_improvement.md"))
    return tab, imp


def visualize_tangent_views(model, sample, cfg: MethodConfig, out_dir: str, max_views: int = 2):
    """Original polar region | tangent image | model prediction | re-projected prediction."""
    dai = DistortionAwareInference(model, use_cache=False)
    planes = dai.planes_for(cfg)[:max_views]
    imgs = render_tangent_images(sample.rgb, planes)
    preds = model.predict_batch(imgs, kind="perspective")
    H, W = sample.depth.shape
    for k, (p, im, pr) in enumerate(zip(planes, imgs, preds)):
        r = tangent_to_erp(pr.astype(np.float64), p, H, W)
        tangent_panel(sample.rgb, p, im, pr, r.values, r.valid, sample.depth,
                      os.path.join(out_dir, f"tangent_view_{sample.id}_{k}.png"),
                      title=f"{sample.id}: tangent view {k} (raw model output, before alignment)")
