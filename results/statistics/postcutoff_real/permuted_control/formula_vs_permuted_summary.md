# Post-cutoff: formula vs permuted-formula (dataset-level)

Runs: 35 (skipped: 0); datasets: 6. semantic = raw+formula minus raw+permuted-formula (each generated column independently row-permuted, seed 42); design fraction 0.2, seed 42, no cap. Wilcoxon (two-sided, exact) across datasets.

## roc_auc_ovr

| Model | N | mean Δ | W/L | p |
|---|---|---|---|---|
| xgboost | 6 | +0.0185 | 6/0 | 0.0312 |
| logistic_regression | 6 | +0.0436 | 6/0 | 0.0312 |
| random_forest | 6 | +0.0169 | 5/1 | 0.1562 |
| knn | 6 | +0.0762 | 5/1 | 0.0625 |

## balanced_accuracy

| Model | N | mean Δ | W/L | p |
|---|---|---|---|---|
| xgboost | 6 | +0.0339 | 6/0 | 0.0312 |
| logistic_regression | 6 | +0.0421 | 6/0 | 0.0312 |
| random_forest | 6 | +0.0373 | 5/1 | 0.0625 |
| knn | 6 | +0.0777 | 6/0 | 0.0312 |
