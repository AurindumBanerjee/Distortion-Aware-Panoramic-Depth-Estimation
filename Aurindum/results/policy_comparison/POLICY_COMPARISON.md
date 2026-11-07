# Policy comparison (offline, from the capture-fault study files)

`core_loo`: fixes chosen on the other core sets only (headline, external sets never train). `all_loo`: chosen on every other set incl. Stanford2D3D and NYC. `all_in`: chosen on all sets incl. the tested one (in-sample, optimistic, not held out). A cell is one (model, fault, tested set); its value is the median per-frame change of the fault metric when the chosen fix is applied (0 = no fix). Improved / worse: change below -1% / above +1%. Faults are scored one at a time; the combined pipeline is not rerun here.

## All cells

| policy | cells | fix applied | improved | worse | mean change (%) | summed gain | summed loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| core_loo | 216 | 76 | 57 | 13 | -6.16 | 1423 | 93 |
| all_loo | 216 | 78 | 63 | 11 | -6.03 | 1389 | 86 |
| all_in | 216 | 78 | 66 | 8 | -7.09 | 1573 | 41 |

## Per model

| model | core_loo: applied / improved / worse / mean % | all_loo: applied / improved / worse / mean % | all_in: applied / improved / worse / mean % |
|---|---|---|---|
| midas | 16 / 8 / 4 / -0.65 | 18 / 11 / 4 / -1.84 | 18 / 12 / 3 / -2.55 |
| dap | 30 / 29 / 1 / -17.21 | 30 / 29 / 1 / -15.68 | 30 / 29 / 1 / -17.92 |
| da360 | 8 / 6 / 2 / -1.39 | 12 / 11 / 1 / -1.69 | 12 / 11 / 1 / -1.69 |
| da2 | 22 / 14 / 6 / -5.38 | 18 / 12 / 5 / -4.92 | 18 / 14 / 3 / -6.20 |

## Per tested set

| set | core_loo: applied / improved / worse / mean % | all_loo: applied / improved / worse / mean % | all_in: applied / improved / worse / mean % |
|---|---|---|---|
| s3 | 12 / 9 / 1 / -6.76 | 13 / 10 / 1 / -6.88 | 13 / 10 / 1 / -8.11 |
| panox | 14 / 10 / 3 / -5.13 | 12 / 11 / 1 / -6.49 | 13 / 12 / 1 / -7.24 |
| holo_in | 13 / 11 / 1 / -5.25 | 13 / 12 / 1 / -5.35 | 13 / 12 / 1 / -5.35 |
| holo_out | 13 / 9 / 3 / -3.75 | 14 / 11 / 2 / -3.10 | 13 / 11 / 1 / -4.93 |
| stanford | 12 / 9 / 2 / -9.07 | 14 / 10 / 3 / -7.48 | 13 / 10 / 2 / -8.72 |
| nyc | 12 / 9 / 3 / -6.98 | 12 / 9 / 3 / -6.92 | 13 / 11 / 2 / -8.19 |

## Cells where core_loo and all_loo choose differently

| model | fault | tested | core_loo | all_loo | all_in |
|---|---|---|---|---|---|
| midas | vfov | panox | none | inpaint_tangent (-42.6%) | inpaint_tangent (-42.6%) |
| midas | nadir | holo_in | plane_fill (+0.2%) | none | none |
| midas | nadir | holo_out | plane_fill (+11.6%) | none | none |
| midas | vfov | holo_out | none | inpaint_tangent (-11.4%) | inpaint_tangent (-11.4%) |
| midas | nadir | stanford | none | plane_fill (+11.9%) | none |
| midas | vfov | stanford | none | inpaint_tangent (-10.6%) | inpaint_tangent (-10.6%) |
| dap | nadir | holo_out | plane_fill (-70.0%) | inpaint_erp (-21.5%) | plane_fill (-70.0%) |
| dap | vfov | stanford | inpaint_erp (-61.0%) | plane_fill (-26.6%) | inpaint_erp (-61.0%) |
| da360 | tilt | s3 | none | relevel_known (-4.1%) | relevel_known (-4.1%) |
| da360 | jpeg | panox | bilateral (+1.0%) | none | none |
| da360 | tilt | holo_in | none | relevel_known (-3.2%) | relevel_known (-3.2%) |
| da360 | tilt | holo_out | none | relevel_known (-2.3%) | relevel_known (-2.3%) |
| da360 | tilt | stanford | none | relevel_known (-4.0%) | relevel_known (-4.0%) |
| da360 | tilt | nyc | none | relevel_known (-1.8%) | relevel_known (-1.8%) |
| da2 | tilt | panox | relevel_known (-0.9%) | none | none |
| da2 | jpeg | panox | bilateral (+6.2%) | none | none |
| da2 | tilt | stanford | relevel_known (-27.2%) | none | none |
| da2 | nadir | stanford | plane_fill (-80.3%) | inpaint_erp (-81.6%) | plane_fill (-80.3%) |
| da2 | yawblur | nyc | wiener (-4.3%) | none | wiener (-4.3%) |
