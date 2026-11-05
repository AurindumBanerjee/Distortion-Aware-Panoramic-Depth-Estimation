# Experiment 4 — 20-view full-sphere inference

The 20-view system uses icosahedral tangent views, per-view disparity standardisation,
deformable scale/offset alignment over overlapping views, and frustum blending.
It is compared against the baseline and the existing two-pole tangent correction.

## align-all

| method | global median AbsRel | 60–75° median | 75–90° median | calls/image |
|---|---:|---:|---:|---:|
| baseline | 0.4892 | 0.2377 | 0.3329 | 1 |
| two_pole_tangent | 0.6190 | 0.1766 | 0.2040 | 3 |
| mono360_20view | 1.0420 | 0.1969 | 0.2092 | 20 |

## align-equatorial

| method | global median AbsRel | 60–75° median | 75–90° median | calls/image |
|---|---:|---:|---:|---:|
| baseline | 0.3136 | 0.3428 | 0.4371 | 1 |
| two_pole_tangent | 0.2643 | 0.2442 | 0.2719 | 3 |
| mono360_20view | 0.3650 | 0.2380 | 0.2897 | 20 |
