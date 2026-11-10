"""Streamlit app for Distortion-Aware Panoramic Depth Estimation.

Run from the repository root (or from app/):
    python -m streamlit run app/streamlit_app.py

The app only reads precomputed results that are already in the repository
(figures, per-image metric CSVs and correction JSONs). No model weights or
datasets are needed. Examples are filtered so each method page shows only the
scenes where that method actually helps.
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from pano.paths import (
    ROOT,
    BENCHMARK_RESULTS as BENCH_RES,
    PROJECTION_RESULTS as PROJ_RES,
    NYC_RESULTS,
    FOLLOWUP_RESULTS,
    ARCHIVES,
    REPORT,
)
from scripts.figures import example_panels as EP

# A method must lower polar AbsRel by at least this fraction to count as a "good" example.
GOOD_GAIN = 0.10

PROJ_DATASETS = {
    "Structured3D": "structured3d",
    "Holo360D indoor": "holo360d_indoor",
    "Holo360D outdoor": "holo360d_outdoor",
}

st.set_page_config(page_title="Panoramic Depth Methods", layout="wide",
                   initial_sidebar_state="expanded")

# --------------------------------------------------------------------------------------
# Visual identity
# --------------------------------------------------------------------------------------
# Fixed categorical order (validated for colour-blind separation); baseline is neutral grey.
COLORS = {
    "baseline": "#8a8f98",
    "tangent": "#2a78d6",
    "rotation": "#eb6834",
    "hybrid": "#1baf7a",
    "mono360": "#eda100",
    "acgf": "#e87ba4",
    "faults": "#6250d6",
}
LABELS = {"baseline": "Baseline", "tangent": "Tangent", "rotation": "Rotation", "hybrid": "Hybrid",
          "mono360": "360MonoDepth", "acgf": "ACGF v2"}

CSS = """
<style>
:root { --ink:#1d2433; --muted:#5b6474; --line:#e3e7ee; --soft:#f4f6fa; --accent:#2a78d6; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1280px; }
h1, h2, h3 { letter-spacing: -0.01em; }
section[data-testid="stSidebar"] { background: #f4f6fa; border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

.hero { background: linear-gradient(120deg, #0f2747 0%, #17406f 50%, #2a78d6 100%);
        border-radius: 18px; padding: 26px 30px 22px; margin: 0 0 18px; color: #fff; position: relative; overflow: hidden; }
.hero::after { content: ""; position: absolute; right: -60px; top: -60px; width: 260px; height: 260px;
               border-radius: 50%; border: 36px solid rgba(255,255,255,.06); }
.hero .eyebrow { font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; color: #a9c6ee; font-weight: 600; }
.hero h1 { color: #fff; font-size: 2.05rem; margin: 4px 0 6px; padding: 0; line-height: 1.2; }
.hero p { color: #dbe6f5; margin: 0; font-size: 1.02rem; max-width: 860px; }
.chips { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px; }
.chip { background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.28); color: #fff;
        padding: 3px 12px; border-radius: 999px; font-size: .8rem; }

.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 12px; margin: 4px 0 18px; }
.fact { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }
.fact .k { font-size: .72rem; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); font-weight: 600; }
.fact .v { font-size: 1.02rem; font-weight: 650; color: var(--ink); margin-top: 3px; }

.stat { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; text-align: center; }
.stat .n { font-size: 1.9rem; font-weight: 700; color: var(--ink); line-height: 1.1; }
.stat .l { font-size: .8rem; color: var(--muted); margin-top: 4px; }

.sec { display: flex; align-items: baseline; gap: 10px; margin: 26px 0 8px; }
.sec .t { font-size: 1.25rem; font-weight: 700; color: var(--ink); }
.sec .s { color: var(--muted); font-size: .92rem; }

.card { background: #fff; border: 1px solid var(--line); border-top: 4px solid var(--c);
        border-radius: 14px; padding: 14px 16px 10px; height: 178px; margin-bottom: 8px; display: flex; flex-direction: column; }
.card .b { margin-top: auto !important; align-self: flex-start; }
.card .h { font-weight: 700; font-size: 1.02rem; color: var(--ink); }
.card .who { font-size: .74rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-top: 2px; }
.card .d { color: #39414f; font-size: .9rem; margin-top: 8px; line-height: 1.45; }
.card .b { display: inline-block; margin-top: 8px; font-size: .78rem; background: var(--soft); border-radius: 999px;
           padding: 2px 10px; color: var(--ink); }

.legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: .8rem; color: var(--muted); margin-top: 4px; }
.legend span::before { content: ""; display: inline-block; width: 11px; height: 11px; border-radius: 3px;
                       margin-right: 6px; vertical-align: -1px; background: var(--c); border: 1px solid var(--b); }
.callout { background: #eef5fd; border: 1px solid #cfe1f7; border-left: 4px solid var(--accent);
           padding: 12px 16px; border-radius: 10px; color: var(--ink); margin: 10px 0; }
.howto { color: #39414f; font-size: .97rem; line-height: 1.6; }

div[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 12px 16px; }
div[data-testid="stMetricLabel"] p { font-size: .8rem; color: var(--muted); }
div[data-testid="stImage"] img { border-radius: 10px; }
button[data-baseweb="tab"] p { font-size: .95rem; font-weight: 600; }
.sb-brand { font-weight: 800; font-size: 1.15rem; color: var(--ink); }
.sb-sub { font-size: .8rem; color: var(--muted); margin-bottom: 6px; }
.pan { margin: 0 0 6px; }
.pan .tt { font-weight: 700; font-size: .86rem; color: var(--ink); text-align: center; margin-bottom: 4px; }
.pan .g { display: grid; grid-template-columns: 30px minmax(0, 1fr); column-gap: 4px; }
.pan .ya { position: relative; font-size: .62rem; color: var(--muted); }
.pan .ya span { position: absolute; right: 2px; transform: translateY(-50%); white-space: nowrap; }
.pan .ya .yl { position: absolute; left: -2px; top: 50%; transform: translate(-30%, -50%) rotate(-90deg); font-size: .62rem; }
.pan img { width: 100%; display: block; border: 1px solid #c9ced8; border-radius: 2px; }
.pan .xa { position: relative; height: 13px; font-size: .62rem; color: var(--muted); }
.pan .xa span { position: absolute; transform: translateX(-50%); top: 1px; }
.pan .xl { text-align: center; font-size: .62rem; color: var(--muted); margin-top: 1px; }
.pan .cb { height: 9px; border-radius: 2px; border: 1px solid #c9ced8; margin-top: 7px; }
.pan .ct { position: relative; height: 13px; font-size: .64rem; color: #39414f; }
.pan .ct span { position: absolute; transform: translateX(-50%); top: 1px; white-space: nowrap; }
.pan .cl { text-align: center; font-size: .66rem; color: var(--muted); }
.sb-card { background: #fff; border: 1px solid var(--line); border-left: 4px solid var(--c); border-radius: 10px;
           padding: 10px 12px; font-size: .85rem; color: #39414f; margin-top: 8px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, eyebrow: str = "", chips: list[str] | None = None):
    chips_html = "".join(f'<span class="chip">{c}</span>' for c in chips or [])
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p>'
                f'<div class="chips">{chips_html}</div></div>', unsafe_allow_html=True)


def facts(items: list[tuple[str, str]]):
    st.markdown('<div class="facts">' + "".join(f'<div class="fact"><div class="k">{k}</div><div class="v">{v}</div></div>'
                                                for k, v in items) + "</div>", unsafe_allow_html=True)


def section(title: str, sub: str = ""):
    st.markdown(f'<div class="sec"><span class="t">{title}</span><span class="s">{sub}</span></div>', unsafe_allow_html=True)


EX_MODES = {"help": "Where it helps", "hurt": "Where it hurts", "all": "All stored examples"}


def ex_mode() -> str:
    return st.session_state.get("ex_mode", "help")


def keep_gain(gain: float, mode: str) -> bool:
    """Example filter. help: error drops by >= GOOD_GAIN; hurt: error rises; all: no filter."""
    if mode == "help":
        return gain >= GOOD_GAIN
    if mode == "hurt":
        return gain < 0
    return True


def ex_sub(what: str = "error") -> str:
    m = ex_mode()
    if m == "help":
        return f"only stored scenes where {what} drops by at least {GOOD_GAIN:.0%} (change in the sidebar)"
    if m == "hurt":
        return f"only stored scenes where {what} gets worse (change in the sidebar)"
    return "every stored scene, whether the method helps or not (change in the sidebar)"


def ex_order(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("gain", ascending=ex_mode() == "hurt")


def ex_label() -> str:
    return {"help": "Example (best first)", "hurt": "Example (worst first)", "all": "Example (best first)"}[ex_mode()]


def share_line(better: int, worse: int, n: int, scope: str):
    if n:
        st.caption(f"Across {n} {scope}: **{better / n:.0%} improved**, **{worse / n:.0%} worse**, "
                   f"{(n - better - worse) / n:.0%} about the same (within 1%). "
                   "The examples below are a filtered subset; these shares are not.")


def callout(text: str):
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)  # allow **bold** inside the HTML box
    st.markdown(f'<div class="callout">{text}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------------------
# Pipeline diagrams
# --------------------------------------------------------------------------------------
N_IN = 'shape=box, style="rounded,filled", fillcolor="#e3eefc", color="#9ec5f4"'
N_BASE = 'shape=box, style="rounded,filled", fillcolor="#eef0f4", color="#c9ced8"'
HL = 'shape=box, style="rounded,filled", fillcolor="#fde6d6", color="#eb6834", penwidth=1.4'
N_OUT = 'shape=box, style="rounded,filled", fillcolor="#d9f3e8", color="#1baf7a", penwidth=1.4'
BASE_NODES = f"""
  rgb [label="ERP panorama\\n512×1024", {N_IN}];
  model [label="Frozen depth model", {N_BASE}];
  base [label="Baseline ERP depth", {N_BASE}];
"""
PIPE_LEGEND = ('<div class="legend"><span style="--c:#e3eefc;--b:#9ec5f4">input</span>'
               '<span style="--c:#eef0f4;--b:#c9ced8">baseline path (shared)</span>'
               '<span style="--c:#fde6d6;--b:#eb6834">added by this method</span>'
               '<span style="--c:#d9f3e8;--b:#1baf7a">output</span></div>')


def graph(body: str, rankdir: str = "LR") -> str:
    return ('digraph G { rankdir=' + rankdir + '; bgcolor="transparent"; nodesep=0.25; ranksep=0.35;'
            'node [fontname="Helvetica", fontsize=11, margin="0.14,0.07", fontcolor="#1d2433"];'
            'edge [color="#8a93a3", arrowsize=0.7, fontname="Helvetica", fontsize=9, fontcolor="#5b6474"];'
            + BASE_NODES + body + "}")


def pipeline(dot: str, stretch: bool = True):
    with st.container(border=True):
        st.graphviz_chart(dot, use_container_width=stretch)
        st.markdown(PIPE_LEGEND, unsafe_allow_html=True)


# --------------------------------------------------------------------------------------
# Method catalogue
# --------------------------------------------------------------------------------------
METHODS = {
    "tangent": dict(
        name="Tangent-plane views", prefix="tangent", fig="tangent", run="acgf_midas_{ds}",
        tagline="Re-sample each polar cap into an undistorted pinhole view and fuse it back.",
        facts=[("Extra views", "2 gnomonic (N, S)"), ("Model calls", "3"), ("Fusion", "Cosine latitude blend"),
               ("Runtime", "2.6× baseline"), ("Best at", "Holo360D indoor poles")],
        idea=(
            "The poles of an ERP image are stretched by 1/cos φ (×2 at 60°, ×3.9 at 75°). "
            "This method re-samples each polar cap (|φ| > 45°) into an undistorted **gnomonic (pinhole) view** "
            "pointed straight up / down, runs the frozen model on it, converts planar depth z to range, "
            "aligns it to the baseline on trusted pixels (no ground truth), back-projects to ERP and "
            "blends it in with a cosine latitude ramp."
        ),
        diff=["Adds **2 pinhole views** of the poles", "Only the caps |φ| > 45° change; the equator stays the baseline",
              "Alignment uses baseline pixels only, never ground truth"],
        graph=graph(f"""
  rgb -> model -> base;
  tp [label="Gnomonic views\\nN & S poles, FOV 110°", {HL}];
  m2 [label="Frozen model\\n(perspective input)", {HL}];
  al [label="z → range +\\nrobust align", {HL}];
  bp [label="Back-project\\nto ERP", {HL}];
  fu [label="Cosine latitude blend\\n|φ| > 45° ± 10°", {HL}];
  out [label="Corrected depth", {N_OUT}];
  rgb -> tp -> m2 -> al -> bp -> fu -> out; base -> al [style=dashed, label="anchors"]; base -> fu;
"""),
        extra="tangent_view",
    ),
    "rotation": dict(
        name="Rotation ensemble", prefix="rotation", fig="rotation", run="acgf_midas_{ds}",
        tagline="Rotate the sphere so each pole lands on the undistorted equator.",
        facts=[("Extra views", "2 rotated ERPs (pitch ±90°)"), ("Model calls", "3"), ("Fusion", "Prior cos(λ)² + blend"),
               ("Runtime", "4.4× baseline"), ("Best at", "Structured3D (2nd)")],
        idea=(
            "Instead of pinhole views, the whole sphere is **rotated** (a true SO(3) resampling, not a pixel roll). "
            "A pitch of ±90° moves each pole onto the equator of a new ERP, where it is barely distorted. "
            "The model runs on each rotated ERP, the predictions are rotated back, merged with a per-pixel "
            "distortion prior cos(λ)² and blended with the baseline."
        ),
        diff=["Model still sees **full ERP panoramas**, just rotated", "No pinhole conversion needed (range is rotation-invariant)",
              "Each pixel trusts the view where it sat closest to the equator"],
        graph=graph(f"""
  rgb -> model -> base;
  r1 [label="Rotate sphere\\npitch +90°", {HL}]; r2 [label="Rotate sphere\\npitch −90°", {HL}];
  m2 [label="Frozen model\\n(ERP input)", {HL}];
  ib [label="Rotate predictions\\nback", {HL}];
  mg [label="Merge with\\nprior cos(λ)²", {HL}];
  fu [label="Cosine latitude\\nblend", {HL}];
  out [label="Corrected depth", {N_OUT}];
  rgb -> r1 -> m2; rgb -> r2 -> m2; m2 -> ib -> mg -> fu -> out; base -> fu;
"""),
    ),
    "hybrid": dict(
        name="Hybrid (tangent + rotation)", prefix="hybrid", fig="hybrid", run="acgf_midas_{ds}",
        tagline="Pool pinhole and rotated views; the least distorted one wins per pixel.",
        facts=[("Extra views", "2 gnomonic + 2 rotated"), ("Model calls", "5"), ("Fusion", "Pooled prior + blend"),
               ("Runtime", "5.8× baseline"), ("Best at", "Robust all-rounder")],
        idea=(
            "Puts the tangent views **and** the rotated-sphere passes into one pool. Each view carries its own "
            "distortion coordinate λ (off-axis angle for pinhole views, in-image latitude for rotated ERPs), so "
            "the prior cos(λ)² lets the least distorted view win per pixel before blending with the baseline."
        ),
        diff=["Union of the tangent and rotation views", "One shared distortion coordinate makes the views comparable",
              "More views means more model calls (5 instead of 3)"],
        graph=graph(f"""
  rgb -> model -> base;
  tp [label="Gnomonic\\npole views", {HL}]; rot [label="Rotated\\nspheres ±90°", {HL}];
  m2 [label="Frozen model", {HL}];
  al [label="Align each view\\nto baseline", {HL}];
  mg [label="Pool & merge\\nprior cos(λ)²", {HL}];
  fu [label="Cosine latitude\\nblend", {HL}];
  out [label="Corrected depth", {N_OUT}];
  rgb -> tp -> m2; rgb -> rot -> m2; m2 -> al -> mg -> fu -> out; base -> al [style=dashed]; base -> fu;
"""),
    ),
    "mono360": dict(
        name="360MonoDepth", prefix="mono360", fig="mono360",
        run="acgf_midas_{ds}",
        tagline="Cover the sphere with 20 pinhole views and stitch them into one panorama.",
        facts=[("Extra views", "20 icosahedral"), ("Model calls", "20 (no ERP pass)"), ("Fusion", "Deformable grids"),
               ("Runtime", "24× baseline"), ("Best at", "Structured3D")],
        idea=(
            "Prior work used as a reference: the sphere is covered by **20 icosahedral pinhole views**. Each view "
            "gets a deformable per-view scale/offset grid fitted so the views agree with **each other** (not with "
            "the ERP pass), then they are blended into a full panorama. Strongest on Structured3D, but not "
            "anchored to the baseline, so it is less stable on real captures."
        ),
        diff=["Replaces the **whole** panorama, equator included", "Never uses the baseline ERP prediction",
              "Most accurate on synthetic scenes, least stable on real captures"],
        graph=graph(f"""
  ico [label="20 icosahedral\\npinhole views", {HL}];
  m2 [label="Frozen model\\n×20 calls", {HL}];
  gr [label="Deformable scale/offset\\ngrids (mutual fit)", {HL}];
  bl [label="Blend all views\\nto ERP", {HL}];
  out [label="Panoramic depth\\n(baseline unused)", {N_OUT}];
  rgb -> ico -> m2 -> gr -> bl -> out;
"""),
    ),
    "acgf": dict(
        name="ACGF v2", prefix="acgf", fig="acgf", run="acgf_midas_{ds}_v2",
        tagline="Fuse pole views in the gradient domain, with a gate that falls back to the baseline.",
        facts=[("Extra views", "2 stereographic + 2 gnomonic"), ("Model calls", "5"), ("Fusion", "Gradient solve + gate γ"),
               ("Runtime", "~22× baseline"), ("Best at", "Holo360D outdoor poles")],
        idea=(
            "**Adaptive Conformal Gradient Fusion.** Pole views (stereographic, FOV 180° and gnomonic, FOV 110°) are "
            "fused in the **gradient domain**: the views' depth gradients define the polar caps, a sparse Poisson-type "
            "solve integrates them while the equator stays fixed to the baseline, and a **gate γ** measures "
            "per-pixel view agreement versus the baseline so untrusted corrections fall back to the baseline. "
            "v2 fuses in linear disparity and applies the gate to the solved values."
        ),
        diff=["Fuses **gradients**, not values, so seams vanish", "Gate γ keeps the baseline where views disagree",
              "Designed to *do no harm*: fewest severe failures of all methods"],
        graph=graph(f"""
  rgb -> model -> base;
  sv [label="Stereographic +\\ngnomonic pole views", {HL}];
  m2 [label="Frozen model", {HL}];
  gd [label="Per-edge gradient\\nconsensus", {HL}];
  so [label="Sparse solve\\n(equator fixed)", {HL}];
  ga [label="Gate γ\\n(trust views?)", {HL}];
  out [label="Corrected depth", {N_OUT}];
  rgb -> sv -> m2 -> gd -> so -> ga -> out; base -> so [style=dashed, label="boundary"]; base -> ga;
"""),
        extra="acgf_views",
    ),
}

# Published results (projection corrections study §10.2): MiDaS DPT-Hybrid, align-equatorial, full test splits.
_SETS = ["Structured3D", "Holo360D indoor", "Holo360D outdoor"]
POLAR = pd.DataFrame([[0.536, 0.363, 0.707], [0.379, 0.321, 0.784], [0.256, 0.566, 0.841],
                      [0.274, 0.393, 0.589], [0.171, 0.416, 0.663], [0.329, 0.386, 0.579]],
                     index=list(LABELS.values()), columns=_SETS)
WHOLE = pd.DataFrame([[0.354, 0.345, 0.517], [0.297, 0.333, 0.543], [0.239, 0.403, 0.554],
                      [0.248, 0.352, 0.486], [0.170, 0.399, 0.475], [0.276, 0.349, 0.476]],
                     index=list(LABELS.values()), columns=_SETS)
RUNTIME = pd.Series([1.0, 2.6, 4.4, 5.8, 24.0, 22.0], index=list(LABELS.values()))

FAULTS = {
    "tilt": "Camera tilt (horizon not level)",
    "nadir": "Nadir hole (tripod / masked floor cap)",
    "vfov": "Limited vertical FOV (missing caps)",
    "yawblur": "Yaw motion blur",
    "jpeg": "Heavy JPEG compression",
    "nadir+jpeg": "Nadir hole + JPEG",
}
FAULT_MODELS = {"MiDaS DPT-Hybrid": "midas", "DAP": "dap", "DA²": "da2", "DA360": "da360"}
FAULT_SETS = {
    "Structured3D": ("s3", BENCH_RES),
    "PanoX": ("panox", BENCH_RES),
    "Holo360D indoor": ("holo_in", BENCH_RES),
    "Holo360D outdoor": ("holo_out", BENCH_RES),
    "Stanford2D3D (external)": ("stanford", BENCH_RES / "external"),
    "NYC panoramas (external)": ("nyc", BENCH_RES / "external"),
}


# --------------------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def scene_metrics(run: str) -> pd.DataFrame:
    """Per image × method: whole-image and polar (60–90°) AbsRel, MiDaS align-equatorial protocol."""
    f = PROJ_RES / run / "rows_align-equatorial.csv"
    if not f.is_file():
        return pd.DataFrame()
    d = pd.read_csv(f, dtype={"image": str}, usecols=["image", "method", "band", "weighting", "n", "abs_rel"])
    d = d[d.weighting == "pixel"]
    d["m"] = d.method.str.split("|").str[0]
    whole = d[d.band == "all"].groupby(["image", "m"]).abs_rel.mean().rename("whole")
    pol = d[d.band.isin(["60-75", "75-90"])].copy()
    pol["w"] = pol.abs_rel * pol.n
    pol = pol.groupby(["image", "m"]).agg(w=("w", "sum"), n=("n", "sum"))
    polar = (pol.w / pol.n).rename("polar")
    return pd.concat([whole, polar], axis=1).reset_index()


def qual_scenes(run: str, fig: str) -> list[str]:
    q = PROJ_RES / run / "qualitative"
    return sorted(p.name[: -len(f"_{fig}.png")] for p in q.glob(f"*_{fig}.png")) if q.is_dir() else []


@st.cache_data(show_spinner=False)
def good_examples(method_key: str, ds: str, mode: str = "help") -> pd.DataFrame:
    """Scenes with a qualitative figure, filtered by mode (see keep_gain)."""
    m = METHODS[method_key]
    run = m["run"].format(ds=ds)
    met = scene_metrics(run)
    rows = []
    for sc in qual_scenes(run, m["fig"]):
        s = met[met.image == sc].set_index("m")
        if "baseline" not in s.index or m["prefix"] not in s.index:
            continue
        b, c = s.loc["baseline"], s.loc[m["prefix"]]
        gain = 1 - c.polar / b.polar
        if keep_gain(gain, mode):
            rows.append(dict(scene=sc, base_polar=b.polar, polar=c.polar, base_whole=b.whole, whole=c.whole, gain=gain))
    return pd.DataFrame(rows).sort_values("gain", ascending=False) if rows else pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_json(path: str):
    p = Path(path)
    return json.loads(p.read_text()) if p.is_file() else None


def fault_metric_key(sc: str) -> str:
    return "region" if sc in ("nadir", "vfov", "nadir+jpeg") else "all"


def finite(x) -> bool:
    return x is not None and np.isfinite(x)


@st.cache_data(show_spinner=False)
def fault_examples(model: str, ds: str, folder: str, mode: str = "help") -> pd.DataFrame:
    c = load_json(str(Path(folder) / f"correction_{model}_{ds}.json"))
    if not c or not c.get("examples"):
        return pd.DataFrame()
    rows = []
    for r in c["rows"]:
        if r["id"] not in c["examples"]:
            continue
        for sc, v in r.items():
            if sc in ("id", "clean") or not isinstance(v, dict):
                continue
            k = fault_metric_key(sc)
            raw, fixed, clean = v["raw"].get(k), v["fixed"].get(k), v["clean"].get(k)
            if not (finite(raw) and finite(fixed)) or "no fault detected" in v.get("log", []):
                continue
            if raw > 0 and keep_gain(1 - fixed / raw, mode):
                rows.append(dict(scene=r["id"], fault=sc, raw=raw, fixed=fixed, clean=clean,
                                 fix=", ".join(v["log"]), gain=1 - fixed / raw))
    return pd.DataFrame(rows)


# Colour scales used when the example images were written (scripts/run/distortion_study.py, save_examples):
#   depth: turbo(1 - x), x = log depth scaled between the 2nd and 98th percentile of the frame's true depth
#          -> red = near, blue = far;
#   error: magma(min(|pred - true| / true, 0.5) / 0.5), grey = no ground truth.
TURBO_R = "linear-gradient(90deg,#7a0403,#d23105,#fb8022,#edd03a,#a4fc3c,#2ee5ae,#28bceb,#4686fb,#3e378f,#30123b)"
MAGMA = "linear-gradient(90deg,#000004,#1c1044,#4f127b,#812581,#b5367a,#e55964,#fb8761,#fec287,#fcfdbf)"


@st.cache_data(show_spinner=False)
def _b64(path: str) -> str:
    p = Path(path)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def panel(path: Path, title: str, kind: str = "rgb") -> bool:
    """An ERP image with a title, latitude/longitude axes and, for depth and error maps, a labelled colour bar."""
    if not path.is_file():
        st.session_state.setdefault("_missing", []).append(
            str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path))
        return False
    ys = "".join(f'<span style="top:{t}%">{l}</span>' for t, l in
                 [(0, "+90°"), (25, "+45°"), (50, "0°"), (75, "−45°"), (100, "−90°")])
    xs = "".join(f'<span style="left:{t}%">{l}</span>' for t, l in
                 [(2, "−180°"), (25, "−90°"), (50, "0°"), (75, "+90°"), (98, "+180°")])
    bar = ""
    if kind == "depth":
        ticks = "".join(f'<span style="left:{t}%">{l}</span>' for t, l in [(4, "near"), (50, "mid"), (96, "far")])
        bar = (f'<div class="cb" style="background:{TURBO_R}"></div><div class="ct">{ticks}</div>'
               '<div class="cl">depth, log scale (frame\'s 2nd–98th percentile of true depth)</div>')
    elif kind == "err":
        ticks = "".join(f'<span style="left:{t}%">{l}</span>' for t, l in
                        [(2, "0"), (20, "0.1"), (40, "0.2"), (60, "0.3"), (80, "0.4"), (97, "≥0.5")])
        bar = (f'<div class="cb" style="background:{MAGMA}"></div><div class="ct">{ticks}</div>'
               '<div class="cl">per-pixel AbsRel |pred − true| / true · grey = no ground truth</div>')
    st.markdown(
        f'<div class="pan"><div class="tt">{title}</div><div class="g">'
        f'<div class="ya">{ys}<span class="yl">latitude</span></div><img src="{_b64(str(path))}"></div>'
        f'<div class="g"><div></div><div><div class="xa">{xs}</div><div class="xl">longitude</div>{bar}</div></div></div>',
        unsafe_allow_html=True)
    return True


ALIGN_NOTE = {"dap": "DAP depth is in raw metres.",
              "midas": "MiDaS depth is shown after a scale-and-shift fit to the ground truth.",
              "da360": "DA360 depth is shown after a scale-and-shift fit to the ground truth.",
              "da2": "DA² depth is shown after a least-squares scale fit to the ground truth."}


@st.cache_data(show_spinner=False)
def _example_png(rows: str, title: str, ds: str, fid: str, note: str) -> bytes:
    import matplotlib.image as mpimg
    rows_ = json.loads(rows)
    first = next(p for r in rows_ for _, p, _ in r if p and Path(p).is_file())
    h = mpimg.imread(first).shape[0]
    info = EP.gt_info(ds, fid, h, BENCH_RES)
    rows_ = [[(t, (str(BENCH_RES / info["gt"]) if (p == "GT" and info) else (None if p == "GT" else p)), k)
              for t, p, k in r] for r in rows_]
    return EP.figure(rows_, title, info, note)


def show_example(rows, title: str, ds: str, fid: str, note: str = ""):
    """rows: [[(panel title, Path | 'GT', kind), ...], ...]; 'GT' = the frame's ground-truth depth."""
    flat = [p for r in rows for _, p, _ in r if p != "GT"]
    for p in flat:
        if not Path(p).is_file():
            st.session_state.setdefault("_missing", []).append(
                str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else str(p))
    if not any(Path(p).is_file() for p in flat):
        return
    rows_s = json.dumps([[(t, p if p == "GT" else str(p), k) for t, p, k in r] for r in rows])
    st.image(_example_png(rows_s, title, ds, fid, note), use_container_width=True)


def proj_share(run: str, prefix: str) -> tuple[int, int, int]:
    met = scene_metrics(run)
    if met.empty:
        return 0, 0, 0
    pv = met.pivot_table(index="image", columns="m", values="polar")
    if "baseline" not in pv or prefix not in pv:
        return 0, 0, 0
    pv = pv[["baseline", prefix]].dropna()
    r = pv[prefix] / pv["baseline"]
    return int((r < 0.99).sum()), int((r > 1.01).sum()), len(pv)


def correction_share(model: str, ds: str, folder: str, fault: str) -> tuple[int, int, int]:
    c = load_json(str(Path(folder) / f"correction_{model}_{ds}.json"))
    b = w = n = 0
    for r in (c or {}).get("rows", []):
        v = r.get(fault)
        if not isinstance(v, dict):
            continue
        k = fault_metric_key(fault)
        raw, fixed = v["raw"].get(k), v["fixed"].get(k)
        if not (finite(raw) and finite(fixed)) or raw <= 0:
            continue
        n += 1
        b += fixed < 0.99 * raw
        w += fixed > 1.01 * raw
    return b, w, n


def img(path: Path, caption: str | None = None) -> bool:
    """Show an image if it exists; otherwise record it once and show nothing in place."""
    if path.is_file():
        st.image(str(path), caption=caption, use_container_width=True)
        return True
    st.session_state.setdefault("_missing", []).append(str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path))
    return False


def choose(container, label: str, ids, fmt, kind: str = "selectbox", **kw):
    """A selectbox/radio that shows fmt(id) and returns the id (labels are plain options, no format_func)."""
    ids = list(ids)
    labels = [fmt(i) for i in ids]
    return ids[labels.index(getattr(container, kind)(label, labels, **kw))]


def pct(x: float) -> str:
    return f"{x * 100:+.0f}%"


def short_id(s: str) -> str:
    return s.replace("scene_", "Scene ").replace("_", "-") if s.startswith("scene_") else f"Frame {s}"


def bar_chart(values: pd.Series, title: str, fmt: str = ".3f", height: int = 230):
    """Horizontal bars, one colour per method (fixed order), names on the axis and values as labels."""
    df = values.rename("v").rename_axis("method").reset_index()
    inv = {v: k for k, v in LABELS.items()}
    df["key"] = df.method.map(lambda m: inv.get(m, m))
    order = list(df.method)
    base = alt.Chart(df).encode(
        y=alt.Y("method:N", sort=order, title=None, axis=alt.Axis(labelFontSize=12, labelColor="#1d2433", ticks=False,
                                                                  domain=False, labelPadding=8)),
        x=alt.X("v:Q", title=title, scale=alt.Scale(domain=[0, float(values.max()) * 1.18], nice=False), axis=alt.Axis(grid=True, gridColor="#eef0f4", domain=False, tickColor="#c9ced8",
                                                  labelColor="#5b6474", titleColor="#5b6474", format=fmt)),
        tooltip=[alt.Tooltip("method:N", title="Method"), alt.Tooltip("v:Q", title=title, format=fmt)],
    )
    bars = base.mark_bar(cornerRadiusEnd=4, height=18).encode(
        color=alt.Color("key:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values())), legend=None))
    text = base.mark_text(align="left", dx=6, fontSize=12, color="#1d2433").encode(text=alt.Text("v:Q", format=fmt))
    st.altair_chart((bars + text).properties(height=height).configure_view(stroke=None), use_container_width=True)


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
def go_to(page: str):
    st.session_state["page"] = page


def page_overview():
    hero("Distortion-Aware Panoramic Depth Estimation",
         "Reducing the polar error of frozen monocular depth models on 360° panoramas at inference time, "
         "with the depth model treated as a black box.",
         eyebrow="CV coursework · IIT Jodhpur",
         chips=["Panoramic Depth", "Inference-Time Correction", "No retraining", "6 datasets · 4 models"])

    section("The problem", "equirectangular (ERP) panoramas stretch every row by 1/cos φ")
    c = st.columns(4)
    for col, (n, l) in zip(c, [("×1.41", "stretch at 45° latitude"), ("×2.0", "stretch at 60°"),
                               ("×3.9", "stretch at 75°"), ("∞", "at the poles")]):
        col.markdown(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns([1.05, 1])
    with c1:
        with st.container(border=True):
            img(PROJ_RES / "acgf_midas_structured3d" / "report_align-equatorial" / "profile_acgf_main_align-equatorial.png")
            st.caption("MiDaS DPT-Hybrid on Structured3D: error vs |latitude|. The baseline's error rises steeply "
                       "towards the poles; the corrections flatten it.")
    with c2:
        st.markdown('<div class="howto">Depth networks learn local appearance, so the stretched floor and ceiling '
                    'look unlike anything they saw in training. All projection corrections share one skeleton: '
                    'show the model a <b>less distorted re-projection</b> of the poles, then <b>align and fuse</b> '
                    'the result back into the baseline without using any ground truth.</div>', unsafe_allow_html=True)
        pipeline(graph(f"""
  rgb -> model -> base;
  alt [label="Less-distorted\\nre-projection", {HL}];
  m2 [label="Same frozen\\nmodel", {HL}];
  fu [label="Align + fuse\\n(no ground truth)", {HL}];
  out [label="Corrected depth", {N_OUT}];
  rgb -> alt -> m2 -> fu -> out; base -> fu;
""", rankdir="TB"), stretch=False)

    section("What the final report concludes", "report/final_report.pdf")
    c = st.columns(4)
    for col, (n, l) in zip(c, [("−34.8%", "DAP error on Stanford2D3D's real black polar caps, after the capture-fault fix"),
                               ("−47.4%", "DAP error on tilted NYC street panoramas, after re-levelling"),
                               ("−89.3%", "DAP error under a blocked bottom (tripod) on NYC, after the fix"),
                               ("0.638 → 0.205", "DA² NYC error when only the scoring rule changes (least squares → median fit)")]):
        col.markdown(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    st.write("")
    callout("<b>Main finding:</b> for current panoramic models the polar error is mostly <b>not</b> a projection effect. "
            "What costs far more are ordinary capture faults (tilt, a blocked or missing top/bottom, shake, JPEG), and a "
            "per-model correction step learned on held-out data repairs several of them. Stanford2D3D and NYC were never "
            "used to choose anything.")
    with st.expander("Report outline"):
        st.markdown("Abstract · 1 Introduction · 2 Literature review · 3 Problem statement · "
                    "4 Proposed method (4.1 Measuring the distortion effect, 4.2 Corrections) · "
                    "5 Experiments and results (5.1 Setup, 5.2 Results) · 6 Limitations · 7 Conclusions · References · "
                    "Appendices A–E (additional figures, stricter selection rules, DA² under two alignment protocols, "
                    "nadir and JPEG diagnosis, stability of the learned policy)")

    section("The work", "pick a card to open its page")
    groups = [
        ("Inference-time projection corrections", [
            (k, PAGE_OF[k], m["tagline"], m["facts"][3][1], COLORS[k]) for k, m in METHODS.items()]),
        ("Latitude analysis, ensembles & capture faults", [
            ("sweeps", "Measurement sweeps", "Rotate, dilate and flip content to test whether ERP distortion causes the polar error.", "4 models · 6 datasets", "#6250d6"),
            ("ens", "Gradient fusion & Möbius TTA", "Poisson-fused pole views and Möbius-warped ensembles vs a compute-matched control.", "helps MiDaS only", "#6250d6"),
            ("cat", "Capture-fault catalogue", "Ten realistic capture faults, what each costs every model, and the fix.", "10 faults", "#6250d6"),
            ("faults", "Capture-fault correction", "Detect faults from the image and apply the per-model fix learned on held-out data.", "end to end", "#6250d6"),
            ("rob", "Robustness checks", "Two scoring rules for DA², the nadir+JPEG diagnosis, stricter rules and policy stability.", "report appendices", "#6250d6")]),
        ("Real-world evaluation & follow-up studies", [
            ("nyc", "NYC street panoramas", "The projection corrections on 75 real outdoor city panoramas.", "outdoor", "#008300"),
            ("fu", "Follow-up studies", "Scale-only protocol, LOEO gate, distillation, 20 views, FOV sweep.", "6 studies", "#008300")]),
    ]
    for title, cards in groups:
        st.markdown(f"**{title}**")
        cols = st.columns(4)
        for i, (key, page, desc, badge, color) in enumerate(cards):
            with cols[i % 4]:
                st.markdown(f'<div class="card" style="--c:{color}"><div class="h">{page}</div>'
                            f'<div class="d">{desc}</div><span class="b">{badge}</span></div>', unsafe_allow_html=True)
                st.button("Open →", key=f"open_{key}", on_click=go_to, args=(page,), use_container_width=True)
            if i % 4 == 3 and i < len(cards) - 1:
                cols = st.columns(4)
        st.write("")

    section("Headline results", "MiDaS DPT-Hybrid, full test splits, AbsRel (lower is better)")
    t1, t2, t3 = st.tabs(["Polar error (60–90°)", "Whole-image error", "Runtime"])
    with t1:
        ds = st.radio("Dataset", _SETS, key="ov_ds_polar", horizontal=True, label_visibility="collapsed")
        cc = st.columns([1, 1])
        with cc[0]:
            bar_chart(POLAR[ds or _SETS[0]], "Polar AbsRel")
        with cc[1]:
            st.dataframe(POLAR.style.format("{:.3f}").highlight_min(color="#c9ecd3"), use_container_width=True)
    with t2:
        ds = st.radio("Dataset", _SETS, key="ov_ds_whole", horizontal=True, label_visibility="collapsed")
        cc = st.columns([1, 1])
        with cc[0]:
            bar_chart(WHOLE[ds or _SETS[0]], "Whole-image AbsRel")
        with cc[1]:
            st.dataframe(WHOLE.style.format("{:.3f}").highlight_min(color="#c9ecd3"), use_container_width=True)
    with t3:
        bar_chart(RUNTIME, "Runtime (× baseline, Kaggle T4)", fmt=".1f")
    callout("<b>No method wins everywhere.</b> 360MonoDepth leads on Structured3D, tangent views on Holo360D indoor, "
            "and ACGF v2 on Holo360D outdoor, where it also does the least harm. "
            "Source: projection corrections study §10.2, ground truth aligned on |φ| &lt; 30°.")


def page_baseline():
    hero("Baseline: a single ERP pass", "The reference every method is compared with: the panorama goes through "
         "the depth model once, as-is.", eyebrow="Reference", chips=["1 model call", "4 frozen models", "No correction"])
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown('<div class="howto">Compare a <b>perspective</b> model (MiDaS) with <b>panorama-trained</b> models '
                    '(DAP, DA360) on the same scene. Bright areas in the error map are where the prediction is worst; '
                    'for MiDaS they cluster on the floor and ceiling.</div>', unsafe_allow_html=True)
    with c2:
        pipeline(graph(f'rgb -> model -> base; base -> out; out [label="Depth\\n(polar caps distorted)", '
                       f'shape=box, style="rounded,filled", fillcolor="#fde0e0", color="#e34948"];'))

    section("Example", "choose a model, dataset and scene")
    c1, c2, c3 = st.columns(3)
    model_lbl = c1.selectbox("Model", list(FAULT_MODELS))
    ds_lbl = c2.selectbox("Dataset", [k for k in FAULT_SETS if "external" not in k])
    model = FAULT_MODELS[model_lbl]
    ds, folder = FAULT_SETS[ds_lbl]
    c = load_json(str(folder / f"correction_{model}_{ds}.json"))
    if not c or not c.get("examples"):
        st.info("No examples stored for this combination.")
        return
    rows = {r["id"]: r for r in c["rows"]}
    scene = choose(c3, "Scene", c["examples"], short_id)
    names = c["examples"][scene]
    clean = rows[scene]["clean"]["clean"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Whole-image AbsRel", f"{clean['all']:.3f}")
    m2.metric("Polar AbsRel", f"{clean['polar']:.3f}")
    m3.metric("Polar vs whole", f"{clean['polar'] / clean['all']:.2f}×",
              help="Above 1× means the poles are worse than the image on average.")
    imdir = folder / f"correction_{model}_{ds}_img"
    with st.container(border=True):
        show_example([[("Input ERP", imdir / names["rgb"], "rgb"), ("Ground-truth depth", "GT", "depth")],
                      [("Predicted depth", imdir / names["clean"], "depth"), ("AbsRel of the prediction", imdir / names["err_clean"], "err")]],
                     f"{scene}: {model_lbl} on {ds_lbl}, single ERP pass", ds, scene, ALIGN_NOTE.get(model, ""))
    callout("<b>Key finding:</b> panorama-trained DAP shows <b>no polar degradation</b> (indoor polar 0.179 = equator "
            "0.179), while perspective MiDaS roughly doubles its error at the poles. The projection corrections therefore "
            "target perspective models; on DAP every one of them makes things worse (projection corrections study §11).")


def page_projection(key: str):
    m = METHODS[key]
    hero(m["name"], m["tagline"], eyebrow="Method · Projection Correction",
         chips=["MiDaS DPT-Hybrid (frozen)", "Inference-time only", "No ground truth at inference"])
    facts(m["facts"])

    c1, c2 = st.columns([1, 1.35])
    with c1:
        st.markdown("##### How it works")
        st.markdown(m["idea"])
        st.markdown("##### How it differs from the baseline")
        st.markdown("\n".join(f"- {d}" for d in m["diff"]))
    with c2:
        st.markdown("##### Pipeline")
        pipeline(m["graph"])

    mode = ex_mode()
    avail = {lbl: ds for lbl, ds in PROJ_DATASETS.items() if not good_examples(key, ds, mode).empty}
    section("Examples", ex_sub("polar error"))
    if not avail:
        st.info("No stored example matches this filter for this method. Try another option in the sidebar.")
        nav_buttons()
        return
    c1, c2 = st.columns([1.2, 1])
    with c1:
        ds_lbl = st.radio("Dataset", list(avail), key=f"ds_{key}", horizontal=True)
    share_line(*proj_share(m["run"].format(ds=avail[ds_lbl]), m["prefix"]), "test scenes of this dataset (polar error)")
    ex = ex_order(good_examples(key, avail[ds_lbl], mode))
    gains = ex.set_index("scene").gain
    with c2:
        scene = choose(st, ex_label(), ex.scene, lambda s: f"{short_id(s)}  ·  {pct(-gains[s])} polar error")
    r = ex.set_index("scene").loc[scene]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Polar AbsRel · baseline", f"{r.base_polar:.3f}")
    k2.metric(f"Polar AbsRel · {LABELS[key]}", f"{r.polar:.3f}", f"{pct(r.polar / r.base_polar - 1)}", delta_color="inverse")
    k3.metric("Whole AbsRel · baseline", f"{r.base_whole:.3f}")
    k4.metric(f"Whole AbsRel · {LABELS[key]}", f"{r.whole:.3f}", f"{pct(r.whole / r.base_whole - 1)}", delta_color="inverse")

    run_dir = PROJ_RES / m["run"].format(ds=avail[ds_lbl]) / "qualitative"
    report = PROJ_RES / m["run"].format(ds=avail[ds_lbl]) / "report_align-equatorial" / "profile_acgf_main_align-equatorial.png"
    tabs = st.tabs(["Result vs baseline", "Inside the pipeline", "Error by latitude"])
    with tabs[0]:
        st.caption("Left column = baseline, right column = this method. Improvement map: blue = better, orange = worse. "
                   "Dashed lines mark the ±45° correction threshold.")
        with st.container(border=True):
            img(run_dir / f"{scene}_{m['fig']}.png")
    with tabs[1]:
        if m.get("extra") == "tangent_view":
            st.caption("The polar cap is resampled into an undistorted pinhole view, predicted, and re-projected to ERP.")
            for i in (0, 1):
                with st.container(border=True):
                    img(run_dir / f"tangent_view_{scene}_{i}.png", ["North pole view", "South pole view"][i])
        elif m.get("extra") == "acgf_views":
            st.caption("Top: the four pole views the model sees. Bottom: the gate γ (yellow = views trusted) and the "
                       "final log-ratio correction applied to the baseline.")
            with st.container(border=True):
                img(run_dir / f"acgf_views_{scene}.png")
        elif key == "rotation":
            callout("A pitch of +90° maps <b>both</b> poles onto the equator (north to the front, south to the back), "
                    "where the model sees them with almost no stretch. The prediction is then rotated back exactly. "
                    "No intermediate views are stored for this method; see the result figure.")
        elif key == "hybrid":
            callout("The hybrid reuses the tangent views and the rotated spheres. Open the <b>Tangent-plane views</b> "
                    "page to see the pinhole views for the same scenes.")
        else:
            callout("360MonoDepth's 20 per-face views are not stored; the result figure shows the stitched panorama.")
    with tabs[2]:
        with st.container(border=True):
            img(report, "AbsRel vs |latitude| over the whole test split of this dataset")

    nav_buttons()


def page_faults():
    hero("Capture-fault correction", "Real panoramas often fail because of how they were captured, not because of "
         "ERP stretch. Detect the fault, fix it, then run the model.", eyebrow="Method · Capture Faults",
         chips=["MiDaS · DAP · DA2 · DA360", "Leave-one-dataset-out policy", "6 datasets"])
    facts([("Faults handled", "Tilt, nadir, vFOV, blur, JPEG"), ("Detection", "From the image alone"),
           ("Fixes", "Re-level · inpaint · deblur · denoise"), ("Model calls", "1"),
           ("Safe default", "No fault → pass through")])
    c1, c2 = st.columns([1, 1.35])
    with c1:
        st.markdown("##### How it works")
        st.markdown("A tilted camera, a tripod hole at the nadir, cropped vertical FOV, motion blur or heavy JPEG "
                    "each damage the depth estimate in a different way. This front end **detects** the fault and "
                    "applies **one fix per fault** *before* the model runs. The fix for each fault is chosen "
                    "leave-one-dataset-out, so every dataset is scored with a policy picked on the others.")
    with c2:
        st.markdown("##### Pipeline")
        pipeline(f"""digraph G {{ rankdir=LR; bgcolor="transparent"; nodesep=0.25; ranksep=0.35;
  node [fontname="Helvetica", fontsize=11, margin="0.14,0.07", fontcolor="#1d2433"];
  edge [color="#8a93a3", arrowsize=0.7, fontname="Helvetica", fontsize=9, fontcolor="#5b6474"];
  rgb [label="Captured ERP\\n(possibly faulty)", {N_IN}];
  det [label="Fault detector", {HL}];
  fix [label="Per-fault fix\\nre-level · inpaint ·\\ndeblur · bilateral", {HL}];
  model [label="Frozen depth model", {N_BASE}];
  out [label="Depth", {N_OUT}];
  rgb -> det -> fix -> model -> out; det -> model [style=dashed, label="no fault"]; }}""")

    mode = ex_mode()
    section("Examples", ex_sub())
    c1, c2, c3 = st.columns(3)
    model_lbl = c1.selectbox("Model", list(FAULT_MODELS))
    model = FAULT_MODELS[model_lbl]
    sets = {k: v for k, v in FAULT_SETS.items() if not fault_examples(model, v[0], str(v[1]), mode).empty}
    if not sets:
        st.info("No stored example matches this filter for this model. Try another option in the sidebar.")
    else:
        ds_lbl = c2.selectbox("Dataset", list(sets))
        ds, folder = sets[ds_lbl]
        ex = fault_examples(model, ds, str(folder), mode)
        faults = [f for f in FAULTS if f in set(ex.fault)]
        fault = choose(c3, "Fault", faults, FAULTS.get)
        share_line(*correction_share(model, ds, str(folder), fault), "frames of this dataset with this fault")
        exf = ex_order(ex[ex.fault == fault])
        gains = exf.set_index("scene").gain
        scene = choose(st, ex_label(), exf.scene, lambda s: f"{short_id(s)}  ·  {pct(-gains[s])} error")
        _fault_example(model, ds, folder, fault, exf, scene)
    _fault_summary()


def _fault_example(model, ds, folder, fault, exf, scene):
    r = exf.set_index("scene").loc[scene]
    region = " · affected region" if fault_metric_key(fault) == "region" else ""
    k1, k2, k3 = st.columns(3)
    k1.metric(f"AbsRel, clean input{region}", f"{r.clean:.3f}" if finite(r.clean) else "–")
    k2.metric(f"AbsRel, faulty input{region}", f"{r.raw:.3f}")
    k3.metric(f"AbsRel, after the fix{region}", f"{r.fixed:.3f}", pct(r.fixed / r.raw - 1), delta_color="inverse")
    st.caption(f"Fix applied: `{r.fix}`")

    names = load_json(str(folder / f"correction_{model}_{ds}.json"))["examples"][scene]
    imdir = folder / f"correction_{model}_{ds}_img"
    g = lambda k: imdir / names.get(k, "__none__")
    with st.container(border=True):
        show_example([[("Input with the fault", g(f"{fault}_input"), "rgb"), ("Ground-truth depth", "GT", "depth")],
                      [("Depth without the fix", g(f"{fault}_raw"), "depth"), ("Depth with the fix", g(f"{fault}_fixed"), "depth")],
                      [("AbsRel without the fix", g(f"err_{fault}_raw"), "err"), ("AbsRel with the fix", g(f"err_{fault}_fixed"), "err")],
                      [("Reference: depth on the clean input", g("clean"), "depth"), ("Reference: AbsRel on the clean input", g("err_clean"), "err")]],
                     f"{scene}: {model} · {ds} · {FAULTS.get(fault, fault)} · fix: {r.fix}", ds, scene,
                     ALIGN_NOTE.get(model, "") + " Depth and error are shown in the original (unrotated) frame.")


def _fault_summary():
    section("Does it hold up everywhere?", "every model × dataset, and two external datasets never used for any choice")
    t1, t2, t3 = st.tabs(["Gain per model and dataset", "Do no harm", "External validation (DAP)"])
    with t1:
        st.caption("Median change in error vs uncorrected (green = better); right panel: share of frames made worse.")
        img(BENCH_RES / "figures" / "fig_correction_gain.png")
    with t2:
        img(BENCH_RES / "figures" / "fig_do_no_harm.png")
    with t3:
        ext = pd.DataFrame(
            [["Stanford2D3D", "clean (real caps)", -34.8, "99 / 1%"], ["Stanford2D3D", "tilt", -32.0, "99 / 1%"],
             ["Stanford2D3D", "shake", -32.9, "97 / 2%"], ["Stanford2D3D", "JPEG", -47.1, "98 / 2%"],
             ["NYC", "tilt", -47.4, "98 / 2%"], ["NYC", "blocked bottom", -89.3, "79 / 20%"],
             ["NYC", "top/bottom missing", -36.4, "99 / 1%"], ["NYC", "shake", -60.4, "92 / 7%"],
             ["NYC", "JPEG", -7.9, "82 / 12%"], ["NYC", "blocked bottom + JPEG", 1.3, "47 / 52%"]],
            columns=["Dataset", "Scenario", "Median change (%)", "Frames better / worse"])
        def _shade(v):  # green = error down, red = error up; no matplotlib needed
            a = min(abs(v) / 60, 1) * 0.55
            return f"background-color: rgba({'27,175,122' if v < 0 else '227,73,72'},{a:.2f})"
        styler = ext.style.format({"Median change (%)": "{:+.1f}"})
        styler_map = getattr(styler, "map", getattr(styler, "applymap", None))
        if styler_map:
            styler = styler_map(_shade, subset=["Median change (%)"])
        st.dataframe(styler, use_container_width=True, hide_index=True)
        st.caption("Green = error goes down after the fix, red = it goes up; stronger colour = larger change.")
        st.caption("Stanford2D3D: 373 frames, 73 rooms. NYC: 147 frames. Policy learned on the four core datasets only. "
                   "Source: final report, Section 5.2.4 (external validation).")
    nav_buttons()


def page_compare():
    hero("Compare all methods", "Same scene, same frozen model (MiDaS DPT-Hybrid): how each pipeline changes the result.",
         eyebrow="Side by side", chips=["6 methods", "3 datasets", "Per-scene metrics"])
    c1, c2 = st.columns([1.2, 1])
    with c1:
        ds_lbl = st.radio("Dataset", list(PROJ_DATASETS), key="cmp_ds", horizontal=True)
    ds = PROJ_DATASETS[ds_lbl]
    met = scene_metrics(f"acgf_midas_{ds}")
    v2 = scene_metrics(f"acgf_midas_{ds}_v2")
    scenes = qual_scenes(f"acgf_midas_{ds}", "hybrid")

    def best_gain(sc):
        s = met[met.image == sc].set_index("m")
        return (1 - s.polar.drop("baseline", errors="ignore") / s.polar.get("baseline", np.nan)).max()

    scenes = sorted(scenes, key=best_gain, reverse=True)
    with c2:
        scene = choose(st, "Scene", scenes, short_id)
    s = met[met.image == scene].set_index("m")[["whole", "polar"]]
    if not v2.empty and (v2.image == scene).any():
        s.loc["acgf"] = v2[(v2.image == scene) & (v2.m == "acgf")][["whole", "polar"]].iloc[0]
    order = ["baseline", "tangent", "rotation", "hybrid", "mono360", "acgf"]
    s = s.reindex([o for o in order if o in s.index]).rename(index=LABELS).rename_axis(None)
    best = s.polar.idxmin()

    c1, c2 = st.columns([3, 2])
    with c1:
        metric = st.radio("Metric", ["Polar (60–90°)", "Whole image"], key="cmp_m", horizontal=True)
        col = "whole" if metric == "Whole image" else "polar"
        bar_chart(s[col], f"{'Whole-image' if col == 'whole' else 'Polar'} AbsRel (lower is better)")
    with c2:
        st.write("")
        st.dataframe(s.rename(columns={"whole": "Whole", "polar": "Polar"}).style.format("{:.3f}")
                     .highlight_min(color="#c9ecd3"), use_container_width=True)
        st.markdown(f'<div class="callout">Best at the poles on this scene: <b>{best}</b> '
                    f'({pct(s.polar[best] / s.polar["Baseline"] - 1)} vs baseline)</div>', unsafe_allow_html=True)

    section("Result figures", "left column = baseline, right column = method")
    keys = [o for o in order if o != "baseline"]
    tabs = st.tabs([LABELS[k] for k in keys])
    for tab, key in zip(tabs, keys):
        with tab:
            with st.container(border=True):
                img(PROJ_RES / METHODS[key]["run"].format(ds=ds) / "qualitative" / f"{scene}_{METHODS[key]['fig']}.png")


# --------------------------------------------------------------------------------------
# Benchmark study: measurement sweeps, inference-time ensembles, capture-fault catalogue
# --------------------------------------------------------------------------------------
BENCH_FIG = BENCH_RES / "figures"
BENCH_MODELS = {"DAP": "dap", "MiDaS DPT-Hybrid": "midas", "DA360": "da360", "DA²": "da2"}
BENCH_SETS = {"Structured3D": "s3", "PanoX": "panox", "Holo360D indoor": "holo_in", "Holo360D outdoor": "holo_out",
              "Stanford2D3D (external)": "stanford", "NYC streets (external)": "nyc"}
FAULTS10 = {
    "tilt": "Camera tilt (12° pitch, 8° roll)",
    "nadir": "Blocked nadir (tripod below −62°)",
    "vfov": "Limited vertical FOV (±50°)",
    "seam": "Stitching seam (exposure jump)",
    "parallax": "Stitching parallax",
    "vignette": "Lens vignetting",
    "yawblur": "Yaw motion blur",
    "noise": "Sensor noise",
    "jpeg": "Heavy JPEG compression",
    "lowres": "Low resolution",
}
FIXES = {
    "relevel_known": "Re-level with the known tilt (IMU)", "relevel_self": "Re-level with a self-estimated tilt",
    "inpaint_erp": "Inpaint the missing cap in ERP", "inpaint_tangent": "Inpaint the cap in a tangent view",
    "plane_fill": "Fill the cap with a floor/ceiling plane", "gain_match": "Match exposure across the seam",
    "seam_inpaint": "Inpaint the parallax seam", "flatfield": "Flat-field correction", "wiener": "Wiener deblur",
    "denoise": "Denoise", "bilateral": "Bilateral filter",
}


def study_file(m: str, ds: str) -> Path:
    return BENCH_RES / f"study_{m}_{ds}.json"


@st.cache_data(show_spinner=False)
def fault_study_examples(m: str, ds: str, mode: str = "help") -> pd.DataFrame:
    """Frames with stored images where the fault costs something, filtered by the effect of the best fix."""
    s = load_json(str(study_file(m, ds)))
    if not s:
        return pd.DataFrame()
    rows = []
    for r in s["rows"]:
        if r["id"] not in s.get("examples", {}):
            continue
        for f in FAULTS10:
            fix = r.get(f"{f}|best_example")
            none, fixed, clean = r.get(f"{f}|none"), r.get(f"{f}|{fix}") if fix else None, r.get(f"{f}|clean")
            if not (fix and isinstance(none, dict) and isinstance(fixed, dict)):
                continue
            k = "region" if "region" in none else "all"
            a, b, c0 = none.get(k), fixed.get(k), (clean or {}).get(k)
            hurts = finite(c0) and a >= (1 + GOOD_GAIN) * c0  # the fault itself must cost something
            if finite(a) and finite(b) and a > 0 and hurts and keep_gain(1 - b / a, mode):
                rows.append(dict(scene=r["id"], fault=f, fix=fix, key=k, none=a, fixed=b,
                                 clean=(clean or {}).get(k), gain=1 - b / a))
    return pd.DataFrame(rows)


def page_sweeps():
    hero("Measurement sweeps", "Is the polar error really caused by ERP distortion? Move the same content to "
         "different latitudes while the ground truth stays fixed, and watch the error.",
         eyebrow="Study · Distortion Analysis", chips=["4 frozen models", "6 datasets", "80 panoramas per dataset",
                                           "Cluster-robust bootstrap"])
    facts([("Rotation", "Tip the scene: poles → equator"), ("Dilation", "Magnify content like near a pole"),
           ("Flip", "Same latitude, upside down"), ("Measures", "Error ratio R(L) vs latitude"),
           ("Verdict", "Mostly not a projection effect")])
    c1, c2 = st.columns([1, 1.35])
    with c1:
        st.markdown("##### How it works")
        st.markdown(
            "For every frame the scene is rendered into the model at a series of latitudes, and the error of the "
            "**same pixels** is compared with the pass where they sit closest to the equator:")
        st.latex(r"R(L)=\frac{E(L)}{E_{\mathrm{ref}}(L)}")
        st.markdown(
            "R = 1 means no excess error. A real distortion effect must show up in **both** rotation and dilation; "
            "flip isolates an *orientation* prior (models assume up is up).")
    with c2:
        st.markdown("##### Pipeline")
        pipeline(f"""digraph G {{ rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.3;
  node [fontname="Helvetica", fontsize=11, margin="0.14,0.07", fontcolor="#1d2433"];
  edge [color="#8a93a3", arrowsize=0.7];
  rgb [label="ERP panorama\\n+ fixed ground truth", {N_IN}];
  sw [label="Re-render at latitude L\\n(rotate / dilate / flip)", {HL}];
  model [label="Frozen model", {N_BASE}];
  back [label="Map prediction back\\nto the original pixels", {HL}];
  cmp [label="Same pixels, same GT:\\nerror at L vs at equator", {HL}];
  out [label="R(L) curve\\n+ onset latitude", {N_OUT}];
  rgb -> sw -> model -> back -> cmp -> out; }}""", stretch=False)

    section("Results across models", "solid = core datasets, dashed = external NYC")
    t = st.tabs(["Rotation sweep", "Dilation sweep", "Flip (orientation)"])
    notes = [
        "Rotation produces **no onset** for MiDaS, DAP or DA2 on any core dataset; only DA360 on PanoX rises "
        "(onset 70°). Moving the pole to the equator does not make these models better: the stretch is not the problem.",
        "Dilation looks dramatic for DAP on Structured3D (ratio 3.69 at 75–90°), but it is a **scale cue**: shrunk "
        "content reads as farther away. Re-fitting scale per latitude band drops the excess to ≈ 0.",
        "The **orientation prior is real**: upside-down content costs DAP +0.07 to +0.18 AbsRel indoors and +0.48 "
        "on NYC; DA360 ratio 1.85, DA2 1.48 on Structured3D.",
    ]
    for tab, mode, note in zip(t, ["rotation", "dilation", "flip"], notes):
        with tab:
            callout(note)
            with st.container(border=True):
                img(BENCH_FIG / f"fig_sweeps_{mode}.png")

    section("Explore one model and dataset")
    c1, c2, c3 = st.columns(3)
    mode = c1.radio("Sweep", ["rotation", "dilation", "flip"], horizontal=True, key="sw_mode")
    m = BENCH_MODELS[c2.selectbox("Model", list(BENCH_MODELS), key="sw_m")]
    pre = "sweep_" if mode == "rotation" else f"sweep_{mode}_"
    sets = {lbl: ds for lbl, ds in BENCH_SETS.items()
            if any((BENCH_RES / f"{pre}{m}_{ds}_{sp}.png").is_file() for sp in ("all", "eval"))}
    ds = sets[c3.selectbox("Dataset", list(sets), key="sw_ds")] if sets else None
    if ds:
        f = next(BENCH_RES / f"{pre}{m}_{ds}_{sp}.png" for sp in ("all", "eval") if (BENCH_RES / f"{pre}{m}_{ds}_{sp}.png").is_file())
        with st.container(border=True):
            img(f)
    nav_buttons()


def page_ensembles():
    hero("Gradient fusion & Möbius TTA", "Two model-agnostic inference-time corrections, tested against a "
         "compute-matched control so that gains cannot come from simple averaging.",
         eyebrow="Methods · Ensembling", chips=["MiDaS · DAP · DA360 · DA2", "Compute-matched yaw control", "No retraining"])
    facts([("Method 1", "Gradient-domain polar fusion"), ("Method 2", "Möbius test-time augmentation"),
           ("Control", "Yaw ensemble, same passes"), ("Helps", "MiDaS (perspective)"),
           ("Does not help", "DAP, DA360, DA2")])
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("##### Method 1: gradient-domain polar fusion")
            st.markdown("Re-estimate the polar cap from tangent or rotated views, then merge it into the ERP "
                        "prediction by solving a **Poisson problem**: match a latitude-blended gradient field, "
                        "pinned to the ERP prediction at the equator, periodic in longitude.")
            st.latex(r"u^\star=\arg\min_u\sum_p\big\|\nabla u-\big[(1-\alpha)\nabla d_{\mathrm{erp}}+\alpha\,\nabla d_{\mathrm{polar}}\big]\big\|^2")
            st.graphviz_chart(graph(f"""
  rgb -> model -> base;
  pv [label="Tangent / rotated\\npole views", {HL}];
  al [label="Align to ERP", {HL}];
  ps [label="Poisson solve\\n(latitude ramp α)", {HL}];
  out [label="Fused depth", {N_OUT}];
  rgb -> pv -> al -> ps -> out; base -> ps;
""", rankdir="TB"), use_container_width=False)
    with c2:
        with st.container(border=True):
            st.markdown("##### Method 2: Möbius test-time augmentation")
            st.markdown("Run K passes on **Möbius-transformed** copies (rotation plus dilation of the sphere), map "
                        "each back to the ERP grid, **re-anchor** it to the base pass on |φ| < 30° and average.")
            st.latex(r"\hat d(p)=\frac{1}{K}\sum_{k=1}^{K}\big(a_k\,\hat d_k(p)+b_k\big)")
            st.graphviz_chart(graph(f"""
  rgb -> model -> base;
  mb [label="K Möbius-warped\\ncopies", {HL}];
  m2 [label="Frozen model\\n×K", {HL}];
  ra [label="Map back +\\naffine re-anchor", {HL}];
  av [label="Average", {HL}];
  out [label="Ensembled depth", {N_OUT}];
  rgb -> mb -> m2 -> ra -> av -> out; base -> ra [style=dashed];
""", rankdir="TB"), use_container_width=False)

    section("Results", "75–90° polar error change, Möbius TTA (from the final report)")
    c = st.columns(4)
    for col, (n, l) in zip(c, [("−46.9%", "MiDaS, 3 passes, Structured3D (align-equatorial)"),
                               ("−18.4%", "MiDaS, PanoX (CI excludes zero)"),
                               ("±3%", "Yaw-only control, same compute"),
                               ("+32%", "DAP gets worse indoors (raw metres)")]):
        col.markdown(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    st.write("")
    res = pd.DataFrame({"Setting": ["MiDaS · 3 passes", "MiDaS · 5–7 passes", "MiDaS · PanoX", "Yaw control (same passes)", "DAP · Structured3D"],
                        "align-all": ["−12.6%", "−22.6%", "−18.4%", "within ±3%", "+32% (worse)"],
                        "align-equatorial": ["−46.9%", "−26.5%", "–", "within ±3%", "–"]}).set_index("Setting")
    st.dataframe(res, use_container_width=True)
    callout("<b>Reading:</b> the gain is real and not just averaging (the yaw ensemble with the same compute does "
            "nothing), but it only appears for the perspective-trained MiDaS. Panoramic foundation models have already "
            "learned the projection, so re-projecting their input only moves them off their training distribution.")
    nav_buttons()


def page_fault_catalogue():
    hero("Capture-fault catalogue", "Ten realistic ways a 360° capture goes wrong, what each one costs every model, "
         "and the fix that undoes it.", eyebrow="Study · Distortion Analysis",
         chips=["10 faults", "4 models", "6 datasets", "40 frames per cell"])
    facts([("Worst fault", "Limited vFOV on DAP (29×)"), ("Most fragile", "DAP (best on clean input)"),
           ("Strongest fix", "Re-level: 96% recovery"), ("Per-model", "A fix can help one model, hurt another"),
           ("Excluded", "Denoise, seam inpaint, self-tilt")])
    section("What each fault costs", "error with the fault ÷ error on the clean image (1.0× = no cost)")
    with st.container(border=True):
        img(BENCH_FIG / "fig_fault_cost.png")
    callout("Capture faults cost far more than the projection: removing the top and bottom of the panorama raises "
            "DAP's error in the affected region from 0.026 to 0.761 on Structured3D.")

    mode = ex_mode()
    section("Examples", "faulty input vs the best fix; " + ex_sub())
    c1, c2, c3 = st.columns(3)
    m = BENCH_MODELS[c1.selectbox("Model", list(BENCH_MODELS), key="fc_m")]
    sets = {lbl: ds for lbl, ds in BENCH_SETS.items() if not fault_study_examples(m, ds, mode).empty}
    if not sets:
        st.info("No stored example matches this filter for this model. Try another option in the sidebar.")
        nav_buttons()
        return
    ds = sets[c2.selectbox("Dataset", list(sets), key="fc_ds")]
    ex = fault_study_examples(m, ds, mode)
    faults = [f for f in FAULTS10 if f in set(ex.fault)]
    fault = choose(c3, "Fault", faults, FAULTS10.get, key="fc_f")
    allx = fault_study_examples(m, ds, "all")
    allf = allx[allx.fault == fault]
    share_line(int((allf.gain > 0.01).sum()), int((allf.gain < -0.01).sum()), len(allf),
               "stored example frames where this fault costs at least 10% (best fix per frame)")
    exf = ex_order(ex[ex.fault == fault])
    gains = exf.set_index("scene").gain
    scene = choose(st, ex_label(), exf.scene, lambda s: f"{short_id(s)}  ·  {pct(-gains[s])} error", key="fc_s")
    r = exf.set_index("scene").loc[scene]
    region = " · affected region" if r.key == "region" else ""
    k1, k2, k3 = st.columns(3)
    k1.metric(f"AbsRel, clean{region}", f"{r.clean:.3f}" if finite(r.clean) else "–")
    k2.metric(f"AbsRel, with fault{region}", f"{r.none:.3f}")
    k3.metric(f"AbsRel, fixed{region}", f"{r.fixed:.3f}", pct(r.fixed / r.none - 1), delta_color="inverse")
    st.caption(f"Fix: **{FIXES.get(r.fix, r.fix)}**")
    names = load_json(str(study_file(m, ds)))["examples"][scene]
    imdir = BENCH_RES / f"study_{m}_{ds}_img"
    g = lambda k: imdir / names.get(k, "__none__")
    with st.container(border=True):
        show_example([[("Input with the fault", g(f"{fault}_rgb"), "rgb"), ("Ground-truth depth", "GT", "depth")],
                      [("Depth, no fix", g(f"{fault}_none"), "depth"), ("Depth, best fix", g(f"{fault}_best"), "depth")],
                      [("AbsRel, no fix", g(f"err_{fault}_none"), "err"), ("AbsRel, best fix", g(f"err_{fault}_best"), "err")],
                      [("Reference: depth on the clean input", g("clean"), "depth"), ("Reference: AbsRel on the clean input", g("err_clean"), "err")]],
                     f"{scene}: {m} · {ds} · {FAULTS10.get(fault, fault)} · fix: {FIXES.get(r.fix, r.fix)}", ds, scene,
                     ALIGN_NOTE.get(m, ""))
    vm = sorted((BENCH_FIG / "visual_models").glob(f"{ds}_{fault}_*.png"))
    if vm:
        with st.expander("Same fault on all four models"):
            img(vm[0])
    nav_buttons()


# --------------------------------------------------------------------------------------
# External evaluation: NYC street panoramas and follow-up studies
# --------------------------------------------------------------------------------------
NYC_GAIN = 0.05


@st.cache_data(show_spinner=False)
def nyc_metrics() -> pd.DataFrame:
    f = NYC_RESULTS / "midas_dpt_hybrid_nyc" / "rows_align-equatorial.csv"
    if not f.is_file():
        return pd.DataFrame()
    d = pd.read_csv(f, dtype={"image": str}, usecols=["image", "method", "band", "weighting", "n", "abs_rel"])
    d = d[(d.weighting == "pixel") & d.band.isin(["60-75", "75-90"])]
    d = d[d.method.isin(["baseline", "tangent|t45|v1|cosine|prior", "rotation|t45|pitch90_pm|cosine|prior",
                         "hybrid|t45|v1|pitch90_pm|cosine|prior"])]
    d = d.assign(m=d.method.str.split("|").str[0], w=d.abs_rel * d.n).groupby(["image", "m"]).agg(w=("w", "sum"), n=("n", "sum"))
    return (d.w / d.n).rename("polar").reset_index().pivot(index="image", columns="m", values="polar")


@st.cache_data(show_spinner=False)
def nyc_examples() -> pd.DataFrame:
    f = NYC_RESULTS / "midas_dpt_hybrid_nyc" / "rows_align-equatorial.csv"
    if not f.is_file():
        return pd.DataFrame()
    d = pd.read_csv(f, dtype={"image": str}, usecols=["image", "method", "band", "weighting", "n", "abs_rel"])
    d = d[(d.weighting == "pixel")]
    d = d[d.method.isin(["baseline", "tangent|t45|v1|cosine|prior", "rotation|t45|pitch90_pm|cosine|prior",
                         "hybrid|t45|v1|pitch90_pm|cosine|prior"])]
    d["m"] = d.method.str.split("|").str[0]
    whole = d[d.band == "all"].groupby(["image", "m"]).abs_rel.mean().rename("whole")
    pol = d[d.band.isin(["60-75", "75-90"])].assign(w=lambda x: x.abs_rel * x.n).groupby(["image", "m"]).agg(w=("w", "sum"), n=("n", "sum"))
    met = pd.concat([whole, (pol.w / pol.n).rename("polar")], axis=1).reset_index()
    rows = []
    debug_dir = ARCHIVES / "nyc" / "root_debug_samples_20261110"
    for p in sorted(debug_dir.glob("_panorama_*_*.png")):
        i, meth = p.stem[len("_panorama_"):].split("_", 1)
        s = met[met.image == f"C:_panorama_{i}"].set_index("m")
        if "baseline" not in s.index or meth not in s.index:
            continue
        b, c = s.loc["baseline"], s.loc[meth]
        rows.append(dict(scene=f"Panorama {i}", file=str(p), method=meth, base_polar=b.polar, polar=c.polar,
                         base_whole=b.whole, whole=c.whole, gain=1 - c.polar / b.polar))
    return pd.DataFrame(rows)


def page_nyc():
    hero("NYC street panoramas", "Does the projection correction carry over from indoor rooms to real outdoor "
         "city streets? The same pipeline, run on 75 NYC panoramas.", eyebrow="Study · NYC Outdoor",
         chips=["MiDaS DPT-Hybrid (frozen)", "75 outdoor panoramas", "Depth up to 1000 m"])
    facts([("Dataset", "NYC streets (DAP release)"), ("Methods", "Tangent · rotation · hybrid"),
           ("Best", "Tangent / hybrid: 0.529 → 0.48"), ("Worst", "Rotation: polar → 0.651"),
           ("Why", "Sky and far range at the top cap")])
    tbl = pd.DataFrame({"Whole": [0.3752, 0.3627, 0.4225, 0.3557], "Polar 60–90°": [0.5286, 0.4820, 0.6509, 0.4815],
                        "Model calls": [1, 3, 3, 5]}, index=["Baseline", "Tangent", "Rotation", "Hybrid"])
    c1, c2 = st.columns([3, 2])
    with c1:
        bar_chart(tbl["Polar 60–90°"], "Polar AbsRel, 75 NYC panoramas (lower is better)", height=180)
    with c2:
        st.dataframe(tbl.style.format({"Whole": "{:.3f}", "Polar 60–90°": "{:.3f}", "Model calls": "{:d}"})
                     .highlight_min(subset=["Whole", "Polar 60–90°"], color="#c9ecd3"), use_container_width=True)
    callout("Outdoors the gains are smaller than indoors: tangent views and the hybrid cut polar error by about 9%, "
            "while the rotation ensemble makes it worse, because the rotated sky and kilometre-scale depths fall "
            "outside what MiDaS handles well. Source: earlier NYC evaluation results.")

    ex = nyc_examples()
    mode = ex_mode()
    if not ex.empty:
        ex = ex[ex.gain >= NYC_GAIN] if mode == "help" else ex[ex.gain < 0] if mode == "hurt" else ex
    sub = (f"stored panoramas where the method lowers polar error by at least {NYC_GAIN:.0%}" if mode == "help"
           else ex_sub("polar error"))
    section("Examples", sub)
    if ex.empty:
        st.info("No stored example matches this filter. Try another option in the sidebar.")
    else:
        c1, c2 = st.columns(2)
        meths = [k for k in ["tangent", "hybrid", "rotation"] if k in set(ex.method)]
        meth = choose(c1, "Method", meths, LABELS.get, kind="radio", horizontal=True, key="nyc_m")
        pv = nyc_metrics()
        if not pv.empty and meth in pv and "baseline" in pv:
            r_ = (pv[meth] / pv["baseline"]).dropna()
            share_line(int((r_ < 0.99).sum()), int((r_ > 1.01).sum()), len(r_), "NYC panoramas (polar error)")
        exm = ex_order(ex[ex.method == meth])
        gains = exm.set_index("scene").gain
        scene = choose(c2, ex_label(), exm.scene, lambda s: f"{s}  ·  {pct(-gains[s])} polar error", key="nyc_s")
        r = exm.set_index("scene").loc[scene]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Polar AbsRel · baseline", f"{r.base_polar:.3f}")
        k2.metric(f"Polar AbsRel · {LABELS[meth]}", f"{r.polar:.3f}", pct(r.polar / r.base_polar - 1), delta_color="inverse")
        k3.metric("Whole AbsRel · baseline", f"{r.base_whole:.3f}")
        k4.metric(f"Whole AbsRel · {LABELS[meth]}", f"{r.whole:.3f}", pct(r.whole / r.base_whole - 1), delta_color="inverse")
        with st.container(border=True):
            img(Path(r.file))
    with st.expander("Error by latitude over all 75 panoramas"):
        img(NYC_RESULTS / "midas_dpt_hybrid_nyc" / "report_align-equatorial" / "profile_main_align-equatorial.png")
    nav_buttons()


def latest_report(study: str) -> Path | None:
    runs = sorted((FOLLOWUP_RESULTS / study / "outputs").glob("*/REPORT.md"), key=lambda p: p.parent.name.split("_", 1)[-1])
    return runs[-1] if runs else None


@st.cache_data(show_spinner=False)
def report_tables(path: str) -> dict:
    """Markdown tables of a REPORT.md, keyed by the heading above them ('' before any heading)."""
    out, head, buf = {}, "", []

    def flush():
        if len(buf) >= 3:
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in buf]
            df = pd.DataFrame(rows[2:], columns=rows[0])
            for col in df.columns[1:]:
                num = pd.to_numeric(df[col].str.replace("%", "").str.replace("°", "").str.replace("²", ""), errors="coerce")
                if num.notna().all():
                    df[col] = num
            out.setdefault(head, []).append(df)
        buf.clear()

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            buf.append(line)
            continue
        flush()
        if line.startswith("#"):
            head = line.lstrip("#").strip()
    flush()
    return out


def grouped_bars(df: pd.DataFrame, x: str, series: list[str], title: str, colors: list[str], height: int = 260):
    long = df.melt(id_vars=[x], value_vars=series, var_name="series", value_name="v")
    ch = alt.Chart(long).mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X(f"{x}:N", sort=list(df[x]), title=None, axis=alt.Axis(labelAngle=0, labelColor="#1d2433")),
        xOffset=alt.XOffset("series:N", sort=series),
        y=alt.Y("v:Q", title=title, axis=alt.Axis(gridColor="#eef0f4", labelColor="#5b6474", titleColor="#5b6474")),
        color=alt.Color("series:N", sort=series, scale=alt.Scale(domain=series, range=colors),
                        legend=alt.Legend(orient="top", title=None, labelColor="#1d2433")),
        tooltip=[alt.Tooltip(f"{x}:N"), alt.Tooltip("series:N"), alt.Tooltip("v:Q", format=".4f")],
    ).properties(height=height).configure_view(stroke=None)
    st.altair_chart(ch, use_container_width=True)


STUDIES = {
    "01": dict(dir="scale_only_protocol", name="Scale-only evaluation protocol", model="DA360 · Structured3D (200)",
               q="Does an affine fit (a·d + b) hide polar error that a stricter scale-only fit (s·d) reveals?",
               finding="Yes, under the equator-anchored protocol: the affine shift absorbs part of the polar error. "
                       "Scale-only gives 5.7% lower median polar error at 75–90° (CI excludes zero). With a global fit "
                       "the two protocols agree.",
               graph=f"""rgb [label="DA360 prediction", {N_IN}]; s [label="Fit s·d\\n(scale only)", {HL}];
  a [label="Fit a·d + b\\n(affine)", {N_BASE}]; e [label="AbsRel per\\nlatitude band", {N_OUT}];
  rgb -> s -> e; rgb -> a -> e;"""),
    "02": dict(dir="domain_conditioned_gate", name="Domain-conditioned rotation gate", model="DA360 · PanoX (8 environments)",
               q="Can a gate that decides when to apply rotation correction be calibrated on some environments and "
                 "transferred to a held-out one?",
               finding="The leave-one-environment-out gate chose 'no correction' in all 8 folds, which was the right call: "
                       "a fixed 45° rotation gate makes error 55% worse, and even the per-environment oracle is worse "
                       "than the baseline on average.",
               graph=f"""tr [label="7 training\\nenvironments", {N_IN}]; th [label="Pick threshold\\n30°–70° or none", {HL}];
  ho [label="Held-out\\nenvironment", {N_IN}]; ap [label="Apply gate", {HL}]; e [label="AbsRel", {N_OUT}];
  tr -> th -> ap; ho -> ap -> e;"""),
    "03": dict(dir="panda_style_finetuning", name="PanDA-style student distillation", model="Teacher DA360 → U-Net student · PanoX",
               q="Can a small student learn polar-robust depth from teacher pseudo-labels plus spherical consistency, "
                 "with no ground truth in training?",
               finding="No: the compact student stays far behind its teacher (median AbsRel 0.31 vs 0.06 with a global "
                       "fit, and worse at the poles). Distillation without ground truth did not transfer the teacher's "
                       "polar accuracy.",
               graph=f"""rgb [label="Unlabelled\\nPanoX ERPs", {N_IN}]; t [label="Frozen DA360\\nteacher", {N_BASE}];
  aug [label="Yaw / reflection\\naugmentation", {HL}]; st [label="U-Net student\\n(patch-normalised loss)", {HL}];
  e [label="Held-out\\nenvironments", {N_OUT}]; rgb -> t -> st; rgb -> aug -> st -> e;"""),
    "04": dict(dir="mono360_20view", name="20-view 360MonoDepth vs two-pole tangent", model="MiDaS DPT-Hybrid · PanoX (200)",
               q="Does a full-sphere 20-view icosahedral pipeline beat the cheap two-pole tangent correction?",
               finding="Only slightly: 20 views reach 0.155 polar error vs 0.166 for two pole views, at about 7× the "
                       "model calls. Two pole views capture over 90% of the gain for 3 calls instead of 20.",
               graph=f"""rgb [label="ERP panorama", {N_IN}]; tp [label="2 pole views\\n(3 calls)", {HL}];
  ic [label="20 icosahedral views\\n(20 calls)", {HL}]; e [label="Polar AbsRel\\nvs cost", {N_OUT}];
  rgb -> tp -> e; rgb -> ic -> e;"""),
    "05": dict(dir="fov_resolution_sweep", name="Tangent FOV × resolution sweep", model="MiDaS DPT-Hybrid · PanoX (200)",
               q="How sensitive is the tangent correction to the view's field of view and pixel resolution?",
               finding="Field of view dominates: going from 70° to 110° cuts polar error by about half, while raising "
                       "resolution from 256² to 512² at a fixed FOV changes almost nothing. 110° is the sweet spot.",
               graph=f"""rgb [label="ERP panorama", {N_IN}]; fv [label="FOV 70°–130°", {HL}]; rs [label="Size 256²–512²", {HL}];
  tp [label="Pole tangent\\nviews", {HL}]; e [label="Polar AbsRel", {N_OUT}]; rgb -> fv -> tp; rgb -> rs -> tp; tp -> e;"""),
    "06": dict(dir="structure_at_poles_gate", name="Structure-at-the-poles gate", model="Designed, not yet run",
               q="Instead of gating on latitude or environment, gate the correction on what is actually at the poles "
                 "(capture artefacts such as a tripod or missing caps).",
               finding="Motivated by studies 01 and 02 and by the capture-fault study: whether correction helps depends "
                       "on capture artefacts, not latitude. The gate code is written; no results are stored yet.",
               graph=f"""rgb [label="ERP panorama", {N_IN}]; d [label="Detect structure\\nat the poles", {HL}];
  g [label="Gate: correct\\nor keep baseline", {HL}]; e [label="Depth", {N_OUT}]; rgb -> d -> g -> e;"""),
}


def study_graph(body: str) -> str:
    return ('digraph G { rankdir=LR; bgcolor="transparent"; nodesep=0.25; ranksep=0.35;'
            'node [fontname="Helvetica", fontsize=11, margin="0.14,0.07", fontcolor="#1d2433"];'
            'edge [color="#8a93a3", arrowsize=0.7];' + body + "}")


def study_results(sid: str, tables: dict):
    blue, orange = "#2a78d6", "#eb6834"
    if sid == "01":
        for head in ["align-equatorial", "align-all"]:
            for df in tables.get(head, []):
                st.markdown(f"**{head}**")
                d = df.rename(columns={df.columns[0]: "Band"})
                grouped_bars(d, "Band", [d.columns[1], d.columns[2]], "Median AbsRel", [blue, orange], 220)
                st.dataframe(d.set_index("Band"), use_container_width=True)
    elif sid == "02":
        dfs = tables.get(next(iter(tables), ""), [])
        if dfs:
            d = dfs[0].set_index(dfs[0].columns[0])
            bar_chart(d.iloc[:, 0].rename(None), "Mean AbsRel (lower is better)", fmt=".4f", height=150)
            st.dataframe(d, use_container_width=True)
        folds = [df for v in tables.values() for df in v if "Held-out environment" in df.columns]
        if folds:
            with st.expander("Fold decisions"):
                st.dataframe(folds[0].set_index("Held-out environment"), use_container_width=True)
    elif sid in ("03", "04"):
        for head in ["align-all", "align-equatorial"]:
            for df in tables.get(head, []):
                st.markdown(f"**{head}**")
                d = df.rename(columns={df.columns[0]: "row"})
                if sid == "03":
                    grouped_bars(d, "row", [d.columns[1], d.columns[2]], "Median AbsRel", [blue, orange], 220)
                else:
                    long = d.melt(id_vars=["row"], value_vars=[c for c in d.columns if "median" in c], var_name="band", value_name="v")
                    long["band"] = long.band.str.replace(" median AbsRel", "").str.replace(" median", "")
                    wide = long.pivot(index="band", columns="row", values="v").reset_index()
                    grouped_bars(wide, "band", list(d.row), "Median AbsRel", ["#8a8f98", blue, "#eda100"], 220)
                st.dataframe(d.set_index("row"), use_container_width=True)
    elif sid == "05":
        for head in ["align-equatorial", "align-all"]:
            for df in tables.get(head, []):
                st.markdown(f"**{head}**")
                d = df.rename(columns={"median AbsRel (75–90°)": "v"})
                d["Size"] = d["size"].astype(int).astype(str) + "²"
                ch = alt.Chart(d).mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2).encode(
                    x=alt.X("FOV:Q", title="Tangent view FOV (°)", scale=alt.Scale(domain=[65, 135]),
                            axis=alt.Axis(values=[70, 90, 110, 130], gridColor="#eef0f4")),
                    y=alt.Y("v:Q", title="Median polar AbsRel (75–90°)", axis=alt.Axis(gridColor="#eef0f4")),
                    color=alt.Color("Size:N", scale=alt.Scale(domain=["256²", "384²", "512²"], range=[blue, orange, "#1baf7a"]),
                                    legend=alt.Legend(orient="top", title="Resolution")),
                    tooltip=["config", "FOV", "Size", alt.Tooltip("v:Q", format=".4f")],
                ).properties(height=240).configure_view(stroke=None)
                st.altair_chart(ch, use_container_width=True)
    else:
        readme = FOLLOWUP_RESULTS / STUDIES[sid]["dir"] / "README.md"
        if readme.is_file():
            with st.expander("Design notes (README)"):
                st.markdown(readme.read_text(encoding="utf-8"))


def page_followups():
    hero("Follow-up studies", "Six targeted experiments that stress-test the corrections: evaluation protocol, "
         "gating, distillation, view count and view geometry.", eyebrow="Studies · Follow-ups",
         chips=["DA360 · MiDaS", "PanoX · Structured3D", "Kaggle 2× T4", "Timestamped, reproducible runs"])
    sid = choose(st, "Study", STUDIES, lambda s: f"{s} · {STUDIES[s]['name']}", kind="radio", horizontal=True, key="fu_sid")
    s = STUDIES[sid]
    rep = latest_report(s["dir"])
    facts([("Study", s["name"]), ("Model · data", s["model"]),
           ("Run", rep.parent.name if rep else "not run")])
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("##### Question")
        st.markdown(s["q"])
        st.markdown("##### Finding")
        callout(s["finding"])
    with c2:
        st.markdown("##### Setup")
        with st.container(border=True):
            st.graphviz_chart(study_graph(s["graph"]), use_container_width=True)
    section("Results", f"from {rep.relative_to(ROOT).as_posix()}" if rep else "no stored run")
    study_results(sid, report_tables(str(rep)) if rep else {})
    nav_buttons()



def page_robustness():
    hero("Robustness checks", "Four checks from the report's appendices that test whether the main results depend "
         "on a scoring choice, a hidden cause, a loose rule or a small sample.", eyebrow="Study · Robustness",
         chips=["Appendix B–E", "External sets never used for choices", "Same frames, same code"])
    t = st.tabs(["Two scoring rules for DA²", "Nadir + JPEG diagnosis", "Stricter selection rules", "Policy stability"])
    with t[0]:
        callout("DA² gives relative depth, so it must be rescaled before scoring. <b>Least squares</b> lets a few very "
                "far pixels (sky, distant buildings) dominate; a <b>median fit</b> uses the typical ratio. On NYC the same "
                "predictions score <b>0.638</b> with least squares and <b>0.205</b> with the median fit; on Structured3D "
                "the two agree (0.053 and 0.051). 8 of 30 policy choices differ between the two rules.")
        with st.container(border=True):
            img(BENCH_FIG / "fig_da2_protocols.png", "DA² error under the two scale-fitting rules, by dataset")
        with st.expander("Sweeps under both rules"):
            img(BENCH_FIG / "fig_da2_sweeps_protocols.png")
    with t[1]:
        callout("The only strong fault with no gain: <b>blocked bottom + JPEG, DAP on NYC</b> (+1.3%, interval includes "
                "zero). One factor at a time, 147 frames: with the true cap mask the fill lowers the region error by "
                "<b>3.0%</b> [−8.1, −1.3] in raw metres but by <b>18.6%</b> [−26.3, −11.5] after a median scale fit; the "
                "filled cap still lies at 0.73 of the true depth (0.98 without JPEG). The detected mask costs a further "
                "part (−6.4% [−10.3, −3.3] after the scale fit). Fill order and a 1.5° margin make no measurable "
                "difference. The limit is mainly <b>metric scale</b>, then the mask.")
        with st.container(border=True):
            img(BENCH_FIG / "fig_diag_nadir_jpeg.png", "Each bar is one variant of the repair")
    with t[2]:
        callout("A fix is kept only if it lowers the median error by more than a set gain and helps a set share of "
                "training frames. Raising the rule from 2% / 60% to <b>5% / 70%</b> and running the full pipeline on the "
                "external sets cuts harmful cells from <b>7 to 5</b> of 48, while the median change over all cells moves "
                "only from −13.8% to −13.4%.")
        tbl = pd.DataFrame({"Harmful cells (2%/60% → 5%/70%)": ["3 → 2", "4 → 3", "7 → 5"],
                            "Median change (2%/60% → 5%/70%)": ["−17.3% → −16.1%", "−10.3% → −10.7%", "−13.8% → −13.4%"]},
                           index=["Stanford2D3D", "NYC", "All 48 cells"])
        st.dataframe(tbl, use_container_width=True)
        with st.container(border=True):
            img(BENCH_FIG / "fig_strict_rules.png")
    with t[3]:
        callout("The fault studies behind the policy used 40 frames per cell. Repeating them with 100 frames (71 for "
                "Holo360D outdoor) gives the <b>same choice in 137 of 144 cells (95%)</b>, with 52 cells applying a fix "
                "either way. The headline results still use the 40-frame policy, so this shows how often the choice "
                "would change, not what that would do to the error.")
        stab = pd.DataFrame({"Cells": [36, 36, 36, 36], "Same choice": [35, 35, 33, 34], "Different": [1, 1, 3, 2],
                             "Fix applied (40 frames)": [12, 20, 6, 14], "Fix applied (100 frames)": [11, 20, 7, 14]},
                            index=["MiDaS", "DAP", "DA360", "DA²"])
        st.dataframe(stab, use_container_width=True)
        diff = pd.DataFrame([["MiDaS", "Structured3D", "limited vFOV", "inpaint_tangent", "none"],
                             ["DAP", "Holo360D indoor", "limited vFOV", "inpaint_erp", "plane_fill"],
                             ["DA360", "PanoX", "JPEG", "bilateral", "none"],
                             ["DA360", "Holo360D indoor", "tilt", "none", "relevel_known"],
                             ["DA360", "Holo360D outdoor", "tilt", "none", "relevel_known"],
                             ["DA²", "PanoX", "yaw blur", "none", "wiener"],
                             ["DA²", "PanoX", "JPEG", "bilateral", "none"]],
                            columns=["Model", "Held-out set", "Fault", "40 frames", "100 frames"])
        st.dataframe(diff, use_container_width=True, hide_index=True)
    nav_buttons()


# --------------------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------------------
PAGE_OF = {"tangent": "Tangent-plane views", "rotation": "Rotation ensemble", "hybrid": "Hybrid (tangent + rotation)",
           "mono360": "360MonoDepth", "acgf": "ACGF v2"}
# (page, function, author, sidebar note, accent colour)
_PAGE_SPEC = [
    ("Overview", page_overview, "Overview", "The problem, every method at a glance, and the headline numbers.", "#2a78d6"),
    ("Baseline (single ERP pass)", page_baseline, "Baseline", "One plain pass of the frozen model: the reference.", COLORS["baseline"]),
    *[(PAGE_OF[k], (lambda k=k: page_projection(k)), "Projection Corrections", METHODS[k]["tagline"], COLORS[k]) for k in PAGE_OF],
    ("Measurement sweeps", page_sweeps, "Distortion Analysis", "Is the polar error really distortion? Move content across latitudes.", "#6250d6"),
    ("Gradient fusion & Möbius TTA", page_ensembles, "Ensembles", "Two inference-time ensembles with a compute-matched control.", "#6250d6"),
    ("Capture-fault catalogue", page_fault_catalogue, "Capture Faults", "Ten capture faults, their cost per model, and their fixes.", "#6250d6"),
    ("Capture-fault correction", page_faults, "Capture Faults", "Detect and fix capture faults before the model runs.", "#6250d6"),
    ("Robustness checks", page_robustness, "Analysis", "Scoring rules, the nadir+JPEG diagnosis, stricter rules, stability.", "#6250d6"),
    ("NYC street panoramas", page_nyc, "Real-World Evaluation", "The projection corrections on real outdoor city streets.", "#008300"),
    ("Follow-up studies", page_followups, "Follow-Up Studies", "Six stress tests: protocol, gating, distillation, views, FOV.", "#008300"),
    ("Compare all methods", page_compare, "Comparison", "All six projection pipelines on the same scene.", "#2a78d6"),
]
PAGES = {n: f for n, f, *_ in _PAGE_SPEC}
AUTHOR = {n: a for n, _, a, *_ in _PAGE_SPEC}
SIDEBAR_NOTE = {n: (note, c) for n, _, _, note, c in _PAGE_SPEC}
NAMES = list(PAGES)


def nav_buttons():
    i = NAMES.index(st.session_state.get("page", NAMES[0]))
    st.write("")
    a, _, b = st.columns([1, 2, 1])
    if i > 0:
        a.button(f"← {NAMES[i - 1]}", on_click=go_to, args=(NAMES[i - 1],), use_container_width=True, key="prev")
    if i < len(NAMES) - 1:
        b.button(f"{NAMES[i + 1]} →", on_click=go_to, args=(NAMES[i + 1],), use_container_width=True, key="next", type="primary")


_SLUG = {n: n.split(" (")[0].lower().replace(" & ", "-").replace("ö", "o").replace(" ", "-") for n in NAMES}
if "page" not in st.session_state:
    _q = st.query_params.get("page")
    st.session_state["page"] = next((n for n, sl in _SLUG.items() if sl == _q), NAMES[0])

with st.sidebar:
    st.markdown('<div class="sb-brand">Panoramic Depth</div>'
                '<div class="sb-sub">Distortion-aware depth on 360° images</div>', unsafe_allow_html=True)
    choice = st.selectbox("Method", NAMES, key="page", format_func=lambda n: f"{n}  ·  {AUTHOR[n]}" if n in AUTHOR else n)
    note, color = SIDEBAR_NOTE[choice]
    st.markdown(f'<div class="sb-card" style="--c:{color}">{note}</div>', unsafe_allow_html=True)
    st.divider()
    st.radio("Examples to show", list(EX_MODES), format_func=EX_MODES.get, key="ex_mode",
             help="Which stored examples the method pages list. Shares of frames improved are always over all frames.")
    st.markdown("**How to read this app**")
    st.caption("Each method page shows its pipeline (orange = what it adds to the baseline), the share of frames it "
               "improves, and stored examples filtered by the option above. All results are precomputed; no models run here.")
    _pdf = REPORT / "final_report.pdf"
    if _pdf.is_file():
        st.download_button("Download the final report (PDF)", _pdf.read_bytes(), file_name="Final_Report.pdf",
                           mime="application/pdf", use_container_width=True)
    _pdf_ext = REPORT / "extended_report.pdf"
    if _pdf_ext.is_file():
        st.download_button("Download extended report with future scope (PDF)", _pdf_ext.read_bytes(),
                           file_name="Extended_Report.pdf", mime="application/pdf", use_container_width=True)
    st.divider()
    st.caption("Distortion-Aware Panoramic Depth Estimation\n\nIIT Jodhpur · Computer Vision")

st.query_params["page"] = _SLUG[choice]
st.session_state["_missing"] = []
PAGES[choice]()
if st.session_state["_missing"]:
    _miss = sorted(set(st.session_state["_missing"]))
    with st.expander(f"{len(_miss)} stored image(s) for this page are not in this copy of the repository"):
        st.caption("These are hidden above. They are present in the full repository; a partial checkout or the "
                   "code-only zip leaves them out.")
        st.code("\n".join(_miss[:50]), language=None)
