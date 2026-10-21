# Anonymized-Column Memorization Control

Schema generator: gpt-5.5-pro; column names -> x001..xNNN, dataset identity removed, distributional stats preserved.
Dataset-level means (families averaged), Wilcoxon across datasets.

Re-scored offline from the cached anonymized schemas by scripts/rescore_anonymized_control_offline.py.

## roc_auc_ovr

| Downstream | N | direct Δ | vs-random Δ | semantic Δ | semantic W/L | semantic p |
|---|---|---|---|---|---|---|
| xgboost | 10 | -0.0006 | +0.0102 | +0.0037 | 7/3 | 0.1934 |
| logistic_regression | 10 | +0.0048 | +0.0094 | +0.0110 | 10/0 | 0.0020 |
| random_forest | 10 | -0.0001 | +0.0101 | +0.0060 | 8/2 | 0.1309 |
| knn | 10 | +0.0087 | +0.0724 | +0.0699 | 10/0 | 0.0020 |

## balanced_accuracy

| Downstream | N | direct Δ | vs-random Δ | semantic Δ | semantic W/L | semantic p |
|---|---|---|---|---|---|---|
| xgboost | 10 | +0.0033 | +0.0469 | +0.0328 | 10/0 | 0.0020 |
| logistic_regression | 10 | +0.0077 | +0.0115 | +0.0182 | 9/1 | 0.0039 |
| random_forest | 10 | +0.0081 | +0.0698 | +0.0625 | 10/0 | 0.0020 |
| knn | 10 | +0.0338 | +0.1094 | +0.1097 | 10/0 | 0.0020 |
