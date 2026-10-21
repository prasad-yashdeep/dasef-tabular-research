# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 30
- Matrix comparisons analyzed: 480
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 142
- Comparisons with 95% bootstrap CI entirely below zero: 214
- Formula-vs-raw comparisons: 120
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema                     | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2153 | [+0.2003, +0.2313] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1819 | [+0.1686, +0.1964] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1229 | [+0.0848, +0.1620] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1227 | [+0.1089, +0.1358] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1101 | [+0.0848, +0.1330] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1008 | [+0.0917, +0.1087] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0991 | [+0.0867, +0.1103] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0914 | [+0.0802, +0.1020] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0813 | [+0.0398, +0.1267] | 0.01  |
| house_8l                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0772 | [+0.0690, +0.0853] | 0.002 |
| fried                                  | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0754 | [+0.0693, +0.0817] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.073  | [+0.0669, +0.0793] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0705 | [+0.0628, +0.0772] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0685 | [+0.0620, +0.0747] | 0.002 |
| customer_churn_classification_nominal  | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0684 | [+0.0625, +0.0738] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0681 | [+0.0575, +0.0786] | 0.002 |
| house_16h                              | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.066  | [+0.0549, +0.0773] | 0.002 |
| customer_churn_classification_nominal  | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0655 | [+0.0594, +0.0712] | 0.002 |
| news_channel                           | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0625 | [+0.0549, +0.0699] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0618 | [+0.0445, +0.0804] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema                     | model               | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------------|:-------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1471 | [-0.1566, -0.1378] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | random_forest       | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.136  | [-0.1495, -0.1232] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1318 | [-0.1376, -0.1265] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1252 | [-0.1326, -0.1169] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | xgboost             | raw -> raw_plus_random_formula | -0.1087 | [-0.1437, -0.0775] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0981 | [-0.1224, -0.0767] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0924 | [-0.1512, -0.0442] | 0.006 |
| volcanoes_c1                           | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_random_all     | -0.0879 | [-0.1229, -0.0573] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | random_forest       | raw -> raw_plus_random_formula | -0.0867 | [-0.1475, -0.0279] | 0.027 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0841 | [-0.1222, -0.0490] | 0.01  |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0836 | [-0.0895, -0.0779] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0797 | [-0.0857, -0.0728] | 0.002 |
| house_8l                               | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.0791, -0.0672] | 0.002 |
| volcanoes_c1                           | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.1061, -0.0423] | 0.006 |
| airlines                               | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0723 | [-0.0832, -0.0613] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0713 | [-0.0899, -0.0507] | 0.002 |
| house_16h                              | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.067  | [-0.0727, -0.0612] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema                     | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2153 | [+0.2003, +0.2313] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1819 | [+0.1686, +0.1964] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1229 | [+0.0848, +0.1620] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1227 | [+0.1089, +0.1358] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1101 | [+0.0848, +0.1330] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1008 | [+0.0917, +0.1087] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0991 | [+0.0867, +0.1103] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0914 | [+0.0802, +0.1020] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0813 | [+0.0398, +0.1267] | 0.01  |
| house_8l                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0772 | [+0.0690, +0.0853] | 0.002 |
| fried                                  | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0754 | [+0.0693, +0.0817] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.073  | [+0.0669, +0.0793] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema                     | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1471 | [-0.1566, -0.1378] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| employee_turnover_at_techco            | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.136  | [-0.1495, -0.1232] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1318 | [-0.1376, -0.1265] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1252 | [-0.1326, -0.1169] | 0.002 |
| amazon_employee_access                 | claude-opus-4.7/linear_svm | xgboost       | raw -> raw_plus_random_formula | -0.1087 | [-0.1437, -0.0775] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
