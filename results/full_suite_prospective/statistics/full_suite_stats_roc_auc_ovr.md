# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 48
- Matrix comparisons analyzed: 768
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 202
- Comparisons with 95% bootstrap CI entirely below zero: 353
- Formula-vs-raw comparisons: 192
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset           | schema                              | model               | pair                                        |   delta | 95% CI             |     p |
|:------------------|:------------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| car_evaluation    | gemini-3.1-pro-preview/distance_knn | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1849 | [+0.1730, +0.1992] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/tree              | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1711 | [+0.1576, +0.1874] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/linear_svm   | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1682 | [+0.1537, +0.1857] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/distance_knn      | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1657 | [+0.1515, +0.1794] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/tree         | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1636 | [+0.1510, +0.1787] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/tree              | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1601 | [+0.1509, +0.1688] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/tree              | logistic_regression | raw -> raw_plus_formula                     |  0.1509 | [+0.1408, +0.1599] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/distance_knn | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1501 | [+0.1431, +0.1569] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/linear_svm        | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1476 | [+0.1333, +0.1620] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1437 | [+0.1380, +0.1506] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/distance_knn | logistic_regression | raw -> raw_plus_formula                     |  0.1409 | [+0.1329, +0.1488] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/tree         | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1374 | [+0.1309, +0.1439] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw -> raw_plus_formula                     |  0.1345 | [+0.1256, +0.1436] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/tree         | logistic_regression | raw -> raw_plus_formula                     |  0.1282 | [+0.1220, +0.1345] | 0.002 |
| electricity       | claude-sonnet-4.6/tree              | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1146 | [+0.1116, +0.1185] | 0.002 |
| electricity       | gemini-3.1-pro-preview/linear_svm   | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1101 | [+0.1079, +0.1126] | 0.002 |
| blood_transfusion | gemini-3.1-pro-preview/tree         | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1066 | [+0.0793, +0.1330] | 0.002 |
| blood_transfusion | gemini-3.1-pro-preview/linear_svm   | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1066 | [+0.0756, +0.1377] | 0.002 |
| blood_transfusion | claude-sonnet-4.6/distance_knn      | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1057 | [+0.0710, +0.1417] | 0.002 |
| electricity       | gemini-3.1-pro-preview/distance_knn | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1051 | [+0.1023, +0.1086] | 0.002 |

## Negative CI Excluding Zero

| dataset           | schema                              | model   | pair                           |   delta | 95% CI             |     p |
|:------------------|:------------------------------------|:--------|:-------------------------------|--------:|:-------------------|------:|
| car_evaluation    | claude-sonnet-4.6/linear_svm        | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/tree         | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/linear_svm   | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_formula | -0.1769 | [-0.1923, -0.1626] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/tree         | knn     | raw -> raw_plus_random_formula | -0.1769 | [-0.1923, -0.1626] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_formula | -0.1769 | [-0.1923, -0.1626] | 0.002 |
| car_evaluation    | gemini-3.1-pro-preview/linear_svm   | knn     | raw -> raw_plus_random_formula | -0.1769 | [-0.1923, -0.1626] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/linear_svm        | knn     | raw -> raw_plus_random_formula | -0.1717 | [-0.1871, -0.1557] | 0.002 |
| car_evaluation    | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_formula | -0.1717 | [-0.1871, -0.1557] | 0.002 |
| electricity       | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_all     | -0.1192 | [-0.1220, -0.1161] | 0.002 |
| electricity       | gemini-3.1-pro-preview/tree         | knn     | raw -> raw_plus_random_all     | -0.1192 | [-0.1220, -0.1161] | 0.002 |
| electricity       | gemini-3.1-pro-preview/linear_svm   | knn     | raw -> raw_plus_random_all     | -0.1192 | [-0.1220, -0.1161] | 0.002 |
| electricity       | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_all     | -0.1192 | [-0.1220, -0.1161] | 0.002 |
| electricity       | gemini-3.1-pro-preview/linear_svm   | knn     | raw -> raw_plus_random_formula | -0.1139 | [-0.1163, -0.1118] | 0.002 |
| blood_transfusion | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_formula | -0.1123 | [-0.1511, -0.0770] | 0.002 |
| blood_transfusion | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_formula | -0.1123 | [-0.1511, -0.0770] | 0.002 |
| blood_transfusion | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_formula | -0.1123 | [-0.1511, -0.0770] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset        | schema                              | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1849 | [+0.1730, +0.1992] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1711 | [+0.1576, +0.1874] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1682 | [+0.1537, +0.1857] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1657 | [+0.1515, +0.1794] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1636 | [+0.1510, +0.1787] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1601 | [+0.1509, +0.1688] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | logistic_regression | raw -> raw_plus_formula                     |  0.1509 | [+0.1408, +0.1599] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1501 | [+0.1431, +0.1569] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1476 | [+0.1333, +0.1620] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1437 | [+0.1380, +0.1506] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | logistic_regression | raw -> raw_plus_formula                     |  0.1409 | [+0.1329, +0.1488] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1374 | [+0.1309, +0.1439] | 0.002 |

## Largest Negative Deltas

| dataset        | schema                              | model   | pair                           |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------|:-------------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_all     | -0.2053 | [-0.2242, -0.1877] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_formula | -0.1769 | [-0.1923, -0.1626] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_formula | -0.1769 | [-0.1923, -0.1626] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
