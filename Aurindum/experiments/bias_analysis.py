"""Signed-error analysis of the individual correction views (why does the hybrid work?).

For each image: the baseline, each tangent view and each rotated view are aligned to the
baseline exactly as in the pipeline (no GT), then converted to metric depth with the SAME
GT alignment parameters as the baseline (fitted on |lat| < 30 deg of the baseline), and the
signed log error log(pred / gt) is averaged over polar pixels (|lat| >= 60). If tangent and
rotated views err in opposite directions, averaging them cancels bias, which would explain
a hybrid gain larger than either component.

    python -m experiments.bias_analysis --config configs/default.yaml --n 8
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from experiments.common import load_config, make_dataset, make_model
from geometry.spherical import latitude_map
from inference.pipeline import DistortionAwareInference, MethodConfig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()
    cfg = load_config(a.config)
    model, tmodel = make_model(cfg)
    ds = make_dataset(cfg, limit=a.n)
    dai = DistortionAwareInference(model, tmodel)
    inf = cfg["inference"]
    mc = MethodConfig("hybrid", lat_threshold=inf["polar_threshold"], tangent_size=inf["tangent_size"],
                      rotations=inf["rotation_angles"])
    rows = []
    for s in ds:
        H, W = s.depth.shape
        lat = latitude_map(H, W)
        r = dai.run(s.rgb, s.id, mc, return_views=True)
        gt = np.nan_to_num(s.depth, nan=1.0)
        fit = s.valid & (np.abs(lat) < 30)
        space = model.spec.space
        # GT alignment parameters of the baseline, reused for every view (so only view differences show)
        from evaluation.metrics import to_metric_depth as tmd
        _, info = tmd(r["baseline"], gt, fit, space, "affine" if space == "disparity" else "none")
        def metric(x):
            if space == "disparity":
                d = np.clip(info["scale"] * x + info["shift"], 1e-3, 1e3)
                return 1.0 / d
            return x
        polar = s.valid & (np.abs(lat) >= 60)
        cands = [("baseline", r["baseline"], np.isfinite(r["baseline"]))]
        for v in r["views"]:
            tag = v.source + (f"_lat{v.meta['plane']['lat_deg']:+.0f}" if v.source == "tangent" else
                              f"_pitch{v.meta['ypr'][1]:+.0f}")
            cands.append((tag, v.values, v.valid))
        cands.append(("hybrid_final", r["pred"], np.isfinite(r["pred"])))
        for name, x, valid in cands:
            for pole, pm in (("north", polar & (lat > 0)), ("south", polar & (lat < 0))):
                m = pm & valid & np.isfinite(x)
                if m.sum() < 100:
                    continue
                e = np.log(metric(x[m])) - np.log(gt[m])
                rows.append({"image": s.id, "view": name, "pole": pole, "signed_log_err": float(e.mean()),
                             "abs_rel": float(np.mean(np.abs(np.exp(e) - 1))), "n": int(m.sum())})
        print(s.id, flush=True)
    df = pd.DataFrame(rows)
    out = os.path.join(cfg["output_dir"], "bias_analysis.csv")
    df.to_csv(out, index=False)
    g = df.groupby(["pole", "view"])[["signed_log_err", "abs_rel"]].agg(["mean", "std"]).round(4)
    g.to_csv(out.replace(".csv", "_summary.csv"))
    print(g.to_string())


if __name__ == "__main__":
    main()
