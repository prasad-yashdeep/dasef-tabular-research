# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 34
- Matrix comparisons analyzed: 544
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 182
- Comparisons with 95% bootstrap CI entirely below zero: 175
- Formula-vs-raw comparisons: 136
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema    | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2832 | [+0.2796, +0.2866] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2588 | [+0.2555, +0.2616] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2379 | [+0.2342, +0.2415] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2344 | [+0.2298, +0.2385] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.2331 | [+0.2301, +0.2360] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2322 | [+0.2274, +0.2365] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2306 | [+0.2278, +0.2331] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2158 | [+0.2118, +0.2192] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2086 | [+0.2038, +0.2124] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2043 | [+0.2004, +0.2080] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2006 | [+0.1957, +0.2051] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1983 | [+0.1946, +0.2018] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.196  | [+0.1927, +0.1993] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1933 | [+0.1885, +0.1985] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1929 | [+0.1895, +0.1962] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1914 | [+0.1870, +0.1958] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1908 | [+0.1869, +0.1949] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1904 | [+0.1872, +0.1938] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1892 | [+0.1856, +0.1930] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.1804 | [+0.1774, +0.1831] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema    | model   | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------|:-------------------------------|--------:|:-------------------|------:|
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all     | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.1312 | [-0.1346, -0.1279] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.1312 | [-0.1346, -0.1279] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.1312 | [-0.1346, -0.1279] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.1312 | [-0.1346, -0.1279] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all     | -0.1312 | [-0.1346, -0.1279] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.1302 | [-0.1333, -0.1271] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.1299 | [-0.1331, -0.1263] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.1299 | [-0.1331, -0.1263] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.1291 | [-0.1326, -0.1254] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_formula | -0.1291 | [-0.1326, -0.1254] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.128  | [-0.1396, -0.1166] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.128  | [-0.1396, -0.1166] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.128  | [-0.1396, -0.1166] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_formula | -0.128  | [-0.1396, -0.1166] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema    | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2832 | [+0.2796, +0.2866] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2588 | [+0.2555, +0.2616] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2379 | [+0.2342, +0.2415] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2344 | [+0.2298, +0.2385] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw -> raw_plus_formula                     |  0.2331 | [+0.2301, +0.2360] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2322 | [+0.2274, +0.2365] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2306 | [+0.2278, +0.2331] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2158 | [+0.2118, +0.2192] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2086 | [+0.2038, +0.2124] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2043 | [+0.2004, +0.2080] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2006 | [+0.1957, +0.2051] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1983 | [+0.1946, +0.2018] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema    | model   | pair                       |   delta | 95% CI             |     p |
|:---------------------------------------|:----------|:--------|:---------------------------|--------:|:-------------------|------:|
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_ro_real_estate_20260503     | None/None | knn     | raw -> raw_plus_random_all | -0.1482 | [-0.1603, -0.1355] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all | -0.1312 | [-0.1346, -0.1279] | 0.002 |
| postcutoff_prediction_markets_20260517 | None/None | knn     | raw -> raw_plus_random_all | -0.1312 | [-0.1346, -0.1279] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
