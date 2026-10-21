# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 31
- Matrix comparisons analyzed: 496
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 138
- Comparisons with 95% bootstrap CI entirely below zero: 174
- Formula-vs-raw comparisons: 124
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema                 | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| pricerunner                            | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.44   | [+0.4280, +0.4509] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2535 | [+0.2408, +0.2650] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2502 | [+0.2346, +0.2665] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.2213 | [+0.2080, +0.2355] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2203 | [+0.2098, +0.2319] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1686 | [+0.1560, +0.1823] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1637 | [+0.1507, +0.1790] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.1531 | [+0.1411, +0.1658] | 0.002 |
| loan_status                            | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1407 | [+0.1285, +0.1518] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1406 | [+0.1307, +0.1500] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.1279 | [+0.1141, +0.1428] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost             | raw -> raw_plus_formula                     |  0.1249 | [+0.1093, +0.1414] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.1095 | [+0.0997, +0.1191] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.1066 | [+0.1007, +0.1126] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1062 | [+0.0998, +0.1126] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1057 | [+0.0983, +0.1127] | 0.002 |
| house_8l                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0964 | [+0.0890, +0.1028] | 0.002 |
| kr_vs_kp                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0904 | [+0.0802, +0.0998] | 0.002 |
| customer_churn_classification_nominal  | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0879 | [+0.0798, +0.0957] | 0.002 |
| splice                                 | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.086  | [+0.0785, +0.0939] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema                 | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| pricerunner                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.6885 | [-0.6983, -0.6797] | 0.002 |
| pricerunner                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.4463 | [-0.4573, -0.4348] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1726 | [-0.1899, -0.1573] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1439 | [-0.1553, -0.1322] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.1368 | [-0.1485, -0.1242] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1347 | [-0.1474, -0.1229] | 0.002 |
| loan_status                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.1256 | [-0.1382, -0.1114] | 0.002 |
| kr_vs_kp                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1248 | [-0.1343, -0.1155] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1247 | [-0.1356, -0.1137] | 0.002 |
| law_school_admission_bianry            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.121  | [-0.1313, -0.1129] | 0.002 |
| loan_status                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1202 | [-0.1331, -0.1064] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1124 | [-0.1207, -0.1014] | 0.002 |
| kr_vs_kp                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1114 | [-0.1209, -0.1031] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost       | raw -> raw_plus_random_all     | -0.1017 | [-0.1158, -0.0884] | 0.002 |
| law_school_admission_bianry            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1009 | [-0.1113, -0.0898] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.0978 | [-0.1088, -0.0894] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.0971 | [-0.1091, -0.0859] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost       | raw -> raw_plus_random_formula | -0.0965 | [-0.1138, -0.0793] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema                 | model         | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------|:--------------------------------------------|--------:|:-------------------|------:|
| pricerunner                            | gpt-5.5-pro/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.44   | [+0.4280, +0.4509] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest | raw_plus_random_formula -> raw_plus_formula |  0.2535 | [+0.2408, +0.2650] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | random_forest | raw_plus_random_formula -> raw_plus_formula |  0.2502 | [+0.2346, +0.2665] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost       | raw_plus_random_formula -> raw_plus_formula |  0.2213 | [+0.2080, +0.2355] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.2203 | [+0.2098, +0.2319] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1686 | [+0.1560, +0.1823] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1637 | [+0.1507, +0.1790] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_formula                     |  0.1531 | [+0.1411, +0.1658] | 0.002 |
| loan_status                            | gpt-5.5-pro/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1407 | [+0.1285, +0.1518] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1406 | [+0.1307, +0.1500] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_formula                     |  0.1279 | [+0.1141, +0.1428] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost       | raw -> raw_plus_formula                     |  0.1249 | [+0.1093, +0.1414] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema                 | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| pricerunner                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.6885 | [-0.6983, -0.6797] | 0.002 |
| pricerunner                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.4463 | [-0.4573, -0.4348] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1726 | [-0.1899, -0.1573] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1439 | [-0.1553, -0.1322] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.1368 | [-0.1485, -0.1242] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1347 | [-0.1474, -0.1229] | 0.002 |
| loan_status                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
