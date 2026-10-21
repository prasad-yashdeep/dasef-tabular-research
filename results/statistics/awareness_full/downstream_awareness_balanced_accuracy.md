# Downstream-Awareness Diagnostic

This report asks whether the schema family matched to a downstream model
beats the best mismatched schema family for the same dataset, schema generator,
downstream model, matrix pair, and metric.

## Scope

- Matched comparisons: 160
- Matched family beats best mismatch: 48
- Matched family loses to best mismatch: 112
- Ties: 0

## Strongest Matched Wins

| dataset           | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| car_evaluation    | gpt-5.5-pro            | knn                 | distance_knn |          0.2346 | tree            |                0.164  |         0.0706 |
| bank_marketing    | claude-sonnet-4.6      | knn                 | distance_knn |          0.0441 | tree            |                0.0136 |         0.0305 |
| phoneme           | claude-opus-4.7        | logistic_regression | linear_svm   |          0.0667 | tree            |                0.0388 |         0.0279 |
| phoneme           | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.0508 | distance_knn    |                0.025  |         0.0258 |
| car_evaluation    | gpt-5.5-pro            | xgboost             | tree         |          0.0486 | distance_knn    |                0.0229 |         0.0257 |
| car_evaluation    | gpt-5.5-pro            | random_forest       | tree         |          0.0381 | distance_knn    |                0.0145 |         0.0236 |
| bank_marketing    | gemini-3.1-pro-preview | knn                 | distance_knn |          0.0176 | tree            |               -0.0052 |         0.0228 |
| blood_transfusion | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0042 | distance_knn    |               -0.0127 |         0.0169 |
| bank_marketing    | claude-opus-4.7        | random_forest       | tree         |          0.0664 | linear_svm      |                0.0515 |         0.0149 |
| blood_transfusion | gpt-5.5-pro            | xgboost             | tree         |          0.0195 | distance_knn    |                0.0054 |         0.0141 |
| pima_diabetes     | gemini-3.1-pro-preview | knn                 | distance_knn |          0.0334 | linear_svm      |                0.02   |         0.0134 |
| credit_g          | gpt-5.5-pro            | xgboost             | tree         |          0.0102 | distance_knn    |               -0.0031 |         0.0133 |

## Strongest Matched Losses

| dataset           | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| car_evaluation    | claude-sonnet-4.6      | knn                 | distance_knn |          0.1107 | tree            |                0.1838 |        -0.0732 |
| credit_g          | claude-opus-4.7        | knn                 | distance_knn |         -0.0202 | tree            |                0.0514 |        -0.0716 |
| credit_g          | gpt-5.5-pro            | knn                 | distance_knn |         -0.0068 | linear_svm      |                0.0549 |        -0.0617 |
| bank_marketing    | gemini-3.1-pro-preview | random_forest       | tree         |         -0.0064 | distance_knn    |                0.049  |        -0.0554 |
| pima_diabetes     | gemini-3.1-pro-preview | xgboost             | tree         |         -0.0185 | linear_svm      |                0.0162 |        -0.0347 |
| car_evaluation    | claude-opus-4.7        | knn                 | distance_knn |          0.215  | tree            |                0.2496 |        -0.0346 |
| phoneme           | gpt-5.5-pro            | logistic_regression | linear_svm   |          0.0114 | tree            |                0.0444 |        -0.033  |
| car_evaluation    | claude-opus-4.7        | logistic_regression | linear_svm   |         -0.0041 | tree            |                0.0257 |        -0.0298 |
| credit_g          | gemini-3.1-pro-preview | knn                 | distance_knn |         -0.0111 | tree            |                0.0182 |        -0.0293 |
| blood_transfusion | claude-opus-4.7        | knn                 | distance_knn |         -0.0052 | tree            |                0.0219 |        -0.0271 |
| phoneme           | gpt-5.5-pro            | knn                 | distance_knn |         -0.0303 | linear_svm      |               -0.0044 |        -0.0259 |
| blood_transfusion | gemini-3.1-pro-preview | knn                 | distance_knn |         -0.0112 | linear_svm      |                0.0134 |        -0.0245 |

## Guardrail

This is a diagnostic over existing runs, not a final statistical test.
Use it to decide whether downstream-awareness is a headline claim or a secondary characterization.
