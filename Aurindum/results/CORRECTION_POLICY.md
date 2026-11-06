# Capture-aware correction: learned policy and held-out test

Fix per (model, fault) chosen on the other datasets (leave-one-dataset-out) and scored on the held-out one. A fix is kept only if its median change vs no fix is below -2% and it improves at least 60% of training frames; otherwise no fix ('none').

Columns per held-out dataset: chosen fix · median change vs uncorrected · frames improved · median recovery (frames hurt >= 5%). The metric is the affected region for missing-pixel faults, else the whole panorama. `relevel_known` and `wiener` need sensor data (IMU / gyro).

## da2

| fault | final policy | holo_in | holo_out | panox | s3 |
|---|---|---|---|---|---|
| tilt | relevel_known | none | relevel_known · +17% · 28% · 100% | relevel_known · -1% · 50% · 89% | none |
| nadir | plane_fill | plane_fill · -8% · 57% · 77% | plane_fill · +0% · 48% · 12% | inpaint_erp · -46% · 70% · 83% | inpaint_erp · -65% · 95% · 84% |
| vfov | inpaint_erp | inpaint_erp · -22% · 80% · 62% | inpaint_erp · -7% · 65% · 75% | inpaint_erp · -3% · 52% · -25% | inpaint_erp · -40% · 95% · 63% |
| seam | none | none | none | none | none |
| parallax | none | none | none | none | none |
| vignette | none | none | none | none | none |
| yawblur | wiener | wiener · -1% · 52% · 13% | wiener · -6% · 57% · 112% | none | wiener · -4% · 60% · 51% |
| noise | none | none | none | none | none |
| jpeg | none | none | none | bilateral · +6% · 25% · -13% | none |

## da360

| fault | final policy | holo_in | holo_out | panox | s3 |
|---|---|---|---|---|---|
| tilt | none | none | none | relevel_known · +3% · 40% · 23% | none |
| nadir | none | none | none | none | none |
| vfov | none | none | none | none | none |
| seam | none | none | none | none | none |
| parallax | none | none | none | none | none |
| vignette | none | none | none | none | none |
| yawblur | wiener | wiener · -3% · 57% · 44% | wiener · -9% · 70% · 73% | wiener · -17% · 75% · 65% | wiener · -24% · 85% · 57% |
| noise | none | none | none | none | none |
| jpeg | none | none | none | bilateral · +1% · 48% · -5% | none |

## dap

| fault | final policy | holo_in | holo_out | panox | s3 |
|---|---|---|---|---|---|
| tilt | relevel_known | relevel_known · -24% · 88% · 92% | relevel_known · +6% · 32% · -17% | relevel_known · -24% · 72% · 105% | relevel_known · -71% · 98% · 96% |
| nadir | plane_fill | plane_fill · -27% · 92% · 34% | plane_fill · -70% · 100% · 101% | plane_fill · -24% · 80% · 85% | plane_fill · -5% · 68% · 6% |
| vfov | inpaint_erp | inpaint_erp · -59% · 98% · 72% | inpaint_erp · -33% · 90% · 50% | inpaint_erp · -44% · 92% · 60% | plane_fill · -24% · 100% · 25% |
| seam | none | none | none | none | none |
| parallax | none | none | none | none | none |
| vignette | none | none | none | none | none |
| yawblur | wiener | wiener · -29% · 80% · 85% | wiener · -10% · 92% · 54% | wiener · -19% · 90% · 89% | wiener · -12% · 65% · 57% |
| noise | none | none | none | none | none |
| jpeg | bilateral | bilateral · -9% · 85% · 12% | bilateral · -8% · 65% · 47% | bilateral · -4% · 72% · 13% | bilateral · -7% · 75% · 14% |

## midas

| fault | final policy | holo_in | holo_out | panox | s3 |
|---|---|---|---|---|---|
| tilt | relevel_known | relevel_known · -7% · 72% · 107% | relevel_known · -7% · 78% · 36% | relevel_known · -9% · 75% · 87% | relevel_known · -0% · 50% · 114% |
| nadir | none | plane_fill · +0% · 48% · 6% | plane_fill · +12% · 48% · 125% | none | none |
| vfov | none | inpaint_tangent · +6% · 32% · -24% | none | none | inpaint_tangent · +10% · 30% · 87% |
| seam | none | none | none | none | none |
| parallax | none | none | none | none | none |
| vignette | none | none | none | none | none |
| yawblur | wiener | wiener · -6% · 70% · 97% | wiener · -19% · 98% · 81% | wiener · -5% · 57% · 75% | wiener · -1% · 60% · 70% |
| noise | none | none | none | none | none |
| jpeg | none | none | none | none | none |

## Overall (held-out)

- (model, fault, dataset) cells: 144; a fix was applied in 52, left off in 92.
- Of the applied cells, 42 improved the median, 10 made it worse: da2/tilt/holo_out (+17%), da2/nadir/holo_out (+0%), da2/jpeg/panox (+6%), da360/tilt/panox (+3%), da360/jpeg/panox (+1%), dap/tilt/holo_out (+6%), midas/nadir/holo_in (+0%), midas/nadir/holo_out (+12%), midas/vfov/holo_in (+6%), midas/vfov/s3 (+10%).
- Median change over applied cells: -8%.

