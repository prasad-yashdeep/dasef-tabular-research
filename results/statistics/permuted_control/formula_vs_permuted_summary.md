# Formula vs Permuted-Formula (Dataset-Level)

If formula > permuted consistently, the gain is from semantic row-alignment,
not just the marginal distribution of feature values.

## roc_auc_ovr

| Downstream | N | Mean Δ | W/L/T | p (Wilcoxon) |
|---|---|---|---|---|
| xgboost | 10 | +0.0053 | 8/2/0 | 0.0488 |
| logistic_regression | 10 | +0.0115 | 10/0/0 | 0.0020 |
| random_forest | 10 | +0.0043 | 7/3/0 | 0.1602 |
| knn | 10 | +0.0632 | 10/0/0 | 0.0020 |

## balanced_accuracy

| Downstream | N | Mean Δ | W/L/T | p (Wilcoxon) |
|---|---|---|---|---|
| xgboost | 10 | +0.0256 | 10/0/0 | 0.0020 |
| logistic_regression | 10 | +0.0135 | 10/0/0 | 0.0020 |
| random_forest | 10 | +0.0506 | 10/0/0 | 0.0020 |
| knn | 10 | +0.0945 | 10/0/0 | 0.0020 |
