# Downstream-Awareness Diagnostic

This report asks whether the schema family matched to a downstream model
beats the best mismatched schema family for the same dataset, schema generator,
downstream model, matrix pair, and metric.

## Scope

- Matched comparisons: 63
- Matched family beats best mismatch: 21
- Matched family loses to best mismatch: 42
- Ties: 0

## Strongest Matched Wins

| dataset           | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| phoneme           | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.0556 | tree            |                0.0157 |         0.0399 |
| car_evaluation    | gemini-3.1-pro-preview | knn                 | distance_knn |          0.008  | linear_svm      |               -0.0087 |         0.0167 |
| pima_diabetes     | gemini-3.1-pro-preview | knn                 | distance_knn |          0.0145 | linear_svm      |                0.0051 |         0.0094 |
| blood_transfusion | gemini-3.1-pro-preview | xgboost             | tree         |         -0.0083 | linear_svm      |               -0.0158 |         0.0076 |
| phoneme           | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0468 | tree            |                0.04   |         0.0068 |
| blood_transfusion | gemini-3.1-pro-preview | logistic_regression | linear_svm   |         -0.0007 | distance_knn    |               -0.0042 |         0.0035 |
| adult_income      | gemini-3.1-pro-preview | random_forest       | tree         |         -0.0015 | linear_svm      |               -0.0042 |         0.0027 |
| pima_diabetes     | claude-sonnet-4.6      | knn                 | distance_knn |          0.0111 | tree            |                0.0085 |         0.0027 |
| blood_transfusion | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0068 | distance_knn    |                0.0042 |         0.0026 |
| pima_diabetes     | claude-sonnet-4.6      | logistic_regression | linear_svm   |         -0.0026 | distance_knn    |               -0.0044 |         0.0018 |
| electricity       | gemini-3.1-pro-preview | random_forest       | tree         |         -0.0097 | linear_svm      |               -0.0113 |         0.0017 |
| spambase          | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.0066 | tree            |                0.0055 |         0.0011 |

## Strongest Matched Losses

| dataset           | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| car_evaluation    | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0732 | tree            |                0.1509 |        -0.0778 |
| blood_transfusion | gemini-3.1-pro-preview | knn                 | distance_knn |         -0.016  | tree            |               -0.0019 |        -0.0141 |
| credit_g          | gemini-3.1-pro-preview | xgboost             | tree         |         -0.014  | distance_knn    |               -0.0027 |        -0.0113 |
| credit_g          | claude-sonnet-4.6      | xgboost             | tree         |         -0.0111 | distance_knn    |               -0.0002 |        -0.0109 |
| phoneme           | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0133 | linear_svm      |               -0.0027 |        -0.0106 |
| credit_g          | gemini-3.1-pro-preview | logistic_regression | linear_svm   |         -0.0036 | distance_knn    |                0.0061 |        -0.0097 |
| pima_diabetes     | claude-sonnet-4.6      | xgboost             | tree         |         -0.0057 | distance_knn    |                0.0036 |        -0.0092 |
| blood_transfusion | claude-sonnet-4.6      | xgboost             | tree         |         -0.0135 | linear_svm      |               -0.0044 |        -0.0091 |
| pima_diabetes     | claude-sonnet-4.6      | random_forest       | tree         |         -0.0043 | linear_svm      |                0.0045 |        -0.0089 |
| pima_diabetes     | gemini-3.1-pro-preview | xgboost             | tree         |         -0.0049 | distance_knn    |                0.0029 |        -0.0078 |
| car_evaluation    | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.1345 | distance_knn    |                0.1409 |        -0.0064 |
| credit_g          | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0169 | tree            |               -0.011  |        -0.0059 |

## Guardrail

This is a diagnostic over existing runs, not a final statistical test.
Use it to decide whether downstream-awareness is a headline claim or a secondary characterization.
