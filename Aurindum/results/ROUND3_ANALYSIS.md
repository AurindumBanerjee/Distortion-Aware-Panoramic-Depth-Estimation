# Round 3, Part A: distortion analysis

Causal onset: first seen-latitude bin (sweep, content fixed per pixel) whose excess error is significant (cluster CI) and >= 10% of the equator-seen error. `None` = no measurable distortion effect: Part B then leaves this model unchanged.

Modes: rotation (tips the scene), dilation (keeps up, magnifies), flip (same latitude upside down: dE is the orientation penalty). A distortion effect should appear in BOTH rotation and dilation; an orientation effect makes rotation dE negative, dilation ~0 and flip dE positive.

| sweep tag | mode | model | frames / clusters | onset (deg) | onset non-planar | dE 75-90 [95% CI] | ratio 75-90 | dE 75-90 planar / non-planar |
|---|---|---|---:|---:|---:|---:|---:|---:|
| da2_holo_in_all | rotation | da2 | 80 / 12 | None | n/a | 0.0012 [-0.0215, 0.0234] | 1.01 | -0.0860 / 0.0253 |
| da2_holo_out_all | rotation | da2 | 71 / 3 | None | n/a | -0.1224 [-0.1382, -0.1044] | 0.81 | -0.3369 / 0.0008 |
| da2_panox_all | rotation | da2 | 80 / 8 | None | n/a | -0.5343 [-1.2168, -0.1225] | 0.42 | -0.7973 / 0.1630 |
| da2_s3_calib | rotation | da2 | 120 / 86 | None | n/a | 0.0089 [0.0003, 0.0171] | 1.08 | 0.0128 / 0.0128 |
| da2_s3_eval | rotation | da2 | 80 / 61 | None | n/a | 0.0098 [0.0005, 0.0189] | 1.08 | 0.0111 / 0.0170 |
| da360_holo_in_all | rotation | da360 | 80 / 12 | None | n/a | 0.0077 [-0.0014, 0.0174] | 1.09 | -0.0166 / 0.0159 |
| da360_holo_out_all | rotation | da360 | 71 / 3 | None | n/a | 0.0251 [-0.0034, 0.0457] | 1.12 | 0.0025 / 0.0289 |
| da360_panox_all | rotation | da360 | 80 / 8 | 70.0 | n/a | 0.0744 [0.0078, 0.1748] | 1.91 | -0.0129 / 0.1772 |
| da360_s3_calib | rotation | da360 | 120 / 86 | None | n/a | -0.0047 [-0.0097, -0.0005] | 0.88 | -0.0175 / 0.0042 |
| da360_s3_eval | rotation | da360 | 80 / 61 | None | n/a | -0.0023 [-0.0094, 0.0069] | 0.94 | -0.0175 / 0.0079 |
| dap_holo_in_all | rotation | dap | 80 / 12 | None | n/a | -0.1155 [-0.1692, -0.0593] | 0.72 | -0.2786 / 0.0326 |
| dap_holo_out_all | rotation | dap | 71 / 3 | None | n/a | 0.0213 [-0.1742, 0.1291] | 1.05 | -0.1438 / 0.1295 |
| dap_panox_all | rotation | dap | 80 / 8 | None | n/a | -0.1960 [-0.2586, -0.1273] | 0.64 | -0.3639 / 0.1580 |
| dap_s3_calib | rotation | dap | 120 / 86 | None | n/a | -0.1141 [-0.1311, -0.0976] | 0.57 | -0.2071 / -0.0220 |
| dap_s3_eval | rotation | dap | 80 / 61 | None | n/a | -0.1129 [-0.1318, -0.0938] | 0.59 | -0.2180 / 0.0037 |
| dilation_da2_holo_in_all | dilation | da2 | 80 / 12 | None | 75.0 | 0.1166 [0.0574, 0.1793] | 1.34 | 0.1034 / 0.1350 |
| dilation_da2_holo_out_all | dilation | da2 | 71 / 3 | 80.0 | 80.0 | 0.5700 [0.3845, 0.7953] | 1.88 | 0.6318 / 0.4828 |
| dilation_da2_nyc_all | dilation | da2 | 80 / 70 | None | None | -0.2633 [-0.2951, -0.2258] | 0.63 | -0.3607 / -0.2078 |
| dilation_da2_panox_all | dilation | da2 | 80 / 8 | None | 80.0 | 0.2943 [-0.0338, 0.7688] | 1.49 | 0.1239 / 0.4190 |
| dilation_da2_s3_calib | dilation | da2 | 120 / 86 | None | None | -0.1603 [-0.1749, -0.1461] | 0.64 | -0.2957 / -0.0978 |
| dilation_da2_s3_eval | dilation | da2 | 80 / 61 | None | None | -0.1642 [-0.1821, -0.1467] | 0.64 | -0.2950 / -0.0921 |
| dilation_da360_holo_in_all | dilation | da360 | 80 / 12 | 25.0 | 25.0 | 0.1727 [0.1531, 0.1899] | 1.97 | 0.2676 / 0.1256 |
| dilation_da360_holo_out_all | dilation | da360 | 71 / 3 | 35.0 | 35.0 | 0.1919 [0.1667, 0.2219] | 1.66 | 0.4163 / 0.1272 |
| dilation_da360_nyc_all | dilation | da360 | 80 / 70 | 30.0 | 30.0 | 0.1777 [0.1583, 0.1974] | 1.84 | 0.2704 / 0.1183 |
| dilation_da360_panox_all | dilation | da360 | 80 / 8 | 30.0 | 30.0 | 0.0548 [-0.1845, 0.2054] | 1.23 | 0.1853 / -0.0756 |
| dilation_da360_s3_calib | dilation | da360 | 120 / 86 | 25.0 | 25.0 | 0.1077 [0.0976, 0.1181] | 1.97 | 0.0693 / 0.1114 |
| dilation_da360_s3_eval | dilation | da360 | 80 / 61 | 25.0 | 25.0 | 0.1087 [0.0937, 0.1242] | 1.95 | 0.0864 / 0.1045 |
| dilation_dap_holo_in_all | dilation | dap | 80 / 12 | 55.0 | 45.0 | 1.1033 [0.6985, 1.5003] | 3.19 | 1.8439 / 0.6588 |
| dilation_dap_holo_out_all | dilation | dap | 71 / 3 | 65.0 | 60.0 | 1.6910 [0.7528, 2.6209] | 4.70 | 2.3926 / 1.4460 |
| dilation_dap_nyc_all | dilation | dap | 80 / 70 | 45.0 | 40.0 | 1.6549 [1.2987, 2.0434] | 4.40 | 3.0574 / 1.0920 |
| dilation_dap_panox_all | dilation | dap | 80 / 8 | 70.0 | 60.0 | 1.3691 [0.6042, 2.3129] | 3.09 | 1.6530 / 1.0015 |
| dilation_dap_s3_calib | dilation | dap | 120 / 86 | 40.0 | 35.0 | 1.2948 [1.2042, 1.3893] | 3.83 | 1.3965 / 1.2217 |
| dilation_dap_s3_eval | dilation | dap | 80 / 61 | 45.0 | 35.0 | 1.2557 [1.1508, 1.3567] | 3.69 | 1.5069 / 1.1609 |
| dilation_midas_holo_in_all | dilation | midas_dpt_hybrid_384 | 80 / 12 | 80.0 | None | 0.0460 [0.0284, 0.0632] | 1.14 | 0.0369 / 0.0375 |
| dilation_midas_holo_out_all | dilation | midas_dpt_hybrid_384 | 71 / 3 | 75.0 | 75.0 | 0.0811 [0.0458, 0.1347] | 1.24 | 0.0021 / 0.0888 |
| dilation_midas_nyc_all | dilation | midas_dpt_hybrid_384 | 80 / 70 | 55.0 | 60.0 | 0.0799 [0.0677, 0.0923] | 1.29 | -0.0465 / 0.1335 |
| dilation_midas_panox_all | dilation | midas_dpt_hybrid_384 | 80 / 8 | None | None | 0.0396 [-0.0231, 0.0918] | 1.14 | 0.0150 / 0.0574 |
| dilation_midas_s3_calib | dilation | midas_dpt_hybrid_384 | 120 / 86 | None | None | 0.0222 [0.0059, 0.0361] | 1.09 | 0.0219 / 0.0286 |
| dilation_midas_s3_eval | dilation | midas_dpt_hybrid_384 | 80 / 61 | None | None | 0.0263 [0.0064, 0.0423] | 1.11 | 0.0170 / 0.0327 |
| flip_da2_holo_in_all | flip | da2 | 80 / 12 | 15.0 | 15.0 | -0.0051 [-0.0390, 0.0293] | 0.98 | -0.0280 / -0.0177 |
| flip_da2_holo_out_all | flip | da2 | 71 / 3 | None | None | -0.0838 [-0.2688, 0.0655] | 0.89 | -0.1413 / -0.0429 |
| flip_da2_nyc_all | flip | da2 | 80 / 70 | None | None | 0.0373 [-0.0126, 0.0862] | 1.05 | -0.0182 / 0.0598 |
| flip_da2_panox_all | flip | da2 | 80 / 8 | None | None | 0.4079 [-0.1075, 1.2929] | 2.35 | 0.4202 / 0.0663 |
| flip_da2_s3_calib | flip | da2 | 120 / 86 | 50.0 | 45.0 | 0.0294 [0.0212, 0.0371] | 1.45 | 0.0207 / 0.0349 |
| flip_da2_s3_eval | flip | da2 | 80 / 61 | 30.0 | 30.0 | 0.0305 [0.0212, 0.0417] | 1.48 | 0.0175 / 0.0417 |
| flip_da360_holo_in_all | flip | da360 | 80 / 12 | 15.0 | 15.0 | 0.0009 [-0.0109, 0.0157] | 1.01 | 0.0117 / -0.0178 |
| flip_da360_holo_out_all | flip | da360 | 71 / 3 | 20.0 | 20.0 | -0.0631 [-0.0972, -0.0332] | 0.85 | 0.0242 / -0.1202 |
| flip_da360_nyc_all | flip | da360 | 80 / 70 | 15.0 | 15.0 | 0.0425 [0.0287, 0.0568] | 2.39 | 0.0245 / 0.1244 |
| flip_da360_panox_all | flip | da360 | 80 / 8 | 15.0 | 15.0 | 0.0794 [0.0343, 0.1381] | 3.69 | 0.0786 / 0.0861 |
| flip_da360_s3_calib | flip | da360 | 120 / 86 | 15.0 | 15.0 | 0.0174 [0.0103, 0.0269] | 1.95 | 0.0136 / 0.0205 |
| flip_da360_s3_eval | flip | da360 | 80 / 61 | 15.0 | 15.0 | 0.0152 [0.0043, 0.0247] | 1.85 | 0.0145 / 0.0206 |
| flip_dap_holo_in_all | flip | dap | 80 / 12 | 15.0 | 15.0 | 0.1493 [0.0271, 0.2645] | 1.90 | 0.1387 / 0.1833 |
| flip_dap_holo_out_all | flip | dap | 71 / 3 | None | None | 0.1338 [-0.0597, 0.2689] | 1.37 | 0.2628 / 0.0604 |
| flip_dap_nyc_all | flip | dap | 80 / 70 | 15.0 | 15.0 | 0.4760 [0.4405, 0.5114] | 25.48 | 0.4665 / 0.4836 |
| flip_dap_panox_all | flip | dap | 80 / 8 | 15.0 | 15.0 | 0.1771 [0.0942, 0.2566] | 1.82 | 0.1703 / 0.1910 |
| flip_dap_s3_calib | flip | dap | 120 / 86 | 15.0 | 15.0 | 0.1014 [0.0806, 0.1246] | 4.17 | 0.1063 / 0.1092 |
| flip_dap_s3_eval | flip | dap | 80 / 61 | 15.0 | 15.0 | 0.0746 [0.0582, 0.0915] | 3.18 | 0.0785 / 0.0783 |
| flip_midas_holo_in_all | flip | midas_dpt_hybrid_384 | 80 / 12 | None | None | -0.0111 [-0.0607, 0.0447] | 0.95 | -0.0153 / -0.0308 |
| flip_midas_holo_out_all | flip | midas_dpt_hybrid_384 | 71 / 3 | 15.0 | 15.0 | -0.0374 [-0.1744, 0.0995] | 1.02 | 0.1066 / -0.0636 |
| flip_midas_nyc_all | flip | midas_dpt_hybrid_384 | 80 / 70 | 15.0 | 15.0 | 0.2298 [0.1442, 0.3204] | 2.08 | 0.3475 / 0.4653 |
| flip_midas_panox_all | flip | midas_dpt_hybrid_384 | 80 / 8 | 20.0 | 20.0 | 0.1532 [0.0564, 0.2520] | 1.84 | 0.1770 / 0.2868 |
| flip_midas_s3_calib | flip | midas_dpt_hybrid_384 | 120 / 86 | None | None | -0.0040 [-0.0136, 0.0053] | 0.98 | -0.0024 / -0.0062 |
| flip_midas_s3_eval | flip | midas_dpt_hybrid_384 | 80 / 61 | None | None | -0.0053 [-0.0215, 0.0110] | 0.98 | -0.0101 / -0.0079 |
| midas_holo_in_all | rotation | midas_dpt_hybrid_384 | 80 / 12 | None | n/a | -0.0706 [-0.1080, -0.0376] | 0.82 | -0.2120 / 0.0272 |
| midas_holo_out_all | rotation | midas_dpt_hybrid_384 | 71 / 3 | None | n/a | -0.0810 [-0.1314, -0.0278] | 0.85 | -0.5411 / 0.0477 |
| midas_panox_all | rotation | midas_dpt_hybrid_384 | 80 / 8 | None | n/a | -0.0476 [-0.1145, 0.0161] | 0.89 | -0.2640 / 0.3151 |
| midas_s3_calib | rotation | midas_dpt_hybrid_384 | 120 / 86 | None | n/a | 0.0201 [0.0027, 0.0389] | 1.09 | -0.0642 / 0.0704 |
| midas_s3_eval | rotation | midas_dpt_hybrid_384 | 80 / 61 | None | n/a | 0.0230 [0.0003, 0.0434] | 1.09 | -0.0719 / 0.0719 |
| rotation_da2_holo_in_all | rotation | da2 | 80 / 12 | None | None | 0.0012 [-0.0215, 0.0234] | 1.01 | -0.0860 / 0.0253 |
| rotation_da2_holo_out_all | rotation | da2 | 71 / 3 | None | 45.0 | -0.1224 [-0.1382, -0.1044] | 0.81 | -0.3369 / 0.0008 |
| rotation_da2_nyc_all | rotation | da2 | 80 / 70 | 50.0 | 60.0 | 0.1943 [0.1722, 0.2168] | 1.45 | 0.2373 / 0.1535 |
| rotation_da2_panox_all | rotation | da2 | 80 / 8 | None | None | -0.5343 [-1.2168, -0.1225] | 0.42 | -0.7973 / 0.1630 |
| rotation_da2_s3_calib | rotation | da2 | 120 / 86 | None | None | 0.0089 [0.0003, 0.0171] | 1.08 | 0.0128 / 0.0128 |
| rotation_da2_s3_eval | rotation | da2 | 80 / 61 | None | None | 0.0098 [0.0005, 0.0189] | 1.08 | 0.0111 / 0.0170 |
| rotation_da360_holo_in_all | rotation | da360 | 80 / 12 | None | None | 0.0077 [-0.0014, 0.0174] | 1.09 | -0.0166 / 0.0159 |
| rotation_da360_holo_out_all | rotation | da360 | 71 / 3 | None | None | 0.0251 [-0.0034, 0.0457] | 1.12 | 0.0025 / 0.0289 |
| rotation_da360_nyc_all | rotation | da360 | 80 / 70 | None | 75.0 | 0.0046 [-0.0044, 0.0133] | 1.05 | -0.0150 / 0.0408 |
| rotation_da360_panox_all | rotation | da360 | 80 / 8 | 70.0 | 40.0 | 0.0744 [0.0078, 0.1748] | 1.91 | -0.0129 / 0.1772 |
| rotation_da360_s3_calib | rotation | da360 | 120 / 86 | None | None | -0.0047 [-0.0097, -0.0005] | 0.88 | -0.0175 / 0.0042 |
| rotation_da360_s3_eval | rotation | da360 | 80 / 61 | None | None | -0.0023 [-0.0094, 0.0069] | 0.94 | -0.0175 / 0.0079 |
| rotation_dap_holo_in_all | rotation | dap | 80 / 12 | None | 40.0 | -0.1155 [-0.1692, -0.0593] | 0.72 | -0.2786 / 0.0326 |
| rotation_dap_holo_out_all | rotation | dap | 71 / 3 | None | None | 0.0213 [-0.1742, 0.1291] | 1.05 | -0.1438 / 0.1295 |
| rotation_dap_nyc_all | rotation | dap | 80 / 70 | 15.0 | 15.0 | -0.2038 [-0.2182, -0.1897] | 0.56 | -0.4854 / 0.1536 |
| rotation_dap_panox_all | rotation | dap | 80 / 8 | None | 35.0 | -0.1960 [-0.2586, -0.1273] | 0.64 | -0.3639 / 0.1580 |
| rotation_dap_s3_calib | rotation | dap | 120 / 86 | None | 40.0 | -0.1141 [-0.1311, -0.0976] | 0.57 | -0.2071 / -0.0220 |
| rotation_dap_s3_eval | rotation | dap | 80 / 61 | None | 40.0 | -0.1129 [-0.1318, -0.0938] | 0.59 | -0.2180 / 0.0037 |
| rotation_midas_holo_in_all | rotation | midas_dpt_hybrid_384 | 80 / 12 | None | None | -0.0706 [-0.1080, -0.0376] | 0.82 | -0.2120 / 0.0272 |
| rotation_midas_holo_out_all | rotation | midas_dpt_hybrid_384 | 71 / 3 | None | None | -0.0810 [-0.1314, -0.0278] | 0.85 | -0.5411 / 0.0477 |
| rotation_midas_nyc_all | rotation | midas_dpt_hybrid_384 | 80 / 70 | None | 65.0 | -0.1224 [-0.1893, -0.0568] | 0.75 | -0.5164 / 0.1434 |
| rotation_midas_panox_all | rotation | midas_dpt_hybrid_384 | 80 / 8 | None | 70.0 | -0.0476 [-0.1145, 0.0161] | 0.89 | -0.2640 / 0.3151 |
| rotation_midas_s3_calib | rotation | midas_dpt_hybrid_384 | 120 / 86 | None | 80.0 | 0.0201 [0.0027, 0.0389] | 1.09 | -0.0642 / 0.0704 |
| rotation_midas_s3_eval | rotation | midas_dpt_hybrid_384 | 80 / 61 | None | 80.0 | 0.0230 [0.0003, 0.0434] | 1.09 | -0.0719 / 0.0719 |

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
