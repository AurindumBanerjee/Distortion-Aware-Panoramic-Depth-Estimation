# End-to-end: stricter do-no-harm rules on the external sets

Same frames (matched by id), same code; only the policy rule differs. Rule `s<G>w<W>`: a fix needs a median gain of G% and W% of training frames improved, chosen on the four core sets (Stanford2D3D and NYC never train). Cells: median per-frame change of AbsRel (headline / strict).

## Rule s5w70

| set | model | frames | policy differs in | tilt | nadir | vfov | yawblur | jpeg | nadir+jpeg |
|---|---|---:|---|---|---|---|---|---|---|
| stanford | midas | 100 | tilt: relevel_known->none | +1.3% / +0.0% | +0.0% / +0.0% | +0.0% / +0.0% | +0.4% / +0.4% | +0.0% / +0.0% | +0.0% / +0.0% |
| stanford | dap | 100 | - | -32.0% / -32.0% | -40.9% / -40.9% | -59.7% / -59.7% | -33.6% / -33.6% | -49.2% / -49.2% | -69.0% / -69.0% |
| stanford | da360 | 100 | - | +0.0% / +0.0% | +0.0% / +0.0% | +0.0% / +0.0% | -7.2% / -7.2% | +0.0% / +0.0% | +0.0% / +0.0% |
| stanford | da2 | 100 | nadir: plane_fill->inpaint_erp, tilt: relevel_known->none, yawblur: wiener->none | -29.1% / +0.0% | -78.8% / -78.8% | -25.9% / -25.9% | -3.6% / -2.3% | +8.7% / +8.7% | +2.9% / +2.9% |
| nyc | midas | 147 | tilt: relevel_known->none | -2.8% / +0.0% | +0.0% / +0.0% | +0.0% / +0.0% | -7.6% / -7.6% | +0.0% / +0.0% | +0.0% / +0.0% |
| nyc | dap | 147 | - | -47.4% / -47.4% | -89.3% / -89.3% | -36.4% / -36.4% | -60.4% / -60.4% | -7.9% / -7.9% | +1.3% / +1.3% |
| nyc | da360 | 147 | - | +0.0% / +0.0% | +0.0% / +0.0% | +0.0% / +0.0% | -17.5% / -17.5% | +0.0% / +0.0% | +0.0% / +0.0% |
| nyc | da2 | 147 | nadir: plane_fill->inpaint_erp, tilt: relevel_known->none, yawblur: wiener->none | +13.7% / +0.0% | +6.3% / +3.0% | +6.1% / +6.1% | -4.5% / +0.0% | +0.0% / +0.0% | +0.0% / +0.0% |

Over 48 (model, set, scenario) cells: harmful scenarios 7 (headline) vs 5 (strict); mean change -13.79% vs -13.39%.

