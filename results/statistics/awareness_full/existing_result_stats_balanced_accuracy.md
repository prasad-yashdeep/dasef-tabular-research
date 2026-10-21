# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 213
- Matrix comparisons analyzed: 4437
- Metric: `balanced_accuracy`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 1421
- Comparisons with 95% bootstrap CI entirely below zero: 1084
- Formula-vs-raw comparisons: 480
- Judgment-vs-raw comparisons: 839
- Judgment incremental-over-formula comparisons: 839

## Positive CI Excluding Zero

| dataset        | schema                              | model         | pair                                                  |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------|:------------------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-opus-4.7/tree                | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4655 | [+0.4407, +0.4890] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4523 | [+0.4262, +0.4785] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.4456 | [+0.4231, +0.4695] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.4297 | [+0.4088, +0.4481] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4245 | [+0.3972, +0.4548] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4177 | [+0.3850, +0.4504] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.4109 | [+0.3847, +0.4449] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4107 | [+0.3909, +0.4334] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4009 | [+0.3693, +0.4343] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3988 | [+0.3644, +0.4331] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.3975 | [+0.3688, +0.4248] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3872 | [+0.3668, +0.4093] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.3864 | [+0.3438, +0.4264] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.3789 | [+0.3590, +0.4007] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.378  | [+0.3630, +0.3954] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3646 | [+0.3439, +0.3845] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3595 | [+0.3348, +0.3824] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | knn           | raw_plus_random_formula -> raw_plus_formula           |  0.3591 | [+0.3144, +0.4021] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn           | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3583 | [+0.3276, +0.3871] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.343  | [+0.2970, +0.3889] | 0.002 |

## Negative CI Excluding Zero

| dataset        | schema                              | model         | pair                           |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------------|:-------------------------------|--------:|:-------------------|------:|
| car_evaluation | gpt-5.5-pro/linear_svm              | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-opus-4.7/linear_svm          | random_forest | raw -> raw_plus_random_all     | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | random_forest | raw -> raw_plus_random_formula | -0.2664 | [-0.2931, -0.2404] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | random_forest | raw -> raw_plus_random_formula | -0.2664 | [-0.2931, -0.2404] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | random_forest | raw -> raw_plus_random_formula | -0.2664 | [-0.2931, -0.2404] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | random_forest | raw -> raw_plus_random_formula | -0.2664 | [-0.2931, -0.2404] | 0.002 |
| car_evaluation | claude-opus-4.7/linear_svm          | random_forest | raw -> raw_plus_random_formula | -0.2664 | [-0.2931, -0.2404] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | random_forest | raw -> raw_plus_random_formula | -0.2658 | [-0.3053, -0.2257] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | random_forest | raw -> raw_plus_random_formula | -0.2658 | [-0.3053, -0.2257] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | random_forest | raw -> raw_plus_random_formula | -0.2658 | [-0.3053, -0.2257] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset        | schema                              | model   | pair                                                  |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------|:------------------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4655 | [+0.4407, +0.4890] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4523 | [+0.4262, +0.4785] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.4456 | [+0.4231, +0.4695] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.4297 | [+0.4088, +0.4481] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4245 | [+0.3972, +0.4548] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4177 | [+0.3850, +0.4504] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.4109 | [+0.3847, +0.4449] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4107 | [+0.3909, +0.4334] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.4009 | [+0.3693, +0.4343] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3988 | [+0.3644, +0.4331] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.3975 | [+0.3688, +0.4248] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.3872 | [+0.3668, +0.4093] | 0.002 |

## Largest Negative Deltas

| dataset        | schema                            | model         | pair                       |   delta | 95% CI             |     p |
|:---------------|:----------------------------------|:--------------|:---------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-sonnet-4.6/distance_knn    | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree       | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm      | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn      | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn          | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | claude-opus-4.7/linear_svm        | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                  | random_forest | raw -> raw_plus_random_all | -0.3154 | [-0.3510, -0.2781] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
