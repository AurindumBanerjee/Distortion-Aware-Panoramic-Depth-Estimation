#!/usr/bin/env python3
"""Why does the nadir + JPEG correction give DAP no gain on NYC although the cap is detected (88% at 512 x 1024)?

For every frame, the nadir cap is simulated (a tripod patch below -62 deg), optionally followed by JPEG q8, and one
model is run through a ladder of variants that change ONE thing at a time:

  raw                          the degraded image, no fix
  oracle:F                     cap fix F with the TRUE cap mask (F: inpaint_erp, inpaint_tangent, plane_fill)
  oracle+1.5:F                 true mask grown by the JPEG margin (1.5 deg)
  detected:F, detected+1.5:F   the mask found by detect_caps (without / with the margin the pipeline uses after JPEG)
  deblock_oracle:F             bilateral deblocking of the image first, then F with the true mask
  pipe_photometric:F           the deployed correct() path (photometric fix, then the cap fix), flags={'jpeg'}
  pipe_cap_first:F             the same with order='cap_first'
  bilateral_only               JPEG fix without any cap fix

Each variant is scored (a) on the occluded region, (b) outside it, (c) in a ring 12 deg above the cap edge and (d) on the whole
panorama, under the model's headline protocol AND a global median-scale fit (align-all), so that a raw-metre scale offset of a
metric model (DAP) can be told apart from a genuine failure of the fix. The median pred / gt ratio inside the region is
recorded as 'bias'. Outputs: results/diag/nadir_jpeg_<tag>.json and NADIR_JPEG_<tag>.md (per-variant median, change vs raw,
frames improved, bootstrap 95% CI over frames).

  python scripts/nadir_jpeg_diagnosis.py --config 3_structured3d_benchmark/config_dap_nyc.yaml --tag dap_nyc --max_scenes 147
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

CAP_FIXES = ("inpaint_erp", "inpaint_tangent", "plane_fill")
KINDS = ("nadir", "nadir+jpeg")
NADIR_DEG = 62.0
RING_DEG = 12.0


def region_masks(H, W, nadir_from=NADIR_DEG, ring_deg=RING_DEG):
    from distortions.catalogue import occlusion_mask
    from geometry.spherical import latitude_map
    cap = occlusion_mask(H, W, {"nadir_from": nadir_from})
    lat = latitude_map(H, W)
    ring = (lat < 0) & (np.abs(lat) >= nadir_from - ring_deg) & ~cap
    return {"region": cap, "outside": ~cap, "ring": ring, "all": np.ones((H, W), bool)}


def score_variant(pred, gt, valid, model, masks, protocol, min_d, max_d):
    from evaluation.protocol import align_to_gt
    al = align_to_gt(pred, gt, valid, model, protocol=protocol, min_depth=min_d, max_depth=max_d)
    e = np.abs(al - gt) / np.where(gt > 0, gt, 1.0)
    out = {}
    for k, m in masks.items():
        mm = valid & m
        out[k] = float(np.mean(e[mm])) if mm.sum() >= 50 else float("nan")
    m = valid & masks["region"]
    out["bias"] = float(np.median(al[m] / gt[m])) if m.sum() >= 50 else float("nan")
    return out


def build_variants(model, x, kind, true_caps):
    """{variant: prediction on x's grid}; every entry changes one thing relative to its neighbours."""
    from distortions.catalogue import MITIGATIONS
    from distortions.correction import JPEG_EDGE_MARGIN_DEG, CaptureMeta, _image_after, cap_fault, correct, detect_caps, grow_caps
    fx = lambda k: MITIGATIONS[k][1]
    jpeg = kind.endswith("jpeg")
    det = detect_caps(x)
    out = {"raw": np.asarray(model.predict(x, kind="erp"), dtype=np.float64)}
    info = {"detected": cap_fault(det), "nadir_from_detected": det.get("nadir_from"), "zenith_from_detected": det.get("zenith_from")}
    deblocked = _image_after("bilateral", x, {}) if jpeg else x
    if jpeg:
        out["bilateral_only"] = np.asarray(fx("bilateral")(model, x, {}), dtype=np.float64)
    for f in CAP_FIXES:
        out[f"oracle:{f}"] = np.asarray(fx(f)(model, x, dict(true_caps)), dtype=np.float64)
        out[f"oracle+1.5:{f}"] = np.asarray(fx(f)(model, x, grow_caps(true_caps, JPEG_EDGE_MARGIN_DEG)), dtype=np.float64)
        if det.get("nadir_from") is not None:
            dc = {"nadir_from": det["nadir_from"], "zenith_from": None}
            out[f"detected:{f}"] = np.asarray(fx(f)(model, x, dc), dtype=np.float64)
            out[f"detected+1.5:{f}"] = np.asarray(fx(f)(model, x, grow_caps(dc, JPEG_EDGE_MARGIN_DEG)), dtype=np.float64)
        else:
            out[f"detected:{f}"] = out["raw"]            # nothing detected: the pipeline runs uncorrected
            out[f"detected+1.5:{f}"] = out["raw"]
        if jpeg:
            out[f"deblock_oracle:{f}"] = np.asarray(fx(f)(model, deblocked, dict(true_caps)), dtype=np.float64)
            for order in ("photometric_first", "cap_first"):
                pol = {"nadir": f, "vfov": f, "jpeg": "bilateral"}
                out[f"pipe_{'photometric' if order == 'photometric_first' else 'cap_first'}:{f}"] = np.asarray(
                    correct(model, x, CaptureMeta(flags={"jpeg"}), pol, order=order)[0], dtype=np.float64)
        else:
            out[f"pipe:{f}"] = np.asarray(correct(model, x, CaptureMeta(), {"nadir": f, "vfov": f})[0], dtype=np.float64)
    return out, info


def boot_ci(v, n=2000, seed=0):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if len(v) < 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    m = np.median(v[rng.integers(0, len(v), (n, len(v)))], axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def summarize(rows, kind, protocol, metric):
    """[(variant, median value, median rel. change vs raw, share improved, ci_lo, ci_hi)] for one kind / protocol / metric."""
    names = [k for k in rows[0][kind][protocol] if k != "raw"] if rows else []
    raw = np.array([r[kind][protocol]["raw"][metric] for r in rows], float)
    out = []
    for n in names:
        v = np.array([r[kind][protocol][n][metric] for r in rows if n in r[kind][protocol]], float)
        rr = np.array([r[kind][protocol]["raw"][metric] for r in rows if n in r[kind][protocol]], float)
        ok = np.isfinite(v) & np.isfinite(rr) & (rr > 0)
        if not ok.any():
            continue
        rel = (v[ok] - rr[ok]) / rr[ok]
        lo, hi = boot_ci(rel)
        out.append((n, float(np.median(v[ok])), float(np.median(rel)), float(np.mean(v[ok] < rr[ok])), lo, hi))
    return float(np.nanmedian(raw)) if len(raw) else float("nan"), out


def report(rows, tag, model_name, protocols):
    L = [f"# Nadir + JPEG diagnosis: {tag}", "",
         f"model `{model_name}` · {len(rows)} frames · nadir cap below -{NADIR_DEG:.0f} deg · JPEG q8. Protocols: "
         + ", ".join(f"`{p}`" for p in protocols) + ". Change = median over frames of (variant - raw) / raw; bootstrap 95% CI over frames.", ""]
    det = {k: [r[k]["info"] for r in rows] for k in KINDS}
    for k in KINDS:
        d = det[k]
        ok = np.mean([i["detected"] == "nadir" for i in d])
        edge = np.array([i["nadir_from_detected"] - NADIR_DEG for i in d if i["nadir_from_detected"] is not None], float)
        L.append(f"* `{k}`: cap detected as nadir in {100 * ok:.0f}% of frames; detected edge minus true edge: "
                 + (f"median {np.median(edge):+.2f} deg (p5 {np.percentile(edge, 5):+.2f}, p95 {np.percentile(edge, 95):+.2f})" if len(edge) else "n/a"))
    L.append("")
    for prot in protocols:
        for k in KINDS:
            for metric in ("region", "outside", "ring", "all"):
                raw, tab = summarize(rows, k, prot, metric)
                L += [f"## {k} · protocol `{prot}` · {metric} AbsRel (raw median {raw:.4f})", "",
                      "| variant | median AbsRel | change vs raw | frames improved | 95% CI of change |", "|---|---:|---:|---:|---:|"]
                for n, med, rel, win, lo, hi in tab:
                    L.append(f"| {n} | {med:.4f} | {100 * rel:+.1f}% | {100 * win:.0f}% | [{100 * lo:+.1f}, {100 * hi:+.1f}] |")
                L.append("")
    b = {}
    for k in KINDS:
        for prot in protocols[:1]:
            for n in ("raw", "oracle:plane_fill", "oracle:inpaint_erp"):
                v = [r[k][prot][n]["bias"] for r in rows if n in r[k][prot]]
                b[(k, n)] = float(np.nanmedian(v)) if v else float("nan")
    L += ["## Median predicted / true depth inside the cap (bias), headline protocol", "", "| input | raw | oracle plane_fill | oracle inpaint_erp |", "|---|---:|---:|---:|"]
    for k in KINDS:
        L.append(f"| {k} | {b[(k, 'raw')]:.3f} | {b[(k, 'oracle:plane_fill')]:.3f} | {b[(k, 'oracle:inpaint_erp')]:.3f} |")
    return "\n".join(L) + "\n"


def main():
    from analysis_common import ROOT, add_common_args, depth_range, load_config, load_dataset, load_model
    from distortions.catalogue import CATALOGUE, jpeg_apply
    from evaluation.distortion_analysis import headline_protocol
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(ap)
    ap.set_defaults(split="all", max_scenes=100)
    a = ap.parse_args()
    cfg = load_config(a.config, a.overrides)
    model = load_model(cfg)
    ds = load_dataset(cfg, a.split, a.max_scenes)
    min_d, max_d = depth_range(cfg)
    nad = {d.key: d for d in CATALOGUE}["nadir"]
    head = headline_protocol(model)
    protocols = [head] if head == "align-all" else [head, "align-all"]
    rows = []
    for i in range(len(ds)):
        smp = ds[i]
        gt = np.nan_to_num(smp.depth, nan=0.0)
        valid = smp.valid & (gt >= min_d) & (gt <= max_d)
        H, W = gt.shape
        masks = region_masks(H, W)
        rec = {"id": smp.id}
        clean = np.asarray(model.predict(smp.rgb, kind="erp"), dtype=np.float64)
        rec["clean"] = {p: score_variant(clean, gt, valid, model, masks, p, min_d, max_d) for p in protocols}
        for kind in KINDS:
            x, ctx = nad.apply(smp.rgb, {"seed": i, "depth": np.where(valid, gt, 2.0)})
            if kind.endswith("jpeg"):
                x, _ = jpeg_apply(x, ctx)
            true_caps = {"nadir_from": ctx["nadir_from"], "zenith_from": None}
            preds, info = build_variants(model, x, kind, true_caps)
            rec[kind] = {"info": info}
            for p in protocols:
                rec[kind][p] = {n: score_variant(v, gt, valid, model, masks, p, min_d, max_d) for n, v in preds.items()}
        rows.append(rec)
        r0 = rec["nadir+jpeg"][protocols[0]]
        print(f"[{i + 1}/{len(ds)}] {smp.id}: nadir+jpeg region raw {r0['raw']['region']:.3f} -> oracle plane_fill "
              f"{r0['oracle:plane_fill']['region']:.3f}, detected+1.5 {r0['detected+1.5:plane_fill']['region']:.3f}", flush=True)
    out = ROOT / "results" / "diag"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"nadir_jpeg_{a.tag}.json").write_text(json.dumps({"tag": a.tag, "protocols": protocols, "rows": rows}), encoding="utf-8")
    md = report(rows, a.tag, getattr(model, "name", "?"), protocols)
    (out / f"NADIR_JPEG_{a.tag}.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
