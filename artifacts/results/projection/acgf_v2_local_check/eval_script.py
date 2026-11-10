import sys, time, numpy as np, pandas as pd
sys.path.insert(0, '.')
from datasets.panorama import PanoramaDataset
from evaluation.evaluation import Evaluator
from inference.pipeline import DistortionAwareInference, MethodConfig
from models.depth_model import build_model
out_dir = sys.argv[1]; N = int(sys.argv[2]); START = 40
model = build_model(dict(name='midas', model_type='dpt_hybrid_384', weights='weights/dpt_hybrid_384.pt', erp_net_height=384))
A = dict(tangent_size=384, acgf_law='off')
methods = {
 'baseline': MethodConfig('baseline'),
 'hybrid': MethodConfig('hybrid', tangent_size=384, rotations=[[0,90,0],[0,-90,0]], range_guard=True),
 'acgf_v1': MethodConfig('acgf', **A),
 'acgf_v1_value': MethodConfig('acgf', acgf_domain='value', **A),
 'acgf_v2': MethodConfig('acgf', acgf_work='auto', acgf_gate_mode='value', **A),
 'acgf_v2_nogate': MethodConfig('acgf', acgf_work='auto', acgf_gate_mode='value', acgf_gate=False, **A),
}
sets = [('structured3d', 'data/structured3d', 'test_s3250.txt', 10.0), ('holo_indoor', 'data/holo360d', 'test_indoor.txt', 100.0),
        ('holo_outdoor', 'data/holo360d', 'test_outdoor.txt', 100.0)]
rows = []
for name, root, lst, maxd in sets:
    ds = PanoramaDataset(root, lst, 512, 1024, name=name.split('_')[0] if name != 'structured3d' else 'structured3d', limit=START + N)
    ds.items = ds.items[START:START + N]
    evs = {r: Evaluator('disparity', 'affine', align_region=r, max_depth=maxd) for r in ('all', 'equatorial')}
    dai = DistortionAwareInference(model, batch_size=4)
    for s in ds:
        t = time.time()
        for k, mc in methods.items():
            res = dai.run(s.rgb, s.id, mc)
            for ev in evs.values():
                ev.add(s.id, k, res['pred'], s.depth, s.valid)
        dai.clear_cache()
        print(name, s.id, '%.0fs' % (time.time() - t), flush=True)
    for r, ev in evs.items():
        d = ev.frame(); d['dataset'] = name; d['align'] = r; rows.append(d)
    pd.concat(rows).to_csv(f'{out_dir}/v2_rows.csv', index=False)
