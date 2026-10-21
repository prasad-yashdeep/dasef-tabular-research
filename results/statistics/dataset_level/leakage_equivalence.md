# Leakage Equivalence Check

Question: did cached full-data schema generation inflate `raw -> raw_plus_formula` effects relative to prospective schema generation?

- Prospective result files: 48
- Cached judgment result files: 213
- Overlapping dataset/model/metric cells: 54

## Summary By Metric And Downstream Model

| metric            | downstream_model    |   n_datasets |   prospective_mean_delta |   cached_mean_delta |   mean_difference_cached_minus_prospective |   mean_abs_difference |
|:------------------|:--------------------|-------------:|-------------------------:|--------------------:|-------------------------------------------:|----------------------:|
| balanced_accuracy | knn                 |            9 |                  0.00960 |             0.02355 |                                    0.01396 |               0.01569 |
| balanced_accuracy | logistic_regression |            9 |                  0.00451 |             0.00407 |                                   -0.00044 |               0.00360 |
| balanced_accuracy | random_forest       |            9 |                  0.00156 |             0.00139 |                                   -0.00018 |               0.00422 |
| roc_auc_ovr       | knn                 |            9 |                  0.00074 |             0.00226 |                                    0.00152 |               0.00349 |
| roc_auc_ovr       | logistic_regression |            9 |                  0.00605 |             0.00576 |                                   -0.00029 |               0.00187 |
| roc_auc_ovr       | random_forest       |            9 |                 -0.00072 |            -0.00132 |                                   -0.00060 |               0.00091 |

## Dataset-Level Comparison

| dataset             | downstream_model    | metric            |   mean_delta_cached_full_data |   mean_delta_prospective |   n_runs_cached_full_data |   n_runs_prospective |   difference_cached_minus_prospective |   abs_difference |
|:--------------------|:--------------------|:------------------|------------------------------:|-------------------------:|--------------------------:|---------------------:|--------------------------------------:|-----------------:|
| adult_income        | knn                 | balanced_accuracy |                       0.01688 |                  0.00996 |                  24.00000 |              6.00000 |                               0.00692 |          0.00692 |
| blood_transfusion   | knn                 | balanced_accuracy |                      -0.00184 |                 -0.00638 |                  19.00000 |              6.00000 |                               0.00454 |          0.00454 |
| car_evaluation      | knn                 | balanced_accuracy |                       0.15828 |                  0.06659 |                  24.00000 |              6.00000 |                               0.09169 |          0.09169 |
| credit_g            | knn                 | balanced_accuracy |                       0.02178 |                  0.02026 |                  24.00000 |              6.00000 |                               0.00152 |          0.00152 |
| electricity         | knn                 | balanced_accuracy |                      -0.00603 |                 -0.00228 |                  22.00000 |              4.00000 |                              -0.00375 |          0.00375 |
| phoneme             | knn                 | balanced_accuracy |                      -0.01071 |                 -0.01189 |                  22.00000 |              5.00000 |                               0.00118 |          0.00118 |
| pima_diabetes       | knn                 | balanced_accuracy |                       0.01629 |                 -0.00153 |                  22.00000 |              6.00000 |                               0.01781 |          0.01781 |
| qsar_biodegradation | knn                 | balanced_accuracy |                      -0.00501 |                 -0.00097 |                  22.00000 |              6.00000 |                              -0.00404 |          0.00404 |
| spambase            | knn                 | balanced_accuracy |                       0.02236 |                  0.01260 |                  15.00000 |              3.00000 |                               0.00976 |          0.00976 |
| adult_income        | logistic_regression | balanced_accuracy |                       0.00508 |                  0.00470 |                  24.00000 |              6.00000 |                               0.00037 |          0.00037 |
| blood_transfusion   | logistic_regression | balanced_accuracy |                      -0.00510 |                 -0.00749 |                  19.00000 |              6.00000 |                               0.00239 |          0.00239 |
| car_evaluation      | logistic_regression | balanced_accuracy |                       0.00842 |                  0.00978 |                  24.00000 |              6.00000 |                              -0.00136 |          0.00136 |
| credit_g            | logistic_regression | balanced_accuracy |                       0.00159 |                 -0.00397 |                  24.00000 |              6.00000 |                               0.00556 |          0.00556 |
| electricity         | logistic_regression | balanced_accuracy |                       0.00222 |                  0.00490 |                  22.00000 |              4.00000 |                              -0.00268 |          0.00268 |
| phoneme             | logistic_regression | balanced_accuracy |                       0.03261 |                  0.02707 |                  22.00000 |              5.00000 |                               0.00555 |          0.00555 |
| pima_diabetes       | logistic_regression | balanced_accuracy |                      -0.01002 |                  0.00337 |                  22.00000 |              6.00000 |                              -0.01339 |          0.01339 |
| qsar_biodegradation | logistic_regression | balanced_accuracy |                      -0.00517 |                 -0.00440 |                  22.00000 |              6.00000 |                              -0.00077 |          0.00077 |
| spambase            | logistic_regression | balanced_accuracy |                       0.00698 |                  0.00665 |                  15.00000 |              3.00000 |                               0.00033 |          0.00033 |
| adult_income        | random_forest       | balanced_accuracy |                       0.00853 |                  0.00132 |                  24.00000 |              6.00000 |                               0.00721 |          0.00721 |
| blood_transfusion   | random_forest       | balanced_accuracy |                       0.00159 |                 -0.00361 |                  19.00000 |              6.00000 |                               0.00520 |          0.00520 |
| car_evaluation      | random_forest       | balanced_accuracy |                       0.01271 |                  0.02472 |                  24.00000 |              6.00000 |                              -0.01201 |          0.01201 |
| credit_g            | random_forest       | balanced_accuracy |                       0.00315 |                  0.00474 |                  24.00000 |              6.00000 |                              -0.00159 |          0.00159 |
| electricity         | random_forest       | balanced_accuracy |                      -0.01343 |                 -0.01243 |                  22.00000 |              4.00000 |                              -0.00100 |          0.00100 |
| phoneme             | random_forest       | balanced_accuracy |                      -0.00048 |                 -0.00186 |                  22.00000 |              5.00000 |                               0.00138 |          0.00138 |
| pima_diabetes       | random_forest       | balanced_accuracy |                       0.00805 |                  0.00499 |                  22.00000 |              6.00000 |                               0.00306 |          0.00306 |
| qsar_biodegradation | random_forest       | balanced_accuracy |                      -0.00407 |                  0.00113 |                  22.00000 |              6.00000 |                              -0.00520 |          0.00520 |
| spambase            | random_forest       | balanced_accuracy |                      -0.00358 |                 -0.00493 |                  15.00000 |              3.00000 |                               0.00135 |          0.00135 |
| adult_income        | knn                 | roc_auc_ovr       |                       0.00152 |                  0.00293 |                  24.00000 |              6.00000 |                              -0.00141 |          0.00141 |
| blood_transfusion   | knn                 | roc_auc_ovr       |                      -0.00191 |                 -0.00771 |                  19.00000 |              6.00000 |                               0.00580 |          0.00580 |
| car_evaluation      | knn                 | roc_auc_ovr       |                       0.00218 |                 -0.00081 |                  24.00000 |              6.00000 |                               0.00299 |          0.00299 |
| credit_g            | knn                 | roc_auc_ovr       |                       0.01846 |                  0.01099 |                  24.00000 |              6.00000 |                               0.00747 |          0.00747 |
| electricity         | knn                 | roc_auc_ovr       |                      -0.00612 |                 -0.00174 |                  22.00000 |              4.00000 |                              -0.00438 |          0.00438 |
| phoneme             | knn                 | roc_auc_ovr       |                      -0.00736 |                 -0.00710 |                  22.00000 |              5.00000 |                              -0.00026 |          0.00026 |
| pima_diabetes       | knn                 | roc_auc_ovr       |                       0.00944 |                  0.00718 |                  22.00000 |              6.00000 |                               0.00226 |          0.00226 |
| qsar_biodegradation | knn                 | roc_auc_ovr       |                      -0.00574 |                 -0.00293 |                  22.00000 |              6.00000 |                              -0.00281 |          0.00281 |
| spambase            | knn                 | roc_auc_ovr       |                       0.00989 |                  0.00587 |                  15.00000 |              3.00000 |                               0.00401 |          0.00401 |
| adult_income        | logistic_regression | roc_auc_ovr       |                       0.00597 |                  0.00559 |                  24.00000 |              6.00000 |                               0.00037 |          0.00037 |
| blood_transfusion   | logistic_regression | roc_auc_ovr       |                      -0.00077 |                 -0.00024 |                  19.00000 |              6.00000 |                              -0.00053 |          0.00053 |
| car_evaluation      | logistic_regression | roc_auc_ovr       |                       0.00535 |                  0.00354 |                  24.00000 |              6.00000 |                               0.00181 |          0.00181 |
| credit_g            | logistic_regression | roc_auc_ovr       |                      -0.00066 |                 -0.00164 |                  24.00000 |              6.00000 |                               0.00097 |          0.00097 |
| electricity         | logistic_regression | roc_auc_ovr       |                       0.00313 |                  0.00836 |                  22.00000 |              4.00000 |                              -0.00523 |          0.00523 |
| phoneme             | logistic_regression | roc_auc_ovr       |                       0.03558 |                  0.03949 |                  22.00000 |              5.00000 |                              -0.00391 |          0.00391 |
| pima_diabetes       | logistic_regression | roc_auc_ovr       |                      -0.00055 |                 -0.00351 |                  22.00000 |              6.00000 |                               0.00296 |          0.00296 |
| qsar_biodegradation | logistic_regression | roc_auc_ovr       |                      -0.00149 |                 -0.00248 |                  22.00000 |              6.00000 |                               0.00099 |          0.00099 |
| spambase            | logistic_regression | roc_auc_ovr       |                       0.00524 |                  0.00530 |                  15.00000 |              3.00000 |                              -0.00006 |          0.00006 |
| adult_income        | random_forest       | roc_auc_ovr       |                       0.00257 |                  0.00248 |                  24.00000 |              6.00000 |                               0.00010 |          0.00010 |
| blood_transfusion   | random_forest       | roc_auc_ovr       |                      -0.00287 |                 -0.00104 |                  19.00000 |              6.00000 |                              -0.00183 |          0.00183 |
| car_evaluation      | random_forest       | roc_auc_ovr       |                      -0.00006 |                  0.00110 |                  24.00000 |              6.00000 |                              -0.00115 |          0.00115 |
| credit_g            | random_forest       | roc_auc_ovr       |                       0.00042 |                 -0.00044 |                  24.00000 |              6.00000 |                               0.00086 |          0.00086 |
| electricity         | random_forest       | roc_auc_ovr       |                      -0.01187 |                 -0.01025 |                  22.00000 |              4.00000 |                              -0.00162 |          0.00162 |
| phoneme             | random_forest       | roc_auc_ovr       |                      -0.00059 |                  0.00044 |                  22.00000 |              5.00000 |                              -0.00103 |          0.00103 |
| pima_diabetes       | random_forest       | roc_auc_ovr       |                       0.00403 |                  0.00357 |                  22.00000 |              6.00000 |                               0.00045 |          0.00045 |
| qsar_biodegradation | random_forest       | roc_auc_ovr       |                      -0.00147 |                 -0.00058 |                  22.00000 |              6.00000 |                              -0.00089 |          0.00089 |
| spambase            | random_forest       | roc_auc_ovr       |                      -0.00205 |                 -0.00179 |                  15.00000 |              3.00000 |                              -0.00026 |          0.00026 |

## Interpretation

Mean absolute difference is 0.0050 with signed cached-minus-prospective difference +0.0023; the two schema-generation modes look broadly similar at this aggregation level.