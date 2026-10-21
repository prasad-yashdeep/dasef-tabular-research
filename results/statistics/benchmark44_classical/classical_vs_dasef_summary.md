# Classical AutoFE vs DASEF formulas (restructured benchmark)

| Variant | Model | Metric | N | classical Δ | DASEF Δ | classical − DASEF | W(classical)/W(DASEF) | p |
|---|---|---|---|---|---|---|---|---|
| raw+autofeat | knn | balanced_accuracy | 19 | +0.0093 | +0.0164 | -0.0072 | 9/10 | 0.169 |
| raw+autofeat | knn | roc_auc_ovr | 19 | +0.0092 | +0.0120 | -0.0028 | 8/11 | 0.395 |
| raw+autofeat | logistic_regression | balanced_accuracy | 19 | +0.0150 | +0.0215 | -0.0065 | 5/14 | 0.0663 |
| raw+autofeat | logistic_regression | roc_auc_ovr | 19 | +0.0130 | +0.0177 | -0.0047 | 5/14 | 0.0289 |
| raw+autofeat | random_forest | balanced_accuracy | 19 | +0.0059 | +0.0093 | -0.0034 | 7/12 | 0.182 |
| raw+autofeat | random_forest | roc_auc_ovr | 19 | -0.0005 | +0.0006 | -0.0011 | 7/12 | 0.332 |
| raw+autofeat | xgboost | balanced_accuracy | 19 | +0.0006 | +0.0010 | -0.0004 | 9/9 | 0.899 |
| raw+autofeat | xgboost | roc_auc_ovr | 19 | -0.0003 | +0.0005 | -0.0007 | 8/10 | 0.417 |
| raw+openfe | knn | balanced_accuracy | 47 | +0.0225 | +0.0127 | +0.0098 | 29/17 | 0.00412 |
| raw+openfe | knn | roc_auc_ovr | 47 | +0.0105 | +0.0069 | +0.0037 | 27/20 | 0.0556 |
| raw+openfe | logistic_regression | balanced_accuracy | 47 | +0.0151 | +0.0114 | +0.0037 | 25/22 | 0.498 |
| raw+openfe | logistic_regression | roc_auc_ovr | 47 | +0.0110 | +0.0098 | +0.0012 | 21/25 | 0.905 |
| raw+openfe | random_forest | balanced_accuracy | 47 | +0.0119 | +0.0080 | +0.0039 | 28/18 | 0.0162 |
| raw+openfe | random_forest | roc_auc_ovr | 47 | +0.0027 | +0.0019 | +0.0008 | 30/16 | 0.16 |
| raw+openfe | xgboost | balanced_accuracy | 47 | +0.0029 | +0.0023 | +0.0006 | 27/18 | 0.0906 |
| raw+openfe | xgboost | roc_auc_ovr | 47 | +0.0032 | +0.0003 | +0.0029 | 29/16 | 0.0689 |
| raw+poly | knn | balanced_accuracy | 49 | +0.0092 | +0.0124 | -0.0032 | 19/29 | 0.273 |
| raw+poly | knn | roc_auc_ovr | 49 | +0.0040 | +0.0067 | -0.0027 | 21/28 | 0.235 |
| raw+poly | logistic_regression | balanced_accuracy | 49 | +0.0073 | +0.0111 | -0.0038 | 22/27 | 0.0799 |
| raw+poly | logistic_regression | roc_auc_ovr | 49 | +0.0050 | +0.0096 | -0.0045 | 14/33 | 0.00492 |
| raw+poly | random_forest | balanced_accuracy | 49 | +0.0075 | +0.0076 | -0.0002 | 24/24 | 0.811 |
| raw+poly | random_forest | roc_auc_ovr | 49 | -0.0022 | +0.0019 | -0.0041 | 19/28 | 0.0156 |
| raw+poly | xgboost | balanced_accuracy | 49 | +0.0018 | +0.0018 | +0.0000 | 23/24 | 0.725 |
| raw+poly | xgboost | roc_auc_ovr | 49 | -0.0003 | -0.0000 | -0.0003 | 25/21 | 1 |