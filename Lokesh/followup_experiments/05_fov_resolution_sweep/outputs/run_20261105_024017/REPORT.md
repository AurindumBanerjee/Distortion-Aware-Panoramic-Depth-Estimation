# Experiment 5 — FOV and tangent resolution sweep

This probes how view geometry and sampling density affect inference-time polar correction.
It is DAC-motivated, but uses the current MiDaS perspective wrapper; it is not a DAC model reproduction.

## align-all

| config | FOV | size | median AbsRel (75–90°) | polar coverage | calls/image |
|---|---:|---:|---:|---:|---:|
| fov70_size256 | 70° | 256² | 0.3197 | 100.0% | 3 |
| fov70_size384 | 70° | 384² | 0.3153 | 100.0% | 3 |
| fov70_size512 | 70° | 512² | 0.3160 | 100.0% | 3 |
| fov90_size256 | 90° | 256² | 0.2394 | 100.0% | 3 |
| fov90_size384 | 90° | 384² | 0.2533 | 100.0% | 3 |
| fov90_size512 | 90° | 512² | 0.2502 | 100.0% | 3 |
| fov110_size256 | 110° | 256² | 0.1988 | 100.0% | 3 |
| fov110_size384 | 110° | 384² | 0.2040 | 100.0% | 3 |
| fov110_size512 | 110° | 512² | 0.2037 | 100.0% | 3 |
| fov130_size256 | 130° | 256² | 0.1870 | 100.0% | 3 |
| fov130_size384 | 130° | 384² | 0.1804 | 100.0% | 3 |
| fov130_size512 | 130° | 512² | 0.1800 | 100.0% | 3 |

## align-equatorial

| config | FOV | size | median AbsRel (75–90°) | polar coverage | calls/image |
|---|---:|---:|---:|---:|---:|
| fov70_size256 | 70° | 256² | 0.4161 | 100.0% | 3 |
| fov70_size384 | 70° | 384² | 0.4158 | 100.0% | 3 |
| fov70_size512 | 70° | 512² | 0.4155 | 100.0% | 3 |
| fov90_size256 | 90° | 256² | 0.2920 | 100.0% | 3 |
| fov90_size384 | 90° | 384² | 0.2920 | 100.0% | 3 |
| fov90_size512 | 90° | 512² | 0.2889 | 100.0% | 3 |
| fov110_size256 | 110° | 256² | 0.2708 | 100.0% | 3 |
| fov110_size384 | 110° | 384² | 0.2719 | 100.0% | 3 |
| fov110_size512 | 110° | 512² | 0.2717 | 100.0% | 3 |
| fov130_size256 | 130° | 256² | 0.2628 | 100.0% | 3 |
| fov130_size384 | 130° | 384² | 0.2615 | 100.0% | 3 |
| fov130_size512 | 130° | 512² | 0.2693 | 100.0% | 3 |
