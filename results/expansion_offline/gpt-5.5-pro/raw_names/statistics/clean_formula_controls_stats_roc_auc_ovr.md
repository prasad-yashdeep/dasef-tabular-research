# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 31
- Matrix comparisons analyzed: 496
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 143
- Comparisons with 95% bootstrap CI entirely below zero: 220
- Formula-vs-raw comparisons: 124
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema                 | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2089 | [+0.1953, +0.2238] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1553 | [+0.1431, +0.1698] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1287 | [+0.1204, +0.1393] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.11   | [+0.0953, +0.1218] | 0.002 |
| codexglue                              | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1032 | [+0.0819, +0.1223] | 0.002 |
| employee_turnover_at_techco            | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0972 | [+0.0404, +0.1534] | 0.014 |
| codexglue                              | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0895 | [+0.0734, +0.1041] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0857 | [+0.0800, +0.0915] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0845 | [+0.0795, +0.0888] | 0.002 |
| codexglue                              | gpt-5.5-pro/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.0818 | [+0.0643, +0.0994] | 0.002 |
| house_8l                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0798 | [+0.0746, +0.0856] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0761 | [+0.0719, +0.0807] | 0.002 |
| pricerunner                            | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0759 | [+0.0736, +0.0777] | 0.002 |
| click_prediction_small                 | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0759 | [+0.0582, +0.0943] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.075  | [+0.0714, +0.0792] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.071  | [+0.0663, +0.0754] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0684 | [+0.0635, +0.0727] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0677 | [+0.0563, +0.0783] | 0.002 |
| customer_churn_classification_nominal  | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0673 | [+0.0556, +0.0773] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.0657 | [+0.0616, +0.0697] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema                 | model               | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------------|:-------------------------------|--------:|:-------------------|------:|
| pricerunner                            | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1895 | [-0.1929, -0.1863] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1412 | [-0.1500, -0.1326] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| employee_turnover_at_techco            | gpt-5.5-pro/linear_svm | random_forest       | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| codexglue                              | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1354 | [-0.1514, -0.1194] | 0.002 |
| codexglue                              | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1344 | [-0.1518, -0.1163] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1318 | [-0.1376, -0.1265] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.128  | [-0.1398, -0.1169] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1175 | [-0.1266, -0.1092] | 0.002 |
| employee_turnover_at_techco            | gpt-5.5-pro/linear_svm | random_forest       | raw -> raw_plus_random_formula | -0.0946 | [-0.1585, -0.0246] | 0.037 |
| employee_turnover_at_techco            | gpt-5.5-pro/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0924 | [-0.1512, -0.0442] | 0.006 |
| volcanoes_c1                           | gpt-5.5-pro/linear_svm | logistic_regression | raw -> raw_plus_random_all     | -0.0879 | [-0.1229, -0.0573] | 0.002 |
| kr_vs_kp                               | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0836 | [-0.0895, -0.0779] | 0.002 |
| pricerunner                            | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0759 | [-0.0777, -0.0736] | 0.002 |
| house_8l                               | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.0791, -0.0672] | 0.002 |
| volcanoes_c1                           | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.1061, -0.0423] | 0.006 |
| codexglue                              | gpt-5.5-pro/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0735 | [-0.0843, -0.0618] | 0.002 |
| airlines                               | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0723 | [-0.0832, -0.0613] | 0.002 |
| kr_vs_kp                               | gpt-5.5-pro/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0711 | [-0.0765, -0.0657] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema                 | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2089 | [+0.1953, +0.2238] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1553 | [+0.1431, +0.1698] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1287 | [+0.1204, +0.1393] | 0.002 |
| online_shoppers                        | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.11   | [+0.0953, +0.1218] | 0.002 |
| codexglue                              | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1032 | [+0.0819, +0.1223] | 0.002 |
| employee_turnover_at_techco            | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0972 | [+0.0404, +0.1534] | 0.014 |
| codexglue                              | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0895 | [+0.0734, +0.1041] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0857 | [+0.0800, +0.0915] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0845 | [+0.0795, +0.0888] | 0.002 |
| codexglue                              | gpt-5.5-pro/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.0818 | [+0.0643, +0.0994] | 0.002 |
| house_8l                               | gpt-5.5-pro/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0798 | [+0.0746, +0.0856] | 0.002 |
| fried                                  | gpt-5.5-pro/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0761 | [+0.0719, +0.0807] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema                 | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| pricerunner                            | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1895 | [-0.1929, -0.1863] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware                | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1412 | [-0.1500, -0.1326] | 0.002 |
| mozilla4                               | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| employee_turnover_at_techco            | gpt-5.5-pro/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| codexglue                              | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1354 | [-0.1514, -0.1194] | 0.002 |
| codexglue                              | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1344 | [-0.1518, -0.1163] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | gpt-5.5-pro/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1318 | [-0.1376, -0.1265] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
