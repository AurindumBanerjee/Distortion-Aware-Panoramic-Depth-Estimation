#!/usr/bin/env python3
"""Exploratory study: realistic capture degradations x inference-time mitigations (distortions/catalogue.py).

For every frame: the clean prediction; for every degradation: the degraded prediction and each candidate mitigation,
all brought back to the original grid and scored against the SAME ground truth (align-all for relative models, raw
metres for metric models). Blind mitigations are also applied to the CLEAN image ("do no harm" check).

  python scripts/distortion_study.py --config 3_structured3d_benchmark/config.yaml --tag midas_s3 --max_scenes 40
Writes results/study_<tag>.json (per-frame metrics) and results/STUDY_<tag>.md (medians, win rates), plus example
images in results/study_<tag>_img/ for the first --examples frames.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import ROOT, add_common_args, depth_range, load_config, load_dataset, load_model  # noqa: E402
from distortions.catalogue import CATALOGUE, MITIGATIONS  # noqa: E402
from evaluation.distortion_analysis import headline_protocol  # noqa: E402
from evaluation.protocol import align_to_gt, group_of  # noqa: E402
from geometry.spherical import latitude_map  # noqa: E402

CLEAN_CHECKS = ("relevel_self", "gain_match", "flatfield", "denoise", "bilateral")  # blind fixes a system might always apply


def score(pred, gt, valid, model, region, min_d, max_d):
    al = align_to_gt(pred, gt, valid, model, protocol=headline_protocol(model), min_depth=min_d, max_depth=max_d)
    H, W = gt.shape
    lat = np.abs(latitude_map(H, W))
    e = np.abs(al - gt) / np.where(gt > 0, gt, 1.0)
    out = {"all": float(np.mean(e[valid])), "polar": float(np.mean(e[valid & (lat >= 60)])) if (valid & (lat >= 60)).any() else float("nan")}
    if region is not None:
        m = valid & region
        out["region"] = float(np.mean(e[m])) if m.sum() >= 50 else float("nan")
    return out, al


def save_examples(folder: Path, fid: str, items):
    import cv2
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import cm
    folder.mkdir(parents=True, exist_ok=True)
    gt = items["gt"]
    v = items["valid"]
    lo, hi = np.percentile(gt[v], [2, 98])
    names = {}
    for k, img in items["images"].items():
        if img.ndim == 3:
            rgb = img
        elif k.startswith("err_"):
            x = np.clip(np.nan_to_num(img) / 0.5, 0, 1)
            rgb = (cm.magma(x)[..., :3] * 255).astype(np.uint8)
            rgb[~v] = 40
        else:
            x = np.clip((np.log(np.clip(img, 1e-3, None)) - np.log(lo)) / (np.log(hi) - np.log(lo)), 0, 1)
            rgb = (cm.turbo(1 - x)[..., :3] * 255).astype(np.uint8)
        p = folder / f"{fid}__{k}.jpg"
        cv2.imwrite(str(p), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        names[k] = p.name
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(ap)
    ap.add_argument("--only", default=None, help="comma list of distortion keys (default: all)")
    ap.add_argument("--examples", type=int, default=3, help="frames for which images are saved")
    ap.add_argument("--out_dir", default=None, help="output folder (default results/); used by the separate policy experiments")
    ap.set_defaults(split="all", max_scenes=40)
    a = ap.parse_args()
    cfg = load_config(a.config, a.overrides)
    model = load_model(cfg)
    ds = load_dataset(cfg, a.split, a.max_scenes)
    min_d, max_d = depth_range(cfg)
    dists = [d for d in CATALOGUE if not a.only or d.key in a.only.split(",")]
    out_dir = Path(a.out_dir) if a.out_dir else ROOT / "results"
    img_dir = out_dir / f"study_{a.tag}_img"
    rows, examples = [], {}
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        H, W = gt.shape
        rec = {"id": smp.id, "group": group_of(smp.id)}
        clean = np.asarray(model.predict(smp.rgb, kind="erp"), dtype=np.float64)
        rec["clean"], clean_al = score(clean, gt, valid, model, None, min_d, max_d)
        for key in CLEAN_CHECKS:
            p = MITIGATIONS[key][1](model, smp.rgb, {})
            rec[f"clean+{key}"], _ = score(p, gt, valid, model, None, min_d, max_d)
        ex = i < a.examples
        imgs = {"rgb": smp.rgb, "clean": clean_al, "err_clean": np.abs(clean_al - gt) / np.where(gt > 0, gt, 1)} if ex else {}
        for d in dists:
            # the clean GT range lets physically based degradations (stitching parallax) image the scene from a
            # displaced lens; invalid GT (sky, holes) is treated as lying on the stitching sphere (no displacement)
            depth_ctx = np.where(valid, gt, 2.0)
            rgb_d, ctx = d.apply(smp.rgb, {"seed": i, "depth": depth_ctx})
            region = d.region(H, W, ctx) if d.region else None
            rec[f"{d.key}|clean"], _ = score(clean, gt, valid, model, region, min_d, max_d)
            best = None
            for mk in ["none"] + d.mitigations:
                p = d.to_original(MITIGATIONS[mk][1](model, rgb_d, ctx), ctx)
                s, al = score(p, gt, valid, model, region, min_d, max_d)
                rec[f"{d.key}|{mk}"] = s
                if "Q_est" in ctx:
                    R, Q = ctx["R"], ctx.pop("Q_est")
                    rec[f"{d.key}|{mk}"]["tilt_residual_deg"] = float(np.degrees(np.arccos(np.clip((R @ Q)[1, 1], -1, 1))))
                if ex:
                    if mk == "none":
                        imgs[f"{d.key}_rgb"] = rgb_d
                        imgs[f"{d.key}_none"] = al
                        imgs[f"err_{d.key}_none"] = np.abs(al - gt) / np.where(gt > 0, gt, 1)
                    else:
                        k = "region" if region is not None else "all"
                        if best is None or s[k] < best[0]:
                            best = (s[k], mk, al)
            if ex and best is not None:
                imgs[f"{d.key}_best"] = best[2]
                imgs[f"err_{d.key}_best"] = np.abs(best[2] - gt) / np.where(gt > 0, gt, 1)
                rec[f"{d.key}|best_example"] = best[1]
        if ex:
            examples[smp.id] = save_examples(img_dir, smp.id.replace("/", "_"), {"gt": gt, "valid": valid, "images": imgs})
        rows.append(rec)
        print(f"[{i + 1}/{len(ds)}] {smp.id}: clean {rec['clean']['all']:.3f}", flush=True)

    # aggregate: medians, paired win rate and median relative change vs the degraded prediction
    lines = [f"# Distortion study: {a.tag}", "", f"model `{getattr(model, 'name', '?')}` · {len(rows)} frames · "
             f"{len(set(r['group'] for r in rows))} clusters · AbsRel ({headline_protocol(model)})", "",
             "Recovery = share of the damage undone: (degraded - mitigated) / (degraded - clean), median over the frames where the fault cost at least 5%.", ""]
    med = lambda k, f: float(np.nanmedian([r[k][f] for r in rows if k in r and f in r[k]])) if any(k in r and f in r[k] for r in rows) else float("nan")
    lines += [f"Clean: all {med('clean', 'all'):.4f}, polar >= 60 deg {med('clean', 'polar'):.4f}", "",
              "**Blind mitigations on CLEAN images (do-no-harm check)**", "", "| mitigation | all | polar | worse than clean (frames) |", "|---|---:|---:|---:|"]
    for k in CLEAN_CHECKS:
        worse = np.mean([r[f"clean+{k}"]["all"] > r["clean"]["all"] * 1.01 for r in rows])
        lines.append(f"| {MITIGATIONS[k][0]} | {med('clean+' + k, 'all'):.4f} | {med('clean+' + k, 'polar'):.4f} | {100 * worse:.0f}% |")
    for d in dists:
        f = "region" if d.region is not None else "all"
        lines += ["", f"## {d.title}", "", f"*Cause:* {d.cause}", "",
                  f"| method | all | polar >= 60 | {'affected region' if f == 'region' else '-'} | recovery ({f}) | better than degraded |",
                  "|---|---:|---:|---:|---:|---:|"]
        for mk in ["clean", "none"] + d.mitigations:
            k = f"{d.key}|{mk}"
            name = "clean image" if mk == "clean" else ("degraded, no mitigation" if mk == "none" else MITIGATIONS[mk][0])
            rec_s, win = "", ""
            if mk not in ("clean", "none"):
                r_ = [(r[f"{d.key}|none"][f] - r[k][f]) / max(r[f"{d.key}|none"][f] - r[f"{d.key}|clean"][f], 1e-6) for r in rows
                      # only frames where the fault really hurt (>= 5% worse than clean): elsewhere the ratio's
                      # denominator is ~0 and the recovery is meaningless (e.g. +277% / -645% in the first pass)
                      if np.isfinite(r[k][f]) and r[f"{d.key}|none"][f] - r[f"{d.key}|clean"][f] >= 0.05 * r[f"{d.key}|clean"][f]]
                rec_s = f"{100 * np.median(r_):.0f}%" if r_ else "n/a"
                win = f"{100 * np.mean([r[k][f] < r[f'{d.key}|none'][f] for r in rows if np.isfinite(r[k][f])]):.0f}%"
            extra = ""
            if mk == "relevel_self":
                extra = f" (residual tilt median {np.median([r[k]['tilt_residual_deg'] for r in rows]):.1f} deg)"
            reg = f"{med(k, 'region'):.4f}" if f == "region" else ""
            lines.append(f"| {name}{extra} | {med(k, 'all'):.4f} | {med(k, 'polar'):.4f} | {reg} | {rec_s} | {win} |")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"study_{a.tag}.json").write_text(json.dumps({"tag": a.tag, "model": getattr(model, "name", "?"), "rows": rows,
                                                              "examples": examples}), encoding="utf-8")
    (out_dir / f"STUDY_{a.tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / f'STUDY_{a.tag}.md'}")


if __name__ == "__main__":
    main()
