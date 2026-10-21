# Downstream-Awareness Diagnostic

This report asks whether the schema family matched to a downstream model
beats the best mismatched schema family for the same dataset, schema generator,
downstream model, matrix pair, and metric.

## Scope

- Matched comparisons: 63
- Matched family beats best mismatch: 26
- Matched family loses to best mismatch: 37
- Ties: 0

## Strongest Matched Wins

| dataset           | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| car_evaluation    | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.2915 | distance_knn    |                0.2436 |         0.0479 |
| phoneme           | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.046  | tree            |                0.01   |         0.036  |
| car_evaluation    | gemini-3.1-pro-preview | knn                 | distance_knn |          0.1114 | linear_svm      |                0.0895 |         0.0219 |
| pima_diabetes     | gemini-3.1-pro-preview | knn                 | distance_knn |          0.0129 | linear_svm      |               -0.0055 |         0.0183 |
| credit_g          | claude-sonnet-4.6      | xgboost             | tree         |         -0.0033 | distance_knn    |               -0.0129 |         0.0097 |
| blood_transfusion | gemini-3.1-pro-preview | logistic_regression | linear_svm   |         -0.0003 | tree            |               -0.0095 |         0.0092 |
| pima_diabetes     | gemini-3.1-pro-preview | xgboost             | tree         |          0.005  | linear_svm      |               -0.0033 |         0.0083 |
| car_evaluation    | claude-sonnet-4.6      | random_forest       | tree         |         -0.0121 | linear_svm      |               -0.0191 |         0.007  |
| credit_g          | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0031 | tree            |               -0.0037 |         0.0068 |
| blood_transfusion | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0009 | distance_knn    |               -0.0051 |         0.006  |
| blood_transfusion | gemini-3.1-pro-preview | xgboost             | tree         |          0.0005 | distance_knn    |               -0.0037 |         0.0042 |
| phoneme           | gemini-3.1-pro-preview | random_forest       | tree         |          0.0034 | linear_svm      |               -0.0005 |         0.0038 |

## Strongest Matched Losses

| dataset             | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:--------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| car_evaluation      | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0175 | tree            |                0.1113 |        -0.1288 |
| car_evaluation      | gemini-3.1-pro-preview | random_forest       | tree         |         -0.0158 | distance_knn    |                0.0212 |        -0.037  |
| pima_diabetes       | claude-sonnet-4.6      | random_forest       | tree         |         -0.0163 | linear_svm      |                0.0203 |        -0.0366 |
| car_evaluation      | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.1484 | tree            |                0.1834 |        -0.0351 |
| credit_g            | gemini-3.1-pro-preview | xgboost             | tree         |         -0.0205 | distance_knn    |                0.003  |        -0.0235 |
| pima_diabetes       | claude-sonnet-4.6      | xgboost             | tree         |         -0.0081 | linear_svm      |                0.0141 |        -0.0223 |
| pima_diabetes       | gemini-3.1-pro-preview | logistic_regression | linear_svm   |         -0.01   | distance_knn    |                0.0091 |        -0.0192 |
| credit_g            | gemini-3.1-pro-preview | knn                 | distance_knn |         -0.0187 | tree            |               -0.0042 |        -0.0146 |
| qsar_biodegradation | gemini-3.1-pro-preview | random_forest       | tree         |         -0.0057 | linear_svm      |                0.0075 |        -0.0132 |
| blood_transfusion   | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0043 | linear_svm      |                0.0085 |        -0.0128 |
| credit_g            | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0119 | linear_svm      |               -0.0015 |        -0.0104 |
| phoneme             | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0142 | linear_svm      |               -0.0052 |        -0.009  |

## Guardrail

This is a diagnostic over existing runs, not a final statistical test.
Use it to decide whether downstream-awareness is a headline claim or a secondary characterization.
