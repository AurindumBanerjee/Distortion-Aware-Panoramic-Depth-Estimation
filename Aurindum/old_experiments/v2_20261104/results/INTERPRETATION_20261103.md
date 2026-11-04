# Interpretation of the corrected-suite results (3 Nov 2026)

Statistics below are cluster-robust (scenes resampled by house / environment: 300 Structured3D scenes = 182 houses,
200 PanoX frames = 80 environments). Gain = median relative AbsRel reduction at 75-90 deg (positive = better).

| Setting | Protocol | Method 1 (Poisson) | Method 2 (Möbius TTA) | Yaw control (same #passes) |
|---|---|---|---|---|
| S3, MiDaS | align-all | +15% [10,20] | +14% [8,22] | -0.1% (n.s.) |
| S3, MiDaS | align-equatorial | +54% [50,56] | +57% [53,61] | -2% |
| PanoX, MiDaS | align-equatorial | +21% [4,31] | -153% | -0.2% (n.s.) |
| PanoX, MiDaS | align-all | -35% | -296% | -0.7% (n.s.) |
| S3, DAP | none / align-all | -74% / -79% | -875% / -459% | +4% / +2% |
| PanoX, DAP | none / align-all | -3% (n.s.) / -55% | -408% / -452% | +1% (n.s.) / +2% |

Reading:
1. MiDaS on indoor Structured3D: both methods give a real, significant polar gain; the yaw control is ~0, so the
   gain comes from showing the poles at low distortion, not from test-time averaging. Gains are 3-4x larger under
   align-equatorial because that protocol exposes MiDaS's polar inconsistency; under align-all the baseline is
   already partly fixed by the global fit.
2. DAP is already ERP-native and has no polar deficit (75-90 AbsRel 0.023 vs 0.17 for MiDaS). Our fusion only
   injects out-of-distribution rotated / dilated predictions: M1 mildly hurts, M2 breaks (also at the equator, i.e.
   a pipeline problem: full-weight non-identity passes + dilation destroys metric scale + no metric re-anchor).
   The only thing that helps DAP is plain yaw-TTA (+2-4%): a small, honest result.
3. Outdoor PanoX with MiDaS: M2 fails, M1 only helps under the strict protocol. Indoor-room assumptions
   (bounded depth, similar structure in rotated views) do not transfer to sky / open scenes. Do not claim generality.
4. Synthetic series are unreliable (renderer/texture artefacts); report real-data series only.
5. Clustering shrinks CIs' optimism: S3 M2 align-all p went 5e-4 -> 3e-3, still significant. PanoX MiDaS M1
   align-all flips from n.s. to significantly negative once clustered (cluster means weight blow-ups more).

Patch 7 targets point 2/3: logscale re-anchor for metric models + `gate_lat` (non-identity passes fade in between
|lat| 30 and 55 deg, output == baseline below 30). Enabled for DAP configs only; MiDaS stays ungated until the
ablation (`scripts/run_mobius_ablation.sh`) says whether rotation-only / gated variants rescue PanoX.
