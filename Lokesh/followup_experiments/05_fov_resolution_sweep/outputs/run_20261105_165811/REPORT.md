# Experiment 5 — FOV and tangent resolution sweep

This probes how view geometry and sampling density affect inference-time polar correction.
It is DAC-motivated, but uses the current MiDaS perspective wrapper; it is not a DAC model reproduction.

## align-all

| config | FOV | size | median AbsRel (75–90°) | polar coverage | calls/image |
|---|---:|---:|---:|---:|---:|
| fov70_size256 | 70° | 256² | 0.1402 | 100.0% | 3 |
| fov70_size384 | 70° | 384² | 0.1404 | 100.0% | 3 |
| fov70_size512 | 70° | 512² | 0.1400 | 100.0% | 3 |
| fov90_size256 | 90° | 256² | 0.1041 | 100.0% | 3 |
| fov90_size384 | 90° | 384² | 0.1058 | 100.0% | 3 |
| fov90_size512 | 90° | 512² | 0.1092 | 100.0% | 3 |
| fov110_size256 | 110° | 256² | 0.0963 | 100.0% | 3 |
| fov110_size384 | 110° | 384² | 0.0950 | 100.0% | 3 |
| fov110_size512 | 110° | 512² | 0.0949 | 100.0% | 3 |
| fov130_size256 | 130° | 256² | 0.0941 | 100.0% | 3 |
| fov130_size384 | 130° | 384² | 0.0919 | 100.0% | 3 |
| fov130_size512 | 130° | 512² | 0.0915 | 100.0% | 3 |

## align-equatorial

| config | FOV | size | median AbsRel (75–90°) | polar coverage | calls/image |
|---|---:|---:|---:|---:|---:|
| fov70_size256 | 70° | 256² | 0.3269 | 100.0% | 3 |
| fov70_size384 | 70° | 384² | 0.3273 | 100.0% | 3 |
| fov70_size512 | 70° | 512² | 0.3269 | 100.0% | 3 |
| fov90_size256 | 90° | 256² | 0.1778 | 100.0% | 3 |
| fov90_size384 | 90° | 384² | 0.1761 | 100.0% | 3 |
| fov90_size512 | 90° | 512² | 0.1807 | 100.0% | 3 |
| fov110_size256 | 110° | 256² | 0.1697 | 100.0% | 3 |
| fov110_size384 | 110° | 384² | 0.1659 | 100.0% | 3 |
| fov110_size512 | 110° | 512² | 0.1644 | 100.0% | 3 |
| fov130_size256 | 130° | 256² | 0.1698 | 100.0% | 3 |
| fov130_size384 | 130° | 384² | 0.1697 | 100.0% | 3 |
| fov130_size512 | 130° | 512² | 0.1702 | 100.0% | 3 |
