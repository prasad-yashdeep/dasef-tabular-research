# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 29
- Matrix comparisons analyzed: 464
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 139
- Comparisons with 95% bootstrap CI entirely below zero: 206
- Formula-vs-raw comparisons: 116
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                                | schema                       | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1817 | [+0.1691, +0.1965] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1314 | [+0.1176, +0.1467] | 0.002 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.128  | [+0.0689, +0.1846] | 0.01  |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1224 | [+0.1135, +0.1304] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1026 | [+0.0871, +0.1162] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0842 | [+0.0781, +0.0908] | 0.002 |
| house_8l                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0674 | [+0.0635, +0.0720] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0638 | [+0.0523, +0.0751] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0615 | [+0.0576, +0.0659] | 0.002 |
| customer_churn_classification_nominal  | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0613 | [+0.0554, +0.0667] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0603 | [+0.0571, +0.0641] | 0.002 |
| house_16h                              | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0601 | [+0.0495, +0.0712] | 0.002 |
| news_channel                           | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.059  | [+0.0510, +0.0658] | 0.002 |
| customer_churn_classification_nominal  | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0585 | [+0.0524, +0.0639] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0581 | [+0.0483, +0.0678] | 0.002 |
| loan_status                            | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0546 | [+0.0491, +0.0599] | 0.002 |
| customer_churn_classification_nominal  | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0542 | [+0.0438, +0.0646] | 0.002 |
| compass                                | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0534 | [+0.0437, +0.0642] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0528 | [+0.0446, +0.0615] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.05   | [+0.0413, +0.0582] | 0.002 |

## Negative CI Excluding Zero

| dataset                                | schema                       | model               | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------------|:-------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1412 | [-0.1500, -0.1326] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.136  | [-0.1495, -0.1232] | 0.002 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | random_forest       | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1318 | [-0.1376, -0.1265] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1252 | [-0.1326, -0.1169] | 0.002 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | random_forest       | raw -> raw_plus_random_formula | -0.0946 | [-0.1585, -0.0246] | 0.037 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0912 | [-0.1490, -0.0413] | 0.01  |
| volcanoes_c1                           | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_random_all     | -0.0879 | [-0.1229, -0.0573] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0836 | [-0.0895, -0.0779] | 0.002 |
| house_8l                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.0791, -0.0672] | 0.002 |
| volcanoes_c1                           | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.1061, -0.0423] | 0.006 |
| airlines                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0723 | [-0.0832, -0.0613] | 0.002 |
| kr_vs_kp                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0711 | [-0.0765, -0.0657] | 0.002 |
| house_16h                              | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.067  | [-0.0727, -0.0612] | 0.002 |
| news_channel                           | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0667 | [-0.0706, -0.0620] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0636 | [-0.0684, -0.0589] | 0.002 |
| house_16h                              | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0608 | [-0.0711, -0.0509] | 0.002 |
| house_8l                               | claude-sonnet-4.6/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.0589 | [-0.0633, -0.0543] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                                | schema                       | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1817 | [+0.1691, +0.1965] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1314 | [+0.1176, +0.1467] | 0.002 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.128  | [+0.0689, +0.1846] | 0.01  |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1224 | [+0.1135, +0.1304] | 0.002 |
| online_shoppers                        | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1026 | [+0.0871, +0.1162] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0842 | [+0.0781, +0.0908] | 0.002 |
| house_8l                               | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0674 | [+0.0635, +0.0720] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0638 | [+0.0523, +0.0751] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0615 | [+0.0576, +0.0659] | 0.002 |
| customer_churn_classification_nominal  | claude-sonnet-4.6/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0613 | [+0.0554, +0.0667] | 0.002 |
| fried                                  | claude-sonnet-4.6/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0603 | [+0.0571, +0.0641] | 0.002 |
| house_16h                              | claude-sonnet-4.6/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0601 | [+0.0495, +0.0712] | 0.002 |

## Largest Negative Deltas

| dataset                                | schema                       | model         | pair                           |   delta | 95% CI             |     p |
|:---------------------------------------|:-----------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware                | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1412 | [-0.1500, -0.1326] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| mozilla4                               | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.136  | [-0.1495, -0.1232] | 0.002 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1318 | [-0.1376, -0.1265] | 0.002 |
| jungle_chess_2pcs_raw_endgame_complete | claude-sonnet-4.6/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1252 | [-0.1326, -0.1169] | 0.002 |
| employee_turnover_at_techco            | claude-sonnet-4.6/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.0946 | [-0.1585, -0.0246] | 0.037 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
