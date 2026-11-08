# Same-domain policy experiment

Clusters (Stanford: room; NYC: 20 consecutive ids, an assumed grouping) are split into two folds. `in_domain`: fixes chosen on the other fold of the same dataset. `core`: fixes chosen on the four core sets (the headline policy). Both are scored on the held-out fold, one fault at a time; a cell is (model, fault, fold). Improved / worse: change below -1% / above +1%. Stanford's real black caps overlap the simulated nadir / vfov faults, so those two faults are weakly informative there.

| set | model | frames | clusters | core: applied / improved / worse / mean % | in_domain: applied / improved / worse / mean % |
|---|---|---:|---:|---|---|
| stanford | midas | 150 | 63 | 4 / 0 / 1 / +0.05 | 2 / 2 / 0 / -1.30 |
| stanford | dap | 150 | 63 | 10 / 10 / 0 / -18.66 | 10 / 10 / 0 / -18.66 |
| stanford | da360 | 150 | 63 | 2 / 2 / 0 / -0.66 | 8 / 7 / 0 / -1.99 |
| stanford | da2 | 150 | 63 | 8 / 6 / 0 / -14.78 | 6 / 6 / 0 / -15.01 |
| nyc | midas | 147 | 82 | 4 / 4 / 0 / -1.12 | 8 / 8 / 0 / -6.27 |
| nyc | dap | 147 | 82 | 10 / 10 / 0 / -26.89 | 10 / 10 / 0 / -29.08 |
| nyc | da360 | 147 | 82 | 2 / 2 / 0 / -1.83 | 4 / 3 / 0 / -1.89 |
| nyc | da2 | 147 | 82 | 8 / 2 / 6 / +2.29 | 3 / 3 / 0 / -0.51 |

## Cells where the two policies choose differently

| set | model | fault | fold | core | in_domain |
|---|---|---|---:|---|---|
| stanford | midas | tilt | 0 | relevel_known (-0.3%) | none |
| stanford | midas | vfov | 0 | none | inpaint_tangent (-9.6%) |
| stanford | midas | yawblur | 0 | wiener (+0.3%) | none |
| stanford | midas | tilt | 1 | relevel_known (+1.0%) | none |
| stanford | midas | vfov | 1 | none | inpaint_tangent (-13.8%) |
| stanford | midas | yawblur | 1 | wiener (-0.2%) | none |
| stanford | da360 | tilt | 0 | none | relevel_known (-9.6%) |
| stanford | da360 | tilt | 1 | none | relevel_known (-9.4%) |
| stanford | da360 | nadir | 1 | none | inpaint_erp (-1.9%) |
| stanford | da360 | seam | 1 | none | gain_match (-1.3%) |
| stanford | da360 | vignette | 1 | none | flatfield (-0.2%) |
| stanford | da360 | jpeg | 1 | none | bilateral (-1.6%) |
| stanford | da2 | nadir | 0 | plane_fill (-82.3%) | inpaint_tangent (-85.3%) |
| stanford | da2 | yawblur | 0 | wiener (-0.9%) | none |
| stanford | da2 | nadir | 1 | plane_fill (-82.2%) | inpaint_tangent (-83.9%) |
| stanford | da2 | yawblur | 1 | wiener (+0.3%) | none |
| nyc | midas | nadir | 0 | none | plane_fill (-11.8%) |
| nyc | midas | vfov | 0 | none | inpaint_erp (-32.1%) |
| nyc | midas | nadir | 1 | none | plane_fill (-9.6%) |
| nyc | midas | vfov | 1 | none | inpaint_erp (-39.2%) |
| nyc | dap | vfov | 0 | inpaint_erp (-33.9%) | plane_fill (-55.0%) |
| nyc | dap | vfov | 1 | inpaint_erp (-37.9%) | plane_fill (-56.1%) |
| nyc | da360 | tilt | 1 | none | relevel_known (-1.2%) |
| nyc | da360 | jpeg | 1 | none | bilateral (+0.2%) |
| nyc | da2 | tilt | 0 | relevel_known (+11.6%) | none |
| nyc | da2 | nadir | 0 | plane_fill (+5.7%) | none |
| nyc | da2 | vfov | 0 | inpaint_erp (+7.2%) | none |
| nyc | da2 | yawblur | 0 | wiener (-8.9%) | none |
| nyc | da2 | noise | 0 | none | denoise (-3.0%) |
| nyc | da2 | tilt | 1 | relevel_known (+15.8%) | none |
| nyc | da2 | nadir | 1 | plane_fill (+6.3%) | none |
| nyc | da2 | vfov | 1 | inpaint_erp (+5.4%) | none |
| nyc | da2 | noise | 1 | none | denoise (-4.2%) |
