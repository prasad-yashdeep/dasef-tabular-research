# Random-expression control (count-matched random valid expressions over the dataset's own columns)

cells: 171 | datasets: 49 | draws per cell: 5 to 5 | random expression columns constant on evaluation rows (summed over draws): 29

share of draws the LLM schema beats (ROC-AUC), per model: mean fraction | cells with LLM above the median draw | cells with LLM above every draw
  knn: 0.78 | 0.82 | 0.59
  logistic_regression: 0.74 | 0.78 | 0.48
  random_forest: 0.60 | 0.62 | 0.33
  xgboost: 0.46 | 0.47 | 0.26

## all datasets, generator-averaged (N=49: 10 core + 39 expansion)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 49 | +0.0032 | +0.0003 | 28/21/0 | 0.012 | 0.012 | [+0.0002, +0.0064] |
| logistic_regression | random_formula_semantic | 49 | +0.0083 | +0.0037 | 47/2/0 | 2.5e-14 | 9.9e-14 | [+0.0055, +0.0114] |
| logistic_regression | llm_vs_random_formula | 49 | +0.0064 | +0.0014 | 40/9/0 | 2.1e-07 | 6.2e-07 | [+0.0034, +0.0099] |
| logistic_regression | llm_semantic | 49 | +0.0140 | +0.0051 | 47/1/1 | 1.8e-13 | 6.1e-13 | [+0.0095, +0.0190] |
| logistic_regression | llm_direct | 49 | +0.0096 | +0.0027 | 35/13/1 | 9.9e-06 | 4e-05 | [+0.0049, +0.0148] |
| logistic_regression | random_formula_vs_noise | 49 | +0.0070 | +0.0037 | 43/6/0 | 1.3e-09 | 2.6e-09 | [+0.0044, +0.0101] |
| logistic_regression | semantic_excess | 49 | +0.0057 | +0.0007 | 39/10/0 | 6.5e-05 | 0.00026 | [+0.0026, +0.0092] |
| knn | random_formula_vs_raw | 49 | -0.0068 | -0.0049 | 9/40/0 | 3.7e-05 | 0.00011 | [-0.0107, -0.0031] |
| knn | random_formula_semantic | 49 | +0.0391 | +0.0266 | 48/1/0 | 5e-14 | 1.5e-13 | [+0.0291, +0.0505] |
| knn | llm_vs_random_formula | 49 | +0.0135 | +0.0077 | 43/6/0 | 9.7e-09 | 3.9e-08 | [+0.0087, +0.0188] |
| knn | llm_semantic | 49 | +0.0510 | +0.0428 | 48/1/0 | 1.5e-13 | 6.1e-13 | [+0.0396, +0.0637] |
| knn | llm_direct | 49 | +0.0067 | +0.0019 | 29/20/0 | 0.014 | 0.042 | [+0.0023, +0.0114] |
| knn | random_formula_vs_noise | 49 | +0.0405 | +0.0269 | 43/6/0 | 2.7e-11 | 1.1e-10 | [+0.0292, +0.0533] |
| knn | semantic_excess | 49 | +0.0118 | +0.0075 | 38/11/0 | 0.00015 | 0.00046 | [+0.0061, +0.0183] |
| random_forest | random_formula_vs_raw | 49 | -0.0017 | -0.0011 | 8/39/2 | 8.6e-07 | 3.4e-06 | [-0.0027, -0.0009] |
| random_forest | random_formula_semantic | 49 | +0.0031 | +0.0006 | 29/18/2 | 0.1 | 0.1 | [-0.0006, +0.0076] |
| random_forest | llm_vs_random_formula | 49 | +0.0036 | +0.0005 | 31/16/2 | 0.0024 | 0.0047 | [+0.0017, +0.0057] |
| random_forest | llm_semantic | 49 | +0.0085 | +0.0010 | 30/17/2 | 0.0027 | 0.0027 | [+0.0029, +0.0158] |
| random_forest | llm_direct | 49 | +0.0019 | -0.0000 | 21/26/2 | 0.39 | 0.77 | [+0.0002, +0.0038] |
| random_forest | random_formula_vs_noise | 49 | +0.0065 | +0.0014 | 36/11/2 | 0.00045 | 0.00045 | [+0.0024, +0.0112] |
| random_forest | semantic_excess | 49 | +0.0055 | +0.0010 | 36/11/2 | 0.00025 | 0.00049 | [+0.0026, +0.0089] |
| xgboost | random_formula_vs_raw | 49 | -0.0007 | -0.0001 | 14/32/3 | 0.004 | 0.0079 | [-0.0015, -0.0000] |
| xgboost | random_formula_semantic | 49 | +0.0048 | +0.0018 | 40/6/3 | 1.5e-07 | 3e-07 | [+0.0026, +0.0077] |
| xgboost | llm_vs_random_formula | 49 | +0.0007 | +0.0000 | 22/24/3 | 0.78 | 0.78 | [-0.0008, +0.0022] |
| xgboost | llm_semantic | 49 | +0.0085 | +0.0025 | 39/7/3 | 1.7e-06 | 3.4e-06 | [+0.0038, +0.0141] |
| xgboost | llm_direct | 49 | -0.0000 | -0.0002 | 18/28/3 | 0.52 | 0.77 | [-0.0018, +0.0017] |
| xgboost | random_formula_vs_noise | 49 | +0.0120 | +0.0043 | 42/4/3 | 3.6e-11 | 1.1e-10 | [+0.0071, +0.0181] |
| xgboost | semantic_excess | 49 | +0.0037 | +0.0006 | 32/14/3 | 0.0029 | 0.0029 | [+0.0007, +0.0071] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 49 | +0.0046 | +0.0011 | 33/16/0 | 0.0033 | 0.01 | [+0.0016, +0.0081] |
| logistic_regression | random_formula_semantic | 49 | +0.0101 | +0.0043 | 46/3/0 | 1.1e-11 | 3.4e-11 | [+0.0067, +0.0141] |
| logistic_regression | llm_vs_random_formula | 49 | +0.0065 | +0.0020 | 36/13/0 | 0.00039 | 0.0012 | [+0.0025, +0.0111] |
| logistic_regression | llm_semantic | 49 | +0.0165 | +0.0070 | 45/4/0 | 4e-11 | 1.2e-10 | [+0.0112, +0.0225] |
| logistic_regression | llm_direct | 49 | +0.0111 | +0.0032 | 34/15/0 | 5.9e-05 | 0.00023 | [+0.0058, +0.0171] |
| logistic_regression | random_formula_vs_noise | 49 | +0.0087 | +0.0035 | 40/9/0 | 7.8e-08 | 7.8e-08 | [+0.0053, +0.0126] |
| logistic_regression | semantic_excess | 49 | +0.0064 | +0.0022 | 37/12/0 | 0.0016 | 0.0016 | [+0.0023, +0.0111] |
| knn | random_formula_vs_raw | 49 | -0.0094 | -0.0054 | 10/38/1 | 3.1e-06 | 1.2e-05 | [-0.0151, -0.0045] |
| knn | random_formula_semantic | 49 | +0.0527 | +0.0311 | 46/2/1 | 2.3e-13 | 9.4e-13 | [+0.0379, +0.0701] |
| knn | llm_vs_random_formula | 49 | +0.0218 | +0.0094 | 41/7/1 | 1.3e-07 | 5.2e-07 | [+0.0131, +0.0322] |
| knn | llm_semantic | 49 | +0.0735 | +0.0571 | 46/2/1 | 7.1e-14 | 2.8e-13 | [+0.0545, +0.0956] |
| knn | llm_direct | 49 | +0.0124 | +0.0017 | 30/18/1 | 0.013 | 0.038 | [+0.0049, +0.0205] |
| knn | random_formula_vs_noise | 49 | +0.0546 | +0.0323 | 45/3/1 | 2.6e-12 | 1.1e-11 | [+0.0365, +0.0774] |
| knn | semantic_excess | 49 | +0.0208 | +0.0092 | 35/13/1 | 3.6e-05 | 0.00011 | [+0.0109, +0.0317] |
| random_forest | random_formula_vs_raw | 49 | +0.0007 | -0.0004 | 19/28/2 | 0.092 | 0.18 | [-0.0012, +0.0033] |
| random_forest | random_formula_semantic | 49 | +0.0198 | +0.0095 | 40/8/1 | 1.1e-09 | 1.6e-09 | [+0.0113, +0.0311] |
| random_forest | llm_vs_random_formula | 49 | +0.0069 | +0.0018 | 32/16/1 | 0.00079 | 0.0016 | [+0.0029, +0.0121] |
| random_forest | llm_semantic | 49 | +0.0303 | +0.0142 | 40/8/1 | 4.1e-11 | 1.2e-10 | [+0.0186, +0.0447] |
| random_forest | llm_direct | 49 | +0.0076 | +0.0005 | 28/20/1 | 0.016 | 0.038 | [+0.0026, +0.0146] |
| random_forest | random_formula_vs_noise | 49 | +0.0285 | +0.0159 | 41/7/1 | 4.6e-10 | 1.4e-09 | [+0.0171, +0.0431] |
| random_forest | semantic_excess | 49 | +0.0105 | +0.0037 | 37/11/1 | 5.8e-07 | 2.3e-06 | [+0.0056, +0.0168] |
| xgboost | random_formula_vs_raw | 49 | -0.0004 | +0.0001 | 27/20/2 | 0.85 | 0.85 | [-0.0011, +0.0004] |
| xgboost | random_formula_semantic | 49 | +0.0093 | +0.0038 | 42/5/2 | 8.2e-10 | 1.6e-09 | [+0.0047, +0.0156] |
| xgboost | llm_vs_random_formula | 49 | +0.0021 | -0.0002 | 22/25/2 | 0.54 | 0.54 | [-0.0003, +0.0057] |
| xgboost | llm_semantic | 49 | +0.0137 | +0.0045 | 41/6/2 | 2.5e-09 | 2.5e-09 | [+0.0072, +0.0221] |
| xgboost | llm_direct | 49 | +0.0018 | -0.0001 | 22/25/2 | 0.49 | 0.49 | [-0.0007, +0.0051] |
| xgboost | random_formula_vs_noise | 49 | +0.0176 | +0.0082 | 40/7/2 | 1.3e-09 | 2.6e-09 | [+0.0093, +0.0290] |
| xgboost | semantic_excess | 49 | +0.0044 | +0.0019 | 33/14/2 | 0.0003 | 0.00059 | [+0.0017, +0.0083] |

## expansion only (N=39)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 39 | +0.0032 | +0.0003 | 22/17/0 | 0.04 | 0.04 | [-0.0005, +0.0071] |
| logistic_regression | random_formula_semantic | 39 | +0.0080 | +0.0032 | 37/2/0 | 2.5e-11 | 1e-10 | [+0.0048, +0.0118] |
| logistic_regression | llm_vs_random_formula | 39 | +0.0073 | +0.0022 | 32/7/0 | 2.8e-06 | 8.3e-06 | [+0.0037, +0.0112] |
| logistic_regression | llm_semantic | 39 | +0.0144 | +0.0037 | 37/1/1 | 1.8e-10 | 5.5e-10 | [+0.0090, +0.0204] |
| logistic_regression | llm_direct | 39 | +0.0105 | +0.0026 | 27/11/1 | 0.00028 | 0.0011 | [+0.0049, +0.0166] |
| logistic_regression | random_formula_vs_noise | 39 | +0.0068 | +0.0019 | 33/6/0 | 4.5e-07 | 9.1e-07 | [+0.0036, +0.0106] |
| logistic_regression | semantic_excess | 39 | +0.0064 | +0.0007 | 31/8/0 | 0.00041 | 0.0011 | [+0.0028, +0.0105] |
| knn | random_formula_vs_raw | 39 | -0.0056 | -0.0043 | 9/30/0 | 0.0024 | 0.0071 | [-0.0099, -0.0014] |
| knn | random_formula_semantic | 39 | +0.0354 | +0.0266 | 38/1/0 | 5.1e-11 | 1.5e-10 | [+0.0254, +0.0470] |
| knn | llm_vs_random_formula | 39 | +0.0131 | +0.0077 | 34/5/0 | 1e-06 | 4.2e-06 | [+0.0077, +0.0189] |
| knn | llm_semantic | 39 | +0.0476 | +0.0395 | 38/1/0 | 9.1e-11 | 3.6e-10 | [+0.0354, +0.0614] |
| knn | llm_direct | 39 | +0.0075 | +0.0029 | 25/14/0 | 0.0098 | 0.029 | [+0.0023, +0.0130] |
| knn | random_formula_vs_noise | 39 | +0.0373 | +0.0269 | 33/6/0 | 2.8e-08 | 1.1e-07 | [+0.0251, +0.0513] |
| knn | semantic_excess | 39 | +0.0123 | +0.0075 | 31/8/0 | 0.00036 | 0.0011 | [+0.0057, +0.0197] |
| random_forest | random_formula_vs_raw | 39 | -0.0017 | -0.0011 | 7/30/2 | 5.6e-05 | 0.00022 | [-0.0029, -0.0006] |
| random_forest | random_formula_semantic | 39 | +0.0032 | +0.0005 | 22/15/2 | 0.19 | 0.19 | [-0.0004, +0.0085] |
| random_forest | llm_vs_random_formula | 39 | +0.0042 | +0.0005 | 26/11/2 | 0.0014 | 0.0029 | [+0.0019, +0.0067] |
| random_forest | llm_semantic | 39 | +0.0095 | +0.0006 | 23/14/2 | 0.01 | 0.01 | [+0.0033, +0.0185] |
| random_forest | llm_direct | 39 | +0.0025 | -0.0000 | 16/21/2 | 0.39 | 0.77 | [+0.0005, +0.0048] |
| random_forest | random_formula_vs_noise | 39 | +0.0062 | +0.0013 | 29/8/2 | 0.0011 | 0.0011 | [+0.0017, +0.0117] |
| random_forest | semantic_excess | 39 | +0.0063 | +0.0010 | 30/7/2 | 0.00023 | 0.00093 | [+0.0030, +0.0105] |
| xgboost | random_formula_vs_raw | 39 | -0.0009 | -0.0001 | 11/25/3 | 0.0025 | 0.0071 | [-0.0019, -0.0003] |
| xgboost | random_formula_semantic | 39 | +0.0051 | +0.0013 | 32/4/3 | 1.4e-07 | 2.9e-07 | [+0.0027, +0.0085] |
| xgboost | llm_vs_random_formula | 39 | +0.0008 | +0.0000 | 18/18/3 | 0.57 | 0.57 | [-0.0009, +0.0027] |
| xgboost | llm_semantic | 39 | +0.0095 | +0.0018 | 31/5/3 | 5.4e-06 | 1.1e-05 | [+0.0040, +0.0164] |
| xgboost | llm_direct | 39 | -0.0001 | -0.0000 | 15/21/3 | 0.73 | 0.77 | [-0.0023, +0.0019] |
| xgboost | random_formula_vs_noise | 39 | +0.0123 | +0.0033 | 32/4/3 | 3.1e-08 | 1.1e-07 | [+0.0064, +0.0198] |
| xgboost | semantic_excess | 39 | +0.0044 | +0.0006 | 25/11/3 | 0.0031 | 0.0031 | [+0.0008, +0.0085] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 39 | +0.0053 | +0.0011 | 28/11/0 | 0.0019 | 0.0058 | [+0.0018, +0.0095] |
| logistic_regression | random_formula_semantic | 39 | +0.0100 | +0.0053 | 36/3/0 | 3.9e-09 | 1.2e-08 | [+0.0062, +0.0145] |
| logistic_regression | llm_vs_random_formula | 39 | +0.0071 | +0.0017 | 28/11/0 | 0.0037 | 0.0074 | [+0.0023, +0.0127] |
| logistic_regression | llm_semantic | 39 | +0.0171 | +0.0070 | 35/4/0 | 2.8e-08 | 8.3e-08 | [+0.0107, +0.0243] |
| logistic_regression | llm_direct | 39 | +0.0124 | +0.0026 | 27/12/0 | 0.00027 | 0.0011 | [+0.0060, +0.0197] |
| logistic_regression | random_formula_vs_noise | 39 | +0.0093 | +0.0034 | 33/6/0 | 4.5e-07 | 9.1e-07 | [+0.0053, +0.0140] |
| logistic_regression | semantic_excess | 39 | +0.0071 | +0.0019 | 30/9/0 | 0.0057 | 0.011 | [+0.0021, +0.0128] |
| knn | random_formula_vs_raw | 39 | -0.0101 | -0.0053 | 9/29/1 | 0.00019 | 0.00075 | [-0.0171, -0.0039] |
| knn | random_formula_semantic | 39 | +0.0490 | +0.0327 | 36/2/1 | 2.4e-10 | 9.6e-10 | [+0.0330, +0.0681] |
| knn | llm_vs_random_formula | 39 | +0.0204 | +0.0084 | 31/7/1 | 2.6e-05 | 0.00011 | [+0.0103, +0.0323] |
| knn | llm_semantic | 39 | +0.0686 | +0.0508 | 36/2/1 | 7.3e-11 | 2.9e-10 | [+0.0483, +0.0927] |
| knn | llm_direct | 39 | +0.0103 | +0.0009 | 23/15/1 | 0.079 | 0.16 | [+0.0021, +0.0193] |
| knn | random_formula_vs_noise | 39 | +0.0512 | +0.0297 | 35/3/1 | 2.7e-09 | 1.1e-08 | [+0.0307, +0.0784] |
| knn | semantic_excess | 39 | +0.0196 | +0.0090 | 27/11/1 | 0.0005 | 0.0015 | [+0.0080, +0.0325] |
| random_forest | random_formula_vs_raw | 39 | +0.0008 | -0.0002 | 15/22/2 | 0.12 | 0.25 | [-0.0011, +0.0038] |
| random_forest | random_formula_semantic | 39 | +0.0134 | +0.0075 | 30/8/1 | 9e-07 | 9e-07 | [+0.0075, +0.0209] |
| random_forest | llm_vs_random_formula | 39 | +0.0078 | +0.0018 | 26/12/1 | 0.0015 | 0.0044 | [+0.0029, +0.0140] |
| random_forest | llm_semantic | 39 | +0.0245 | +0.0128 | 30/8/1 | 4.2e-08 | 8.3e-08 | [+0.0136, +0.0386] |
| random_forest | llm_direct | 39 | +0.0086 | +0.0004 | 22/16/1 | 0.037 | 0.11 | [+0.0024, +0.0172] |
| random_forest | random_formula_vs_noise | 39 | +0.0203 | +0.0116 | 31/7/1 | 4.6e-07 | 9.1e-07 | [+0.0118, +0.0308] |
| random_forest | semantic_excess | 39 | +0.0111 | +0.0036 | 29/9/1 | 5.5e-06 | 2.2e-05 | [+0.0052, +0.0187] |
| xgboost | random_formula_vs_raw | 39 | -0.0004 | +0.0001 | 22/15/2 | 0.68 | 0.68 | [-0.0011, +0.0002] |
| xgboost | random_formula_semantic | 39 | +0.0058 | +0.0023 | 33/4/2 | 7.2e-08 | 1.4e-07 | [+0.0031, +0.0097] |
| xgboost | llm_vs_random_formula | 39 | +0.0023 | -0.0002 | 17/20/2 | 0.67 | 0.67 | [-0.0007, +0.0067] |
| xgboost | llm_semantic | 39 | +0.0105 | +0.0041 | 31/6/2 | 1e-06 | 1e-06 | [+0.0051, +0.0188] |
| xgboost | llm_direct | 39 | +0.0018 | +0.0000 | 18/19/2 | 0.64 | 0.64 | [-0.0011, +0.0060] |
| xgboost | random_formula_vs_noise | 39 | +0.0114 | +0.0066 | 31/6/2 | 2.8e-07 | 8.3e-07 | [+0.0063, +0.0177] |
| xgboost | semantic_excess | 39 | +0.0047 | +0.0009 | 25/12/2 | 0.0056 | 0.011 | [+0.0014, +0.0096] |

## core only (N=10)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 10 | +0.0032 | +0.0009 | 6/4/0 | 0.16 | 0.32 | [+0.0000, +0.0082] |
| logistic_regression | random_formula_semantic | 10 | +0.0095 | +0.0063 | 10/0/0 | 0.002 | 0.0078 | [+0.0042, +0.0156] |
| logistic_regression | llm_vs_random_formula | 10 | +0.0028 | +0.0012 | 8/2/0 | 0.037 | 0.11 | [+0.0006, +0.0060] |
| logistic_regression | llm_semantic | 10 | +0.0122 | +0.0073 | 10/0/0 | 0.002 | 0.0078 | [+0.0058, +0.0203] |
| logistic_regression | llm_direct | 10 | +0.0060 | +0.0030 | 8/2/0 | 0.0098 | 0.039 | [+0.0014, +0.0138] |
| logistic_regression | random_formula_vs_noise | 10 | +0.0078 | +0.0063 | 10/0/0 | 0.002 | 0.0078 | [+0.0040, +0.0125] |
| logistic_regression | semantic_excess | 10 | +0.0027 | +0.0010 | 8/2/0 | 0.084 | 0.34 | [+0.0003, +0.0061] |
| knn | random_formula_vs_raw | 10 | -0.0117 | -0.0078 | 0/10/0 | 0.002 | 0.0078 | [-0.0196, -0.0053] |
| knn | random_formula_semantic | 10 | +0.0538 | +0.0250 | 10/0/0 | 0.002 | 0.0078 | [+0.0256, +0.0882] |
| knn | llm_vs_random_formula | 10 | +0.0153 | +0.0082 | 9/1/0 | 0.0039 | 0.016 | [+0.0053, +0.0284] |
| knn | llm_semantic | 10 | +0.0640 | +0.0503 | 10/0/0 | 0.002 | 0.0078 | [+0.0375, +0.0972] |
| knn | llm_direct | 10 | +0.0035 | -0.0007 | 4/6/0 | 0.77 | 1 | [-0.0027, +0.0112] |
| knn | random_formula_vs_noise | 10 | +0.0532 | +0.0307 | 10/0/0 | 0.002 | 0.0078 | [+0.0265, +0.0858] |
| knn | semantic_excess | 10 | +0.0102 | +0.0059 | 7/3/0 | 0.28 | 0.83 | [-0.0016, +0.0249] |
| random_forest | random_formula_vs_raw | 10 | -0.0020 | -0.0012 | 1/9/0 | 0.0039 | 0.012 | [-0.0033, -0.0008] |
| random_forest | random_formula_semantic | 10 | +0.0025 | +0.0006 | 7/3/0 | 0.49 | 0.49 | [-0.0070, +0.0115] |
| random_forest | llm_vs_random_formula | 10 | +0.0015 | +0.0002 | 5/5/0 | 0.56 | 1 | [-0.0012, +0.0045] |
| random_forest | llm_semantic | 10 | +0.0046 | +0.0042 | 7/3/0 | 0.23 | 0.23 | [-0.0065, +0.0145] |
| random_forest | llm_direct | 10 | -0.0005 | +0.0002 | 5/5/0 | 1 | 1 | [-0.0033, +0.0019] |
| random_forest | random_formula_vs_noise | 10 | +0.0079 | +0.0037 | 7/3/0 | 0.13 | 0.13 | [-0.0003, +0.0168] |
| random_forest | semantic_excess | 10 | +0.0022 | +0.0011 | 6/4/0 | 0.49 | 0.98 | [-0.0011, +0.0057] |
| xgboost | random_formula_vs_raw | 10 | +0.0003 | -0.0002 | 3/7/0 | 0.7 | 0.7 | [-0.0012, +0.0020] |
| xgboost | random_formula_semantic | 10 | +0.0038 | +0.0031 | 8/2/0 | 0.13 | 0.26 | [-0.0006, +0.0083] |
| xgboost | llm_vs_random_formula | 10 | +0.0000 | -0.0004 | 4/6/0 | 0.62 | 1 | [-0.0022, +0.0023] |
| xgboost | llm_semantic | 10 | +0.0047 | +0.0035 | 8/2/0 | 0.11 | 0.21 | [-0.0023, +0.0112] |
| xgboost | llm_direct | 10 | +0.0003 | -0.0008 | 3/7/0 | 0.56 | 1 | [-0.0016, +0.0027] |
| xgboost | random_formula_vs_noise | 10 | +0.0109 | +0.0098 | 10/0/0 | 0.002 | 0.0078 | [+0.0059, +0.0168] |
| xgboost | semantic_excess | 10 | +0.0009 | +0.0005 | 7/3/0 | 0.49 | 0.98 | [-0.0026, +0.0043] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 10 | +0.0019 | +0.0007 | 5/5/0 | 0.7 | 1 | [-0.0021, +0.0075] |
| logistic_regression | random_formula_semantic | 10 | +0.0104 | +0.0043 | 10/0/0 | 0.002 | 0.0078 | [+0.0039, +0.0186] |
| logistic_regression | llm_vs_random_formula | 10 | +0.0040 | +0.0035 | 8/2/0 | 0.02 | 0.059 | [+0.0013, +0.0073] |
| logistic_regression | llm_semantic | 10 | +0.0139 | +0.0075 | 10/0/0 | 0.002 | 0.0078 | [+0.0059, +0.0243] |
| logistic_regression | llm_direct | 10 | +0.0058 | +0.0040 | 7/3/0 | 0.11 | 0.32 | [+0.0002, +0.0144] |
| logistic_regression | random_formula_vs_noise | 10 | +0.0063 | +0.0044 | 7/3/0 | 0.064 | 0.064 | [+0.0010, +0.0124] |
| logistic_regression | semantic_excess | 10 | +0.0035 | +0.0023 | 7/3/0 | 0.064 | 0.082 | [+0.0005, +0.0071] |
| knn | random_formula_vs_raw | 10 | -0.0069 | -0.0071 | 1/9/0 | 0.0039 | 0.016 | [-0.0098, -0.0040] |
| knn | random_formula_semantic | 10 | +0.0673 | +0.0305 | 10/0/0 | 0.002 | 0.0078 | [+0.0355, +0.1049] |
| knn | llm_vs_random_formula | 10 | +0.0274 | +0.0256 | 10/0/0 | 0.002 | 0.0078 | [+0.0121, +0.0487] |
| knn | llm_semantic | 10 | +0.0925 | +0.0654 | 10/0/0 | 0.002 | 0.0078 | [+0.0528, +0.1458] |
| knn | llm_direct | 10 | +0.0205 | +0.0150 | 7/3/0 | 0.064 | 0.26 | [+0.0045, +0.0421] |
| knn | random_formula_vs_noise | 10 | +0.0677 | +0.0363 | 10/0/0 | 0.002 | 0.0078 | [+0.0380, +0.1029] |
| knn | semantic_excess | 10 | +0.0252 | +0.0268 | 8/2/0 | 0.027 | 0.082 | [+0.0082, +0.0465] |
| random_forest | random_formula_vs_raw | 10 | +0.0003 | -0.0011 | 4/6/0 | 0.56 | 1 | [-0.0040, +0.0054] |
| random_forest | random_formula_semantic | 10 | +0.0445 | +0.0154 | 10/0/0 | 0.002 | 0.0078 | [+0.0153, +0.0867] |
| random_forest | llm_vs_random_formula | 10 | +0.0036 | +0.0036 | 6/4/0 | 0.32 | 0.64 | [-0.0010, +0.0083] |
| random_forest | llm_semantic | 10 | +0.0527 | +0.0361 | 10/0/0 | 0.002 | 0.0078 | [+0.0227, +0.0961] |
| random_forest | llm_direct | 10 | +0.0040 | +0.0032 | 6/4/0 | 0.32 | 0.64 | [-0.0016, +0.0097] |
| random_forest | random_formula_vs_noise | 10 | +0.0607 | +0.0368 | 10/0/0 | 0.002 | 0.0078 | [+0.0260, +0.1140] |
| random_forest | semantic_excess | 10 | +0.0082 | +0.0069 | 8/2/0 | 0.037 | 0.082 | [+0.0020, +0.0162] |
| xgboost | random_formula_vs_raw | 10 | -0.0001 | +0.0002 | 5/5/0 | 0.85 | 1 | [-0.0026, +0.0024] |
| xgboost | random_formula_semantic | 10 | +0.0227 | +0.0097 | 9/1/0 | 0.0059 | 0.0078 | [+0.0063, +0.0481] |
| xgboost | llm_vs_random_formula | 10 | +0.0016 | +0.0001 | 5/5/0 | 0.62 | 0.64 | [-0.0008, +0.0045] |
| xgboost | llm_semantic | 10 | +0.0260 | +0.0121 | 10/0/0 | 0.002 | 0.0078 | [+0.0086, +0.0520] |
| xgboost | llm_direct | 10 | +0.0015 | -0.0005 | 4/6/0 | 0.62 | 0.64 | [-0.0006, +0.0040] |
| xgboost | random_formula_vs_noise | 10 | +0.0419 | +0.0187 | 9/1/0 | 0.0039 | 0.0078 | [+0.0133, +0.0875] |
| xgboost | semantic_excess | 10 | +0.0032 | +0.0020 | 8/2/0 | 0.0098 | 0.039 | [+0.0011, +0.0062] |

## claude-opus-4.7 (N=40)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 40 | +0.0042 | +0.0006 | 27/12/1 | 0.0035 | 0.0053 | [+0.0008, +0.0078] |
| logistic_regression | random_formula_semantic | 40 | +0.0105 | +0.0059 | 39/0/1 | 3.6e-12 | 1.5e-11 | [+0.0071, +0.0142] |
| logistic_regression | llm_vs_random_formula | 40 | +0.0094 | +0.0032 | 32/7/1 | 9.7e-06 | 2.9e-05 | [+0.0050, +0.0146] |
| logistic_regression | llm_semantic | 40 | +0.0193 | +0.0088 | 37/2/1 | 1.6e-08 | 4.7e-08 | [+0.0121, +0.0271] |
| logistic_regression | llm_direct | 40 | +0.0136 | +0.0044 | 33/6/1 | 1.2e-05 | 5e-05 | [+0.0068, +0.0213] |
| logistic_regression | random_formula_vs_noise | 40 | +0.0085 | +0.0063 | 35/4/1 | 2.8e-08 | 5.5e-08 | [+0.0055, +0.0120] |
| logistic_regression | semantic_excess | 40 | +0.0088 | +0.0034 | 32/7/1 | 0.00011 | 0.00045 | [+0.0030, +0.0147] |
| knn | random_formula_vs_raw | 40 | -0.0061 | -0.0062 | 8/32/0 | 0.0026 | 0.0053 | [-0.0103, -0.0019] |
| knn | random_formula_semantic | 40 | +0.0432 | +0.0262 | 38/2/0 | 2.5e-11 | 7.6e-11 | [+0.0309, +0.0567] |
| knn | llm_vs_random_formula | 40 | +0.0169 | +0.0120 | 35/5/0 | 3.9e-07 | 1.6e-06 | [+0.0108, +0.0237] |
| knn | llm_semantic | 40 | +0.0548 | +0.0418 | 40/0/0 | 1.8e-12 | 7.3e-12 | [+0.0416, +0.0698] |
| knn | llm_direct | 40 | +0.0108 | +0.0044 | 27/13/0 | 0.0037 | 0.011 | [+0.0047, +0.0176] |
| knn | random_formula_vs_noise | 40 | +0.0431 | +0.0311 | 34/6/0 | 1.9e-09 | 5.8e-09 | [+0.0294, +0.0579] |
| knn | semantic_excess | 40 | +0.0117 | +0.0081 | 28/12/0 | 0.0034 | 0.0071 | [+0.0043, +0.0196] |
| random_forest | random_formula_vs_raw | 40 | -0.0020 | -0.0011 | 6/33/1 | 1.6e-05 | 6.4e-05 | [-0.0033, -0.0009] |
| random_forest | random_formula_semantic | 40 | +0.0050 | +0.0009 | 25/14/1 | 0.012 | 0.012 | [+0.0003, +0.0115] |
| random_forest | llm_vs_random_formula | 40 | +0.0033 | +0.0005 | 25/14/1 | 0.0098 | 0.02 | [+0.0012, +0.0056] |
| random_forest | llm_semantic | 40 | +0.0083 | +0.0024 | 31/8/1 | 5.5e-05 | 6.5e-05 | [+0.0037, +0.0134] |
| random_forest | llm_direct | 40 | +0.0013 | -0.0002 | 17/22/1 | 0.96 | 0.96 | [-0.0011, +0.0038] |
| random_forest | random_formula_vs_noise | 40 | +0.0070 | +0.0023 | 31/8/1 | 0.00023 | 0.00023 | [+0.0023, +0.0124] |
| random_forest | semantic_excess | 40 | +0.0033 | +0.0011 | 30/9/1 | 0.0024 | 0.0071 | [-0.0006, +0.0067] |
| xgboost | random_formula_vs_raw | 40 | -0.0009 | -0.0001 | 10/29/1 | 0.00071 | 0.0021 | [-0.0019, -0.0001] |
| xgboost | random_formula_semantic | 40 | +0.0064 | +0.0017 | 35/4/1 | 9.5e-07 | 1.9e-06 | [+0.0028, +0.0120] |
| xgboost | llm_vs_random_formula | 40 | +0.0007 | -0.0000 | 18/21/1 | 0.64 | 0.64 | [-0.0008, +0.0025] |
| xgboost | llm_semantic | 40 | +0.0090 | +0.0027 | 32/7/1 | 3.2e-05 | 6.5e-05 | [+0.0041, +0.0155] |
| xgboost | llm_direct | 40 | -0.0002 | -0.0003 | 15/24/1 | 0.22 | 0.45 | [-0.0019, +0.0016] |
| xgboost | random_formula_vs_noise | 40 | +0.0111 | +0.0045 | 36/3/1 | 9.2e-10 | 3.7e-09 | [+0.0065, +0.0177] |
| xgboost | semantic_excess | 40 | +0.0026 | +0.0001 | 24/15/1 | 0.24 | 0.24 | [-0.0019, +0.0085] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 40 | +0.0049 | +0.0013 | 26/14/0 | 0.0067 | 0.02 | [+0.0014, +0.0090] |
| logistic_regression | random_formula_semantic | 40 | +0.0124 | +0.0052 | 37/3/0 | 3.5e-11 | 1.4e-10 | [+0.0082, +0.0172] |
| logistic_regression | llm_vs_random_formula | 40 | +0.0088 | +0.0045 | 31/9/0 | 0.00051 | 0.0015 | [+0.0016, +0.0156] |
| logistic_regression | llm_semantic | 40 | +0.0211 | +0.0100 | 36/3/1 | 1.8e-08 | 3.6e-08 | [+0.0137, +0.0293] |
| logistic_regression | llm_direct | 40 | +0.0137 | +0.0062 | 29/10/1 | 0.0015 | 0.0059 | [+0.0048, +0.0231] |
| logistic_regression | random_formula_vs_noise | 40 | +0.0097 | +0.0064 | 32/8/0 | 2e-07 | 2e-07 | [+0.0060, +0.0140] |
| logistic_regression | semantic_excess | 40 | +0.0087 | +0.0034 | 33/7/0 | 0.00051 | 0.0015 | [+0.0020, +0.0153] |
| knn | random_formula_vs_raw | 40 | -0.0066 | -0.0051 | 9/30/1 | 0.001 | 0.004 | [-0.0131, -0.0002] |
| knn | random_formula_semantic | 40 | +0.0517 | +0.0358 | 36/3/1 | 9.1e-11 | 2.7e-10 | [+0.0359, +0.0693] |
| knn | llm_vs_random_formula | 40 | +0.0240 | +0.0169 | 34/5/1 | 6.1e-08 | 2.4e-07 | [+0.0154, +0.0337] |
| knn | llm_semantic | 40 | +0.0721 | +0.0558 | 38/1/1 | 1.1e-11 | 4.4e-11 | [+0.0532, +0.0929] |
| knn | llm_direct | 40 | +0.0174 | +0.0087 | 25/13/2 | 0.0022 | 0.0065 | [+0.0075, +0.0283] |
| knn | random_formula_vs_noise | 40 | +0.0511 | +0.0342 | 35/4/1 | 1.1e-09 | 3.4e-09 | [+0.0347, +0.0692] |
| knn | semantic_excess | 40 | +0.0204 | +0.0100 | 32/7/1 | 8.2e-06 | 3.3e-05 | [+0.0112, +0.0309] |
| random_forest | random_formula_vs_raw | 40 | +0.0018 | -0.0002 | 17/22/1 | 0.44 | 0.63 | [-0.0011, +0.0057] |
| random_forest | random_formula_semantic | 40 | +0.0241 | +0.0129 | 34/5/1 | 3.3e-09 | 3.3e-09 | [+0.0132, +0.0386] |
| random_forest | llm_vs_random_formula | 40 | +0.0071 | +0.0014 | 24/15/1 | 0.054 | 0.11 | [+0.0014, +0.0141] |
| random_forest | llm_semantic | 40 | +0.0347 | +0.0169 | 34/5/1 | 5.4e-09 | 1.6e-08 | [+0.0195, +0.0529] |
| random_forest | llm_direct | 40 | +0.0089 | +0.0009 | 22/17/1 | 0.18 | 0.36 | [+0.0013, +0.0192] |
| random_forest | random_formula_vs_noise | 40 | +0.0336 | +0.0165 | 34/5/1 | 7.5e-10 | 3e-09 | [+0.0195, +0.0517] |
| random_forest | semantic_excess | 40 | +0.0106 | +0.0048 | 28/11/1 | 0.00067 | 0.0015 | [+0.0044, +0.0188] |
| xgboost | random_formula_vs_raw | 40 | -0.0007 | -0.0001 | 18/21/1 | 0.32 | 0.63 | [-0.0018, +0.0003] |
| xgboost | random_formula_semantic | 40 | +0.0105 | +0.0038 | 35/4/1 | 3.2e-10 | 6.4e-10 | [+0.0051, +0.0181] |
| xgboost | llm_vs_random_formula | 40 | +0.0015 | +0.0000 | 20/19/1 | 0.93 | 0.93 | [-0.0015, +0.0055] |
| xgboost | llm_semantic | 40 | +0.0143 | +0.0052 | 28/11/1 | 0.00014 | 0.00014 | [+0.0063, +0.0240] |
| xgboost | llm_direct | 40 | +0.0008 | +0.0000 | 19/19/2 | 0.92 | 0.92 | [-0.0021, +0.0043] |
| xgboost | random_formula_vs_noise | 40 | +0.0185 | +0.0084 | 34/5/1 | 3.9e-09 | 7.8e-09 | [+0.0092, +0.0317] |
| xgboost | semantic_excess | 40 | +0.0038 | -0.0000 | 19/20/1 | 0.34 | 0.34 | [-0.0008, +0.0092] |

## claude-sonnet-4.6 (N=39)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 39 | +0.0044 | +0.0013 | 28/10/1 | 0.0011 | 0.0033 | [+0.0000, +0.0090] |
| logistic_regression | random_formula_semantic | 39 | +0.0107 | +0.0056 | 38/0/1 | 7.3e-12 | 2.9e-11 | [+0.0067, +0.0150] |
| logistic_regression | llm_vs_random_formula | 39 | +0.0054 | +0.0032 | 31/7/1 | 0.00077 | 0.0023 | [+0.0006, +0.0103] |
| logistic_regression | llm_semantic | 39 | +0.0144 | +0.0072 | 35/3/1 | 1.4e-07 | 4.2e-07 | [+0.0085, +0.0206] |
| logistic_regression | llm_direct | 39 | +0.0098 | +0.0041 | 33/5/1 | 9.1e-05 | 0.00037 | [+0.0036, +0.0163] |
| logistic_regression | random_formula_vs_noise | 39 | +0.0088 | +0.0055 | 36/2/1 | 6.3e-08 | 1.3e-07 | [+0.0051, +0.0131] |
| logistic_regression | semantic_excess | 39 | +0.0037 | +0.0011 | 28/10/1 | 0.023 | 0.023 | [-0.0017, +0.0091] |
| knn | random_formula_vs_raw | 39 | -0.0054 | -0.0028 | 10/29/0 | 0.0035 | 0.0071 | [-0.0095, -0.0017] |
| knn | random_formula_semantic | 39 | +0.0410 | +0.0282 | 37/2/0 | 3.6e-11 | 1.1e-10 | [+0.0289, +0.0547] |
| knn | llm_vs_random_formula | 39 | +0.0123 | +0.0090 | 33/6/0 | 8.9e-06 | 3.6e-05 | [+0.0065, +0.0189] |
| knn | llm_semantic | 39 | +0.0512 | +0.0361 | 38/1/0 | 9.1e-11 | 3.6e-10 | [+0.0376, +0.0657] |
| knn | llm_direct | 39 | +0.0068 | +0.0042 | 28/11/0 | 0.0062 | 0.019 | [+0.0020, +0.0121] |
| knn | random_formula_vs_noise | 39 | +0.0414 | +0.0301 | 36/3/0 | 5.4e-09 | 1.6e-08 | [+0.0280, +0.0560] |
| knn | semantic_excess | 39 | +0.0102 | +0.0045 | 27/12/0 | 0.011 | 0.021 | [+0.0013, +0.0201] |
| random_forest | random_formula_vs_raw | 39 | -0.0019 | -0.0013 | 9/29/1 | 5.4e-05 | 0.00022 | [-0.0030, -0.0008] |
| random_forest | random_formula_semantic | 39 | +0.0039 | +0.0006 | 25/13/1 | 0.049 | 0.049 | [-0.0003, +0.0093] |
| random_forest | llm_vs_random_formula | 39 | +0.0037 | +0.0006 | 24/14/1 | 0.01 | 0.021 | [+0.0014, +0.0068] |
| random_forest | llm_semantic | 39 | +0.0095 | +0.0019 | 29/9/1 | 0.0002 | 0.0002 | [+0.0028, +0.0194] |
| random_forest | llm_direct | 39 | +0.0019 | +0.0000 | 20/18/1 | 0.65 | 1 | [-0.0003, +0.0046] |
| random_forest | random_formula_vs_noise | 39 | +0.0069 | +0.0022 | 32/6/1 | 0.00019 | 0.00019 | [+0.0021, +0.0128] |
| random_forest | semantic_excess | 39 | +0.0056 | +0.0010 | 31/7/1 | 0.00057 | 0.0023 | [+0.0022, +0.0106] |
| xgboost | random_formula_vs_raw | 39 | -0.0006 | -0.0002 | 13/25/1 | 0.079 | 0.079 | [-0.0016, +0.0001] |
| xgboost | random_formula_semantic | 39 | +0.0049 | +0.0015 | 33/5/1 | 6.6e-06 | 1.3e-05 | [+0.0024, +0.0080] |
| xgboost | llm_vs_random_formula | 39 | -0.0003 | -0.0000 | 18/20/1 | 0.95 | 0.95 | [-0.0018, +0.0011] |
| xgboost | llm_semantic | 39 | +0.0065 | +0.0031 | 34/4/1 | 2.1e-05 | 4.1e-05 | [+0.0024, +0.0108] |
| xgboost | llm_direct | 39 | -0.0009 | -0.0003 | 17/21/1 | 0.53 | 1 | [-0.0033, +0.0010] |
| xgboost | random_formula_vs_noise | 39 | +0.0092 | +0.0046 | 37/1/1 | 1e-10 | 4.1e-10 | [+0.0062, +0.0128] |
| xgboost | semantic_excess | 39 | +0.0015 | +0.0007 | 28/10/1 | 0.0045 | 0.013 | [-0.0010, +0.0038] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 39 | +0.0054 | +0.0015 | 25/13/1 | 0.017 | 0.051 | [+0.0014, +0.0102] |
| logistic_regression | random_formula_semantic | 39 | +0.0122 | +0.0062 | 38/0/1 | 7.3e-12 | 2.9e-11 | [+0.0080, +0.0171] |
| logistic_regression | llm_vs_random_formula | 39 | +0.0071 | +0.0038 | 32/6/1 | 0.00021 | 0.00064 | [+0.0010, +0.0133] |
| logistic_regression | llm_semantic | 39 | +0.0204 | +0.0111 | 36/3/0 | 5e-10 | 1e-09 | [+0.0139, +0.0273] |
| logistic_regression | llm_direct | 39 | +0.0125 | +0.0057 | 31/7/1 | 3.4e-06 | 1.4e-05 | [+0.0061, +0.0196] |
| logistic_regression | random_formula_vs_noise | 39 | +0.0101 | +0.0045 | 31/7/1 | 1.1e-05 | 1.1e-05 | [+0.0054, +0.0155] |
| logistic_regression | semantic_excess | 39 | +0.0082 | +0.0049 | 32/7/0 | 0.00015 | 0.00044 | [+0.0020, +0.0143] |
| knn | random_formula_vs_raw | 39 | -0.0075 | -0.0068 | 9/29/1 | 0.00064 | 0.0026 | [-0.0123, -0.0028] |
| knn | random_formula_semantic | 39 | +0.0496 | +0.0359 | 37/1/1 | 2.2e-11 | 6.5e-11 | [+0.0354, +0.0656] |
| knn | llm_vs_random_formula | 39 | +0.0162 | +0.0159 | 30/8/1 | 2.9e-05 | 0.00011 | [+0.0082, +0.0244] |
| knn | llm_semantic | 39 | +0.0652 | +0.0532 | 36/2/1 | 1e-10 | 4.1e-10 | [+0.0493, +0.0818] |
| knn | llm_direct | 39 | +0.0087 | +0.0072 | 25/13/1 | 0.012 | 0.026 | [+0.0015, +0.0160] |
| knn | random_formula_vs_noise | 39 | +0.0501 | +0.0365 | 36/2/1 | 1e-10 | 4.1e-10 | [+0.0357, +0.0658] |
| knn | semantic_excess | 39 | +0.0155 | +0.0135 | 25/13/1 | 0.0013 | 0.0026 | [+0.0064, +0.0250] |
| random_forest | random_formula_vs_raw | 39 | +0.0004 | -0.0001 | 16/22/1 | 0.41 | 0.83 | [-0.0015, +0.0027] |
| random_forest | random_formula_semantic | 39 | +0.0234 | +0.0098 | 33/5/1 | 3.3e-09 | 6.5e-09 | [+0.0131, +0.0368] |
| random_forest | llm_vs_random_formula | 39 | +0.0076 | +0.0035 | 24/14/1 | 0.0035 | 0.0069 | [+0.0034, +0.0128] |
| random_forest | llm_semantic | 39 | +0.0343 | +0.0216 | 35/3/1 | 1.8e-10 | 5.5e-10 | [+0.0213, +0.0504] |
| random_forest | llm_direct | 39 | +0.0079 | +0.0023 | 26/12/1 | 0.0087 | 0.026 | [+0.0028, +0.0145] |
| random_forest | random_formula_vs_noise | 39 | +0.0321 | +0.0163 | 34/4/1 | 6.4e-10 | 1.9e-09 | [+0.0188, +0.0490] |
| random_forest | semantic_excess | 39 | +0.0109 | +0.0052 | 31/7/1 | 1.7e-05 | 7e-05 | [+0.0053, +0.0179] |
| xgboost | random_formula_vs_raw | 39 | +0.0003 | +0.0002 | 22/16/1 | 0.65 | 0.83 | [-0.0005, +0.0013] |
| xgboost | random_formula_semantic | 39 | +0.0113 | +0.0039 | 33/5/1 | 8.3e-08 | 8.3e-08 | [+0.0053, +0.0193] |
| xgboost | llm_vs_random_formula | 39 | +0.0019 | +0.0003 | 22/16/1 | 0.26 | 0.26 | [+0.0001, +0.0038] |
| xgboost | llm_semantic | 39 | +0.0156 | +0.0063 | 30/8/1 | 1.4e-06 | 1.4e-06 | [+0.0081, +0.0248] |
| xgboost | llm_direct | 39 | +0.0022 | +0.0001 | 20/18/1 | 0.23 | 0.23 | [+0.0001, +0.0045] |
| xgboost | random_formula_vs_noise | 39 | +0.0198 | +0.0098 | 33/5/1 | 1.1e-08 | 2.2e-08 | [+0.0101, +0.0335] |
| xgboost | semantic_excess | 39 | +0.0042 | +0.0017 | 24/14/1 | 0.015 | 0.015 | [+0.0013, +0.0079] |

## gemini-3.1-pro-preview (N=44)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 44 | +0.0019 | +0.0003 | 26/18/0 | 0.027 | 0.027 | [-0.0011, +0.0048] |
| logistic_regression | random_formula_semantic | 44 | +0.0071 | +0.0032 | 43/1/0 | 2.3e-13 | 9.1e-13 | [+0.0046, +0.0100] |
| logistic_regression | llm_vs_random_formula | 44 | +0.0062 | +0.0011 | 35/9/0 | 0.00017 | 0.00051 | [+0.0024, +0.0107] |
| logistic_regression | llm_semantic | 44 | +0.0134 | +0.0036 | 42/2/0 | 3.5e-11 | 1.4e-10 | [+0.0077, +0.0201] |
| logistic_regression | llm_direct | 44 | +0.0081 | +0.0009 | 33/11/0 | 0.00094 | 0.0038 | [+0.0031, +0.0141] |
| logistic_regression | random_formula_vs_noise | 44 | +0.0056 | +0.0032 | 41/3/0 | 6.5e-09 | 1.3e-08 | [+0.0032, +0.0084] |
| logistic_regression | semantic_excess | 44 | +0.0063 | +0.0005 | 28/16/0 | 0.0091 | 0.018 | [+0.0023, +0.0112] |
| knn | random_formula_vs_raw | 44 | -0.0067 | -0.0037 | 9/35/0 | 6.5e-05 | 0.0002 | [-0.0108, -0.0029] |
| knn | random_formula_semantic | 44 | +0.0366 | +0.0245 | 43/1/0 | 3.4e-13 | 1e-12 | [+0.0263, +0.0483] |
| knn | llm_vs_random_formula | 44 | +0.0119 | +0.0088 | 34/10/0 | 2.4e-05 | 9.7e-05 | [+0.0071, +0.0171] |
| knn | llm_semantic | 44 | +0.0476 | +0.0386 | 42/2/0 | 1.4e-10 | 4.3e-10 | [+0.0348, +0.0620] |
| knn | llm_direct | 44 | +0.0052 | +0.0004 | 22/22/0 | 0.15 | 0.46 | [+0.0005, +0.0105] |
| knn | random_formula_vs_noise | 44 | +0.0376 | +0.0249 | 42/2/0 | 6.1e-11 | 2.4e-10 | [+0.0261, +0.0506] |
| knn | semantic_excess | 44 | +0.0110 | +0.0098 | 33/11/0 | 0.00029 | 0.0012 | [+0.0041, +0.0181] |
| random_forest | random_formula_vs_raw | 44 | -0.0020 | -0.0009 | 8/35/1 | 5e-05 | 0.0002 | [-0.0041, -0.0004] |
| random_forest | random_formula_semantic | 44 | +0.0022 | +0.0003 | 26/17/1 | 0.32 | 0.32 | [-0.0014, +0.0063] |
| random_forest | llm_vs_random_formula | 44 | +0.0030 | +0.0008 | 28/15/1 | 0.0042 | 0.0085 | [+0.0009, +0.0059] |
| random_forest | llm_semantic | 44 | +0.0083 | +0.0011 | 26/17/1 | 0.026 | 0.026 | [+0.0017, +0.0191] |
| random_forest | llm_direct | 44 | +0.0010 | -0.0002 | 20/23/1 | 0.85 | 1 | [-0.0006, +0.0027] |
| random_forest | random_formula_vs_noise | 44 | +0.0060 | +0.0020 | 31/12/1 | 0.0048 | 0.0048 | [+0.0024, +0.0100] |
| random_forest | semantic_excess | 44 | +0.0062 | +0.0015 | 29/14/1 | 0.0017 | 0.0051 | [+0.0017, +0.0135] |
| xgboost | random_formula_vs_raw | 44 | -0.0010 | -0.0001 | 11/32/1 | 0.0014 | 0.0028 | [-0.0023, +0.0000] |
| xgboost | random_formula_semantic | 44 | +0.0041 | +0.0019 | 41/2/1 | 8.1e-09 | 1.6e-08 | [+0.0025, +0.0060] |
| xgboost | llm_vs_random_formula | 44 | +0.0007 | +0.0002 | 23/20/1 | 0.49 | 0.49 | [-0.0016, +0.0034] |
| xgboost | llm_semantic | 44 | +0.0081 | +0.0025 | 33/10/1 | 0.00019 | 0.00039 | [+0.0022, +0.0168] |
| xgboost | llm_direct | 44 | -0.0002 | -0.0001 | 18/25/1 | 0.6 | 1 | [-0.0024, +0.0017] |
| xgboost | random_formula_vs_noise | 44 | +0.0118 | +0.0042 | 39/4/1 | 1.2e-10 | 3.7e-10 | [+0.0070, +0.0181] |
| xgboost | semantic_excess | 44 | +0.0040 | +0.0007 | 26/17/1 | 0.048 | 0.048 | [-0.0008, +0.0111] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 44 | +0.0025 | +0.0010 | 28/16/0 | 0.021 | 0.062 | [+0.0001, +0.0051] |
| logistic_regression | random_formula_semantic | 44 | +0.0075 | +0.0039 | 40/4/0 | 3.4e-08 | 6.7e-08 | [+0.0048, +0.0105] |
| logistic_regression | llm_vs_random_formula | 44 | +0.0065 | +0.0009 | 30/14/0 | 0.0038 | 0.011 | [+0.0020, +0.0122] |
| logistic_regression | llm_semantic | 44 | +0.0142 | +0.0043 | 34/10/0 | 1e-05 | 1e-05 | [+0.0079, +0.0215] |
| logistic_regression | llm_direct | 44 | +0.0090 | +0.0019 | 29/15/0 | 0.0014 | 0.0057 | [+0.0034, +0.0159] |
| logistic_regression | random_formula_vs_noise | 44 | +0.0063 | +0.0037 | 36/8/0 | 3.6e-06 | 3.6e-06 | [+0.0036, +0.0092] |
| logistic_regression | semantic_excess | 44 | +0.0067 | +0.0011 | 27/17/0 | 0.026 | 0.027 | [+0.0017, +0.0127] |
| knn | random_formula_vs_raw | 44 | -0.0095 | -0.0053 | 5/37/2 | 1.4e-06 | 5.5e-06 | [-0.0151, -0.0049] |
| knn | random_formula_semantic | 44 | +0.0457 | +0.0277 | 40/3/1 | 5.7e-12 | 2.3e-11 | [+0.0325, +0.0609] |
| knn | llm_vs_random_formula | 44 | +0.0229 | +0.0104 | 33/10/1 | 2.1e-05 | 8.5e-05 | [+0.0123, +0.0355] |
| knn | llm_semantic | 44 | +0.0639 | +0.0471 | 40/2/2 | 3.2e-12 | 1.3e-11 | [+0.0456, +0.0857] |
| knn | llm_direct | 44 | +0.0134 | +0.0021 | 25/18/1 | 0.039 | 0.12 | [+0.0038, +0.0249] |
| knn | random_formula_vs_noise | 44 | +0.0439 | +0.0292 | 40/3/1 | 1.3e-11 | 5e-11 | [+0.0315, +0.0579] |
| knn | semantic_excess | 44 | +0.0182 | +0.0062 | 30/13/1 | 0.0016 | 0.0049 | [+0.0067, +0.0310] |
| random_forest | random_formula_vs_raw | 44 | +0.0008 | -0.0009 | 16/27/1 | 0.045 | 0.09 | [-0.0019, +0.0051] |
| random_forest | random_formula_semantic | 44 | +0.0183 | +0.0089 | 39/5/0 | 4.6e-09 | 1.4e-08 | [+0.0097, +0.0298] |
| random_forest | llm_vs_random_formula | 44 | +0.0049 | +0.0014 | 30/13/1 | 0.009 | 0.018 | [+0.0019, +0.0082] |
| random_forest | llm_semantic | 44 | +0.0268 | +0.0129 | 39/5/0 | 3.1e-10 | 9.4e-10 | [+0.0159, +0.0407] |
| random_forest | llm_direct | 44 | +0.0057 | +0.0005 | 24/19/1 | 0.18 | 0.22 | [+0.0009, +0.0122] |
| random_forest | random_formula_vs_noise | 44 | +0.0269 | +0.0160 | 37/7/0 | 1.7e-09 | 5.1e-09 | [+0.0158, +0.0419] |
| random_forest | semantic_excess | 44 | +0.0085 | +0.0036 | 35/9/0 | 8.4e-06 | 3.4e-05 | [+0.0048, +0.0130] |
| xgboost | random_formula_vs_raw | 44 | -0.0002 | +0.0002 | 23/21/0 | 0.88 | 0.88 | [-0.0011, +0.0007] |
| xgboost | random_formula_semantic | 44 | +0.0088 | +0.0038 | 40/4/0 | 8.2e-08 | 8.2e-08 | [+0.0039, +0.0162] |
| xgboost | llm_vs_random_formula | 44 | +0.0019 | +0.0003 | 26/18/0 | 0.21 | 0.21 | [-0.0003, +0.0042] |
| xgboost | llm_semantic | 44 | +0.0120 | +0.0068 | 36/8/0 | 2.7e-08 | 5.5e-08 | [+0.0072, +0.0185] |
| xgboost | llm_direct | 44 | +0.0017 | +0.0007 | 26/18/0 | 0.11 | 0.22 | [-0.0005, +0.0040] |
| xgboost | random_formula_vs_noise | 44 | +0.0172 | +0.0083 | 40/4/0 | 3.2e-09 | 6.3e-09 | [+0.0089, +0.0295] |
| xgboost | semantic_excess | 44 | +0.0032 | +0.0019 | 28/16/0 | 0.013 | 0.027 | [+0.0005, +0.0061] |

## gpt-5.5-pro (N=48)

### roc_auc_ovr

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 48 | +0.0039 | +0.0003 | 28/20/0 | 0.032 | 0.065 | [+0.0004, +0.0079] |
| logistic_regression | random_formula_semantic | 48 | +0.0088 | +0.0031 | 44/4/0 | 5e-13 | 1.5e-12 | [+0.0056, +0.0127] |
| logistic_regression | llm_vs_random_formula | 48 | +0.0069 | +0.0012 | 36/12/0 | 0.00019 | 0.00058 | [+0.0029, +0.0115] |
| logistic_regression | llm_semantic | 48 | +0.0150 | +0.0056 | 46/1/1 | 7.1e-14 | 2.8e-13 | [+0.0098, +0.0209] |
| logistic_regression | llm_direct | 48 | +0.0108 | +0.0025 | 33/14/1 | 4.9e-05 | 0.0002 | [+0.0055, +0.0168] |
| logistic_regression | random_formula_vs_noise | 48 | +0.0079 | +0.0030 | 40/8/0 | 1.1e-07 | 2.2e-07 | [+0.0047, +0.0117] |
| logistic_regression | semantic_excess | 48 | +0.0062 | +0.0008 | 32/16/0 | 0.0045 | 0.0088 | [+0.0018, +0.0112] |
| knn | random_formula_vs_raw | 48 | -0.0060 | -0.0042 | 9/39/0 | 0.00031 | 0.00092 | [-0.0104, -0.0017] |
| knn | random_formula_semantic | 48 | +0.0388 | +0.0267 | 47/1/0 | 1.4e-13 | 5.4e-13 | [+0.0284, +0.0508] |
| knn | llm_vs_random_formula | 48 | +0.0135 | +0.0086 | 35/13/0 | 5.2e-05 | 0.00021 | [+0.0076, +0.0198] |
| knn | llm_semantic | 48 | +0.0520 | +0.0446 | 44/4/0 | 1.2e-10 | 3.6e-10 | [+0.0387, +0.0664] |
| knn | llm_direct | 48 | +0.0076 | +0.0026 | 29/19/0 | 0.015 | 0.046 | [+0.0023, +0.0132] |
| knn | random_formula_vs_noise | 48 | +0.0402 | +0.0290 | 41/7/0 | 1.2e-10 | 4.8e-10 | [+0.0284, +0.0534] |
| knn | semantic_excess | 48 | +0.0132 | +0.0114 | 33/15/0 | 0.00023 | 0.00094 | [+0.0063, +0.0203] |
| random_forest | random_formula_vs_raw | 48 | -0.0019 | -0.0012 | 8/38/2 | 7.6e-08 | 3e-07 | [-0.0026, -0.0012] |
| random_forest | random_formula_semantic | 48 | +0.0032 | +0.0004 | 28/18/2 | 0.097 | 0.097 | [-0.0006, +0.0083] |
| random_forest | llm_vs_random_formula | 48 | +0.0045 | +0.0001 | 28/18/2 | 0.021 | 0.042 | [+0.0017, +0.0079] |
| random_forest | llm_semantic | 48 | +0.0099 | +0.0018 | 32/14/2 | 0.0026 | 0.0026 | [+0.0029, +0.0191] |
| random_forest | llm_direct | 48 | +0.0026 | -0.0001 | 20/26/2 | 0.93 | 1 | [+0.0001, +0.0058] |
| random_forest | random_formula_vs_noise | 48 | +0.0068 | +0.0018 | 36/10/2 | 0.00062 | 0.00062 | [+0.0023, +0.0123] |
| random_forest | semantic_excess | 48 | +0.0067 | +0.0012 | 34/12/2 | 0.0011 | 0.0032 | [+0.0025, +0.0118] |
| xgboost | random_formula_vs_raw | 48 | -0.0006 | -0.0001 | 17/28/3 | 0.093 | 0.093 | [-0.0013, +0.0001] |
| xgboost | random_formula_semantic | 48 | +0.0048 | +0.0012 | 40/5/3 | 1.3e-07 | 2.5e-07 | [+0.0026, +0.0076] |
| xgboost | llm_vs_random_formula | 48 | +0.0014 | +0.0000 | 24/21/3 | 0.46 | 0.46 | [-0.0004, +0.0037] |
| xgboost | llm_semantic | 48 | +0.0098 | +0.0026 | 37/8/3 | 5.7e-06 | 1.1e-05 | [+0.0034, +0.0178] |
| xgboost | llm_direct | 48 | +0.0009 | -0.0000 | 21/24/3 | 0.93 | 1 | [-0.0013, +0.0032] |
| xgboost | random_formula_vs_noise | 48 | +0.0124 | +0.0042 | 41/4/3 | 1.4e-10 | 4.8e-10 | [+0.0071, +0.0188] |
| xgboost | semantic_excess | 48 | +0.0050 | +0.0007 | 32/13/3 | 0.0044 | 0.0088 | [+0.0003, +0.0107] |

### balanced_accuracy

| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |
|---|---|---|---|---|---|---|---|---|
| logistic_regression | random_formula_vs_raw | 48 | +0.0057 | +0.0012 | 32/16/0 | 0.0019 | 0.0057 | [+0.0020, +0.0104] |
| logistic_regression | random_formula_semantic | 48 | +0.0105 | +0.0038 | 42/6/0 | 1.1e-10 | 3.2e-10 | [+0.0066, +0.0154] |
| logistic_regression | llm_vs_random_formula | 48 | +0.0072 | +0.0024 | 31/17/0 | 0.013 | 0.039 | [+0.0021, +0.0130] |
| logistic_regression | llm_semantic | 48 | +0.0164 | +0.0070 | 40/8/0 | 2.5e-08 | 5e-08 | [+0.0099, +0.0239] |
| logistic_regression | llm_direct | 48 | +0.0129 | +0.0041 | 36/12/0 | 1.1e-05 | 4.4e-05 | [+0.0065, +0.0202] |
| logistic_regression | random_formula_vs_noise | 48 | +0.0096 | +0.0037 | 38/10/0 | 2.6e-07 | 2.6e-07 | [+0.0057, +0.0145] |
| logistic_regression | semantic_excess | 48 | +0.0059 | +0.0013 | 31/17/0 | 0.08 | 0.097 | [-0.0001, +0.0126] |
| knn | random_formula_vs_raw | 48 | -0.0092 | -0.0044 | 12/35/1 | 0.00021 | 0.00085 | [-0.0159, -0.0029] |
| knn | random_formula_semantic | 48 | +0.0522 | +0.0330 | 46/1/1 | 1.3e-12 | 5e-12 | [+0.0367, +0.0699] |
| knn | llm_vs_random_formula | 48 | +0.0218 | +0.0096 | 34/13/1 | 5.2e-05 | 0.00021 | [+0.0112, +0.0344] |
| knn | llm_semantic | 48 | +0.0744 | +0.0555 | 45/1/2 | 8.5e-14 | 3.4e-13 | [+0.0538, +0.0976] |
| knn | llm_direct | 48 | +0.0127 | +0.0018 | 28/19/1 | 0.029 | 0.086 | [+0.0036, +0.0222] |
| knn | random_formula_vs_noise | 48 | +0.0543 | +0.0352 | 42/5/1 | 7.1e-11 | 2.8e-10 | [+0.0357, +0.0780] |
| knn | semantic_excess | 48 | +0.0221 | +0.0092 | 35/12/1 | 0.00017 | 0.00067 | [+0.0107, +0.0350] |
| random_forest | random_formula_vs_raw | 48 | +0.0006 | -0.0003 | 20/26/2 | 0.33 | 0.67 | [-0.0013, +0.0029] |
| random_forest | random_formula_semantic | 48 | +0.0194 | +0.0087 | 37/9/2 | 4.5e-09 | 9e-09 | [+0.0110, +0.0304] |
| random_forest | llm_vs_random_formula | 48 | +0.0088 | +0.0012 | 28/19/1 | 0.013 | 0.039 | [+0.0017, +0.0176] |
| random_forest | llm_semantic | 48 | +0.0322 | +0.0152 | 39/8/1 | 1.6e-10 | 4.9e-10 | [+0.0189, +0.0485] |
| random_forest | llm_direct | 48 | +0.0093 | +0.0006 | 26/20/2 | 0.034 | 0.086 | [+0.0023, +0.0185] |
| random_forest | random_formula_vs_noise | 48 | +0.0278 | +0.0161 | 39/8/1 | 1.6e-09 | 4.8e-09 | [+0.0164, +0.0424] |
| random_forest | semantic_excess | 48 | +0.0128 | +0.0035 | 30/17/1 | 0.00039 | 0.0012 | [+0.0047, +0.0226] |
| xgboost | random_formula_vs_raw | 48 | -0.0004 | +0.0000 | 23/22/3 | 0.96 | 0.96 | [-0.0013, +0.0005] |
| xgboost | random_formula_semantic | 48 | +0.0091 | +0.0034 | 40/6/2 | 1e-08 | 1e-08 | [+0.0047, +0.0149] |
| xgboost | llm_vs_random_formula | 48 | +0.0030 | -0.0006 | 18/28/2 | 0.78 | 0.78 | [-0.0012, +0.0099] |
| xgboost | llm_semantic | 48 | +0.0142 | +0.0053 | 35/11/2 | 2.3e-05 | 2.3e-05 | [+0.0057, +0.0253] |
| xgboost | llm_direct | 48 | +0.0027 | -0.0004 | 18/28/2 | 0.7 | 0.7 | [-0.0014, +0.0090] |
| xgboost | random_formula_vs_noise | 48 | +0.0177 | +0.0070 | 39/7/2 | 1.4e-08 | 2.8e-08 | [+0.0092, +0.0291] |
| xgboost | semantic_excess | 48 | +0.0051 | +0.0006 | 30/16/2 | 0.049 | 0.097 | [+0.0001, +0.0124] |
