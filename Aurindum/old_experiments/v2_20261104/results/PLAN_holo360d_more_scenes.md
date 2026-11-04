# Plan: Holo360D with more scenes (written 3 Nov 2026, while the extra scenes are downloading)

## Why
Holo360D currently has 4 indoor and 2 outdoor scenes. With one cluster per scene, the smallest attainable
Wilcoxon p is 0.125 (n = 4) and 0.5 (n = 2), and a bootstrap over 4 clusters is not a confidence interval.
The Holo360D numbers are therefore direction-only. The extra 8 indoor test scenes give n = 12 indoor clusters
(smallest exact two-sided p about 0.0005), the first size at which a cluster-robust claim is possible.
The 56 train-split indoor scenes can be used too: nothing is trained, so the split is irrelevant for a
frozen-model evaluation (say so in the write-up).

## Steps
1. Copy the new scenes next to the old ones: `data/holo360d/<Scene>/<Scene>/{rgb,mask,depth/mesh_depth}`.
2. `python scripts/make_holo360d_list.py --root data/holo360d --frames_per_scene 25` rewrites the test / indoor /
   outdoor lists (evenly spaced frames, so long scenes do not dominate) and reports skipped frames.
3. Check clustering: `group_of('Indoor_007_1234')` must give `Indoor_007` (one cluster per scene, not per frame).
4. Run, cheap to expensive:
   `STAGES="E F D" scripts/run_next_experiments.sh start`   rotation-only, fit guard, Method 1 on the rotated view, diagnostics
   `STAGES="B D" scripts/run_next_experiments.sh start`     the full baseline table on the enlarged Holo360D
5. Decision rule, fixed now so it is not chosen after seeing the data:
   * rotation-only M2 and M1-on-rotated are the methods; the 4-pass M2 appears only as an ablation row;
   * "transfers to real indoor" requires the cluster CI of the 75-90 deg gain to exclude 0 on at least 12 indoor
     clusters AND the yaw control to stay near 0;
   * if rotation-only is still negative on real indoor at 12 clusters, the honest result is "polar re-centring
     helps on rendered Structured3D only"; the diagnostic (intrinsic vs realised gain) then says whether that is
     the model (intrinsic < 0) or the anchoring (intrinsic > 0, large anchor loss).
6. Outdoor: 2 clusters can never support a statistical claim; more outdoor scenes are needed before it is more than anecdote.
