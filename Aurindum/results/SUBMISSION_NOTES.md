# Submission runs: notes (9 Nov 2026)

## What ran

`scripts/run_submission.sh`, final version (md5 `5ff3de57`), two shells on the GPU server plus the CPU analysis:

| shell | stages | started | finished | failed steps |
|---|---|---|---|---|
| A | `da2both` (DA2 median fit at N=100 on the core sets, rotation and dilation sweeps on five sets) | 8 Nov 22:41 | 9 Nov 00:21 | 0 |
| B | `diag` (13 nadir + JPEG ladders), `strict` (5% / 70% rule end to end, Stanford2D3D N=100, NYC N=147, four models) | 8 Nov 22:41 | 9 Nov 03:55 | 0 |
| C | `analysis` (CPU: threshold sweep, DA2 protocols, strict summary, policy stability, final summary, external report, figures) | 9 Nov 04:10 | 9 Nov 04:14 | 0 |
| D | `study100` (100-frame capture-fault studies, 4 models x 4 core sets, 16 files) then `analysis` | 9 Nov 09:09 | 9 Nov 14:08 | 0 |

Stage D was run after the first three, on its own (`STAGES="study100 analysis"`), because it was not in the default stage list of the first launch.

## What failed or went wrong, and what was done

- A first launch used an older copy of `run_submission.sh` (the laptop file had not been replaced). It was stopped after 5 minutes with nothing finished, the final script was copied (md5 checked on both machines) and restarted.
- A `DRY=1` check wrote a stale `finished_submission_da2both_diag_strict_analysis.md` on the server; it was moved to the server's `to_delete/` so that it could not pass for a finished run.
- `scripts/check_submission.py` first reported 123 false problems because cells are nested (`cell -> raw -> all`); the finite-value check was made recursive.
- The laptop Python has no pytest; the suite runs on the server (134 passed).

## Checks

- `python scripts/check_submission.py`: submission files complete (da2m core rows 100/100/100/71; sweeps n_frames 80 (71 Holo outdoor); 13 diag files with expected rows; 8 strict files with ids a subset of the headline files, no external set in `trained_on`).
- Headline files unchanged: `git diff` is empty for `results/correction_{midas,dap,da360,da2}_*.json`, `results/external/*`, `results/correction_policy.json`; changed are only `results/correction_da2m_{s3,panox,holo_in,holo_out}.json/.md` (40 to 100 frames, intended), `FINAL_ablations.md` (da2m rows only) and regenerated figures.
- `THRESHOLDS.md` regenerated identical to HEAD.

## Findings

1. **Nadir + JPEG, DAP on NYC** (`results/diag/NADIR_JPEG_dap_nyc.md`, 147 frames, region metric, bootstrap CI over frames):
   - headline pipeline (`pipe_photometric:plane_fill`, raw metres) +1.3% [-2.7, +3.5]: reproduces the headline +1.3%.
   - true mask, raw metres: -3.0% [-8.1, -1.3]; after a median scale fit: -18.6% [-26.3, -11.5]. Bottom only, true mask: -89.6% [-91.3, -82.1].
   - median predicted / true depth in the cap after the true-mask plane fill: 0.725 with JPEG, 0.983 without (raw 0.679 and 0.470).
   - detected mask after the scale fit: -6.4% [-10.3, -3.3] (detected in 88% of frames, edge deviation median 0.83 deg); order of steps +1.3% vs +0.5% (raw) and -4.5% vs -5.7% (scale fit), deblocking -21.9% [-30.5, -18.4] vs -18.6%, margin -4.8% vs -6.4%: no measurable effect.
   - side effect in raw metres: ring +13.3% [+10.0, +16.5], outside +5.2% [+4.0, +6.0], whole panorama +1.6% [+0.2, +2.9].
   - supported: a scale offset that persists after the fill, plus the detected mask; not supported: order, deblocking, margin. Not isolated: why the scale offset arises. The offset does not rank datasets (Holo indoor: ratio 0.497 after fill, true-mask gain -22.5% in raw metres).
   - The premise that MiDaS, DA360 and DA2 do gain on NYC nadir + JPEG is not supported: their headline change is +0.0% (no fix applied; 45% detection at 256x512 on 40 frames).
2. **Strict rule 5% / 70% end to end** (`results/threshold_sweep/E2E_STRICT.md`): harmful cells 7 (headline) vs 5 (strict) of 48; mean change -13.79% vs -13.39% (0.40 points given up). Per set: Stanford2D3D 3 vs 2 and -17.32% vs -16.10%; NYC 4 vs 3 and -10.27% vs -10.68%. Offline prediction (5 to 2; -8.03% to -7.90%) holds in direction and for the two cells that stay harmful (DA2 NYC bottom, FOV); the end-to-end count also contains cap-path cells outside the offline count (DA2 Stanford JPEG +8.7%, bottom + JPEG +2.9%; DAP NYC bottom + JPEG +1.3%) and DA2 shake on Stanford2D3D is not harmful end to end (-3.6%).
3. **DA2 under both protocols** (`results/DA2_PROTOCOLS.md`): NYC clean 0.638 vs 0.205; NYC tilt +13.7% vs -22.8%, bottom +6.3% vs -26.0%; Holo outdoor (71 frames) tilt +19.4% vs +5.8%, bottom +0.5% vs -51.6%; Stanford2D3D agrees except JPEG (+8.0% vs +19.5%, cap fix on real caps). Sweeps: rotation NYC onset 50 deg under lsq, none under median; dilation Holo outdoor onset 80 deg vs none; dilation NYC onset 55 deg under median only (negative dE); sign of the 75-90 deg dE changes in 2 of 10 sweeps.

## Decisions taken

- Appendix B table (offline) left as is: `THRESHOLDS.md` is identical to the committed version.
- Appendix C table rebuilt from the JSON on all six sets with matched frame ids (the earlier table had four rows and used 40-frame core data).
- Figure `fig_diag_nadir_jpeg` placed in Appendix A, as requested; it is cited from Appendix D.
- `make_figures.py` outputs do not depend on the new data (it reads no `da2m` files); the report's existing `fig_correction_gain` and `fig_fault_cost` were kept (same data, higher resolution than the regenerated copies).
- Appendix E (policy stability) added after study100 finished. Main text: one clause in Limitations points to it. Main text: only the resolution paragraph (diagnosis sentence replaces the 40-frame fill-order numbers), the Holo outdoor tilt numbers (40 to 71 frames) and one Limitations clause (100 core frames) changed; main text still ends on page 8; report is 17 pages.
- Table 7 (Appendix D) floats to the last page.

## Provenance of numbers in new report text

| report location | number | file | row / key | how computed |
|---|---|---|---|---|
| Results, resolution paragraph; App. D | 88% detection | `results/diag/nadir_jpeg_dap_nyc.json` | `rows[*]['nadir+jpeg']['info']['detected']=='nadir'` | share of 147 frames |
| same; Table 7 | -3.0% [-8.1, -1.3] | same | `['nadir+jpeg']['none']['oracle:plane_fill']['region']` vs `['raw']['region']` | median of (v-raw)/raw over frames; bootstrap B=2000, seed 0 (`nadir_jpeg_diagnosis.summarize`) |
| same; Table 7 | -18.6% [-26.3, -11.5] | same | same with `['align-all']` | same |
| same; Table 7 | -6.4% [-10.3, -3.3] | same | `detected:plane_fill`, `align-all` | same |
| Results; App. D | 0.725 / 0.983 | same | `['nadir+jpeg'|'nadir']['none']['oracle:plane_fill']['bias']` | median over frames |
| Results; App. D | ring +13.3% [+10.0, +16.5] | same | `oracle:plane_fill`, metric `ring`, `none` | same bootstrap |
| App. D text | outside +5.2%, whole +1.6% | same | metrics `outside`, `all` | same |
| App. D, other models | -3.7%, +6.1%, +2.0%, -32.6%; pipeline +23.2%, +3.4%, +2.2%, +8.6% | `results/diag/nadir_jpeg_{midas,da360,da2,da2m}_nyc.json` | `align-all`, `oracle:` / `pipe_photometric:plane_fill`, region | same |
| App. B table | 3/2, -17.32/-16.10 (Stanford2D3D); 4/3, -10.27/-10.68 (NYC); 7/5, -13.79/-13.39 | `results/threshold_sweep/e2e_s5w70/correction_<m>_<set>.json` and `results/external/correction_<m>_<set>.json` | per (model, scenario): median per-frame change over matched ids (`policy_e2e_compare.compare`) | harmful: change > +1%; mean over 24 cells per set (`strict_compare.summarize`) |
| App. B text | 5 to 2; -8.03% to -7.90% | `results/threshold_sweep/thresholds.json` | `0.02|0.6|0` and `0.05|0.7|0`, `external` | `harmful`, `mean_change` |
| App. C table | clean, per-scenario changes, frame counts | `results/correction_da2_<core>.json`, `results/correction_da2m_<core>.json`, `results/external/correction_da2{,m}_{stanford,nyc}.json` | `rows[*]['clean']['raw']['all']`; `final_summary.cell` per scenario | matched ids (`da2_protocol_report.matched`), median per-frame change |
| App. C sweep table | onsets and dE | `results/sweep_{rotation,dilation}_da2{,m}_<set>.json` | `summary.onset_global`; mean of `summary.de_global.mean` over centres >= 75 | `da2_protocol_report.sweep_row` |
| Results, alignment paragraph | +19.4% / +5.8% (71 frames) | `results/correction_da2_holo_out.json`, `results/correction_da2m_holo_out.json` | `rows[*]['tilt']` raw / fixed `all` | matched ids, median change |
| Results, alignment paragraph | 8 of 30 policy choices differ | `results/DA2_PROTOCOLS.md` section 3 | per dataset, lsq vs median policy dicts | counted by hand (3+2+1+0+1+1) |
| App. E, Tables 8 and 9 | 137 of 144 same; applied 52/52; 7 differing cells | `results/policy_stability/POLICY_STABILITY.md` (from `study_<m>_<core>.json` and `policy_stability/study_s100_<m>_<core>.json`) | `scripts/policy_stability.py` | leave-one-dataset-out choice, headline rule; the 7 cells transcribed by hand into Table 9 |

Spot checks recomputed from the raw JSON in this run: NYC clean 0.205 / 0.638 (`results/external/correction_da2m_nyc.json`, `correction_da2_nyc.json`, 147 rows); detection 88% (147 frames); NYC rotation onset 50 (lsq) / none (median), 80 frames each; Holo outdoor tilt +19.4% / +5.8% (71 matched ids); Stanford DA2 JPEG +8.7% headline and strict (100 matched ids).

## Unsure / to verify

1. Appendix C "8 of 30 choices" was counted by hand from the policy dicts in `DA2_PROTOCOLS.md`, not by script.
2. The policy for the median protocol was learned from 40-frame `study_da2m_*` files; the 100-frame stability check covers the four lsq models only, not da2m.
3. NYC cluster blocks (20 consecutive ids) remain an assumed grouping.
4. The scale-offset explanation rests on in-cap bias and the raw-vs-scale-fit contrast for one model on one dataset; it does not rank datasets.
