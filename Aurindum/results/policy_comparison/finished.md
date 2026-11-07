# Finished: policy comparison (core_loo vs all_loo vs all_in)

Completed 2026-11-07. Offline experiment from the existing capture-fault study files (24 files, 4 models x 6 sets); no model was run
and no existing result, policy file or figure was changed. All outputs are in `results/policy_comparison/`.

| file | content |
|---|---|
| `POLICY_COMPARISON.md` | tables: all cells, per model, per tested set, cells where the policies disagree |
| `policy_comparison.json` | the 216 cells (model, fault, tested set) with the chosen fix and median change per policy |
| `scripts/policy_comparison.py`, `tests/test_policy_comparison.py` | code and tests (2 pass) |

Policies: `core_loo` = headline (trained on the other core sets; Stanford and NYC never train); `all_loo` = trained on every other
set including Stanford and NYC; `all_in` = trained on all sets including the tested one (in-sample, optimistic, not held out).

Result (216 cells; improved / worse = change below -1% / above +1%):

| policy | fix applied | improved | worse | mean change |
|---|---:|---:|---:|---:|
| core_loo | 76 | 57 | 13 | -6.16% |
| all_loo | 78 | 63 | 11 | -6.03% |
| all_in | 78 | 66 | 8 | -7.09% |

* Adding the external sets to the training changes 19 of 216 choices and does not improve the mean held-out change (-6.03% vs -6.16%).
* It helps where the extra sets show a fix is safe (DA360 tilt, MiDaS vfov) and hurts DAP's cap fixes: Stanford's real caps push the
  choice from `plane_fill` / `inpaint_erp` to the other one (DAP nadir on Holo outdoor -70% -> -21.5%, DAP vfov on Stanford -61% -> -27%).
* The 144 core-only cells of the earlier report are the 4 core sets x 4 models x 9 faults of this table: 52 applied (same as reported).
* Faults are scored one at a time; the combined pipeline was not rerun under `all_loo`.
