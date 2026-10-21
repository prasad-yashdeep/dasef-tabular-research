# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 29
- Matrix comparisons analyzed: 464
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 129
- Comparisons with 95% bootstrap CI entirely below zero: 167
- Formula-vs-raw comparisons: 116
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema                       | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| online_shoppers                        | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1931 | [+0.1787, +0.2100] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1626 | [+0.1462, +0.1770] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.15   | [+0.1373, +0.1661] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1482 | [+0.1355, +0.1622] | 0.002 |
| loan_status                            | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1471 | [+0.1339, +0.1581] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1352 | [+0.1205, +0.1491] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1169 | [+0.1040, +0.1319] | 0.002 |
| law_school_admission_bianry            | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1117 | [+0.0972, +0.1267] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1108 | [+0.0894, +0.1322] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.0961 | [+0.0861, +0.1082] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0948 | [+0.0860, +0.1034] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0817 | [+0.0749, +0.0890] | 0.002 |
| house_8l                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0812 | [+0.0730, +0.0887] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0806 | [+0.0720, +0.0891] | 0.002 |
| customer_churn_classification_nominal  | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0772 | [+0.0710, +0.0832] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.076  | [+0.0643, +0.0882] | 0.002 |
| house_16h                              | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0672 | [+0.0587, +0.0755] | 0.002 |
| customer_churn_classification_nominal  | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0653 | [+0.0569, +0.0738] | 0.002 |
| news_channel                           | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.064  | [+0.0556, +0.0718] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0627 | [+0.0510, +0.0739] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema                       | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1716 | [-0.1864, -0.1567] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1439 | [-0.1553, -0.1322] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1424 | [-0.1530, -0.1320] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.1368 | [-0.1485, -0.1242] | 0.002 |
| loan_status                            | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.1277 | [-0.1417, -0.1111] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1248 | [-0.1343, -0.1155] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1247 | [-0.1356, -0.1137] | 0.002 |
| law_school_admission_bianry            | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.121  | [-0.1313, -0.1129] | 0.002 |
| loan_status                            | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1202 | [-0.1331, -0.1064] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1124 | [-0.1207, -0.1014] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1114 | [-0.1209, -0.1031] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | xgboost       | raw -> raw_plus_random_all     | -0.1029 | [-0.1167, -0.0889] | 0.002 |
| law_school_admission_bianry            | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1009 | [-0.1113, -0.0898] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.0978 | [-0.1088, -0.0894] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.0971 | [-0.1091, -0.0859] | 0.002 |
| house_8l                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0953 | [-0.1086, -0.0818] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | xgboost       | raw -> raw_plus_random_formula | -0.0929 | [-0.1150, -0.0691] | 0.002 |
| house_16h                              | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0848 | [-0.0906, -0.0788] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema                       | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| online_shoppers                        | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1931 | [+0.1787, +0.2100] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1626 | [+0.1462, +0.1770] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.15   | [+0.1373, +0.1661] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1482 | [+0.1355, +0.1622] | 0.002 |
| loan_status                            | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1471 | [+0.1339, +0.1581] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1352 | [+0.1205, +0.1491] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1169 | [+0.1040, +0.1319] | 0.002 |
| law_school_admission_bianry            | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1117 | [+0.0972, +0.1267] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1108 | [+0.0894, +0.1322] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.0961 | [+0.0861, +0.1082] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0948 | [+0.0860, +0.1034] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0817 | [+0.0749, +0.0890] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema                       | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1716 | [-0.1864, -0.1567] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1439 | [-0.1553, -0.1322] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1424 | [-0.1530, -0.1320] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.1368 | [-0.1485, -0.1242] | 0.002 |
| loan_status                            | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.1277 | [-0.1417, -0.1111] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1248 | [-0.1343, -0.1155] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
