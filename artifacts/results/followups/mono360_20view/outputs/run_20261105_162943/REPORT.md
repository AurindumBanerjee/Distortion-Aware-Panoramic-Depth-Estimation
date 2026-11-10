# Experiment 4 — 20-view full-sphere inference

The 20-view system uses icosahedral tangent views, per-view disparity standardisation,
deformable scale/offset alignment over overlapping views, and frustum blending.
It is compared against the baseline and the existing two-pole tangent correction.

## align-all

| method | global median AbsRel | 60–75° median | 75–90° median | calls/image |
|---|---:|---:|---:|---:|
| baseline | 0.1898 | 0.1394 | 0.1514 | 1 |
| two_pole_tangent | 0.1632 | 0.1020 | 0.0950 | 3 |
| mono360_20view | 0.1645 | 0.0801 | 0.0832 | 20 |

## align-equatorial

| method | global median AbsRel | 60–75° median | 75–90° median | calls/image |
|---|---:|---:|---:|---:|
| baseline | 0.2321 | 0.2389 | 0.3468 | 1 |
| two_pole_tangent | 0.1913 | 0.1661 | 0.1659 | 3 |
| mono360_20view | 0.1615 | 0.1429 | 0.1550 | 20 |
