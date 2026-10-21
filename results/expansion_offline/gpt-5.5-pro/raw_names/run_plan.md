# Clean Formula-Control Run Plan

This plan evaluates existing cached DASEF schemas with leakage-safe evaluation rows,
formula-only DASEF features, and random-control matrices. It does not call LLM APIs.

Important: cached schemas are publishable under the leakage-safe protocol only if
they were generated from the same schema-design split. Otherwise this is rehearsal
evidence for pipeline validation and screening.

## Summary

- Planned runs: 32
- Missing schemas: 0
- Skipped by max-runs: 0

## Runs

| dataset                                | family     | schema_model   | schema_path                                                                                              |   feature_count |   formula_feature_count |   judgment_feature_count | status   |
|:---------------------------------------|:-----------|:---------------|:---------------------------------------------------------------------------------------------------------|----------------:|------------------------:|-------------------------:|:---------|
| 2dplanes                               | linear_svm | gpt-5.5-pro    | cache/schemas/2dplanes/linear_svm/gpt-5.5-pro/schema_113bf7e5a9692080.json                               |              12 |                      10 |                        2 | planned  |
| ailerons                               | linear_svm | gpt-5.5-pro    | cache/schemas/ailerons/linear_svm/gpt-5.5-pro/schema_d73ec22e6ac6fccc.json                               |              12 |                      10 |                        2 | planned  |
| airlines                               | linear_svm | gpt-5.5-pro    | cache/schemas/airlines/linear_svm/gpt-5.5-pro/schema_18e0454925649461.json                               |              12 |                       6 |                        6 | planned  |
| bitcoinheist_ransomware                | linear_svm | gpt-5.5-pro    | cache/schemas/bitcoinheist_ransomware/linear_svm/gpt-5.5-pro/schema_0cbcf61c8bed67b1.json                |              12 |                      10 |                        2 | planned  |
| bng_breast_w                           | linear_svm | gpt-5.5-pro    | cache/schemas/bng_breast_w/linear_svm/gpt-5.5-pro/schema_f4995186986f025a.json                           |              12 |                      10 |                        2 | planned  |
| click_prediction_small                 | linear_svm | gpt-5.5-pro    | cache/schemas/click_prediction_small/linear_svm/gpt-5.5-pro/schema_8dfd10156e090b0e.json                 |              12 |                      10 |                        2 | planned  |
| codexglue                              | linear_svm | gpt-5.5-pro    | cache/schemas/codexglue/linear_svm/gpt-5.5-pro/schema_6426c47834a64afa.json                              |              12 |                       6 |                        6 | planned  |
| coil2000_insurance_policies            | linear_svm | gpt-5.5-pro    | cache/schemas/coil2000_insurance_policies/linear_svm/gpt-5.5-pro/schema_241907e06852df9e.json            |              12 |                      10 |                        2 | planned  |
| compass                                | linear_svm | gpt-5.5-pro    | cache/schemas/compass/linear_svm/gpt-5.5-pro/schema_7f0cf1e7c3788062.json                                |              12 |                      10 |                        2 | planned  |
| customer_churn_classification_nominal  | linear_svm | gpt-5.5-pro    | cache/schemas/customer_churn_classification_nominal/linear_svm/gpt-5.5-pro/schema_6c744d19758ff065.json  |              12 |                      10 |                        2 | planned  |
| employee_turnover_at_techco            | linear_svm | gpt-5.5-pro    | cache/schemas/employee_turnover_at_techco/linear_svm/gpt-5.5-pro/schema_ee6b420b77b8d987.json            |              12 |                      10 |                        2 | planned  |
| first_order_theorem_proving            | linear_svm | gpt-5.5-pro    | cache/schemas/first_order_theorem_proving/linear_svm/gpt-5.5-pro/schema_40f52d6e7e62b4b6.json            |              12 |                      10 |                        2 | planned  |
| fried                                  | linear_svm | gpt-5.5-pro    | cache/schemas/fried/linear_svm/gpt-5.5-pro/schema_f4e72253c44fd3a0.json                                  |              12 |                      10 |                        2 | planned  |
| house_16h                              | linear_svm | gpt-5.5-pro    | cache/schemas/house_16h/linear_svm/gpt-5.5-pro/schema_d7345cfc4a0c2652.json                              |              12 |                      10 |                        2 | planned  |
| house_8l                               | linear_svm | gpt-5.5-pro    | cache/schemas/house_8l/linear_svm/gpt-5.5-pro/schema_ce038c5eb40fc657.json                               |              12 |                      10 |                        2 | planned  |
| jungle_chess_2pcs_raw_endgame_complete | linear_svm | gpt-5.5-pro    | cache/schemas/jungle_chess_2pcs_raw_endgame_complete/linear_svm/gpt-5.5-pro/schema_28b8229b15d15f2b.json |              12 |                      10 |                        2 | planned  |
| kr_vs_kp                               | linear_svm | gpt-5.5-pro    | cache/schemas/kr_vs_kp/linear_svm/gpt-5.5-pro/schema_f6a77690850ad9cc.json                               |              12 |                      10 |                        2 | planned  |
| law_school_admission_bianry            | linear_svm | gpt-5.5-pro    | cache/schemas/law_school_admission_bianry/linear_svm/gpt-5.5-pro/schema_4cf0ab576434f315.json            |              12 |                      10 |                        2 | planned  |
| loan_approval_status_classification    | linear_svm | gpt-5.5-pro    | cache/schemas/loan_approval_status_classification/linear_svm/gpt-5.5-pro/schema_bd78ba7c56a3bc10.json    |              12 |                      10 |                        2 | planned  |
| loan_status                            | linear_svm | gpt-5.5-pro    | cache/schemas/loan_status/linear_svm/gpt-5.5-pro/schema_aeaccdb7d8950fb5.json                            |              12 |                      10 |                        2 | planned  |
| microaggregation2                      | linear_svm | gpt-5.5-pro    | cache/schemas/microaggregation2/linear_svm/gpt-5.5-pro/schema_fb9ebb9415db79fe.json                      |              12 |                      10 |                        2 | planned  |
| mozilla4                               | linear_svm | gpt-5.5-pro    | cache/schemas/mozilla4/linear_svm/gpt-5.5-pro/schema_db9f697e466b4067.json                               |              12 |                      10 |                        2 | planned  |
| mv                                     | linear_svm | gpt-5.5-pro    | cache/schemas/mv/linear_svm/gpt-5.5-pro/schema_e25839b0222a9a82.json                                     |              12 |                      10 |                        2 | planned  |
| news_channel                           | linear_svm | gpt-5.5-pro    | cache/schemas/news_channel/linear_svm/gpt-5.5-pro/schema_f7e166e11baf7663.json                           |              12 |                       8 |                        4 | planned  |
| nursery                                | linear_svm | gpt-5.5-pro    | cache/schemas/nursery/linear_svm/gpt-5.5-pro/schema_696e07ca3f927412.json                                |              12 |                      10 |                        2 | planned  |
| online_shoppers                        | linear_svm | gpt-5.5-pro    | cache/schemas/online_shoppers/linear_svm/gpt-5.5-pro/schema_ce36a569eff0b306.json                        |              12 |                      10 |                        2 | planned  |
| optdigits                              | linear_svm | gpt-5.5-pro    | cache/schemas/optdigits/linear_svm/gpt-5.5-pro/schema_0144ab756551ddaf.json                              |              12 |                      10 |                        2 | planned  |
| pol                                    | linear_svm | gpt-5.5-pro    | cache/schemas/pol/linear_svm/gpt-5.5-pro/schema_f84d8ae1b8cb52f0.json                                    |              12 |                      10 |                        2 | planned  |
| pricerunner                            | linear_svm | gpt-5.5-pro    | cache/schemas/pricerunner/linear_svm/gpt-5.5-pro/schema_aef2e8218a3336cf.json                            |              12 |                       3 |                        9 | planned  |
| splice                                 | linear_svm | gpt-5.5-pro    | cache/schemas/splice/linear_svm/gpt-5.5-pro/schema_843cb057d722fc3e.json                                 |              12 |                      10 |                        2 | planned  |
| taiwanese_bankruptcy_prediction        | linear_svm | gpt-5.5-pro    | cache/schemas/taiwanese_bankruptcy_prediction/linear_svm/gpt-5.5-pro/schema_50d1f1873f10f5f3.json        |              12 |                      11 |                        1 | planned  |
| volcanoes_c1                           | linear_svm | gpt-5.5-pro    | cache/schemas/volcanoes_c1/linear_svm/gpt-5.5-pro/schema_7b5d2ab0584c1a68.json                           |              12 |                      10 |                        2 | planned  |