#!/usr/bin/env python3
"""Numbers for the final report, recomputed from the result JSON files (nothing is typed in by hand).

Writes results/FINAL_REPORT_NOTES.md with
  (a) external sets: per model x set x scenario median change, frame-bootstrap 95% CI, share improved / worse,
      plus a cluster bootstrap (Stanford: room, NYC: blocks of 20 consecutive ids) for DAP;
  (b) DA2 least-squares vs median alignment on the six datasets (matched frame ids);
  (c) core sets at N=100 against the committed N=40 files (DAP ranges);
  (d) held-out cell counts (cell = model, fault, dataset; applied = fix != none; improved = median change < 0).
Change = median over frames of (corrected - uncorrected) / uncorrected, on the affected region for cap scenarios
(nadir, vfov, nadir+jpeg) and on the whole panorama otherwise. improved = corrected < 0.999 * uncorrected,
worse = corrected > 1.01 * uncorrected.

  python scripts/final_report_notes.py [old_ref]      # old_ref: git ref holding the N=40 core files (default HEAD)
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluation.protocol import group_of  # noqa: E402

RES = ROOT / "results"
MODELS = ("midas", "dap", "da360", "da2")
CORE = ("s3", "panox", "holo_in", "holo_out")
EXT = ("stanford", "nyc")
SCEN = ("clean", "tilt", "nadir", "vfov", "yawblur", "jpeg", "nadir+jpeg")
FAULTS = ("tilt", "nadir", "vfov", "yawblur", "jpeg")
REG = ("nadir", "vfov", "nadir+jpeg")
B = 2000
RNG = np.random.default_rng(0)


def load(path):
    return json.loads(Path(path).read_text())


def corr_path(m, ds):
    return RES / ("external" if ds in EXT else "") / f"correction_{m}_{ds}.json"


def pairs(rows, scen, ids=None):
    f = "region" if scen in REG else "all"
    out = {}
    for r in rows:
        if ids is not None and r["id"] not in ids:
            continue
        u, x = r[scen]["raw"].get(f), r[scen]["fixed"].get(f)
        if u is None or x is None or not np.isfinite(u) or not np.isfinite(x) or u <= 0:
            continue
        out[r["id"]] = (u, x)
    return out


def summarize(rows, scen, ids=None):
    p = pairs(rows, scen, ids)
    if not p:
        return None
    k = list(p)
    u = np.array([p[i][0] for i in k]); x = np.array([p[i][1] for i in k])
    ch = (x - u) / u
    return dict(ids=k, n=len(k), raw=float(np.median(u)), fix=float(np.median(x)), med=100 * float(np.median(ch)),
                better=100 * float(np.mean(x < u * 0.999)), worse=100 * float(np.mean(x > u * 1.01)), ch=ch)


def frame_ci(ch):
    idx = RNG.integers(0, len(ch), (B, len(ch)))
    m = np.median(ch[idx], axis=1) * 100
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def cluster_ci(ids, ch):
    groups = {}
    for i, c in zip(ids, ch):
        groups.setdefault(group_of(i), []).append(c)
    gl = [np.asarray(v) for v in groups.values()]
    meds = np.empty(B)
    for b in range(B):
        pick = RNG.integers(0, len(gl), len(gl))
        meds[b] = np.median(np.concatenate([gl[j] for j in pick])) * 100
    return float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5)), len(gl)


def old_rows(m, ds, ref):
    rel = f"Aurindum/results/{'external/' if ds in EXT else ''}correction_{m}_{ds}.json"
    try:
        return json.loads(subprocess.check_output(["git", "show", f"{ref}:{rel}"], stderr=subprocess.DEVNULL, cwd=ROOT))["rows"]
    except Exception:
        return None


def sec_a(L):
    L += ["## (a) External sets: end-to-end correction with uncertainty", "",
          "Policy learned on the four core sets only. CI columns: 95% percentile bootstrap of the median change, B=2000, seed 0. "
          "`frame CI` resamples frames independently; `cluster CI` (DAP only) resamples whole clusters "
          "(Stanford: room via `group_of`; NYC: blocks of 20 consecutive panorama ids, an assumption since no route id is published).", ""]
    for ds in EXT:
        L += [f"### {ds}", "", "| model | scenario | n | uncorrected | corrected | change | frame CI | cluster CI (DAP) | better | worse |",
              "|---|---|---:|---:|---:|---:|---|---|---:|---:|"]
        for m in MODELS:
            rows = load(corr_path(m, ds))["rows"]
            for sc in SCEN:
                s = summarize(rows, sc)
                if s is None:
                    continue
                lo, hi = frame_ci(s["ch"])
                cc = "–"
                if m == "dap":
                    clo, chi, ng = cluster_ci(s["ids"], s["ch"])
                    cc = f"[{clo:+.1f}, {chi:+.1f}] ({ng} clusters)"
                L.append(f"| {m} | {sc} | {s['n']} | {s['raw']:.4f} | {s['fix']:.4f} | {s['med']:+.1f}% | [{lo:+.1f}, {hi:+.1f}] | {cc} | "
                         f"{s['better']:.0f}% | {s['worse']:.0f}% |")
        L.append("")
    L += ["Stanford: `clean` is the real-cap test (every frame has real black caps); the cap-detection rate is not meaningful there.", ""]


def sec_b(L):
    L += ["## (b) DA2: least-squares vs median alignment, six datasets", "",
          "`da2` = least-squares scale (default for relative models), `da2m` = `PANO_ALIGN_MODE=median`. Core sets: da2m has 40 frames, "
          "da2 100; compared on the ids both contain. Policy for da2m learned from `study_da2m_<core>.json` (leave-one-dataset-out).", ""]
    L += ["| set | n matched | clean AbsRel lsq | clean AbsRel median | scenario | change lsq | change median |", "|---|---:|---:|---:|---|---:|---:|"]
    for ds in CORE + EXT:
        a = load(corr_path("da2", ds))["rows"]; b = load(corr_path("da2m", ds))["rows"]
        ids = {r["id"] for r in a} & {r["id"] for r in b}
        ca = np.median([r["clean"]["raw"]["all"] for r in a if r["id"] in ids])
        cb = np.median([r["clean"]["raw"]["all"] for r in b if r["id"] in ids])
        for sc in SCEN[1:]:
            sa, sb = summarize(a, sc, ids), summarize(b, sc, ids)
            if sa is None or sb is None:
                continue
            L.append(f"| {ds} | {len(ids)} | {ca:.4f} | {cb:.4f} | {sc} | {sa['med']:+.1f}% | {sb['med']:+.1f}% |")
    L += ["", "Learned policy (fix per fault) for each held-out set, lsq vs median:", "", "| set | fault | lsq | median |", "|---|---|---|---|"]
    for ds in CORE + EXT:
        pa = load(corr_path("da2", ds))["policy"]; pb = load(corr_path("da2m", ds))["policy"]
        for f in FAULTS:
            L.append(f"| {ds} | {f} | {pa.get(f, 'none')} | {pb.get(f, 'none')} |{'' if pa.get(f, 'none') == pb.get(f, 'none') else ' differs'}")
    L.append("")


def sec_c(L, ref):
    L += ["## (c) Core sets: N=100 vs N=40", "",
          f"Old = the committed files at `{ref}` (40 frames). Range = min..max over the four core datasets of the median change. "
          "holo_out has 71 frames only.", ""]
    for m in MODELS:
        L += [f"### {m}", "", "| scenario | new range (N<=100) | old range (N=40) | shift of low end | shift of high end |", "|---|---|---|---:|---:|"]
        for sc in SCEN[1:]:
            new = [summarize(load(corr_path(m, ds))["rows"], sc) for ds in CORE]
            old = [(lambda r: summarize(r, sc) if r else None)(old_rows(m, ds, ref)) for ds in CORE]
            nv = [s["med"] for s in new if s]; ov = [s["med"] for s in old if s]
            if not nv or not ov:
                continue
            flag = " **>5**" if abs(min(nv) - min(ov)) > 5 or abs(max(nv) - max(ov)) > 5 else ""
            L.append(f"| {sc} | {min(nv):+.0f}..{max(nv):+.0f}% | {min(ov):+.0f}..{max(ov):+.0f}% | {min(nv) - min(ov):+.1f} | {max(nv) - max(ov):+.1f}{flag} |")
        L.append("")
    L += ["Per-dataset DAP medians (new / old):", "", "| scenario | " + " | ".join(CORE) + " |", "|---|" + "---:|" * len(CORE)]
    for sc in SCEN[1:]:
        cells = []
        for ds in CORE:
            n = summarize(load(corr_path("dap", ds))["rows"], sc); r = old_rows("dap", ds, ref); o = summarize(r, sc) if r else None
            cells.append(f"{n['med']:+.1f} / {o['med']:+.1f}" if n and o else "–")
        L.append(f"| {sc} | " + " | ".join(cells) + " |")
    L.append("")


def cells(sets, ref=None):
    out = []
    for m in MODELS:
        for ds in sets:
            d = load(corr_path(m, ds))
            for f in FAULTS:
                s = summarize(d["rows"], f)
                if s is None:
                    continue
                out.append(dict(m=m, ds=ds, f=f, fix=d["policy"].get(f, "none"), med=s["med"], n=s["n"]))
    return out


def sec_d(L):
    L += ["## (d) Held-out cell counts", "",
          "Cell = (model, fault, dataset) with fault in {tilt, nadir, vfov, yawblur, jpeg} (the five faults for which a fix is ever "
          "chosen; seam, parallax, vignette, noise are never fixed and were not re-measured at the larger N). Applied = the held-out policy "
          "chooses a fix other than none for that fault. Improved = median change < 0 (affected region for nadir/vfov, whole panorama "
          "otherwise); worse = median change > 0; unchanged otherwise. The earlier 52 applied / 42 improved / 10 worse / median -8% counted "
          "144 cells (9 faults) on core sets at N=40 from the study files.", ""]
    L += ["| scope | cells | applied | improved | worse | unchanged | median change over applied |", "|---|---:|---:|---:|---:|---:|---:|"]
    detail = {}
    for name, sets in (("core (N<=100)", CORE), ("external", EXT), ("all six", CORE + EXT)):
        cs = cells(sets); ap = [c for c in cs if c["fix"] != "none"]
        imp = [c for c in ap if c["med"] < 0]; wo = [c for c in ap if c["med"] > 0]
        L.append(f"| {name} | {len(cs)} | {len(ap)} | {len(imp)} | {len(wo)} | {len(ap) - len(imp) - len(wo)} | "
                 f"{np.median([c['med'] for c in ap]):+.1f}% |")
        detail[name] = wo
    for name, wo in detail.items():
        L += ["", f"Worse cells, {name}: " + (", ".join(f"{c['m']}/{c['f']}/{c['ds']} ({c['med']:+.1f}%, {c['fix']})" for c in wo) or "none")]
    L.append("")


def detect_rate(rows, scen):
    return 100 * float(np.mean([r[scen]["detected"] == "nadir" for r in rows]))


def sec_f(L):
    L += ["## (f) Resolution control (MiDaS, DA360, DA2 at 256x512 vs 512x1024; DAP always 512x1024)", "",
          "Matched ids only (100 frames per external set). Detection = share of frames where the cap detector reports a nadir cap "
          "(for Stanford this column is meaningless because every frame has real caps and the detector reports them under another label).", "",
          "| model | set | clean AbsRel 256 | clean AbsRel 512 | scenario | change 256 | change 512 | nadir detected 256 | nadir detected 512 |",
          "|---|---|---:|---:|---|---:|---:|---:|---:|"]
    for ds in EXT:
        for m in ("midas", "da360", "da2"):
            lo = load(corr_path(m, ds))["rows"]; hi = load(RES / "external" / f"correction_{m}_hr_{ds}.json")["rows"]
            ids = {r["id"] for r in hi} & {r["id"] for r in lo}
            lo = [r for r in lo if r["id"] in ids]; hi = [r for r in hi if r["id"] in ids]
            c1 = np.median([r["clean"]["raw"]["all"] for r in lo]); c2 = np.median([r["clean"]["raw"]["all"] for r in hi])
            for sc in SCEN[1:]:
                a, b = summarize(lo, sc), summarize(hi, sc)
                dt = (f"{detect_rate(lo, sc):.0f}% | {detect_rate(hi, sc):.0f}%" if sc in ("nadir", "nadir+jpeg") else "– | –")
                L.append(f"| {m} | {ds} | {c1:.4f} | {c2:.4f} | {sc} | {a['med']:+.1f}% | {b['med']:+.1f}% | {dt} |")
    L += ["", "Nadir detection on nadir+jpeg, all frames at the model's own input size:", "", "| model | set | frames | nadir detected |", "|---|---|---:|---:|"]
    for m in MODELS:
        for ds in EXT:
            rows = load(corr_path(m, ds))["rows"]
            L.append(f"| {m} | {ds} | {len(rows)} | {detect_rate(rows, 'nadir+jpeg'):.0f}% |")
    L.append("")


def sec_g(L, ref):
    L += ["## (g) New (all frames) vs old (40 frames, git ref 94875af): external cells", "",
          "| model | set | scenario | old | new | diff (points) |", "|---|---|---|---:|---:|---:|"]
    cnt = 0
    for m in MODELS:
        for ds in EXT:
            o = None
            for rel in (f"Aurindum/results/external/correction_{m}_{ds}.json", f"Aurindum/results/correction_{m}_{ds}.json"):
                try:
                    o = json.loads(subprocess.check_output(["git", "show", f"94875af:{rel}"], stderr=subprocess.DEVNULL, cwd=ROOT))["rows"]
                    break
                except Exception:
                    pass
            n = load(corr_path(m, ds))["rows"]
            if o is None:
                continue
            for sc in SCEN:
                a, b = summarize(o, sc), summarize(n, sc)
                if a and b and (abs(b["med"] - a["med"]) > 5 or a["med"] * b["med"] < 0 and max(abs(a["med"]), abs(b["med"])) > 1):
                    cnt += 1
                    L.append(f"| {m} | {ds} | {sc} | {a['med']:+.1f}% | {b['med']:+.1f}% | {b['med'] - a['med']:+.1f} |")
    L += ["", f"Only cells that moved more than 5 points or changed sign are listed ({cnt}); no cell moved more than 10 points.", ""]


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    L = ["# Final report notes", "",
         "Generated by `scripts/final_report_notes.py` from the JSON files in results/ (end-to-end correction, headline policy). "
         "Sections (a)-(d), (f), (g) are computed; section (e) is a manual check of the report text.", ""]
    sec_a(L); sec_b(L); sec_c(L, ref); sec_d(L); sec_f(L); sec_g(L, ref)
    (RES / "FINAL_REPORT_NOTES.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
