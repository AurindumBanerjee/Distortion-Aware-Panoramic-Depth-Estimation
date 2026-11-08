# Stricter do-no-harm rules: offline threshold test

Choice always made on core datasets only. 'core LOO' = policy learned on the other three core sets, scored on the held-out core set; 'external' = policy learned on all four core sets, scored on Stanford2D3D and NYC (40-frame study files). Cells are (model, fault, dataset); a cell counts as harmful if an applied fix has median change above +1%. Mean change counts 'no fix' as 0. Models: da2, da2m, da360, dap, midas; pooled totals leave out da2m (DA2 under the median fit, core sets only) so that DA2 is not counted twice. Headline rule: min_gain 2%, min_win 60%, no per-dataset consistency requirement.

| min_gain | min_win | every set better | core: applied | core: harmful | core: mean change | external: applied | external: harmful | external: mean change | core mean change minus headline (+ = less gain) |
|---:|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 0% | 50% | no | 87 | 14 | -5.24% | 46 | 9 | -8.59% | -0.02 pts |
| 0% | 50% | yes | 52 | 6 | -4.68% | 22 | 4 | -6.83% | +0.54 pts |
| 0% | 60% | no | 59 | 10 | -5.19% | 26 | 5 | -8.03% | +0.03 pts |
| 0% | 60% | yes | 49 | 6 | -4.56% | 20 | 4 | -6.82% | +0.66 pts |
| 0% | 70% | no | 32 | 2 | -3.61% | 18 | 2 | -7.90% | +1.61 pts |
| 0% | 70% | yes | 31 | 2 | -3.44% | 16 | 2 | -6.79% | +1.78 pts |
| 0% | 80% | no | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 0% | 80% | yes | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 0% | 90% | no | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 0% | 90% | yes | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 2% | 50% | no | 60 | 9 | -4.82% | 32 | 6 | -8.65% | +0.41 pts |
| 2% | 50% | yes | 45 | 5 | -4.68% | 20 | 4 | -6.82% | +0.54 pts |
| 2% (headline) | 60% | no | 52 | 8 | -5.22% | 24 | 5 | -8.03% | +0.00 pts |
| 2% | 60% | yes | 44 | 5 | -4.58% | 20 | 4 | -6.82% | +0.64 pts |
| 2% | 70% | no | 32 | 2 | -3.61% | 18 | 2 | -7.90% | +1.61 pts |
| 2% | 70% | yes | 31 | 2 | -3.44% | 16 | 2 | -6.79% | +1.78 pts |
| 2% | 80% | no | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 2% | 80% | yes | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 2% | 90% | no | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 2% | 90% | yes | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 5% | 50% | no | 46 | 5 | -4.96% | 26 | 6 | -8.02% | +0.26 pts |
| 5% | 50% | yes | 38 | 2 | -4.43% | 20 | 4 | -6.82% | +0.79 pts |
| 5% | 60% | no | 46 | 5 | -5.07% | 24 | 5 | -8.03% | +0.15 pts |
| 5% | 60% | yes | 38 | 2 | -4.43% | 20 | 4 | -6.82% | +0.79 pts |
| 5% | 70% | no | 31 | 2 | -3.56% | 18 | 2 | -7.90% | +1.66 pts |
| 5% | 70% | yes | 30 | 2 | -3.40% | 16 | 2 | -6.79% | +1.83 pts |
| 5% | 80% | no | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 5% | 80% | yes | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 5% | 90% | no | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 5% | 90% | yes | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 10% | 50% | no | 30 | 5 | -3.82% | 14 | 2 | -7.44% | +1.40 pts |
| 10% | 50% | yes | 22 | 2 | -3.29% | 12 | 2 | -6.40% | +1.94 pts |
| 10% | 60% | no | 30 | 5 | -3.93% | 14 | 2 | -7.44% | +1.30 pts |
| 10% | 60% | yes | 22 | 2 | -3.29% | 12 | 2 | -6.40% | +1.94 pts |
| 10% | 70% | no | 22 | 2 | -3.06% | 14 | 2 | -7.50% | +2.16 pts |
| 10% | 70% | yes | 21 | 2 | -2.89% | 12 | 2 | -6.40% | +2.33 pts |
| 10% | 80% | no | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 10% | 80% | yes | 12 | 1 | -2.25% | 6 | 0 | -4.61% | +2.98 pts |
| 10% | 90% | no | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |
| 10% | 90% | yes | 5 | 0 | -1.15% | 2 | 0 | -1.39% | +4.07 pts |

## Pareto front on core LOO only (harmful cells against mean change; no rule beats these on both)

| min_gain | min_win | every set better | core harmful | core mean change | external harmful | external mean change |
|---:|---:|:---:|---:|---:|---:|---:|
| 10% | 90% | yes | 0 | -1.15% | 0 | -1.39% |
| 10% | 80% | yes | 1 | -2.25% | 0 | -4.61% |
| 5% | 60% | yes | 2 | -4.43% | 4 | -6.82% |
| 5% | 60% | no | 5 | -5.07% | 5 | -8.03% |
| 2% | 60% | no | 8 | -5.22% | 5 | -8.03% |
| 0% | 50% | no | 14 | -5.24% | 9 | -8.59% |

## External cells that are harmful under the headline rule

| model | dataset | fault | headline fix | change | 5/80 | 10/80 | 2/90 | 2/60+all | 5/70+all |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| da2 | stanford | yawblur | wiener | +2.8% | none | none | none | wiener +2.8% | none |
| da2 | nyc | tilt | relevel_known | +15.3% | none | none | none | none | none |
| da2 | nyc | nadir | plane_fill | +6.5% | none | none | none | inpaint_erp +2.9% | inpaint_erp +2.9% |
| da2 | nyc | vfov | inpaint_erp | +5.1% | none | none | none | inpaint_erp +5.1% | inpaint_erp +5.1% |
| midas | stanford | tilt | relevel_known | +2.0% | none | none | none | relevel_known +2.0% | none |

## Per model, headline

| model | core applied | core harmful | core mean | external applied | external harmful | external mean |
|---|---:|---:|---:|---:|---:|---:|
| da2 | 14 | 2 | -4.99% | 8 | 4 | -6.18% |
| da2m | 14 | 3 | -10.31% | 0 | 0 | n/a |
| da360 | 6 | 2 | -1.37% | 2 | 0 | -1.42% |
| dap | 20 | 1 | -13.81% | 10 | 0 | -24.01% |
| midas | 12 | 3 | -0.72% | 4 | 1 | -0.50% |

## Per model, 5% / 80% / every set better

| model | core applied | core harmful | core mean | external applied | external harmful | external mean |
|---|---:|---:|---:|---:|---:|---:|
| da2 | 1 | 0 | -0.07% | 0 | 0 | +0.00% |
| da2m | 4 | 2 | -1.92% | 0 | 0 | n/a |
| da360 | 0 | 0 | +0.00% | 0 | 0 | +0.00% |
| dap | 11 | 1 | -8.91% | 6 | 0 | -18.46% |
| midas | 0 | 0 | +0.00% | 0 | 0 | +0.00% |
