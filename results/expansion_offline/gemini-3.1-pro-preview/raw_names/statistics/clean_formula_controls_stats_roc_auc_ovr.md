# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 28
- Matrix comparisons analyzed: 448
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 124
- Comparisons with 95% bootstrap CI entirely below zero: 192
- Formula-vs-raw comparisons: 112
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                               | schema                            | model               | pair                                        |   delta | 95% CI             |     p |
|:--------------------------------------|:----------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2122 | [+0.1992, +0.2272] | 0.002 |
| mozilla4                              | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1206 | [+0.1096, +0.1342] | 0.002 |
| employee_turnover_at_techco           | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1124 | [+0.0833, +0.1479] | 0.002 |
| codexglue                             | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1106 | [+0.0994, +0.1206] | 0.002 |
| amazon_employee_access                | gemini-3.1-pro-preview/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1001 | [+0.0716, +0.1291] | 0.002 |
| online_shoppers                       | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0982 | [+0.0870, +0.1085] | 0.002 |
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0842 | [+0.0721, +0.0945] | 0.002 |
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0785 | [+0.0676, +0.0888] | 0.002 |
| okcupid_stem                          | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.075  | [+0.0624, +0.0875] | 0.002 |
| fried                                 | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0747 | [+0.0708, +0.0789] | 0.002 |
| fried                                 | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0735 | [+0.0703, +0.0773] | 0.002 |
| click_prediction_small                | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0733 | [+0.0554, +0.0922] | 0.002 |
| fried                                 | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0718 | [+0.0654, +0.0784] | 0.002 |
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.071  | [+0.0589, +0.0827] | 0.002 |
| house_8l                              | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0637 | [+0.0596, +0.0676] | 0.002 |
| news_channel                          | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0632 | [+0.0568, +0.0696] | 0.002 |
| online_shoppers                       | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.052  | [+0.0409, +0.0641] | 0.002 |
| customer_churn_classification_nominal | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0507 | [+0.0418, +0.0613] | 0.002 |
| house_16h                             | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0492 | [+0.0376, +0.0597] | 0.002 |
| first_order_theorem_proving           | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.047  | [+0.0428, +0.0515] | 0.002 |

## Negative CI Excluding Zero

| dataset                     | schema                            | model               | pair                           |   delta | 95% CI             |     p |
|:----------------------------|:----------------------------------|:--------------------|:-------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1412 | [-0.1500, -0.1326] | 0.002 |
| mozilla4                    | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| employee_turnover_at_techco | gemini-3.1-pro-preview/linear_svm | random_forest       | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.1354 | [-0.1514, -0.1194] | 0.002 |
| mozilla4                    | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.128  | [-0.1398, -0.1169] | 0.002 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_formula | -0.1219 | [-0.1313, -0.1107] | 0.002 |
| amazon_employee_access      | gemini-3.1-pro-preview/linear_svm | xgboost             | raw -> raw_plus_random_formula | -0.0989 | [-0.1281, -0.0698] | 0.002 |
| employee_turnover_at_techco | gemini-3.1-pro-preview/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0912 | [-0.1490, -0.0413] | 0.01  |
| volcanoes_c1                | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_random_all     | -0.0879 | [-0.1229, -0.0573] | 0.002 |
| employee_turnover_at_techco | gemini-3.1-pro-preview/linear_svm | random_forest       | raw -> raw_plus_random_formula | -0.0867 | [-0.1475, -0.0279] | 0.027 |
| amazon_employee_access      | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0841 | [-0.1222, -0.0490] | 0.01  |
| house_8l                    | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.0791, -0.0672] | 0.002 |
| volcanoes_c1                | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0736 | [-0.1061, -0.0423] | 0.006 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0733 | [-0.0843, -0.0615] | 0.002 |
| airlines                    | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0723 | [-0.0832, -0.0613] | 0.002 |
| amazon_employee_access      | gemini-3.1-pro-preview/linear_svm | xgboost             | raw -> raw_plus_random_all     | -0.0719 | [-0.0907, -0.0512] | 0.002 |
| okcupid_stem                | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.0706 | [-0.0794, -0.0612] | 0.002 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | random_forest       | raw -> raw_plus_random_all     | -0.0678 | [-0.0787, -0.0580] | 0.002 |
| house_16h                   | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_random_all     | -0.067  | [-0.0727, -0.0612] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                     | schema                            | model               | pair                                        |   delta | 95% CI             |     p |
|:----------------------------|:----------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2122 | [+0.1992, +0.2272] | 0.002 |
| mozilla4                    | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1206 | [+0.1096, +0.1342] | 0.002 |
| employee_turnover_at_techco | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1124 | [+0.0833, +0.1479] | 0.002 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1106 | [+0.0994, +0.1206] | 0.002 |
| amazon_employee_access      | gemini-3.1-pro-preview/linear_svm | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1001 | [+0.0716, +0.1291] | 0.002 |
| online_shoppers             | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0982 | [+0.0870, +0.1085] | 0.002 |
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0842 | [+0.0721, +0.0945] | 0.002 |
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0785 | [+0.0676, +0.0888] | 0.002 |
| okcupid_stem                | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.075  | [+0.0624, +0.0875] | 0.002 |
| fried                       | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0747 | [+0.0708, +0.0789] | 0.002 |
| fried                       | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.0735 | [+0.0703, +0.0773] | 0.002 |
| click_prediction_small      | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0733 | [+0.0554, +0.0922] | 0.002 |

## Largest Negative Deltas

| dataset                     | schema                            | model         | pair                           |   delta | 95% CI             |     p |
|:----------------------------|:----------------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1529 | [-0.1670, -0.1378] | 0.002 |
| bitcoinheist_ransomware     | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1412 | [-0.1500, -0.1326] | 0.002 |
| mozilla4                    | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1373 | [-0.1477, -0.1255] | 0.002 |
| employee_turnover_at_techco | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.136  | [-0.1840, -0.0859] | 0.004 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1354 | [-0.1514, -0.1194] | 0.002 |
| mozilla4                    | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.128  | [-0.1398, -0.1169] | 0.002 |
| codexglue                   | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1219 | [-0.1313, -0.1107] | 0.002 |
| amazon_employee_access      | gemini-3.1-pro-preview/linear_svm | xgboost       | raw -> raw_plus_random_formula | -0.0989 | [-0.1281, -0.0698] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
