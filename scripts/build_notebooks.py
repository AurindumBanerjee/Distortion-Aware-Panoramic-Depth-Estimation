"""Generate the four notebooks (code lives in the package; notebooks only call it and show results).

    python scripts/build_notebooks.py && jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
"""
import os

import nbformat as nbf

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(HERE, "notebooks")

SETUP = """import os, sys, json
ROOT = os.path.abspath('..') if os.path.basename(os.getcwd()) == 'notebooks' else os.getcwd()
sys.path.insert(0, ROOT); os.chdir(ROOT)
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from IPython.display import Image, Markdown, display
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
RES = 'results/midas_dpt_hybrid_synthetic'   # change to e.g. results/dap_stanford2d3d after running DAP
REP = os.path.join(RES, 'report_align-all')
def show(p, w=900):
    p = os.path.join(RES, p) if not os.path.exists(p) else p
    display(Image(filename=p, width=w)) if os.path.exists(p) else print('missing', p)"""


def md(s):
    return nbf.v4.new_markdown_cell(s)


def code(s):
    return nbf.v4.new_code_cell(s)


def write(name, cells):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nbf.write(nb, os.path.join(NB, name))


def nb01():
    write("01_baseline.ipynb", [
        md("# 01 - Dataset and baseline ERP inference\n\nFrozen model, full ERP in, ERP depth out. "
           "This notebook runs the baseline live on one panorama and then loads the dataset-level results "
           "written by `python run_experiment.py`."),
        code(SETUP),
        md("## Dataset\nProcedural indoor panoramas with exact ground-truth range (see `datasets/synthetic.py`). "
           "Replace with Stanford2D3D / Matterport3D via the configs in `configs/`."),
        code("""from experiments.common import load_config, make_dataset
cfg = load_config('configs/default.yaml')
ds = make_dataset(cfg)
s = ds[0]
print(len(ds), 'panoramas;', s.rgb.shape, 'GT range', np.nanmin(s.depth), '-', np.nanmax(s.depth), 'm')
fig, ax = plt.subplots(1, 2, figsize=(14, 3.6))
ax[0].imshow(s.rgb); ax[0].set_title('ERP RGB'); ax[1].imshow(s.depth, cmap='magma'); ax[1].set_title('GT range (m)')
[a.axis('off') for a in ax]; plt.show()"""),
        md("## Baseline inference (live, one image)"),
        code("""from models.depth_model import build_model
from evaluation.metrics import to_metric_depth
from evaluation.latitude_analysis import per_band_metrics
model = build_model(dict(cfg['model']))
pred = model.predict(s.rgb, 'erp')
depth, info = to_metric_depth(pred, np.nan_to_num(s.depth, nan=1.0), s.valid, model.spec.space, 'affine')
print(model.describe(), info)
m = per_band_metrics(depth, np.nan_to_num(s.depth, nan=1.0), s.valid)
pd.DataFrame(m).T[['n','abs_rel','sq_rel','rmse','rmse_log','mae','medae','d1','d2','d3','pct_bad']]"""),
        code("""err = np.where(s.valid, np.abs(depth - s.depth) / s.depth, np.nan)
fig, ax = plt.subplots(1, 2, figsize=(14, 3.6))
lo, hi = np.nanpercentile(s.depth, [1, 99])
ax[0].imshow(depth, cmap='magma', vmin=lo, vmax=hi); ax[0].set_title('Baseline prediction (affine-aligned to GT)')
im = ax[1].imshow(err, cmap='Reds', vmin=0, vmax=0.5); ax[1].set_title('AbsRel'); plt.colorbar(im, ax=ax[1], fraction=0.02)
[a.axis('off') for a in ax]; plt.show()"""),
        md("## Dataset-level baseline (from `run_experiment.py`)"),
        code("pd.read_csv(os.path.join(REP, 'latitude_bands_align-all.csv'), index_col=0)"),
        code("show('report_align-all/baseline_band_metrics_align-all.png')"),
    ])


def nb02():
    write("02_latitude_analysis.ipynb", [
        md("# 02 - ERP distortion as a function of latitude\n\n"
           "Observation first, interpretation second: we measure how error varies with latitude, then use a "
           "rotation control to separate *distortion in the model input* from *scene content* (floors/ceilings "
           "always sit at the poles of upright indoor panoramas)."),
        code(SETUP),
        md("## How strong is the ERP distortion?\nHorizontal stretch 1/cos(phi): x1.15 at 30 deg, x1.41 at 45, x2 at 60, x3.9 at 75."),
        code("show('report_align-all/erp_distortion.png')"),
        md("## Error vs latitude (baseline)"),
        code("""for r in ['all', 'equatorial']:
    display(Markdown(f'**eval alignment fitted on: {r}**'))
    display(pd.read_csv(os.path.join(RES, f'report_align-{r}', f'latitude_bands_align-{r}.csv'), index_col=0))
    show(f'report_align-{r}/abs_rel_vs_abs_latitude_align-{r}.png', 650)"""),
        md("## Where does degradation start? (paired bootstrap vs the |lat|<15 reference)"),
        code("""on = json.load(open(os.path.join(REP, 'onset_align-all.json')))
print('onset |lat|:', on['onset_abs_lat'])
pd.DataFrame(on['bins']).round(4)"""),
        md("## Per-pixel mean error"),
        code("show('report_align-all/heatmap_baseline.png')"),
        md("## Control: content vs latitude\nThe same panoramas rotated by pitch 0/30/60/90 deg (GT rotated identically). "
           "Left: error against latitude in the image the model saw. Right: against latitude of the content in the "
           "upright scene. The GT alignment of the relative model is fitted on (a) all pixels, (b) the input's equator "
           "(the situation of inference-time correction, which trusts the equator), (c) the content's equator."),
        code("""for a in ['view_equatorial', 'all', 'content_equatorial']:
    d = os.path.join(RES, 'latitude_control', f'align-{a}')
    display(Markdown(f'### GT alignment fitted on: {a}'))
    show(os.path.join(d, 'latitude_control.png'), 900)
    display(Markdown('Within one pitch, same image and content band: % change of AbsRel when the content sits further from the input equator (median is robust to the few degenerate fits):'))
    display(pd.read_csv(os.path.join(d, 'control_within_pitch_view_effect.csv')).round(2))"""),
        md("## Why does the hybrid work? Signed polar bias of each view (8 images)"),
        code("""p = os.path.join(RES, 'bias_analysis_summary.csv')
pd.read_csv(p, header=[0, 1], index_col=[0, 1]) if os.path.exists(p) else print('run: python -m experiments.bias_analysis')"""),
    ])


def nb03():
    write("03_tangent_projection.ipynb", [
        md("# 03 - Spherical geometry: tangent planes, rotations, validation\n\n"
           "All projection code is in `geometry/`; this notebook demonstrates and *validates* it before any "
           "experiment is trusted."),
        code(SETUP),
        md("## Validation (exact maths and interpolation error)"),
        code("""from geometry.validation import run_all
g = run_all(save_path=None)
display(Markdown('**Point level** (sphere -> ERP -> sphere -> tangent -> 3D -> ERP, known depth)'))
display(pd.DataFrame(g['point_level']).T)
display(Markdown('**Image level** (bilinear resampling of an analytic field; plane depth z->range check)'))
display(pd.DataFrame(g['image_level']).T[['erp2tan_mean_rel_err','roundtrip_mean_rel_err','roundtrip_max_rel_err',
                                          'plane_range_max_rel_err','plane_range_err_if_z_used_as_range_max']])
display(Markdown('**Rotations**'))
pd.DataFrame(g['rotation']).T"""),
        md("## Tangent views of the polar caps"),
        code("""from experiments.common import load_config, make_dataset
from geometry.tangent_plane import polar_tangent_layout, erp_to_tangent, tangent_to_erp
cfg = load_config('configs/default.yaml'); s = make_dataset(cfg)[0]
planes = polar_tangent_layout(45, views_per_pole=3, size=256)
for p in planes[:3]: print(p)
fig, ax = plt.subplots(1, 3, figsize=(12, 4))
for a, p in zip(ax, planes[:3]):
    a.imshow(erp_to_tangent(s.rgb.astype(np.float32), p).astype(np.uint8)); a.set_title(f'lon {p.lon_deg:.0f} lat {p.lat_deg:.0f} fov {p.fov_deg:.0f}'); a.axis('off')
plt.show()"""),
        code("""cover = np.zeros(s.depth.shape, int)
for p in planes: cover += tangent_to_erp(np.ones((p.size, p.size)), p, *s.depth.shape).valid
plt.figure(figsize=(10, 3.5)); plt.imshow(cover, cmap='Blues'); plt.colorbar(label='# tangent views covering pixel')
plt.title('Coverage of the |lat|>45 caps by 2x3 tangent views'); plt.axis('off'); plt.show()"""),
        md("## Spherical rotation (not a pixel shift)\nPitch +90 deg brings BOTH poles onto the equator (north at the front, south at the back)."),
        code("""from geometry.erp_projection import rotate_erp
from geometry.spherical import rotation_from_ypr
R = rotation_from_ypr(0, 90, 0)
rot = rotate_erp(s.rgb.astype(np.float32), R).astype(np.uint8)
back = rotate_erp(rot.astype(np.float32), R.T).astype(np.uint8)
fig, ax = plt.subplots(3, 1, figsize=(10, 10))
for a, im, t in zip(ax, [s.rgb, rot, back], ['original', 'rotated (pitch 90)', 'rotated back']): a.imshow(im); a.set_title(t); a.axis('off')
plt.show()"""),
        md("## The full tangent pipeline on one view (from the experiment run)"),
        code("""import glob
for p in sorted(glob.glob(os.path.join(RES, 'qualitative', 'tangent_view_*.png')))[:2]: show(p, 1100)"""),
    ])


def nb04():
    write("04_results.ipynb", [
        md("# 04 - End-to-end: dataset -> baseline -> latitude analysis -> tangent -> rotation -> fusion -> evaluation -> ablation\n\n"
           "Part A runs the whole method live on one panorama. Part B loads the complete experiment "
           "(`python run_experiment.py --config configs/default.yaml`)."),
        code(SETUP),
        md("## A. Live run on one panorama"),
        code("""from experiments.common import load_config, make_dataset
from models.depth_model import build_model
from inference.pipeline import DistortionAwareInference, MethodConfig
from evaluation.evaluation import Evaluator
cfg = load_config('configs/default.yaml'); s = make_dataset(cfg)[1]
model = build_model(dict(cfg['model']))
dai = DistortionAwareInference(model)
ev = Evaluator(model.spec.space, 'affine')
cfgs = [MethodConfig('baseline'), MethodConfig('tangent', lat_threshold=45, fusion='cosine'),
        MethodConfig('rotation', rotations=[[0,90,0],[90,90,0]], fusion='cosine'),
        MethodConfig('hybrid', rotations=[[0,90,0],[90,90,0]], fusion='cosine')]
for c in cfgs:
    r = dai.run(s.rgb, s.id, c); ev.add(s.id, c.label(), r['pred'], s.depth, s.valid, r)
    print(f"{c.label():32s} model calls {r['model_calls']:2d}  runtime {r['runtime_s']:.1f}s")
ev.summary().pivot(index='method', columns='band', values='abs_rel').round(4)"""),
        md("## B. Full experiment\n### Main comparison (Experiments 1-4)"),
        code("pd.read_csv(os.path.join(REP, 'main_comparison.csv'), index_col=0).round(4)"),
        code("show('report_align-all/profile_main_align-all.png', 700)"),
        md("### Latitude-specific improvement tables (paired over images; 95% bootstrap CI; Wilcoxon)"),
        code("""for name in ['tangent_plane', 'rotation', 'hybrid']:
    display(Markdown(f'**{name}** (eval alignment: all pixels)'))
    display(pd.read_csv(os.path.join(REP, f'{name}_improvement.csv')).round(4))
    display(Markdown(f'**{name}** (eval alignment fitted on |lat|<30 only)'))
    display(pd.read_csv(os.path.join(RES, 'report_align-equatorial', f'{name}_improvement.csv')).round(4))"""),
        md("### Ablations (Experiments 5-7)"),
        code("""cols = ['abs_rel','abs_rel_0-15','abs_rel_45-60','abs_rel_60-75','abs_rel_75-90','abs_rel_polar_60_90','d1','model_calls','runtime_ratio']
ab = pd.read_csv(os.path.join(REP, 'ablation.csv'), index_col=0)
for e, d in ab.groupby('experiment', sort=False):
    display(Markdown(f'**{e}**')); display(d[cols].round(4))"""),
        code("""for f in ['profile_threshold_tangent', 'profile_threshold_rotation', 'profile_views', 'profile_fusion_rotation', 'profile_rotation_sets']:
    show(f'report_align-all/{f}_align-all.png', 650)"""),
        md("### Resolution (Experiment 8) and runtime (Experiment 9)"),
        code("""display(pd.read_csv(os.path.join(RES, 'resolution.csv'), index_col=0).round(4))
display(pd.read_csv(os.path.join(RES, 'runtime_cold.csv'), index_col=0).round(3))
show('report_align-all/runtime_vs_accuracy.png', 650)"""),
        md("### Qualitative"),
        code("""import glob
for p in sorted(glob.glob(os.path.join(RES, 'qualitative', 'scene_*_rotation.png')))[:2]: show(p, 900)
for p in sorted(glob.glob(os.path.join(RES, 'qualitative', 'scene_*_tangent.png')))[:1]: show(p, 900)"""),
        md("### Error heatmaps (same colour scale)"),
        code("""for m in ['baseline', 'tangent', 'rotation', 'hybrid']: show(f'report_align-all/heatmap_{m}.png', 650)"""),
    ])


if __name__ == "__main__":
    os.makedirs(NB, exist_ok=True)
    nb01(); nb02(); nb03(); nb04()
    print("notebooks written to", NB)
