#!/usr/bin/env python
"""Single entry point for all experiments.

    python run_experiment.py --config configs/default.yaml                 # everything
    python run_experiment.py --config configs/default.yaml --stages main reports
    python run_experiment.py --config configs/dap_stanford2d3d.yaml --set dataset.limit=50

Stages (in order): geometry, main, reports, control, resolution, timing, qualitative.
`reports` only reads the CSV/NPZ written by `main`, so it can be re-run cheaply.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd


from experiments.projection import ablation, rotation_ensemble, tangent_plane  # noqa: E402
from experiments.projection import acgf as exp_acgf  # noqa: E402
from experiments.projection import baseline as exp_baseline  # noqa: E402
from experiments.projection.common import (MAIN_TAGS, build_plan, environment_info, load_config,  # noqa: E402
                                make_dataset, make_model, method_table, resolve_eval_align, run_plan, seed_everything, write_markdown_table)

ALL_STAGES = ["geometry", "main", "reports", "control", "resolution", "timing", "qualitative"]


class LoadedEval:
    """Read-only view of a finished evaluation (rows CSV + profiles NPZ)."""

    def __init__(self, out_dir, region, plan_names):
        self.df = pd.read_csv(os.path.join(out_dir, f"rows_align-{region}.csv"))
        z = np.load(os.path.join(out_dir, f"profiles_align-{region}.npz"))
        self.profile_centres = z["centres"]
        key = {n.replace("|", "_"): n for n in plan_names}
        self.profiles = {key.get(k, k): z[k] for k in z.files if k != "centres"}

    def frame(self):
        return self.df

    def summary(self, weighting="pixel"):
        d = self.df[self.df.weighting == weighting]
        cols = ["abs_rel", "sq_rel", "rmse", "rmse_log", "mae", "medae", "d1", "d2", "d3", "err_var", "pct_bad"]
        return d.groupby(["method", "band"], sort=False)[cols].mean().reset_index()


def log_to(path):
    f = open(path, "a")

    def _log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        f.write(line + "\n")
        f.flush()
    return _log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/projection/default.yaml")
    ap.add_argument("--stages", nargs="+", default=ALL_STAGES)
    ap.add_argument("--set", nargs="*", default=[], help="overrides, e.g. dataset.limit=4")
    ap.add_argument("--tags", nargs="*", default=None, help="restrict the plan to methods carrying one of these tags")
    args = ap.parse_args()
    cfg = load_config(args.config, args.set)
    out = cfg["output_dir"]
    os.makedirs(out, exist_ok=True)
    log = log_to(os.path.join(out, "log.txt"))
    seed_everything(cfg["seed"])
    with open(os.path.join(out, "config_resolved.json"), "w") as f:
        json.dump({"config": cfg, "env": environment_info(), "argv": sys.argv}, f, indent=2)
    plan = build_plan(cfg)
    if args.tags:
        plan = [(t, mc) for t, mc in plan if set(t) & set(args.tags + ["E1_baseline"])]
    with open(os.path.join(out, "plan.json"), "w") as f:
        json.dump([{"tags": t, "config": mc.__dict__} for t, mc in plan], f, indent=1, default=str)
    names = [mc.name for _, mc in plan]
    log(f"plan: {len(plan)} methods; stages {args.stages}")

    # ---------------------------------------------------------------- geometry gate
    if "geometry" in args.stages:
        from pano.geometry.validation import run_all
        g = run_all(os.path.join(out, "geometry_validation.json"))
        worst_pt = max(v["max_angle_err_deg"] for v in g["point_level"].values())
        worst_img = max(v["roundtrip_mean_rel_err"] for v in g["image_level"].values())
        log(f"geometry: worst point angle err {worst_pt:.2e} deg, worst ERP->tan->ERP mean rel err {worst_img:.2e}")
        if worst_pt > 1e-8 or worst_img > 1e-3:
            raise SystemExit("Geometry validation failed -- refusing to run experiments.")

    model = tmodel = dataset = None

    def ensure_model():
        nonlocal model, tmodel
        if model is None:
            model, tmodel = make_model(cfg)
            log(f"model: {model.describe()}")
        return model, tmodel

    # ---------------------------------------------------------------- main pass
    if "main" in args.stages:
        ensure_model()
        dataset = make_dataset(cfg)
        log(f"dataset: {cfg['dataset']['name']} n={len(dataset)} at {cfg['dataset']['height']}x{cfg['dataset']['width']}")
        heat = ["baseline"] + [mc.name for t, mc in plan if set(MAIN_TAGS) & set(t)]
        run_plan(cfg, plan, model, tmodel, dataset, out, qualitative=cfg["experiments"]["qualitative"],
                 heatmap_methods=heat, log=log)

    # ---------------------------------------------------------------- reports
    if "reports" in args.stages:
        main_names = {t: mc.name for tags, mc in plan for t in tags if t in ("E2_tangent", "E3_rotation", "E4_hybrid")}
        for region in cfg["evaluation"]["align_regions"]:
            ev = LoadedEval(out, region, names)
            df = ev.frame()
            rdir = os.path.join(out, f"report_align-{region}")
            os.makedirs(rdir, exist_ok=True)
            tab, on = exp_baseline.latitude_report(ev, rdir, tag=f"align-{region}")
            exp_baseline.band_metric_plots(ev, rdir, tag=f"align-{region}")
            method_table(df, ["baseline"]).to_csv(os.path.join(rdir, "baseline.csv"))
            if "acgf" in names:
                exp_acgf.report(df, rdir, names, main_names)
                acgf_groups = {"acgf_main": ["baseline"] + [n for n in [main_names.get("E4_hybrid"), "mono360", "acgf"]
                                                            if n in names],
                               "acgf_ablation": ["baseline", "acgf"] + [n for n in names if n.startswith("acgf|")
                                                                        and not n.startswith("acgf|t")],
                               "acgf_threshold": ["baseline"] + [n for n in names if n.startswith("acgf|t")]}
                ablation.profile_plots(ev, rdir, acgf_groups, tag=f"align-{region}")
                exp_acgf.ico_report(df, rdir)
            if not {"E2_tangent", "E3_rotation", "E4_hybrid"} <= set(main_names):
                log(f"reports written to {rdir} (legacy E2-E9 reports skipped: methods not in the plan)")
                continue
            tangent_plane.report(df, rdir, main_names["E2_tangent"], os.path.join(rdir, "tangent_plane.csv"))
            rotation_ensemble.report(df, rdir, main_names["E3_rotation"], os.path.join(rdir, "rotation.csv"))
            rotation_ensemble.report(df, rdir, main_names["E4_hybrid"], os.path.join(rdir, "hybrid.csv"))
            rotation_ensemble.rotation_sets_report(df, rdir)
            ablation.ablation_tables(df, os.path.join(rdir, "ablations"))
            main = ["baseline", main_names["E2_tangent"], main_names["E3_rotation"], main_names["E4_hybrid"]]
            mt = method_table(df, main)
            mt.to_csv(os.path.join(rdir, "main_comparison.csv"))
            write_markdown_table(mt, os.path.join(rdir, "main_comparison.md"))
            groups = {"main": main}
            from experiments.projection.common import default_rotset_name
            rsn = default_rotset_name(cfg)

            def _ok(n, m):
                return n.startswith(m + "|") and (m == "rotation" or "|v1|" in n) and (m == "tangent" or f"|{rsn}|" in n)
            for m in ("tangent", "rotation", "hybrid"):
                groups[f"threshold_{m}"] = ["baseline"] + [n for n in names if _ok(n, m) and n.endswith("|cosine|prior")]
                groups[f"fusion_{m}"] = ["baseline"] + [n for n in names if _ok(n, m) and "|t45|" in n
                                                        and n.endswith("|prior")]
            groups["views"] = ["baseline"] + [n for n in names if n.startswith("tangent|t45|") and n.endswith("cosine|prior")]
            groups["rotation_sets"] = ["baseline"] + [n for n in names if n.startswith("rotation|t45|") and n.endswith("cosine|prior")]
            ablation.profile_plots(ev, rdir, groups, tag=f"align-{region}")
            if region == "all":
                ablation.runtime_tradeoff(df, rdir)
                from pano.visualization.visualize import plot_distortion, plot_error_heatmap
                plot_distortion(os.path.join(rdir, "erp_distortion.png"))
                hs = {}
                for n in main:
                    p = os.path.join(out, f"heatmap__{n.replace('|', '_')}.npy")
                    if os.path.exists(p):
                        hs[n] = np.load(p)
                vmax = np.nanpercentile(hs["baseline"], 99) if "baseline" in hs else None
                for n, h in hs.items():
                    plot_error_heatmap(h, os.path.join(rdir, f"heatmap_{n.split('|')[0]}.png"),
                                       title=f"Mean AbsRel per pixel: {n}", vmax=vmax)
            log(f"reports written to {rdir}")

    # ---------------------------------------------------------------- content-vs-latitude control
    if "control" in args.stages:
        ensure_model()
        lim = cfg["experiments"].get("control_limit")
        ds = make_dataset(cfg, limit=lim)
        cdir = os.path.join(out, "latitude_control")
        df = exp_baseline.latitude_control(model, ds, cdir, cfg["experiments"]["latitude_control_pitches"],
                                           resolve_eval_align(cfg, model), model.spec.space, log=log)
        for aname, d in df.groupby("align"):
            sub = os.path.join(cdir, f"align-{aname}")
            os.makedirs(sub, exist_ok=True)
            exp_baseline.latitude_control_report(d, sub)

    # ---------------------------------------------------------------- resolution
    if "resolution" in args.stages:
        ensure_model()
        rows = []
        main_plan = [(t, mc) for t, mc in plan if {"E1_baseline", "E2_tangent", "E3_rotation", "E4_hybrid"} & set(t)]
        for (h, w) in cfg["experiments"]["resolutions"]:
            ds = make_dataset(cfg, height=h, width=w, limit=cfg["experiments"]["resolution_limit"])
            if hasattr(model, "erp_net_height"):
                model.erp_net_height = min(h, 512)
            import copy
            rplan = []
            for t, mc in main_plan:
                mc2 = copy.deepcopy(mc)
                mc2.tangent_size = int(round(cfg["inference"]["tangent_size"] * h / cfg["dataset"]["height"] / 32)) * 32
                rplan.append((t, mc2))
            rdir = os.path.join(out, f"resolution_{h}x{w}")
            evs = run_plan(cfg, rplan, model, tmodel, ds, rdir, log=log)
            d = evs["all"].frame()
            d["resolution"] = f"{h}x{w}"
            rows.append(d)
        if hasattr(model, "erp_net_height"):
            model.erp_net_height = cfg["model"].get("erp_net_height", 384)
        allr = pd.concat(rows)
        allr.to_csv(os.path.join(out, "resolution_rows.csv"), index=False)
        tabs = []
        for res, d in allr.groupby("resolution", sort=False):
            t = method_table(d, [mc.name for _, mc in main_plan])
            t.insert(0, "resolution", res)
            tabs.append(t)
        rt = pd.concat(tabs)
        rt.to_csv(os.path.join(out, "resolution.csv"))
        write_markdown_table(rt[["resolution", "abs_rel", "abs_rel_0-15", "abs_rel_60-75", "abs_rel_75-90",
                                 "abs_rel_polar_60_90", "runtime_ratio"]], os.path.join(out, "resolution.md"))
        if "equatorial" in cfg["evaluation"]["align_regions"]:
            tabs = []
            for (h, w) in cfg["experiments"]["resolutions"]:
                d = pd.read_csv(os.path.join(out, f"resolution_{h}x{w}", "rows_align-equatorial.csv"))
                t = method_table(d, [mc.name for _, mc in main_plan])
                t.insert(0, "resolution", f"{h}x{w}")
                tabs.append(t)
            pd.concat(tabs).to_csv(os.path.join(out, "resolution_align-equatorial.csv"))

    # ---------------------------------------------------------------- cold timing
    if "timing" in args.stages:
        ensure_model()
        ds = make_dataset(cfg)
        sel = [(t, mc) for t, mc in plan if {"E1_baseline", "E2_tangent", "E3_rotation", "E4_hybrid", "E6_views",
                                             "E10_acgf", "E11_mono360"} & set(t)
               and (mc.method != "hybrid" or "E4_hybrid" in t)]
        ablation.cold_timing(model, tmodel, ds, sel, cfg["experiments"]["timing_images"], out, log=log)

    # ---------------------------------------------------------------- qualitative
    if "qualitative" in args.stages:
        ensure_model()
        from pano.visualization.visualize import qualitative_panel
        ds = make_dataset(cfg)
        qdir = os.path.join(out, "qualitative")
        os.makedirs(qdir, exist_ok=True)
        main_names = {t: mc for tags, mc in plan for t in tags if t in MAIN_TAGS}
        pdir = os.path.join(out, "predictions")
        for i in range(min(cfg["experiments"]["qualitative"], len(ds))):
            s = ds[i]
            bp = os.path.join(pdir, f"{s.id}__baseline.npz")
            if not os.path.exists(bp):
                continue
            base = np.load(bp)["pred_metric"]
            for tag, mc in main_names.items():
                cp = os.path.join(pdir, f"{s.id}__{mc.name.replace('|', '_')}.npz")
                if not os.path.exists(cp):
                    continue
                corr = np.load(cp)["pred_metric"]
                qualitative_panel(s.rgb, np.nan_to_num(s.depth, nan=1.0), base, corr, s.valid,
                                  os.path.join(qdir, f"{s.id}_{mc.method}.png"),
                                  title=f"{s.id}: baseline vs {mc.name}", lat_threshold=mc.lat_threshold)
            if "E2_tangent" in main_names:
                tangent_plane.visualize_tangent_views(model, s, main_names["E2_tangent"], qdir)
            if "E10_acgf" in main_names:
                exp_acgf.visualize_acgf(model, tmodel, s, main_names["E10_acgf"], qdir)
        log(f"qualitative figures in {qdir}")
    log("done")


if __name__ == "__main__":
    main()
