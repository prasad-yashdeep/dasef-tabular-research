# Friedman Test — Multi-Treatment Ranking

Treatments: raw, raw+formula, raw+formula+judgment, raw+random_formula, raw+random_all

## roc_auc_ovr / xgboost
- N = 10 datasets
- Friedman χ² = 24.800, p = 0.0001

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.20 | 0.8900 |
| raw | 4.10 | 0.8898 |
| raw_plus_formula_plus_judgment | 3.30 | 0.8902 |
| raw_plus_random_all | 1.90 | 0.8791 |
| raw_plus_random_formula | 1.50 | 0.8796 |

Nemenyi CD (α=0.05): 1.929

## roc_auc_ovr / logistic_regression
- N = 10 datasets
- Friedman χ² = 32.320, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.60 | 0.8774 |
| raw | 3.80 | 0.8720 |
| raw_plus_formula_plus_judgment | 3.60 | 0.8768 |
| raw_plus_random_formula | 1.60 | 0.8673 |
| raw_plus_random_all | 1.40 | 0.8643 |

Nemenyi CD (α=0.05): 1.929

## roc_auc_ovr / random_forest
- N = 10 datasets
- Friedman χ² = 14.320, p = 0.0063

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula_plus_judgment | 4.00 | 0.8924 |
| raw | 3.50 | 0.8920 |
| raw_plus_formula | 3.50 | 0.8909 |
| raw_plus_random_formula | 2.20 | 0.8823 |
| raw_plus_random_all | 1.80 | 0.8816 |

Nemenyi CD (α=0.05): 1.929

## roc_auc_ovr / knn
- N = 10 datasets
- Friedman χ² = 32.800, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.30 | 0.8656 |
| raw | 4.20 | 0.8636 |
| raw_plus_formula_plus_judgment | 3.50 | 0.8636 |
| raw_plus_random_formula | 1.90 | 0.7982 |
| raw_plus_random_all | 1.10 | 0.7893 |

Nemenyi CD (α=0.05): 1.929

## balanced_accuracy / xgboost
- N = 10 datasets
- Friedman χ² = 26.960, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.30 | 0.7934 |
| raw | 4.00 | 0.7924 |
| raw_plus_formula_plus_judgment | 3.40 | 0.7911 |
| raw_plus_random_all | 2.00 | 0.7545 |
| raw_plus_random_formula | 1.30 | 0.7504 |

Nemenyi CD (α=0.05): 1.929

## balanced_accuracy / logistic_regression
- N = 10 datasets
- Friedman χ² = 15.440, p = 0.0039

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.20 | 0.8042 |
| raw_plus_formula_plus_judgment | 3.70 | 0.8037 |
| raw | 3.00 | 0.7998 |
| raw_plus_random_formula | 2.30 | 0.7946 |
| raw_plus_random_all | 1.80 | 0.7855 |

Nemenyi CD (α=0.05): 1.929

## balanced_accuracy / random_forest
- N = 10 datasets
- Friedman χ² = 24.880, p = 0.0001

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.20 | 0.7788 |
| raw | 3.80 | 0.7748 |
| raw_plus_formula_plus_judgment | 3.70 | 0.7779 |
| raw_plus_random_formula | 1.70 | 0.7140 |
| raw_plus_random_all | 1.60 | 0.7082 |

Nemenyi CD (α=0.05): 1.929

## balanced_accuracy / knn
- N = 10 datasets
- Friedman χ² = 30.880, p = 0.0000

| Treatment | Avg Rank | Mean Score |
|---|---|---|
| raw_plus_formula | 4.30 | 0.7284 |
| raw | 3.90 | 0.7064 |
| raw_plus_formula_plus_judgment | 3.80 | 0.7253 |
| raw_plus_random_formula | 1.70 | 0.6305 |
| raw_plus_random_all | 1.30 | 0.6284 |

Nemenyi CD (α=0.05): 1.929
