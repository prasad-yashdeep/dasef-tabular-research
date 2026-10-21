# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 28
- Matrix comparisons analyzed: 448
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 109
- Comparisons with 95% bootstrap CI entirely below zero: 158
- Formula-vs-raw comparisons: 112
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset                               | schema                            | model               | pair                                        |   delta | 95% CI             |     p |
|:--------------------------------------|:----------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| online_shoppers                       | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1791 | [+0.1645, +0.1924] | 0.002 |
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.174  | [+0.1609, +0.1893] | 0.002 |
| mozilla4                              | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1457 | [+0.1314, +0.1609] | 0.002 |
| online_shoppers                       | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1374 | [+0.1250, +0.1510] | 0.002 |
| loan_status                           | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1324 | [+0.1226, +0.1423] | 0.002 |
| online_shoppers                       | gemini-3.1-pro-preview/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.1118 | [+0.1000, +0.1245] | 0.002 |
| fried                                 | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.1069 | [+0.1008, +0.1133] | 0.002 |
| fried                                 | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.106  | [+0.0983, +0.1137] | 0.002 |
| online_shoppers                       | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0966 | [+0.0866, +0.1078] | 0.002 |
| house_8l                              | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0896 | [+0.0813, +0.0976] | 0.002 |
| fried                                 | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.078  | [+0.0693, +0.0876] | 0.002 |
| okcupid_stem                          | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0736 | [+0.0642, +0.0809] | 0.002 |
| okcupid_stem                          | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0704 | [+0.0644, +0.0770] | 0.002 |
| kr_vs_kp                              | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.069  | [+0.0641, +0.0741] | 0.002 |
| customer_churn_classification_nominal | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0662 | [+0.0585, +0.0743] | 0.002 |
| codexglue                             | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0657 | [+0.0506, +0.0811] | 0.002 |
| splice                                | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0647 | [+0.0570, +0.0719] | 0.002 |
| customer_churn_classification_nominal | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0624 | [+0.0543, +0.0713] | 0.002 |
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.0619 | [+0.0570, +0.0664] | 0.002 |
| bitcoinheist_ransomware               | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0616 | [+0.0491, +0.0744] | 0.002 |

## Negative CI Excluding Zero

| dataset                 | schema                            | model         | pair                           |   delta | 95% CI             |     p |
|:------------------------|:----------------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| mozilla4                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1726 | [-0.1899, -0.1573] | 0.002 |
| loan_status             | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| bitcoinheist_ransomware | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1247 | [-0.1356, -0.1137] | 0.002 |
| loan_status             | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1202 | [-0.1331, -0.1064] | 0.002 |
| bitcoinheist_ransomware | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1124 | [-0.1207, -0.1014] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.0978 | [-0.1088, -0.0894] | 0.002 |
| house_8l                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0953 | [-0.1086, -0.0818] | 0.002 |
| kr_vs_kp                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.0883 | [-0.0942, -0.0823] | 0.002 |
| house_16h               | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0848 | [-0.0906, -0.0788] | 0.002 |
| codexglue               | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0831 | [-0.0998, -0.0677] | 0.002 |
| kr_vs_kp                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0821 | [-0.0887, -0.0753] | 0.002 |
| okcupid_stem            | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.0771 | [-0.0893, -0.0654] | 0.002 |
| codexglue               | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.0733 | [-0.0894, -0.0573] | 0.002 |
| house_8l                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.0728 | [-0.0831, -0.0614] | 0.002 |
| fried                   | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0684 | [-0.0734, -0.0641] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.0673 | [-0.0810, -0.0544] | 0.002 |
| house_16h               | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.0624 | [-0.0708, -0.0542] | 0.002 |
| okcupid_stem            | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_formula | -0.0612 | [-0.0705, -0.0525] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.061  | [-0.0702, -0.0524] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset                 | schema                            | model               | pair                                        |   delta | 95% CI             |     p |
|:------------------------|:----------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.1791 | [+0.1645, +0.1924] | 0.002 |
| bitcoinheist_ransomware | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.174  | [+0.1609, +0.1893] | 0.002 |
| mozilla4                | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1457 | [+0.1314, +0.1609] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1374 | [+0.1250, +0.1510] | 0.002 |
| loan_status             | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1324 | [+0.1226, +0.1423] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | random_forest       | raw -> raw_plus_formula                     |  0.1118 | [+0.1000, +0.1245] | 0.002 |
| fried                   | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw -> raw_plus_formula                     |  0.1069 | [+0.1008, +0.1133] | 0.002 |
| fried                   | gemini-3.1-pro-preview/linear_svm | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.106  | [+0.0983, +0.1137] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | knn                 | raw -> raw_plus_formula                     |  0.0966 | [+0.0866, +0.1078] | 0.002 |
| house_8l                | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.0896 | [+0.0813, +0.0976] | 0.002 |
| fried                   | gemini-3.1-pro-preview/linear_svm | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.078  | [+0.0693, +0.0876] | 0.002 |
| okcupid_stem            | gemini-3.1-pro-preview/linear_svm | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.0736 | [+0.0642, +0.0809] | 0.002 |

## Largest Negative Deltas

| dataset                 | schema                            | model         | pair                           |   delta | 95% CI             |     p |
|:------------------------|:----------------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| mozilla4                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1836 | [-0.1963, -0.1736] | 0.002 |
| mozilla4                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1726 | [-0.1899, -0.1573] | 0.002 |
| loan_status             | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1337 | [-0.1426, -0.1248] | 0.002 |
| bitcoinheist_ransomware | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.1247 | [-0.1356, -0.1137] | 0.002 |
| loan_status             | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1202 | [-0.1331, -0.1064] | 0.002 |
| bitcoinheist_ransomware | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_formula | -0.1124 | [-0.1207, -0.1014] | 0.002 |
| online_shoppers         | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_all     | -0.0978 | [-0.1088, -0.0894] | 0.002 |
| house_8l                | gemini-3.1-pro-preview/linear_svm | knn           | raw -> raw_plus_random_all     | -0.0953 | [-0.1086, -0.0818] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
