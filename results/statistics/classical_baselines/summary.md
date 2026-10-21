# Classical Feature Engineering Baselines (corrected protocol)

Scope: cap-then-split identical to the main DASEF benchmark (`stratified_cap(ds, recorded cap_rows)` then
`schema_design_eval_split(ds, 0.3, 42)`); evaluation rows are row-identical to the stored DASEF matrices.
Each classical system is fit on the design split only (labels allowed there) and applied to the evaluation split;
no evaluation-split label is used outside the CV training folds.
CV: 5-fold x 2-repeat with `xgboost`, `logistic_regression`, `random_forest`, `knn`.

## Run Status

| dataset             |   cap_rows |   design_rows |   eval_rows |   raw_cols | aligned   | poly_status                                         |   poly_fit_s | openfe_status                                                                |   openfe_fit_s | autofeat_status                                                               |   autofeat_fit_s |
|:--------------------|-----------:|--------------:|------------:|-----------:|:----------|:----------------------------------------------------|-------------:|:-----------------------------------------------------------------------------|---------------:|:------------------------------------------------------------------------------|-----------------:|
| adult_income        |       5000 |          1500 |        3500 |         14 | True      | poly selected 12 interactions by MI on design split |          0.2 | OpenFE generated 12 features; fit on design split, transformed on eval split |           20.1 | autofeat generated 1 features; fit on design split, transformed on eval split |              2.6 |
| bank_marketing      |       5000 |          1500 |        3500 |         20 | True      | poly selected 12 interactions by MI on design split |          0.4 | OpenFE generated 12 features; fit on design split, transformed on eval split |           52.1 | autofeat generated 2 features; fit on design split, transformed on eval split |              4.4 |
| blood_transfusion   |        nan |           224 |         524 |          4 | True      | poly selected 6 interactions by MI on design split  |          0   | OpenFE generated 12 features; fit on design split, transformed on eval split |            7.9 | autofeat produced no additional features (fit on design split)                |              0.5 |
| car_evaluation      |        nan |           518 |        1210 |          6 | True      | poly selected 12 interactions by MI on design split |          0   | OpenFE generated 12 features; fit on design split, transformed on eval split |           10.8 | autofeat produced no additional features (fit on design split)                |              1.5 |
| credit_g            |        nan |           300 |         700 |         20 | True      | poly selected 12 interactions by MI on design split |          0.1 | OpenFE generated 12 features; fit on design split, transformed on eval split |           18.8 | autofeat produced no additional features (fit on design split)                |              0.5 |
| electricity         |       5000 |          1500 |        3500 |          7 | True      | poly selected 12 interactions by MI on design split |          0   | OpenFE generated 12 features; fit on design split, transformed on eval split |            7.6 | autofeat produced no additional features (fit on design split)                |              1.1 |
| phoneme             |        nan |          1621 |        3783 |          5 | True      | poly selected 10 interactions by MI on design split |          0   | OpenFE generated 12 features; fit on design split, transformed on eval split |            7.1 | autofeat generated 1 features; fit on design split, transformed on eval split |              0.6 |
| pima_diabetes       |        nan |           230 |         538 |          8 | True      | poly selected 12 interactions by MI on design split |          0   | OpenFE generated 12 features; fit on design split, transformed on eval split |            8   | autofeat produced no additional features (fit on design split)                |              0.4 |
| qsar_biodegradation |        nan |           316 |         739 |         41 | True      | poly selected 12 interactions by MI on design split |          0.6 | OpenFE generated 12 features; fit on design split, transformed on eval split |           38.4 | autofeat generated 1 features; fit on design split, transformed on eval split |              1.8 |
| spambase            |        nan |          1380 |        3221 |         57 | True      | poly selected 12 interactions by MI on design split |          2.7 | OpenFE generated 12 features; fit on design split, transformed on eval split |           93.7 | autofeat generated 7 features; fit on design split, transformed on eval split |             12.6 |

## Mean Deltas vs Raw

| variant      | metric            | model               |   mean_classical_delta |   mean_dasef_formula_delta |   n |
|:-------------|:------------------|:--------------------|-----------------------:|---------------------------:|----:|
| raw+autofeat | accuracy          | knn                 |                 0.0066 |                   nan      |   5 |
| raw+openfe   | accuracy          | knn                 |                 0.0073 |                   nan      |  10 |
| raw+poly     | accuracy          | knn                 |                -0.0015 |                   nan      |  10 |
| raw+autofeat | accuracy          | logistic_regression |                 0.0019 |                   nan      |   5 |
| raw+openfe   | accuracy          | logistic_regression |                 0.0291 |                   nan      |  10 |
| raw+poly     | accuracy          | logistic_regression |                 0.0116 |                   nan      |  10 |
| raw+autofeat | accuracy          | random_forest       |                 0.0002 |                   nan      |   5 |
| raw+openfe   | accuracy          | random_forest       |                 0.0039 |                   nan      |  10 |
| raw+poly     | accuracy          | random_forest       |                -0.0046 |                   nan      |  10 |
| raw+autofeat | accuracy          | xgboost             |                 0.0005 |                   nan      |   5 |
| raw+openfe   | accuracy          | xgboost             |                 0.0004 |                   nan      |  10 |
| raw+poly     | accuracy          | xgboost             |                -0.0023 |                   nan      |  10 |
| raw+autofeat | balanced_accuracy | knn                 |                 0.0126 |                     0.0080 |   5 |
| raw+openfe   | balanced_accuracy | knn                 |                 0.0243 |                     0.0066 |  10 |
| raw+poly     | balanced_accuracy | knn                 |                 0.0099 |                     0.0066 |  10 |
| raw+autofeat | balanced_accuracy | logistic_regression |                 0.0020 |                     0.0115 |   5 |
| raw+openfe   | balanced_accuracy | logistic_regression |                 0.0294 |                     0.0241 |  10 |
| raw+poly     | balanced_accuracy | logistic_regression |                 0.0178 |                     0.0241 |  10 |
| raw+autofeat | balanced_accuracy | random_forest       |                 0.0061 |                     0.0000 |   5 |
| raw+openfe   | balanced_accuracy | random_forest       |                 0.0098 |                    -0.0021 |  10 |
| raw+poly     | balanced_accuracy | random_forest       |                 0.0028 |                    -0.0021 |  10 |
| raw+autofeat | balanced_accuracy | xgboost             |                 0.0004 |                     0.0007 |   5 |
| raw+openfe   | balanced_accuracy | xgboost             |                 0.0019 |                    -0.0006 |  10 |
| raw+poly     | balanced_accuracy | xgboost             |                 0.0005 |                    -0.0006 |  10 |
| raw+autofeat | f1_macro          | knn                 |                 0.0124 |                   nan      |   5 |
| raw+openfe   | f1_macro          | knn                 |                 0.0260 |                   nan      |  10 |
| raw+poly     | f1_macro          | knn                 |                 0.0104 |                   nan      |  10 |
| raw+autofeat | f1_macro          | logistic_regression |                 0.0018 |                   nan      |   5 |
| raw+openfe   | f1_macro          | logistic_regression |                 0.0289 |                   nan      |  10 |
| raw+poly     | f1_macro          | logistic_regression |                 0.0126 |                   nan      |  10 |
| raw+autofeat | f1_macro          | random_forest       |                 0.0049 |                   nan      |   5 |
| raw+openfe   | f1_macro          | random_forest       |                 0.0090 |                   nan      |  10 |
| raw+poly     | f1_macro          | random_forest       |                 0.0006 |                   nan      |  10 |
| raw+autofeat | f1_macro          | xgboost             |                 0.0004 |                   nan      |   5 |
| raw+openfe   | f1_macro          | xgboost             |                 0.0013 |                   nan      |  10 |
| raw+poly     | f1_macro          | xgboost             |                 0.0000 |                   nan      |  10 |
| raw+autofeat | roc_auc_ovr       | knn                 |                 0.0082 |                     0.0018 |   5 |
| raw+openfe   | roc_auc_ovr       | knn                 |                 0.0095 |                    -0.0008 |  10 |
| raw+poly     | roc_auc_ovr       | knn                 |                 0.0059 |                    -0.0008 |  10 |
| raw+autofeat | roc_auc_ovr       | logistic_regression |                 0.0021 |                     0.0118 |   5 |
| raw+openfe   | roc_auc_ovr       | logistic_regression |                 0.0250 |                     0.0165 |  10 |
| raw+poly     | roc_auc_ovr       | logistic_regression |                 0.0093 |                     0.0165 |  10 |
| raw+autofeat | roc_auc_ovr       | random_forest       |                -0.0012 |                    -0.0020 |   5 |
| raw+openfe   | roc_auc_ovr       | random_forest       |                -0.0003 |                    -0.0021 |  10 |
| raw+poly     | roc_auc_ovr       | random_forest       |                -0.0036 |                    -0.0021 |  10 |
| raw+autofeat | roc_auc_ovr       | xgboost             |                -0.0002 |                    -0.0002 |   5 |
| raw+openfe   | roc_auc_ovr       | xgboost             |                -0.0013 |                    -0.0000 |  10 |
| raw+poly     | roc_auc_ovr       | xgboost             |                -0.0000 |                    -0.0000 |  10 |

Dataset-level comparison was also saved to `deltas_vs_dasef_formula.csv`.

## Change vs previous run (split-then-cap, label-selected on eval split)

| variant      | metric            | model               |   mean_corrected |   mean_previous |   mean_change |   n |
|:-------------|:------------------|:--------------------|-----------------:|----------------:|--------------:|----:|
| raw+autofeat | accuracy          | knn                 |           0.0066 |          0.0093 |       -0.0027 |   5 |
| raw+openfe   | accuracy          | knn                 |           0.0073 |          0.0121 |       -0.0048 |  10 |
| raw+poly     | accuracy          | knn                 |          -0.0015 |          0.0031 |       -0.0046 |  10 |
| raw+autofeat | accuracy          | logistic_regression |           0.0019 |          0.0018 |        0.0001 |   5 |
| raw+openfe   | accuracy          | logistic_regression |           0.0291 |          0.0563 |       -0.0271 |  10 |
| raw+poly     | accuracy          | logistic_regression |           0.0116 |          0.0109 |        0.0008 |  10 |
| raw+autofeat | accuracy          | random_forest       |           0.0002 |          0.0004 |       -0.0001 |   5 |
| raw+openfe   | accuracy          | random_forest       |           0.0039 |          0.0080 |       -0.0041 |  10 |
| raw+poly     | accuracy          | random_forest       |          -0.0046 |         -0.0022 |       -0.0024 |  10 |
| raw+autofeat | accuracy          | xgboost             |           0.0005 |          0.0006 |       -0.0001 |   5 |
| raw+openfe   | accuracy          | xgboost             |           0.0004 |          0.0070 |       -0.0066 |  10 |
| raw+poly     | accuracy          | xgboost             |          -0.0023 |         -0.0013 |       -0.0010 |  10 |
| raw+autofeat | balanced_accuracy | knn                 |           0.0126 |          0.0150 |       -0.0024 |   5 |
| raw+openfe   | balanced_accuracy | knn                 |           0.0243 |          0.0382 |       -0.0139 |  10 |
| raw+poly     | balanced_accuracy | knn                 |           0.0099 |          0.0167 |       -0.0068 |  10 |
| raw+autofeat | balanced_accuracy | logistic_regression |           0.0020 |          0.0016 |        0.0004 |   5 |
| raw+openfe   | balanced_accuracy | logistic_regression |           0.0294 |          0.0563 |       -0.0269 |  10 |
| raw+poly     | balanced_accuracy | logistic_regression |           0.0178 |          0.0163 |        0.0015 |  10 |
| raw+autofeat | balanced_accuracy | random_forest       |           0.0061 |          0.0042 |        0.0019 |   5 |
| raw+openfe   | balanced_accuracy | random_forest       |           0.0098 |          0.0185 |       -0.0087 |  10 |
| raw+poly     | balanced_accuracy | random_forest       |           0.0028 |          0.0048 |       -0.0020 |  10 |
| raw+autofeat | balanced_accuracy | xgboost             |           0.0004 |          0.0010 |       -0.0006 |   5 |
| raw+openfe   | balanced_accuracy | xgboost             |           0.0019 |          0.0137 |       -0.0118 |  10 |
| raw+poly     | balanced_accuracy | xgboost             |           0.0005 |          0.0012 |       -0.0007 |  10 |
| raw+autofeat | f1_macro          | knn                 |           0.0124 |          0.0142 |       -0.0017 |   5 |
| raw+openfe   | f1_macro          | knn                 |           0.0260 |          0.0364 |       -0.0104 |  10 |
| raw+poly     | f1_macro          | knn                 |           0.0104 |          0.0169 |       -0.0066 |  10 |
| raw+autofeat | f1_macro          | logistic_regression |           0.0018 |          0.0018 |        0.0000 |   5 |
| raw+openfe   | f1_macro          | logistic_regression |           0.0289 |          0.0661 |       -0.0372 |  10 |
| raw+poly     | f1_macro          | logistic_regression |           0.0126 |          0.0124 |        0.0002 |  10 |
| raw+autofeat | f1_macro          | random_forest       |           0.0049 |          0.0034 |        0.0015 |   5 |
| raw+openfe   | f1_macro          | random_forest       |           0.0090 |          0.0167 |       -0.0078 |  10 |
| raw+poly     | f1_macro          | random_forest       |           0.0006 |          0.0034 |       -0.0028 |  10 |
| raw+autofeat | f1_macro          | xgboost             |           0.0004 |          0.0010 |       -0.0006 |   5 |
| raw+openfe   | f1_macro          | xgboost             |           0.0013 |          0.0129 |       -0.0116 |  10 |
| raw+poly     | f1_macro          | xgboost             |           0.0000 |          0.0010 |       -0.0010 |  10 |
| raw+autofeat | roc_auc_ovr       | knn                 |           0.0082 |          0.0058 |        0.0024 |   5 |
| raw+openfe   | roc_auc_ovr       | knn                 |           0.0095 |          0.0159 |       -0.0065 |  10 |
| raw+poly     | roc_auc_ovr       | knn                 |           0.0059 |          0.0073 |       -0.0015 |  10 |
| raw+autofeat | roc_auc_ovr       | logistic_regression |           0.0021 |          0.0028 |       -0.0007 |   5 |
| raw+openfe   | roc_auc_ovr       | logistic_regression |           0.0250 |          0.0328 |       -0.0078 |  10 |
| raw+poly     | roc_auc_ovr       | logistic_regression |           0.0093 |          0.0096 |       -0.0003 |  10 |
| raw+autofeat | roc_auc_ovr       | random_forest       |          -0.0012 |         -0.0004 |       -0.0008 |   5 |
| raw+openfe   | roc_auc_ovr       | random_forest       |          -0.0003 |          0.0059 |       -0.0062 |  10 |
| raw+poly     | roc_auc_ovr       | random_forest       |          -0.0036 |         -0.0027 |       -0.0009 |  10 |
| raw+autofeat | roc_auc_ovr       | xgboost             |          -0.0002 |          0.0001 |       -0.0003 |   5 |
| raw+openfe   | roc_auc_ovr       | xgboost             |          -0.0013 |          0.0058 |       -0.0071 |  10 |
| raw+poly     | roc_auc_ovr       | xgboost             |          -0.0000 |          0.0006 |       -0.0007 |  10 |

Per-dataset comparison saved to `per_dataset_delta_vs_previous.csv`.
