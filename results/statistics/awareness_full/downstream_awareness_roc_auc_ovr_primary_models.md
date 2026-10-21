# Downstream-Awareness Diagnostic

This report asks whether the schema family matched to a downstream model
beats the best mismatched schema family for the same dataset, schema generator,
downstream model, matrix pair, and metric.

## Scope

- Matched comparisons: 120
- Matched family beats best mismatch: 44
- Matched family loses to best mismatch: 76
- Ties: 0

## Strongest Matched Wins

| dataset             | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:--------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| bank_marketing      | gemini-3.1-pro-preview | knn                 | distance_knn |          0.0138 | tree            |               -0.0147 |         0.0285 |
| phoneme             | gemini-3.1-pro-preview | logistic_regression | linear_svm   |          0.0553 | distance_knn    |                0.0399 |         0.0154 |
| pima_diabetes       | gemini-3.1-pro-preview | knn                 | distance_knn |          0.0231 | linear_svm      |                0.0104 |         0.0127 |
| car_evaluation      | gemini-3.1-pro-preview | knn                 | distance_knn |          0.012  | linear_svm      |               -0.0004 |         0.0124 |
| car_evaluation      | gpt-5.5-pro            | knn                 | distance_knn |          0.0163 | tree            |                0.0073 |         0.009  |
| bank_marketing      | claude-sonnet-4.6      | knn                 | distance_knn |          0.0174 | tree            |                0.0085 |         0.0088 |
| credit_g            | claude-sonnet-4.6      | random_forest       | tree         |          0.008  | linear_svm      |                0.0008 |         0.0072 |
| phoneme             | claude-opus-4.7        | logistic_regression | linear_svm   |          0.0526 | tree            |                0.046  |         0.0066 |
| blood_transfusion   | gpt-5.5-pro            | random_forest       | tree         |          0.0052 | distance_knn    |               -0.0014 |         0.0066 |
| blood_transfusion   | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.007  | distance_knn    |                0.0008 |         0.0062 |
| phoneme             | claude-sonnet-4.6      | logistic_regression | linear_svm   |          0.0449 | tree            |                0.039  |         0.0059 |
| qsar_biodegradation | claude-opus-4.7        | logistic_regression | linear_svm   |          0.0039 | tree            |               -0.0016 |         0.0055 |

## Strongest Matched Losses

| dataset           | schema_model           | model               | matched      |   matched_delta | best_mismatch   |   best_mismatch_delta |   matched-best |
|:------------------|:-----------------------|:--------------------|:-------------|----------------:|:----------------|----------------------:|---------------:|
| credit_g          | gpt-5.5-pro            | knn                 | distance_knn |         -0.0162 | linear_svm      |                0.047  |        -0.0632 |
| credit_g          | claude-opus-4.7        | knn                 | distance_knn |         -0.0068 | linear_svm      |                0.0475 |        -0.0543 |
| phoneme           | gpt-5.5-pro            | logistic_regression | linear_svm   |          0.0042 | distance_knn    |                0.0392 |        -0.035  |
| credit_g          | gemini-3.1-pro-preview | knn                 | distance_knn |         -0.0033 | tree            |                0.021  |        -0.0244 |
| credit_g          | claude-sonnet-4.6      | knn                 | distance_knn |          0.0297 | linear_svm      |                0.0506 |        -0.0209 |
| blood_transfusion | claude-opus-4.7        | knn                 | distance_knn |         -0.0072 | tree            |                0.0109 |        -0.0181 |
| electricity       | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0119 | tree            |                0.0033 |        -0.0152 |
| phoneme           | gpt-5.5-pro            | knn                 | distance_knn |         -0.0188 | linear_svm      |               -0.0045 |        -0.0144 |
| electricity       | gpt-5.5-pro            | knn                 | distance_knn |         -0.0107 | linear_svm      |                0.0018 |        -0.0125 |
| blood_transfusion | claude-opus-4.7        | logistic_regression | linear_svm   |         -0.0049 | tree            |                0.0064 |        -0.0113 |
| blood_transfusion | claude-sonnet-4.6      | knn                 | distance_knn |         -0.0091 | linear_svm      |                0.0022 |        -0.0113 |
| pima_diabetes     | claude-sonnet-4.6      | random_forest       | tree         |          0.0003 | linear_svm      |                0.0112 |        -0.0109 |

## Guardrail

This is a diagnostic over existing runs, not a final statistical test.
Use it to decide whether downstream-awareness is a headline claim or a secondary characterization.
