# Round 3, Part A: distortion analysis

Causal onset: first seen-latitude bin (sweep, content fixed per pixel) whose excess error is significant (cluster CI) and >= 10% of the equator-seen error. `None` = no measurable distortion effect: Part B then leaves this model unchanged.

| sweep tag | model | frames / clusters | causal onset (deg) | dE 75-90 [95% CI] | ratio 75-90 | dE 75-90 planar / non-planar |
|---|---|---:|---:|---:|---:|---:|
| da2_holo_in_all | da2 | 80 / 12 | None | 0.0012 [-0.0215, 0.0234] | 1.01 | -0.0860 / 0.0253 |
| da2_holo_out_all | da2 | 71 / 3 | None | -0.1224 [-0.1382, -0.1044] | 0.81 | -0.3369 / 0.0008 |
| da2_panox_all | da2 | 80 / 8 | None | -0.5343 [-1.2168, -0.1225] | 0.42 | -0.7973 / 0.1630 |
| da2_s3_calib | da2 | 120 / 86 | None | 0.0089 [0.0003, 0.0171] | 1.08 | 0.0128 / 0.0128 |
| da2_s3_eval | da2 | 80 / 61 | None | 0.0098 [0.0005, 0.0189] | 1.08 | 0.0111 / 0.0170 |
| da360_holo_in_all | da360 | 80 / 12 | None | 0.0077 [-0.0014, 0.0174] | 1.09 | -0.0166 / 0.0159 |
| da360_holo_out_all | da360 | 71 / 3 | None | 0.0251 [-0.0034, 0.0457] | 1.12 | 0.0025 / 0.0289 |
| da360_panox_all | da360 | 80 / 8 | 70.0 | 0.0744 [0.0078, 0.1748] | 1.91 | -0.0129 / 0.1772 |
| da360_s3_calib | da360 | 120 / 86 | None | -0.0047 [-0.0097, -0.0005] | 0.88 | -0.0175 / 0.0042 |
| da360_s3_eval | da360 | 80 / 61 | None | -0.0023 [-0.0094, 0.0069] | 0.94 | -0.0175 / 0.0079 |
| dap_holo_in_all | dap | 80 / 12 | None | -0.1155 [-0.1692, -0.0593] | 0.72 | -0.2786 / 0.0326 |
| dap_holo_out_all | dap | 71 / 3 | None | 0.0213 [-0.1742, 0.1291] | 1.05 | -0.1438 / 0.1295 |
| dap_panox_all | dap | 80 / 8 | None | -0.1960 [-0.2586, -0.1273] | 0.64 | -0.3639 / 0.1580 |
| dap_s3_calib | dap | 120 / 86 | None | -0.1141 [-0.1311, -0.0976] | 0.57 | -0.2071 / -0.0220 |
| dap_s3_eval | dap | 80 / 61 | None | -0.1129 [-0.1318, -0.0938] | 0.59 | -0.2180 / 0.0037 |
| midas_holo_in_all | midas_dpt_hybrid_384 | 80 / 12 | None | -0.0706 [-0.1080, -0.0376] | 0.82 | -0.2120 / 0.0272 |
| midas_holo_out_all | midas_dpt_hybrid_384 | 71 / 3 | None | -0.0810 [-0.1314, -0.0278] | 0.85 | -0.5411 / 0.0477 |
| midas_panox_all | midas_dpt_hybrid_384 | 80 / 8 | None | -0.0476 [-0.1145, 0.0161] | 0.89 | -0.2640 / 0.3151 |
| midas_s3_calib | midas_dpt_hybrid_384 | 120 / 86 | None | 0.0201 [0.0027, 0.0389] | 1.09 | -0.0642 / 0.0704 |
| midas_s3_eval | midas_dpt_hybrid_384 | 80 / 61 | None | 0.0230 [0.0003, 0.0434] | 1.09 | -0.0719 / 0.0719 |

Descriptive onset (plain ERP latitude profile; mixes distortion, content and protocol):

| profile tag | model | protocol | onset (deg) | AbsRel 0-15 | AbsRel 75-90 |
|---|---|---|---:|---:|---:|
| da2_holo_in_all | da2 | align-all | 80.0 | 0.1357 | 0.1906 |
| da2_holo_in_all | da2 | align-equatorial | 75.0 | 0.1309 | 0.2011 |
| da2_holo_out_all | da2 | align-all | 47.5 | 0.5509 | 0.7045 |
| da2_holo_out_all | da2 | align-equatorial | 45.0 | 0.5030 | 0.9442 |
| da2_panox_all | da2 | align-all | None | 0.2997 | 0.3019 |
| da2_panox_all | da2 | align-equatorial | None | 0.3028 | 0.3105 |
| da2_s3_calib | da2 | align-all | None | 0.1178 | 0.0656 |
| da2_s3_calib | da2 | align-equatorial | None | 0.1189 | 0.0941 |
| da2_s3_eval | da2 | align-all | None | 0.1179 | 0.0641 |
| da2_s3_eval | da2 | align-equatorial | None | 0.1065 | 0.0883 |
| da360_holo_in_all | da360 | align-all | None | 0.0908 | 0.0667 |
| da360_holo_in_all | da360 | align-equatorial | None | 0.0797 | 0.0916 |
| da360_holo_out_all | da360 | align-all | None | 0.2919 | 0.3024 |
| da360_holo_out_all | da360 | align-equatorial | 77.5 | 0.2225 | 0.4183 |
| da360_panox_all | da360 | align-all | None | 0.1748 | 0.0296 |
| da360_panox_all | da360 | align-equatorial | None | 0.1477 | 0.0675 |
| da360_s3_calib | da360 | align-all | None | 0.0325 | 0.0183 |
| da360_s3_calib | da360 | align-equatorial | None | 0.0311 | 0.0216 |
| da360_s3_eval | da360 | align-all | None | 0.0359 | 0.0179 |
| da360_s3_eval | da360 | align-equatorial | None | 0.0349 | 0.0361 |
| dap_holo_in_all | dap | none | None | 0.1720 | 0.1665 |
| dap_holo_in_all | dap | align-all | None | 0.1623 | 0.1225 |
| dap_holo_in_all | dap | align-equatorial | None | 0.1788 | 0.1990 |
| dap_holo_out_all | dap | none | None | 0.4466 | 1.4512 |
| dap_holo_out_all | dap | align-all | 82.5 | 0.3514 | 1.3832 |
| dap_holo_out_all | dap | align-equatorial | 82.5 | 0.3502 | 1.3984 |
| dap_panox_all | dap | none | None | 0.2888 | 0.2184 |
| dap_panox_all | dap | align-all | None | 0.2248 | 0.0707 |
| dap_panox_all | dap | align-equatorial | None | 0.1894 | 0.1424 |
| dap_s3_calib | dap | none | None | 0.0505 | 0.0320 |
| dap_s3_calib | dap | align-all | None | 0.0384 | 0.0233 |
| dap_s3_calib | dap | align-equatorial | None | 0.0375 | 0.0279 |
| dap_s3_eval | dap | none | None | 0.0480 | 0.0342 |
| dap_s3_eval | dap | align-all | None | 0.0370 | 0.0236 |
| dap_s3_eval | dap | align-equatorial | None | 0.0363 | 0.0254 |
| midas_holo_in_all | midas_dpt_hybrid_384 | align-all | None | 0.3807 | 0.2296 |
| midas_holo_in_all | midas_dpt_hybrid_384 | align-equatorial | 62.5 | 0.2942 | 0.4355 |
| midas_holo_out_all | midas_dpt_hybrid_384 | align-all | None | 0.4082 | 0.3844 |
| midas_holo_out_all | midas_dpt_hybrid_384 | align-equatorial | 80.0 | 0.3835 | 0.7190 |
| midas_panox_all | midas_dpt_hybrid_384 | align-all | None | 0.5072 | 0.1875 |
| midas_panox_all | midas_dpt_hybrid_384 | align-equatorial | None | 0.4500 | 0.3697 |
| midas_s3_calib | midas_dpt_hybrid_384 | align-all | None | 0.3477 | 0.2063 |
| midas_s3_calib | midas_dpt_hybrid_384 | align-equatorial | 45.0 | 0.2309 | 0.5357 |
| midas_s3_eval | midas_dpt_hybrid_384 | align-all | None | 0.3445 | 0.2211 |
| midas_s3_eval | midas_dpt_hybrid_384 | align-equatorial | 47.5 | 0.2433 | 0.6765 |
