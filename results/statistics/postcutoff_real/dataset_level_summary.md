# Post-Cutoff Never-Seen: Dataset-Level Aggregation

Runs aggregated: 35; datasets: 6 (postcutoff_clinical_trials_ai_20260517, postcutoff_prediction_markets_20260517, postcutoff_ro_real_estate_20260503, postcutoff_salmonella_serovar_20260401, postcutoff_tracker_radar_20260316, postcutoff_water_quality_nys_20260406).
semantic = formula - random_formula; direct = formula - raw. Wilcoxon across datasets.

## roc_auc_ovr

| Model | contrast | N | mean Δ | W/L | p |
|---|---|---|---|---|---|
| xgboost | semantic | 6 | +0.0208 | 6/0 | 0.0312 |
| xgboost | direct | 6 | +0.0159 | 4/2 | 0.2188 |
| logistic_regression | semantic | 6 | +0.0416 | 5/1 | 0.0625 |
| logistic_regression | direct | 6 | +0.0418 | 6/0 | 0.0312 |
| random_forest | semantic | 6 | +0.0186 | 5/1 | 0.0625 |
| random_forest | direct | 6 | +0.0119 | 4/2 | 0.3125 |
| knn | semantic | 6 | +0.0841 | 5/1 | 0.0625 |
| knn | direct | 6 | +0.0119 | 4/2 | 0.4375 |

## balanced_accuracy

| Model | contrast | N | mean Δ | W/L | p |
|---|---|---|---|---|---|
| xgboost | semantic | 6 | +0.0344 | 5/1 | 0.2188 |
| xgboost | direct | 6 | +0.0297 | 4/2 | 0.3125 |
| logistic_regression | semantic | 6 | +0.0422 | 6/0 | 0.0312 |
| logistic_regression | direct | 6 | +0.0401 | 6/0 | 0.0312 |
| random_forest | semantic | 6 | +0.0433 | 5/1 | 0.0625 |
| random_forest | direct | 6 | +0.0159 | 3/3 | 1.0000 |
| knn | semantic | 6 | +0.0835 | 6/0 | 0.0312 |
| knn | direct | 6 | +0.0178 | 4/2 | 0.8438 |
