# DASEF Existing Result Statistics

Generated from stored fold-level `raw_scores`; no external API calls were made.

## Scope

- Result files scanned: 213
- Matrix comparisons analyzed: 4449
- Metric: `roc_auc_ovr`
- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;
  final paper claims still need dataset-level aggregation once the larger suite is run.

## Headline

- Comparisons with 95% bootstrap CI entirely above zero: 1472
- Comparisons with 95% bootstrap CI entirely below zero: 1371
- Formula-vs-raw comparisons: 480
- Judgment-vs-raw comparisons: 843
- Judgment incremental-over-formula comparisons: 843

## Positive CI Excluding Zero

| dataset        | schema                              | model   | pair                                                  |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------|:------------------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2319 | [+0.2136, +0.2502] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2316 | [+0.2131, +0.2497] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2295 | [+0.2105, +0.2497] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2263 | [+0.2072, +0.2463] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2262 | [+0.2077, +0.2455] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2259 | [+0.2080, +0.2449] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2255 | [+0.2072, +0.2446] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2254 | [+0.2088, +0.2422] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2214 | [+0.2031, +0.2412] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.2207 | [+0.1995, +0.2418] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2201 | [+0.2020, +0.2391] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.2188 | [+0.1975, +0.2411] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2185 | [+0.2002, +0.2381] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2184 | [+0.1993, +0.2384] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2159 | [+0.1978, +0.2355] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2157 | [+0.1976, +0.2350] | 0.002 |
| car_evaluation | claude-opus-4.7/linear_svm          | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2135 | [+0.1955, +0.2328] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2131 | [+0.1956, +0.2320] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2125 | [+0.1958, +0.2303] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.21   | [+0.1887, +0.2325] | 0.002 |

## Negative CI Excluding Zero

| dataset        | schema                              | model   | pair                           |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------|:-------------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-opus-4.7/linear_svm          | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/linear_svm   | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gpt-5.5-pro/linear_svm              | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn     | raw -> raw_plus_random_all     | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-opus-4.7/linear_svm          | knn     | raw -> raw_plus_random_formula | -0.2077 | [-0.2288, -0.1863] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw -> raw_plus_random_formula | -0.2077 | [-0.2288, -0.1863] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_formula | -0.2077 | [-0.2288, -0.1863] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn     | raw -> raw_plus_random_formula | -0.2077 | [-0.2288, -0.1863] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw -> raw_plus_random_formula | -0.2077 | [-0.2288, -0.1863] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/tree         | knn     | raw -> raw_plus_random_formula | -0.1923 | [-0.2081, -0.1769] | 0.002 |
| car_evaluation | gpt-5.5-pro/linear_svm              | knn     | raw -> raw_plus_random_formula | -0.1923 | [-0.2081, -0.1769] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_formula | -0.1923 | [-0.2081, -0.1769] | 0.002 |

## Largest Positive Deltas, Regardless Of CI

| dataset        | schema                              | model   | pair                                                  |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------|:------------------------------------------------------|--------:|:-------------------|------:|
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2319 | [+0.2136, +0.2502] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2316 | [+0.2131, +0.2497] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2295 | [+0.2105, +0.2497] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2263 | [+0.2072, +0.2463] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2262 | [+0.2077, +0.2455] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2259 | [+0.2080, +0.2449] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2255 | [+0.2072, +0.2446] | 0.002 |
| car_evaluation | gpt-5.5-pro/distance_knn            | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2254 | [+0.2088, +0.2422] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2214 | [+0.2031, +0.2412] | 0.002 |
| car_evaluation | claude-opus-4.7/tree                | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.2207 | [+0.1995, +0.2418] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw_plus_random_all -> raw_plus_formula_plus_judgment |  0.2201 | [+0.2020, +0.2391] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw_plus_random_formula -> raw_plus_formula           |  0.2188 | [+0.1975, +0.2411] | 0.002 |

## Largest Negative Deltas

| dataset        | schema                              | model   | pair                       |   delta | 95% CI             |     p |
|:---------------|:------------------------------------|:--------|:---------------------------|--------:|:-------------------|------:|
| car_evaluation | gpt-5.5-pro/linear_svm              | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gpt-5.5-pro/tree                    | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-sonnet-4.6/linear_svm        | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-opus-4.7/distance_knn        | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-sonnet-4.6/tree              | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | gemini-3.1-pro-preview/distance_knn | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-sonnet-4.6/distance_knn      | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |
| car_evaluation | claude-opus-4.7/linear_svm          | knn     | raw -> raw_plus_random_all | -0.2179 | [-0.2366, -0.1980] | 0.002 |

## Interpretation Guardrails

- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.
- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.
- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.
- Judgment features should be reported separately from formula features; they are costlier and currently mixed.
