# Experiment 6 — Structure-at-the-poles gate (capture-artifact aware)

## Why this experiment exists

Experiments 01 and 02 both found that latitude-based / environment-identity-based
correction does not transfer: the LOEO gate in 02 selected "baseline" (no
correction) in every held-out environment, and its oracle upper bound was
*worse* than baseline in 2 of 8 environments (ClothingStore: 2/25 scenes win,
Mountain_Environment_Set: 0/25 scenes win) while being clearly better in 3
others (ModularBakeryShop, Warehouse, SouthOfFrance: +10% to +25% median
gain). Experiment 01's per-scene scale-only-vs-affine results are similarly
bimodal rather than uniform.

Harshita's cross-model benchmark (MiDaS / DAP / DA360 / DA2) independently
found that the dominant real-world failure mode is not polar distortion as a
function of latitude — it's everyday capture defects: tilted camera, a tripod
occluding the nadir, the top/bottom of the sphere not captured, and heavy
compression. DAP in particular breaks badly on these.

Put together: whether a polar correction helps looks less like a function of
*where* you are on the sphere, and more like a function of *whether there is
real, correctable geometric structure at the poles in this particular
image*. Mountain_Environment_Set has low baseline error and 0/25 scenes
improve under correction — consistent with open sky at the zenith, i.e.
nothing there to correct. That's the same underlying problem as "top/bottom
not captured," just with the defect being "nothing is there" instead of
"the capture clipped it."

This experiment builds a model-agnostic, no-GT, inference-time **gate** that
detects these conditions directly from the input panorama (and, optionally,
the backbone's own uncorrected polar prediction) and decides whether to
apply a correction at all, rather than gating on latitude threshold or
environment identity — both of which experiment 02 showed do not transfer.

## What the gate checks

Four cheap, GT-free signals, computed separately for the north and south
polar caps (default cap = 75-90 deg, matching the band used in experiments
01/02/04/05 so results are directly comparable):

1. **`tripod_occlusion_score`** — looks for a low-variance, near-constant
   blob sitting at the bottom of the frame (nadir cap). A real tripod head
   fills a roughly wedge/disk-shaped region with near-uniform color and
   near-uniform (usually very close-range) disparity. Flags high score.
2. **`missing_coverage_score`** — fraction of invalid/zero-alpha or
   degenerate pixels in the cap, from the input's own valid-pixel mask if
   available, else inferred from near-constant extreme (pure black/white)
   RGB. Flags frames where the top or bottom was never captured.
3. **`flat_sky_score`** — looks for the opposite failure mode surfaced by
   Mountain_Environment_Set: a cap that is real content but has very low
   disparity gradient and low texture (open sky / featureless ceiling)
   and so has no real geometric structure for a tangent-plane or
   rotation-ensemble correction to lock onto. High score here means
   "correction has nothing to correct."
4. **`compression_blockiness_score`** — 8x8 DCT block-edge energy ratio in
   the cap, flags heavy JPEG-style compression artifacts.

These combine into a single `should_correct(cap_scores) -> bool` decision
per pole, with the thresholds left as named constants at the top of
`gate.py` so they can be calibrated on a small held-out slice before the
full LOEO-style run, exactly as experiment 02 calibrated its latitude
threshold.

## How to use it

```python
from gate import compute_cap_scores, should_correct

scores = compute_cap_scores(rgb_equirect, disparity_equirect, valid_mask=None)
# scores = {"north": {...4 subscores...}, "south": {...}}

if should_correct(scores["south"]):
    # apply tangent-plane / rotation-ensemble correction to the south cap
    ...
else:
    # leave the baseline (uncorrected) prediction for the south cap
    ...
```

`run_gate_eval.py` is a thin wrapper that runs this gate over a scene list
in the same format experiments 01/02 use (`scene,environment` columns) and
reports AbsRel for "always correct" vs "gated correct" vs "never correct,"
by pole and pooled — reusing `evaluation/protocol.py`'s median-based
reporting so this experiment's REPORT.md is directly comparable to 01/02/04/05.

## What would make this a real result

Per the plan agreed on: calibrate thresholds on a small slice, then run the
*same* leave-one-environment-out structure experiment 02 used, but gate by
these per-image scores instead of environment identity. If the gated
correction transfers across held-out environments where the identity-based
gate in 02 did not (especially recovering Warehouse/ModularBakeryShop/
SouthOfFrance-style gains without the Mountain_Environment_Set/ClothingStore
collapse), that is the headline result for the PS. Equally informative if it
doesn't transfer — that would mean the real signal needs the backbone's own
prediction (self-consistency across rotations), not just the input image,
which is the natural follow-up (`07_`).
