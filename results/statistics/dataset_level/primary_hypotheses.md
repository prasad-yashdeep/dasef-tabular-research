# DASEF Paper 1 — Dataset-Level Primary Hypotheses

Statistical unit: **dataset** (N=10). Each dataset-level delta is the mean
of all available runs (across schema generators and model families) for that dataset.

Test: Wilcoxon signed-rank (two-sided). Correction: Holm-Bonferroni (primary),
Benjamini-Hochberg FDR (exploratory).

Total hypotheses tested: 40
Significant after Holm (α=0.05): 0
Significant after BH-FDR (α=0.05): 14

## Key Results

### raw → raw_plus_formula

**Metric: roc_auc_ovr**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| logistic_regression | 10 | +0.0053 | 7/3/0 | 0.1309 | 1.0000 | +0.40 | ❌ |
| random_forest | 10 | -0.0011 | 4/6/0 | 0.6250 | 1.0000 | -0.20 | ❌ |
| knn | 10 | +0.0020 | 5/5/0 | 0.6250 | 1.0000 | +0.00 | ❌ |
| xgboost | 10 | +0.0001 | 4/6/0 | 0.9219 | 1.0000 | -0.20 | ❌ |

**Metric: balanced_accuracy**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| knn | 10 | +0.0219 | 6/4/0 | 0.1055 | 1.0000 | +0.20 | ❌ |
| xgboost | 10 | +0.0009 | 6/4/0 | 0.3750 | 1.0000 | +0.20 | ❌ |
| logistic_regression | 10 | +0.0044 | 7/3/0 | 0.3750 | 1.0000 | +0.40 | ❌ |
| random_forest | 10 | +0.0040 | 6/4/0 | 0.4316 | 1.0000 | +0.20 | ❌ |

### raw → raw_plus_formula_plus_judgment

**Metric: roc_auc_ovr**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| logistic_regression | 10 | +0.0048 | 5/5/0 | 0.2754 | 1.0000 | +0.00 | ❌ |
| xgboost | 10 | +0.0003 | 3/7/0 | 0.6250 | 1.0000 | -0.40 | ❌ |
| knn | 10 | -0.0000 | 3/7/0 | 0.6953 | 1.0000 | -0.40 | ❌ |
| random_forest | 10 | +0.0005 | 5/5/0 | 0.7695 | 1.0000 | +0.00 | ❌ |

**Metric: balanced_accuracy**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| knn | 10 | +0.0189 | 5/5/0 | 0.3750 | 1.0000 | +0.00 | ❌ |
| logistic_regression | 10 | +0.0039 | 7/3/0 | 0.4922 | 1.0000 | +0.40 | ❌ |
| random_forest | 10 | +0.0031 | 5/5/0 | 0.5566 | 1.0000 | +0.00 | ❌ |
| xgboost | 10 | -0.0013 | 4/6/0 | 0.6250 | 1.0000 | -0.20 | ❌ |

### raw_plus_formula → raw_plus_formula_plus_judgment

**Metric: roc_auc_ovr**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| logistic_regression | 10 | -0.0005 | 1/9/0 | 0.0488 | 1.0000 | -0.80 | ❌ |
| xgboost | 10 | +0.0002 | 1/9/0 | 0.0840 | 1.0000 | -0.80 | ❌ |
| knn | 10 | -0.0020 | 2/8/0 | 0.1309 | 1.0000 | -0.60 | ❌ |
| random_forest | 10 | +0.0016 | 5/5/0 | 0.8457 | 1.0000 | +0.00 | ❌ |

**Metric: balanced_accuracy**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| xgboost | 10 | -0.0022 | 2/8/0 | 0.1055 | 1.0000 | -0.60 | ❌ |
| random_forest | 10 | -0.0009 | 3/7/0 | 0.1602 | 1.0000 | -0.40 | ❌ |
| knn | 10 | -0.0031 | 3/7/0 | 0.1602 | 1.0000 | -0.40 | ❌ |
| logistic_regression | 10 | -0.0005 | 3/7/0 | 0.4316 | 1.0000 | -0.40 | ❌ |

### raw_plus_random_all → raw_plus_formula_plus_judgment

**Metric: roc_auc_ovr**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| knn | 10 | +0.0743 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| random_forest | 10 | +0.0108 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| logistic_regression | 10 | +0.0126 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| xgboost | 10 | +0.0110 | 9/1/0 | 0.0059 | 0.1758 | +0.80 | ❌ |

**Metric: balanced_accuracy**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| knn | 10 | +0.0969 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| xgboost | 10 | +0.0366 | 9/1/0 | 0.0059 | 0.1758 | +0.80 | ❌ |
| random_forest | 10 | +0.0697 | 9/1/0 | 0.0059 | 0.1758 | +0.80 | ❌ |
| logistic_regression | 10 | +0.0183 | 8/2/0 | 0.0098 | 0.2637 | +0.60 | ❌ |

### raw_plus_random_formula → raw_plus_formula

**Metric: roc_auc_ovr**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| knn | 10 | +0.0674 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| logistic_regression | 10 | +0.0100 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| xgboost | 10 | +0.0104 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| random_forest | 10 | +0.0086 | 8/2/0 | 0.1055 | 1.0000 | +0.60 | ❌ |

**Metric: balanced_accuracy**

| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |
|---|---|---|---|---|---|---|---|
| knn | 10 | +0.0979 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| random_forest | 10 | +0.0649 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| xgboost | 10 | +0.0429 | 10/0/0 | 0.0020 | 0.0781 | +1.00 | ❌ |
| logistic_regression | 10 | +0.0095 | 9/1/0 | 0.0273 | 0.7109 | +0.80 | ❌ |

## Aggregate Win/Loss/Tie Summary

| Pair | Metric | Total W | Total L | Total T | Net |
|---|---|---|---|---|---|
| raw→raw_plus_formula | roc_auc_ovr | 20 | 20 | 0 | +0 |
| raw→raw_plus_formula | balanced_accuracy | 25 | 15 | 0 | +10 |
| raw→raw_plus_formula_plus_judgment | roc_auc_ovr | 16 | 24 | 0 | -8 |
| raw→raw_plus_formula_plus_judgment | balanced_accuracy | 21 | 19 | 0 | +2 |
| raw_plus_formula→raw_plus_formula_plus_judgment | roc_auc_ovr | 9 | 31 | 0 | -22 |
| raw_plus_formula→raw_plus_formula_plus_judgment | balanced_accuracy | 11 | 29 | 0 | -18 |
| raw_plus_random_all→raw_plus_formula_plus_judgment | roc_auc_ovr | 39 | 1 | 0 | +38 |
| raw_plus_random_all→raw_plus_formula_plus_judgment | balanced_accuracy | 36 | 4 | 0 | +32 |
| raw_plus_random_formula→raw_plus_formula | roc_auc_ovr | 38 | 2 | 0 | +36 |
| raw_plus_random_formula→raw_plus_formula | balanced_accuracy | 39 | 1 | 0 | +38 |
