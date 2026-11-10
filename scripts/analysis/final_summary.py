#!/usr/bin/env python3
"""Summary tables of the final experiments -> results/FINAL_ablations.md.

  1. Sample size: per model x external set, number of frames and, per scenario, the median per-frame change of AbsRel
     (corrected vs uncorrected) with a bootstrap 95% CI over frames, share of frames improved / worse.
  2. Alignment protocol for DA2: least squares (tag da2_<set>) vs median (tag da2m_<set>, policy learned under median).
  3. Input resolution: 256 x 512 (tag <m>_<set>) vs 512 x 1024 (tag <m>_hr_<set>) on the cap-detection scenarios.
Missing files are skipped. Frames are bootstrapped independently (street blocks / rooms are not known here), so the CIs are
optimistic for clustered data.
"""
from __future__ import annotations

import json

import numpy as np

from pano.paths import BENCHMARK_RESULTS  # noqa: E402
RES = BENCHMARK_RESULTS
CORE = ("s3", "panox", "holo_in", "holo_out")
EXT = ("stanford", "nyc")
SCEN = ["clean", "tilt", "nadir", "vfov", "yawblur", "jpeg", "nadir+jpeg"]
REGION = {"nadir", "vfov", "nadir+jpeg"}
EXPECT = {"nadir": "nadir", "vfov": "vfov", "nadir+jpeg": "nadir"}


def load(model, ds, tag=None):
    tag = tag or f"{model}_{ds}"
    p = (RES if ds in CORE else RES / "external") / f"correction_{tag}.json"
    return json.loads(p.read_text())["rows"] if p.is_file() else None


def cell(rows, scen, n_boot=1000, seed=0):
    f = "region" if scen in REGION else "all"
    u = np.array([r[scen]["raw"][f] for r in rows], float)
    x = np.array([r[scen]["fixed"][f] for r in rows], float)
    ok = np.isfinite(u) & np.isfinite(x) & (u > 0)
    u, x = u[ok], x[ok]
    if len(u) == 0:
        return None
    ch = 100 * (x - u) / u
    rng = np.random.default_rng(seed)
    meds = np.median(ch[rng.integers(0, len(ch), (n_boot, len(ch)))], axis=1)
    det = np.mean([r[scen]["detected"] == EXPECT[scen] for r in rows]) if scen in EXPECT else np.nan
    return {"n": len(u), "chg": float(np.median(ch)), "lo": float(np.percentile(meds, 2.5)), "hi": float(np.percentile(meds, 97.5)),
            "better": float(np.mean(x < u * 0.999)), "worse": float(np.mean(x > u * 1.01)), "det": float(det)}


def fmt(c):
    return "n/a" if c is None else f"{c['chg']:+.1f}% [{c['lo']:+.1f}, {c['hi']:+.1f}] ({100 * c['better']:.0f}/{100 * c['worse']:.0f})"


def main():
    L = ["# Final experiments", "",
         "Cells: median per-frame change of AbsRel after correction [bootstrap 95% CI over frames] (% frames improved / % worse >1%).",
         "Cap scenarios are scored on the occluded region, the others on the whole panorama.", ""]
    L += ["## 1. Corrections per model and external set", ""]
    for ds in EXT:
        L += [f"### {ds}", "", "| model | frames | " + " | ".join(SCEN[1:]) + " |", "|---|---:|" + "---|" * (len(SCEN) - 1)]
        for m in ("midas", "dap", "da360", "da2"):
            rows = load(m, ds)
            if rows:
                L.append(f"| {m} | {len(rows)} | " + " | ".join(fmt(cell(rows, s)) for s in SCEN[1:]) + " |")
        L.append("")
    L += ["## 2. DA2: least-squares vs median scale alignment", "",
          "| set | protocol | frames | clean AbsRel | " + " | ".join(SCEN[1:]) + " |", "|---|---|---:|---:|" + "---|" * (len(SCEN) - 1)]
    for ds in CORE + EXT:
        for name, tag in (("lsq", None), ("median", f"da2m_{ds}" if ds != "nyc" else None)):
            rows = load("da2", ds, tag)
            if tag is None and name == "median" and ds == "nyc":
                rows = load("da2", ds, "da2_nyc_median")   # the first median check
            if rows:
                cl = np.nanmedian([r["clean"]["clean"]["all"] for r in rows])
                L.append(f"| {ds} | {name} | {len(rows)} | {cl:.3f} | " + " | ".join(fmt(cell(rows, s)) for s in SCEN[1:]) + " |")
    L += ["", "## 3. Input resolution: 256x512 vs 512x1024 (cap detection and fixes)", "",
          "| model | set | input | frames | cap detected (nadir / vfov / nadir+jpeg) | nadir | vfov | nadir+jpeg |", "|---|---|---|---:|---|---|---|---|"]
    for m in ("midas", "da360", "da2"):
        for ds in EXT:
            for name, tag in (("256x512", None), ("512x1024", f"{m}_hr_{ds}")):
                rows = load(m, ds, tag)
                if rows:
                    cs = {s: cell(rows, s) for s in ("nadir", "vfov", "nadir+jpeg")}
                    det = " / ".join(f"{100 * cs[s]['det']:.0f}%" for s in cs)
                    L.append(f"| {m} | {ds} | {name} | {len(rows)} | {det} | " + " | ".join(fmt(cs[s]) for s in cs) + " |")
    (RES / "FINAL_ablations.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
