# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 30
- Matrix comparisons analyzed: 480
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 148
- Comparisons with 95% bootstrap CI entirely below zero: 176
- Formula-vs-raw comparisons: 120
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema                     | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| online_shoppers                        | claude-opus-4.7/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2618 | [+0.2467, +0.2805] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.241  | [+0.2306, +0.2509] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1846 | [+0.1727, +0.1970] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1808 | [+0.1647, +0.1959] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1796 | [+0.1599, +0.1983] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.1617 | [+0.1526, +0.1737] | 0.002 |
| loan_status                            | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1394 | [+0.1267, +0.1510] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1335 | [+0.1142, +0.1533] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1333 | [+0.1175, +0.1480] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.1255 | [+0.1134, +0.1369] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1088 | [+0.0982, +0.1193] | 0.002 |
| house_8l                               | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0996 | [+0.0926, +0.1069] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0898 | [+0.0791, +0.0987] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.088  | [+0.0789, +0.0974] | 0.002 |
| splice                                 | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0874 | [+0.0777, +0.0968] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0863 | [+0.0758, +0.0967] | 0.002 |
| customer_churn_classification_nominal  | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0855 | [+0.0766, +0.0982] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0814 | [+0.0730, +0.0910] | 0.002 |
| fried                                  | claude-opus-4.7/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0784 | [+0.0684, +0.0879] | 0.002 |
| splice                                 | claude-opus-4.7/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0766 | [+0.0701, +0.0840] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema                     | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1716 | [-0.1864, -0.1567] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1439 | [-0.1553, -0.1322] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1424 | [-0.1530, -0.1320] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.1368 | [-0.1485, -0.1242] | 0.002 |
| loan_status                            | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.1277 | [-0.1417, -0.1111] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.125  | [-0.1308, -0.1211] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1248 | [-0.1343, -0.1155] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1247 | [-0.1356, -0.1137] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.122  | [-0.1303, -0.1130] | 0.002 |
| law_school_admission_bianry            | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.121  | [-0.1313, -0.1129] | 0.002 |
| loan_status                            | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1202 | [-0.1331, -0.1064] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | xgboost       | raw -> raw_plus_random_all     | -0.1029 | [-0.1167, -0.0889] | 0.002 |
| law_school_admission_bianry            | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1009 | [-0.1113, -0.0898] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.1001 | [-0.1101, -0.0899] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.0978 | [-0.1088, -0.0894] | 0.002 |
| house_8l                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0953 | [-0.1086, -0.0818] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | xgboost       | raw -> raw_plus_random_formula | -0.0937 | [-0.1158, -0.0700] | 0.002 |
| house_8l                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.0874 | [-0.0989, -0.0770] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema                     | model         | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------|:--------------------------------------------|--------:|:-------------------|------:|
| online_shoppers                        | claude-opus-4.7/linear_svm | random_forest | raw_plus_random_formula -> raw_plus_formula |  0.2618 | [+0.2467, +0.2805] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.241  | [+0.2306, +0.2509] | 0.002 |
| bitcoinheist_ransomware                | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1846 | [+0.1727, +0.1970] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1808 | [+0.1647, +0.1959] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | random_forest | raw_plus_random_formula -> raw_plus_formula |  0.1796 | [+0.1599, +0.1983] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_formula                     |  0.1617 | [+0.1526, +0.1737] | 0.002 |
| loan_status                            | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1394 | [+0.1267, +0.1510] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | xgboost       | raw_plus_random_formula -> raw_plus_formula |  0.1335 | [+0.1142, +0.1533] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1333 | [+0.1175, +0.1480] | 0.002 |
| online_shoppers                        | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_formula                     |  0.1255 | [+0.1134, +0.1369] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.1088 | [+0.0982, +0.1193] | 0.002 |
| house_8l                               | claude-opus-4.7/linear_svm | knn           | raw_plus_random_formula -> raw_plus_formula |  0.0996 | [+0.0926, +0.1069] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema                     | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:---------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1716 | [-0.1864, -0.1567] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1439 | [-0.1553, -0.1322] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1424 | [-0.1530, -0.1320] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.1368 | [-0.1485, -0.1242] | 0.002 |
| loan_status                            | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-opus-4.7/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.1277 | [-0.1417, -0.1111] | 0.002 |
| kr_vs_kp                               | claude-opus-4.7/linear_svm | knn           | raw -> raw_plus_random_formula | -0.125  | [-0.1308, -0.1211] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
