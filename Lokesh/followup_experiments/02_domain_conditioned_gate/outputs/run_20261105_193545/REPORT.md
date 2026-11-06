# Experiment 2 — Leave-one-environment-out domain gate

- Independent PanoX environments: 8
- Candidate thresholds: [30, 40, 45, 50, 60, 70]
- Gate fallback: baseline when best calibration gain < 0.50%

| Strategy | Mean AbsRel | Median AbsRel | Median relative gain |
|---|---:|---:|---:|
| LOEO-selected gate | 0.0389 | 0.0282 | +0.00% |
| Fixed 45° gate | 0.0877 | 0.0621 | -55.44% |
| Per-environment oracle (upper bound) | 0.0720 | 0.0519 | -19.58% |

## Fold decisions

| Held-out environment | Selected threshold | Train environments |
|---|---:|---|
| ClothingStore | baseline | Diner50, FeudalJapan_Meshingun, ModularBakeryShop, Mountain_Environment_Set, SouthOfFrance, Warehouse, YellowParrot |
| Diner50 | baseline | ClothingStore, FeudalJapan_Meshingun, ModularBakeryShop, Mountain_Environment_Set, SouthOfFrance, Warehouse, YellowParrot |
| FeudalJapan_Meshingun | baseline | ClothingStore, Diner50, ModularBakeryShop, Mountain_Environment_Set, SouthOfFrance, Warehouse, YellowParrot |
| ModularBakeryShop | baseline | ClothingStore, Diner50, FeudalJapan_Meshingun, Mountain_Environment_Set, SouthOfFrance, Warehouse, YellowParrot |
| Mountain_Environment_Set | baseline | ClothingStore, Diner50, FeudalJapan_Meshingun, ModularBakeryShop, SouthOfFrance, Warehouse, YellowParrot |
| SouthOfFrance | baseline | ClothingStore, Diner50, FeudalJapan_Meshingun, ModularBakeryShop, Mountain_Environment_Set, Warehouse, YellowParrot |
| Warehouse | baseline | ClothingStore, Diner50, FeudalJapan_Meshingun, ModularBakeryShop, Mountain_Environment_Set, SouthOfFrance, YellowParrot |
| YellowParrot | baseline | ClothingStore, Diner50, FeudalJapan_Meshingun, ModularBakeryShop, Mountain_Environment_Set, SouthOfFrance, Warehouse |

Oracle is diagnostic only and never used as a deployable gate. All frames from one environment
remain in the same fold; no frame-level random split is used.
