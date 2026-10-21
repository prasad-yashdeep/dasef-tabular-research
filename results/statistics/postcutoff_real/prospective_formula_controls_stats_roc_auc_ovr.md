# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 34
- Matrix comparisons analyzed: 544
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 188
- Comparisons with 95% bootstrap CI entirely below zero: 214
- Formula-vs-raw comparisons: 136
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema    | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3417 | [+0.3372, +0.3460] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3263 | [+0.3216, +0.3305] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3141 | [+0.3100, +0.3179] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3086 | [+0.3041, +0.3130] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3086 | [+0.3041, +0.3124] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2389 | [+0.2342, +0.2432] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.2219 | [+0.2160, +0.2272] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2038 | [+0.1995, +0.2081] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2004 | [+0.1963, +0.2048] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1879 | [+0.1826, +0.1926] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1835 | [+0.1782, +0.1884] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1585 | [+0.1541, +0.1629] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1561 | [+0.1507, +0.1613] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1426 | [+0.1373, +0.1473] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1356 | [+0.1304, +0.1401] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1046 | [+0.0936, +0.1155] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1039 | [+0.0921, +0.1157] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1037 | [+0.0927, +0.1147] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1022 | [+0.0916, +0.1126] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1011 | [+0.0906, +0.1117] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema    | model   | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------|:-------------------------------|--------:|:-------------------|------:|
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2485 | [-0.2535, -0.2434] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2435 | [-0.2497, -0.2367] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2435 | [-0.2497, -0.2367] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2409 | [-0.2468, -0.2342] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2409 | [-0.2468, -0.2342] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1173 | [-0.1263, -0.1099] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1173 | [-0.1263, -0.1099] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1173 | [-0.1263, -0.1099] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1173 | [-0.1263, -0.1099] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1173 | [-0.1263, -0.1099] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1173 | [-0.1263, -0.1099] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.0979 | [-0.1088, -0.0869] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.0979 | [-0.1088, -0.0869] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.0979 | [-0.1088, -0.0869] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.0979 | [-0.1088, -0.0869] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema    | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3417 | [+0.3372, +0.3460] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3263 | [+0.3216, +0.3305] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3141 | [+0.3100, +0.3179] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3086 | [+0.3041, +0.3130] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3086 | [+0.3041, +0.3124] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2389 | [+0.2342, +0.2432] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.2219 | [+0.2160, +0.2272] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2038 | [+0.1995, +0.2081] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2004 | [+0.1963, +0.2048] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1879 | [+0.1826, +0.1926] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1835 | [+0.1782, +0.1884] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1585 | [+0.1541, +0.1629] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema    | model   | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------|:-------------------------------|--------:|:-------------------|------:|
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2485 | [-0.2535, -0.2434] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2435 | [-0.2497, -0.2367] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.2435 | [-0.2497, -0.2367] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.2427 | [-0.2476, -0.2375] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
