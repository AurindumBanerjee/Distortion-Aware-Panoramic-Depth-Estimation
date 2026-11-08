#!/usr/bin/env python3
"""Why does Möbius-TTA (pole re-centring) help on Structured3D but not on PanoX / real Holo360D indoor?

For every frame and every rotated pass this separates three things that the benchmark mixes into one number:

  intrinsic gain : does the rotated view really predict the pole better than the identity view?
                   (both fitted to ground truth ON THE POLAR CAP ONLY -> an oracle, upper bound)
  realised gain  : what the fusion actually receives: identity aligned globally to GT (the headline protocol),
                   rotated pass re-anchored to the identity on the equatorial overlap WITHOUT looking at GT
  anchor loss    : realised - intrinsic = what the label-free re-anchoring throws away

plus the label-free quality signal used by `fit_guard` (residual of the anchor fit) and a few scene descriptors
(far-field fraction, depth spread on the anchor, number of anchor pixels), so that the report can say which of
them predicts harm. It runs the model on 1 + #passes images per frame and needs no training.

Usage (from Aurindum/, on the GPU machine):
  python scripts/diagnose_reanchor.py --config 3_structured3d_benchmark/config.yaml --max_scenes 40 --tag s3
  python scripts/diagnose_reanchor.py --config 3_structured3d_benchmark/config_panox.yaml --max_scenes 40 --tag panox
  python scripts/diagnose_reanchor.py --config 3_structured3d_benchmark/config_holo360d_indoor.yaml --tag holo_in
Writes results/diagnose_<tag>.csv and results/DIAGNOSE_<tag>.md.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
for sub in ("", "2_mobius_tta_ensembling", "1_gradient_polar_fusion"):
    sys.path.insert(0, str(ROOT / sub) if sub else str(ROOT))

from evaluation.metrics import to_metric_depth  # noqa: E402
from evaluation.protocol import align_to_gt, model_space  # noqa: E402
from geometry.spherical import latitude_map  # noqa: E402
from mobius_transform import unwarp_depth_mobius, warp_erp_mobius  # noqa: E402
from tta_ensemble import MobiusTTAEnsemble, _robust_fit, fit_quality  # noqa: E402

CAP_LAT = 60.0


def _absrel(pred: np.ndarray, gt: np.ndarray, m: np.ndarray) -> float:
    m = m & np.isfinite(pred) & (gt > 0)
    return float(np.mean(np.abs(pred[m] - gt[m]) / gt[m])) if m.any() else float("nan")


def _auc(score: np.ndarray, harm: np.ndarray) -> float:
    """P(score of a harmful case > score of a harmless case) (Mann-Whitney); 0.5 = no information."""
    s, h = np.asarray(score, float), np.asarray(harm, bool)
    ok = np.isfinite(s)
    s, h = s[ok], h[ok]
    if h.sum() == 0 or (~h).sum() == 0:
        return float("nan")
    order = np.argsort(np.argsort(np.concatenate([s[h], s[~h]]))) + 1.0
    # average ranks for ties
    allv = np.concatenate([s[h], s[~h]])
    ranks = np.empty(len(allv))
    for v in np.unique(allv):
        idx = allv == v
        ranks[idx] = order[idx].mean()
    u = ranks[: h.sum()].sum() - h.sum() * (h.sum() + 1) / 2.0
    return float(u / (h.sum() * (~h).sum()))


def diagnose_frame(model, rgb: np.ndarray, gt: np.ndarray, valid: np.ndarray, passes,
                   reanchor: str = "auto", anchor_max_lat: float = 30.0,
                   min_depth: float = 0.1, max_depth: float = 10.0) -> List[Dict]:
    """One row per rotated pass (|pitch| = 90) of this frame."""
    H, W = gt.shape
    lat = latitude_map(H, W)
    lat_abs = np.abs(lat)
    ens = MobiusTTAEnsemble(model, passes=passes, reanchor=reanchor, anchor_max_lat=anchor_max_lat)
    ref = model.predict(rgb, kind="erp").astype(np.float64)
    ident_global = align_to_gt(ref, gt, valid, model, protocol="align-all", min_depth=min_depth, max_depth=max_depth)
    rows = []
    for pitch, scale in ens.passes:
        if abs(pitch) < 1e-6:
            continue
        sign = 1.0 if pitch > 0 else -1.0
        cap = valid & (lat * sign > CAP_LAT)
        if cap.sum() < 100:
            continue
        warped, lat_seen = warp_erp_mobius(rgb, scale_factor=scale, pitch_deg=pitch)
        raw = unwarp_depth_mobius(model.predict(warped, kind="erp"), scale_factor=scale, pitch_deg=pitch).astype(np.float64)
        anchor = (lat_abs < anchor_max_lat) & (lat_seen < anchor_max_lat)
        n_anchor = int(anchor.sum())
        if n_anchor < 200:
            score = np.maximum(lat_abs, lat_seen)
            anchor = score <= np.percentile(score, 10.0)
        a, b = _robust_fit(raw[anchor], ref[anchor], ens.reanchor)
        res = fit_quality(raw[anchor], ref[anchor], a, b, ens.reanchor)
        anchored = a * raw + b

        # (1) intrinsic: both views fitted to GT on the cap only
        cap_id = align_to_gt(ref, gt, cap, model, protocol="align-all", min_depth=min_depth, max_depth=max_depth)
        cap_rot = align_to_gt(raw, gt, cap, model, protocol="align-all", min_depth=min_depth, max_depth=max_depth)
        e_id_or, e_rot_or = _absrel(cap_id, gt, cap), _absrel(cap_rot, gt, cap)
        # (2) realised: the identity's global GT fit is applied to the anchored pass (they now live in one frame)
        # (2) realised: the identity's global GT fit (align-all) is applied unchanged to the anchored pass, so both
        #     live in one frame and only the label-free re-anchor separates them
        space, scale = model_space(model)
        mode = "affine" if space == "disparity" else ("median" if scale == "metric" else "lsq")
        _, fit = to_metric_depth(ref, gt, valid, space=space, mode=mode, max_depth=max_depth, min_depth=min_depth)
        if space == "disparity":
            disp = np.clip(fit["scale"] * anchored + fit["shift"], 1.0 / max_depth, 1.0 / min_depth)
            real = 1.0 / np.where(np.isfinite(disp), disp, 1.0 / max_depth)
        else:
            real = np.where(np.isfinite(anchored), fit["scale"] * anchored, max_depth)
        real = np.clip(real, min_depth, max_depth)
        e_id_gl, e_real = _absrel(ident_global, gt, cap), _absrel(real, gt, cap)

        gta = gt[anchor & valid]
        rows.append(dict(
            pitch=pitch, scale=scale, n_anchor=n_anchor, a=a, b=b, fit_res=res,
            cap_px=int(cap.sum()),
            err_id_oracle=e_id_or, err_rot_oracle=e_rot_or,
            err_id_global=e_id_gl, err_rot_realised=e_real,
            intrinsic_gain=(e_id_or - e_rot_or) / max(e_id_or, 1e-9),
            realised_gain=(e_id_gl - e_real) / max(e_id_gl, 1e-9),
            anchor_loss=(e_real - e_rot_or) / max(e_rot_or, 1e-9),
            far_frac=float(np.mean(gta > 0.8 * max_depth)) if gta.size else float("nan"),
            gt_cv=float(np.std(gta) / max(np.mean(gta), 1e-9)) if gta.size else float("nan"),
        ))
    return rows


def summarize(rows: List[Dict], tag: str) -> str:
    def med(k):
        v = np.array([r[k] for r in rows], float)
        return float(np.nanmedian(v)) if np.isfinite(v).any() else float("nan")
    harm = np.array([r["realised_gain"] < 0 for r in rows])
    n_ident = len({r["frame"] for r in rows})
    out = [f"# Re-anchor diagnostic: {tag}", "",
           f"{len(rows)} rotated passes from {n_ident} frames. Gains are relative AbsRel reductions on the polar cap "
           f"(|lat| > {CAP_LAT:.0f} deg of the pole the pass targets); positive is better than the identity view.", "",
           "| quantity | median |", "|---|---:|",
           f"| intrinsic gain (oracle polar fit of both views) | {med('intrinsic_gain') * 100:+.1f}% |",
           f"| realised gain (label-free re-anchor, global GT fit of identity) | {med('realised_gain') * 100:+.1f}% |",
           f"| anchor loss (realised error vs oracle error of the rotated view) | {med('anchor_loss') * 100:+.1f}% |",
           f"| anchor fit residual (fit_quality; 0 = perfect) | {med('fit_res'):.2f} |",
           f"| anchor re-scale a | {med('a'):.2f} |",
           f"| anchor pixels | {med('n_anchor'):.0f} |",
           f"| far-field fraction on anchor (> 0.8 max depth) | {med('far_frac'):.2f} |",
           f"| depth spread on anchor (std/mean) | {med('gt_cv'):.2f} |",
           f"| passes with realised gain < 0 | {harm.mean() * 100:.0f}% |",
           f"| passes with intrinsic gain < 0 | {np.mean([r['intrinsic_gain'] < 0 for r in rows]) * 100:.0f}% |", "",
           "## What predicts harm? (AUC: probability that a harmful pass scores higher than a harmless one; 0.5 = no information)", "",
           "| signal | AUC for 'realised gain < 0' |", "|---|---:|"]
    for k in ("fit_res", "far_frac", "gt_cv", "n_anchor"):
        out.append(f"| {k} | {_auc(np.array([r[k] for r in rows], float), harm):.2f} |")
    out.append(f"| |log a| | {_auc(np.abs(np.log(np.clip([r['a'] for r in rows], 1e-6, None))), harm):.2f} |")
    out += ["", "## Reading it",
            "- intrinsic gain > 0 but realised gain < 0 -> the rotated view is better; the label-free re-anchor ruins it (fix the anchoring).",
            "- intrinsic gain < 0 -> the rotated view itself is worse at the pole on this data (the model does not like rotated content); no anchoring fixes that.",
            "- fit_res AUC well above 0.5 -> `fit_guard` can detect these cases without labels; around 0.5 -> it cannot, drop it."]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="a 3_structured3d_benchmark config (data + model + mobius_tta)")
    ap.add_argument("--max_scenes", type=int, default=40)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--set", dest="overrides", action="append", default=[])
    ap.add_argument("--pitches", default="90,-90", help="rotated passes to diagnose")
    ap.add_argument("--subset", default="spread", choices=["spread", "first"],
                    help="which frames when --max_scenes < list length (spread = every scene represented)")
    args = ap.parse_args()
    cfg_path = Path(args.config)
    cfg_path = cfg_path if cfg_path.is_absolute() or cfg_path.exists() else ROOT / args.config
    cfg = yaml.safe_load(open(cfg_path))
    for ov in args.overrides:
        key, _, val = ov.partition("=")
        node = cfg
        for k in key.split(".")[:-1]:
            node = node.setdefault(k, {})
        node[key.split(".")[-1]] = yaml.safe_load(val)

    import importlib.util, logging
    spec = importlib.util.spec_from_file_location("m2run", ROOT / "2_mobius_tta_ensembling" / "run.py")
    m2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m2)
    model = m2.load_model(cfg.get("model", {}), logging.getLogger("diag"))

    from datasets.panorama import PanoramaDataset
    d = cfg["data"]
    name = d.get("dataset", "structured3d")
    root = None
    for cand in [ROOT / d.get("root", f"data/{name}"), ROOT.parent.parent / "Data" / name, ROOT.parent / "Data" / name]:
        if (cand / d.get("list", "test.txt")).is_file():
            root = cand
            break
    if root is None:
        raise FileNotFoundError(f"no {d.get('list', 'test.txt')} for dataset {name}")
    ds = PanoramaDataset(str(root), d.get("list", "test.txt"), height=d.get("height", 256), width=d.get("width", 512),
                         name=name, limit=args.max_scenes, subset=args.subset)
    ev = cfg.get("evaluation", {})
    min_d, max_d = float(ev.get("min_depth", 0.1)), float(ev.get("max_depth", 10.0))
    passes = [{"pitch": float(p), "scale": 1.0} for p in args.pitches.split(",")]
    rows = []
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        for r in diagnose_frame(model, smp.rgb, gt, valid, passes, anchor_max_lat=cfg.get("mobius_tta", {}).get("anchor_max_lat", 30.0),
                                min_depth=min_d, max_depth=max_d):
            r["frame"] = smp.id
            rows.append(r)
        print(f"[{i + 1}/{len(ds)}] {smp.id}", flush=True)
    if not rows:
        raise SystemExit("no rotated pass had >= 100 valid polar-cap pixels; nothing to report")
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with open(out / f"diagnose_{args.tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (out / f"DIAGNOSE_{args.tag}.md").write_text(summarize(rows, args.tag), encoding="utf-8")
    print(f"wrote {out / ('DIAGNOSE_' + args.tag + '.md')}")


if __name__ == "__main__":
    main()
