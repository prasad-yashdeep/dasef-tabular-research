# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 48
- Matrix comparisons analyzed: 768
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 191
- Comparisons with 95% bootstrap CI entirely below zero: 293
- Formula-vs-raw comparisons: 192
- Judgment-vs-raw comparisons: 0
- Judgment incremental-over-formula comparisons: 0

## Positive CI Excluding Zero

| dataset        | schema                              | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.4102 | [+0.3804, +0.4400] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.4101 | [+0.3746, +0.4445] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3882 | [+0.3577, +0.4189] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3591 | [+0.3201, +0.3981] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3374 | [+0.3083, +0.3635] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3205 | [+0.2938, +0.3447] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3115 | [+0.2856, +0.3368] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3041 | [+0.2733, +0.3344] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3004 | [+0.2623, +0.3405] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2977 | [+0.2603, +0.3313] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw -> raw_plus_formula                     |  0.2915 | [+0.2741, +0.3078] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2783 | [+0.2368, +0.3172] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.2684 | [+0.2420, +0.2897] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2498 | [+0.2150, +0.2839] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | logistic_regression | raw -> raw_plus_formula                     |  0.2436 | [+0.2165, +0.2772] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.2028 | [+0.1800, +0.2289] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.2013 | [+0.1791, +0.2261] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.1896 | [+0.1473, +0.2303] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | xgboost             | raw_plus_random_formula -> raw_plus_formula |  0.1868 | [+0.1561, +0.2209] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.1868 | [+0.1541, +0.2180] | 0.002 |

## Negative CI Excluding Zero

| dataset        | schema                              | model         | pair                           |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest | raw -> raw_plus_random_formula | -0.3306 | [-0.3704, -0.2938] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest | raw -> raw_plus_random_formula | -0.3306 | [-0.3704, -0.2938] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest | raw -> raw_plus_random_formula | -0.3161 | [-0.3566, -0.2776] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest | raw -> raw_plus_random_formula | -0.3161 | [-0.3566, -0.2776] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest | raw -> raw_plus_random_formula | -0.3161 | [-0.3566, -0.2776] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | random_forest | raw -> raw_plus_random_formula | -0.3161 | [-0.3566, -0.2776] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn           | raw -> raw_plus_random_all     | -0.315  | [-0.3433, -0.2852] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn           | raw -> raw_plus_random_all     | -0.315  | [-0.3433, -0.2852] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn           | raw -> raw_plus_random_all     | -0.315  | [-0.3433, -0.2852] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn           | raw -> raw_plus_random_all     | -0.315  | [-0.3433, -0.2852] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn           | raw -> raw_plus_random_all     | -0.315  | [-0.3433, -0.2852] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn           | raw -> raw_plus_random_all     | -0.315  | [-0.3433, -0.2852] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn           | raw -> raw_plus_random_formula | -0.2988 | [-0.3331, -0.2627] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn           | raw -> raw_plus_random_formula | -0.2988 | [-0.3331, -0.2627] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset        | schema                              | model               | pair                                        |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------------|:--------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.4102 | [+0.3804, +0.4400] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.4101 | [+0.3746, +0.4445] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3882 | [+0.3577, +0.4189] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn                 | raw_plus_random_formula -> raw_plus_formula |  0.3591 | [+0.3201, +0.3981] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3374 | [+0.3083, +0.3635] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3205 | [+0.2938, +0.3447] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3115 | [+0.2856, +0.3368] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3041 | [+0.2733, +0.3344] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.3004 | [+0.2623, +0.3405] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw_plus_random_formula -> raw_plus_formula |  0.2977 | [+0.2603, +0.3313] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | logistic_regression | raw -> raw_plus_formula                     |  0.2915 | [+0.2741, +0.3078] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest       | raw_plus_random_formula -> raw_plus_formula |  0.2783 | [+0.2368, +0.3172] | 0.002 |

## Largest Negative Deltas

| dataset        | schema                              | model         | pair                           |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| car_evaluation | gemini-3.1-pro-preview/tree         | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest | raw -> raw_plus_random_all     | -0.3871 | [-0.4094, -0.3605] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest | raw -> raw_plus_random_formula | -0.3306 | [-0.3704, -0.2938] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest | raw -> raw_plus_random_formula | -0.3306 | [-0.3704, -0.2938] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
