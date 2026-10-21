# Friedman Test — Multi-Treatment Ranking (restructured benchmark)

Treatments: raw, raw+formula, raw+permuted_formula, raw+random_formula, raw+random_all

## roc_auc_ovr / xgboost
- N = 49 datasets
- Friedman χ² = 99.854, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw | 4.30 | 0.8940 |
| raw_plus_formula | 3.97 | 0.8940 |
| raw_plus_permuted_formula | 2.81 | 0.8855 |
| raw_plus_random_formula | 2.09 | 0.8813 |
| raw_plus_random_all | 1.84 | 0.8792 |

Nemenyi CD (α=0.05): 0.871

## roc_auc_ovr / logistic_regression
- N = 49 datasets
- Friedman χ² = 135.550, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.63 | 0.8732 |
| raw | 4.10 | 0.8636 |
| raw_plus_permuted_formula | 2.37 | 0.8592 |
| raw_plus_random_formula | 2.33 | 0.8598 |
| raw_plus_random_all | 1.57 | 0.8572 |

Nemenyi CD (α=0.05): 0.871

## roc_auc_ovr / random_forest
- N = 49 datasets
- Friedman χ² = 53.855, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw | 3.88 | 0.8911 |
| raw_plus_formula | 3.61 | 0.8930 |
| raw_plus_permuted_formula | 3.10 | 0.8845 |
| raw_plus_random_formula | 2.53 | 0.8828 |
| raw_plus_random_all | 1.88 | 0.8802 |

Nemenyi CD (α=0.05): 0.871

## roc_auc_ovr / knn
- N = 49 datasets
- Friedman χ² = 146.612, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.53 | 0.8598 |
| raw | 4.29 | 0.8531 |
| raw_plus_permuted_formula | 2.61 | 0.8088 |
| raw_plus_random_formula | 2.22 | 0.8057 |
| raw_plus_random_all | 1.35 | 0.7946 |

Nemenyi CD (α=0.05): 0.871

## balanced_accuracy / xgboost
- N = 49 datasets
- Friedman χ² = 79.134, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw | 4.12 | 0.7660 |
| raw_plus_formula | 3.99 | 0.7678 |
| raw_plus_permuted_formula | 2.59 | 0.7541 |
| raw_plus_random_formula | 2.20 | 0.7480 |
| raw_plus_random_all | 2.09 | 0.7473 |

Nemenyi CD (α=0.05): 0.871

## balanced_accuracy / logistic_regression
- N = 49 datasets
- Friedman χ² = 74.501, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.32 | 0.7795 |
| raw | 3.73 | 0.7684 |
| raw_plus_random_formula | 2.55 | 0.7644 |
| raw_plus_random_all | 2.27 | 0.7603 |
| raw_plus_permuted_formula | 2.13 | 0.7630 |

Nemenyi CD (α=0.05): 0.871

## balanced_accuracy / random_forest
- N = 49 datasets
- Friedman χ² = 75.697, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.05 | 0.7584 |
| raw | 3.96 | 0.7508 |
| raw_plus_permuted_formula | 2.77 | 0.7281 |
| raw_plus_random_formula | 2.33 | 0.7230 |
| raw_plus_random_all | 1.90 | 0.7182 |

Nemenyi CD (α=0.05): 0.871

## balanced_accuracy / knn
- N = 49 datasets
- Friedman χ² = 134.094, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.49 | 0.7206 |
| raw | 4.16 | 0.7082 |
| raw_plus_permuted_formula | 2.58 | 0.6471 |
| raw_plus_random_formula | 2.36 | 0.6442 |
| raw_plus_random_all | 1.41 | 0.6326 |

Nemenyi CD (α=0.05): 0.871
