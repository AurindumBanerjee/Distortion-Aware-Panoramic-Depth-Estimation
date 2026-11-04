# Pre-registration: round 3b (written 4 Nov 2026, before any of these runs)

Round 3 found no model with a measurable distortion onset in the rotation sweep, but the planar / non-planar split
showed that the rotation sweep confounds distortion with ORIENTATION: a pitch rotation brings a pole to the equator by
tipping the scene (the floor becomes a wall in front), and depth models rely on "floor is below". Round 3 also found,
post hoc, that a near-uniformly weighted rotation-only ensemble (`r3wonly`) gained on Structured3D and PanoX for MiDaS.
Round 3b separates the two effects and tests the ensemble finding on fresh, fixed terms.

Datasets: Structured3D EVALUATION houses (cluster-hash split, as in round 3), PanoX (8 environments), Holo360D indoor
(12 scenes). Holo360D outdoor (3 scenes) is reported but cannot support any claim. Models: MiDaS DPT-Hybrid, DAP,
DA360, DA^2. All statistics cluster-robust; gains are 75-90 deg AbsRel reductions under each model's headline protocol.

## Part A experiments (measurement)

| id | experiment | what it isolates |
|---|---|---|
| X1 | dilation sweep (stereographic lambda in {1/16, 1/4, 1/2, 1, 2, 4, 16}) | distortion without tipping the scene (confound: local magnification, reported as log_mag) |
| X2 | flip sweep (roll 180 deg) | orientation penalty with the latitude (distortion) unchanged |
| X3 | rotation sweep re-run with the content split | onset on non-planar content (less orientation-dependent) |

Interpretation rule (fixed now):
- **distortion effect** for a model = an onset in BOTH the dilation sweep and the non-planar rotation sweep on the
  Structured3D calibration houses. Only then is the latitude curve used to correct that model.
- **orientation effect** = a positive flip-sweep dE in the 60-90 deg bins (cluster CI excluding 0).
- If a model has an orientation effect, rotation-based passes are expected to be individually worse at the poles than
  the upright view; the ensemble must not let them dominate there (hence uniform weights in X4).

## Part B experiments (correction), fixed configuration

| id | configuration | passes |
|---|---|---|
| X4 (confirmatory) | rotation-only Moebius TTA, **uniform weights** (`weight_power 0`), identity re-anchor, no gate | identity, pitch +90, -90 |
| X5 (dose-response) | uniform rotation ensemble with more views | identity, pitch +-45, +-90 (5) and +-30, +-60, +-90 (7) |
| X6 (orientation-preserving) | uniform dilation ensemble (up stays up) | identity, lambda 1/2, 2 |
| X7 (curve-driven, conditional) | round-3 correction (gate + 1/ratio^2 weights) using the DILATION curve | only for models with an X1 onset |

Every configuration is compared with the compute-matched yaw control (same number of passes, uniform).

**Hypotheses and decision rules (X4)**
- H1: for MiDaS, X4 improves 75-90 AbsRel on each of Structured3D-eval, PanoX and Holo360D indoor. Claimed per
  dataset only if the cluster CI excludes 0 under `align-all`, the 0-30 deg bands are not worse (median change >= -1%),
  and the yaw control stays within +-2%. Claimed as "transfers to real indoor" only if Holo360D indoor passes.
- H2: for DAP, DA360, DA^2, X4 does not improve (no polar deficit); any significant loss is reported as a limit.
- H3 (X5): if the gain comes from decorrelated views, 5 and 7 passes gain at least as much as 3, while their yaw controls
  stay at ~0. If 5 / 7 passes are worse, the gain is specific to the +-90 views.
- H4 (X6): if orientation is what hurts rotated views, the dilation ensemble is at least neutral where X4 loses.
- Nothing is tuned on these datasets: weights are uniform, passes are fixed above.
