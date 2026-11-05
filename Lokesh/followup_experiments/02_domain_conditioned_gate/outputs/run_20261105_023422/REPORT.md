# Experiment 2 — Leave-one-environment-out domain gate

- Independent PanoX environments: 16
- Candidate thresholds: [30, 40, 45, 50, 60, 70]
- Gate fallback: baseline when best calibration gain < 0.50%

| Strategy | Mean AbsRel | Median AbsRel | Median relative gain |
|---|---:|---:|---:|
| LOEO-selected gate | 0.0336 | 0.0237 | +0.00% |
| Fixed 45° gate | 0.2040 | 0.1766 | -480.71% |
| Per-environment oracle (upper bound) | 0.1707 | 0.1718 | -393.99% |

## Fold decisions

| Held-out environment | Selected threshold | Train environments |
|---|---:|---|
| ClothingStore_0002 | baseline | ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0028 | baseline | ClothingStore_0002, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0033 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0067 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0079 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0082 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0092 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0127 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0128 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0141 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0151 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0164 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0168 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0183, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0183 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0186, ClothingStore_0187 |
| ClothingStore_0186 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0187 |
| ClothingStore_0187 | baseline | ClothingStore_0002, ClothingStore_0028, ClothingStore_0033, ClothingStore_0067, ClothingStore_0079, ClothingStore_0082, ClothingStore_0092, ClothingStore_0127, ClothingStore_0128, ClothingStore_0141, ClothingStore_0151, ClothingStore_0164, ClothingStore_0168, ClothingStore_0183, ClothingStore_0186 |

Oracle is diagnostic only and never used as a deployable gate. All frames from one environment
remain in the same fold; no frame-level random split is used.
