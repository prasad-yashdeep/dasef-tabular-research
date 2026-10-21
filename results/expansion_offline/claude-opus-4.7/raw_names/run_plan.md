# Clean Formula-Control Run Plan

This plan evaluates existing cached DASEF schemas with leakage-safe evaluation rows,
formula-only DASEF features, and random-control matrices. It does not call LLM APIs.

Important: cached schemas are publishable under the leakage-safe protocol only if
they were generated from the same schema-design split. Otherwise this is rehearsal
evidence for pipeline validation and screening.

## Summary

- Planned runs: 31
- Missing schemas: 0
- Skipped by max-runs: 0

## Runs

| dataset                                | family     | schema_model    | schema_path                                                                                                  |   feature_count |   formula_feature_count |   judgment_feature_count | status   |
|:---------------------------------------|:-----------|:----------------|:-------------------------------------------------------------------------------------------------------------|----------------:|------------------------:|-------------------------:|:---------|
| 2dplanes                               | linear_svm | claude-opus-4.7 | cache/schemas/2dplanes/linear_svm/claude-opus-4.7/schema_1aeee9785fee29e7.json                               |              12 |                      11 |                        1 | planned  |
| ailerons                               | linear_svm | claude-opus-4.7 | cache/schemas/ailerons/linear_svm/claude-opus-4.7/schema_4eaedc6201da276d.json                               |              12 |                      10 |                        2 | planned  |
| airlines                               | linear_svm | claude-opus-4.7 | cache/schemas/airlines/linear_svm/claude-opus-4.7/schema_9cb74dfaaa8fde9f.json                               |              12 |                      10 |                        2 | planned  |
| amazon_employee_access                 | linear_svm | claude-opus-4.7 | cache/schemas/amazon_employee_access/linear_svm/claude-opus-4.7/schema_377f7a66081cd280.json                 |              12 |                      11 |                        1 | planned  |
| bitcoinheist_ransomware                | linear_svm | claude-opus-4.7 | cache/schemas/bitcoinheist_ransomware/linear_svm/claude-opus-4.7/schema_15efc684ea960857.json                |              12 |                      11 |                        1 | planned  |
| bng_breast_w                           | linear_svm | claude-opus-4.7 | cache/schemas/bng_breast_w/linear_svm/claude-opus-4.7/schema_23b1cdfdde856a3d.json                           |              12 |                      10 |                        2 | planned  |
| click_prediction_small                 | linear_svm | claude-opus-4.7 | cache/schemas/click_prediction_small/linear_svm/claude-opus-4.7/schema_e95f62c6d4dd6169.json                 |              12 |                      11 |                        1 | planned  |
| coil2000_insurance_policies            | linear_svm | claude-opus-4.7 | cache/schemas/coil2000_insurance_policies/linear_svm/claude-opus-4.7/schema_a9a8d661243cfde0.json            |              12 |                      10 |                        2 | planned  |
| compass                                | linear_svm | claude-opus-4.7 | cache/schemas/compass/linear_svm/claude-opus-4.7/schema_a48c9d5054d7cb7d.json                                |              12 |                      11 |                        1 | planned  |
| customer_churn_classification_nominal  | linear_svm | claude-opus-4.7 | cache/schemas/customer_churn_classification_nominal/linear_svm/claude-opus-4.7/schema_ed2b44e7aac5c972.json  |              12 |                      10 |                        2 | planned  |
| employee_turnover_at_techco            | linear_svm | claude-opus-4.7 | cache/schemas/employee_turnover_at_techco/linear_svm/claude-opus-4.7/schema_ee456349157f0d8f.json            |              12 |                      11 |                        1 | planned  |
| first_order_theorem_proving            | linear_svm | claude-opus-4.7 | cache/schemas/first_order_theorem_proving/linear_svm/claude-opus-4.7/schema_af161dd4a73115ef.json            |              12 |                      10 |                        2 | planned  |
| fried                                  | linear_svm | claude-opus-4.7 | cache/schemas/fried/linear_svm/claude-opus-4.7/schema_12c2cd2cf4c350be.json                                  |              12 |                      11 |                        1 | planned  |
| house_16h                              | linear_svm | claude-opus-4.7 | cache/schemas/house_16h/linear_svm/claude-opus-4.7/schema_611e6daf74515e53.json                              |              12 |                      11 |                        1 | planned  |
| house_8l                               | linear_svm | claude-opus-4.7 | cache/schemas/house_8l/linear_svm/claude-opus-4.7/schema_d597abd738e63dbc.json                               |              12 |                      11 |                        1 | planned  |
| jungle_chess_2pcs_raw_endgame_complete | linear_svm | claude-opus-4.7 | cache/schemas/jungle_chess_2pcs_raw_endgame_complete/linear_svm/claude-opus-4.7/schema_06bb340baf9bb2ea.json |              12 |                      11 |                        1 | planned  |
| kr_vs_kp                               | linear_svm | claude-opus-4.7 | cache/schemas/kr_vs_kp/linear_svm/claude-opus-4.7/schema_29cea27e6454c3c3.json                               |              12 |                      11 |                        1 | planned  |
| law_school_admission_bianry            | linear_svm | claude-opus-4.7 | cache/schemas/law_school_admission_bianry/linear_svm/claude-opus-4.7/schema_12ea426d93e6f5d4.json            |              12 |                      10 |                        2 | planned  |
| loan_approval_status_classification    | linear_svm | claude-opus-4.7 | cache/schemas/loan_approval_status_classification/linear_svm/claude-opus-4.7/schema_7fa8f189540672c3.json    |              12 |                      11 |                        1 | planned  |
| loan_status                            | linear_svm | claude-opus-4.7 | cache/schemas/loan_status/linear_svm/claude-opus-4.7/schema_6b550d05b24dd3d2.json                            |              12 |                      10 |                        2 | planned  |
| microaggregation2                      | linear_svm | claude-opus-4.7 | cache/schemas/microaggregation2/linear_svm/claude-opus-4.7/schema_a799106019e6afce.json                      |              12 |                      10 |                        2 | planned  |
| mozilla4                               | linear_svm | claude-opus-4.7 | cache/schemas/mozilla4/linear_svm/claude-opus-4.7/schema_dcda8bede5a0ca72.json                               |              12 |                      11 |                        1 | planned  |
| mv                                     | linear_svm | claude-opus-4.7 | cache/schemas/mv/linear_svm/claude-opus-4.7/schema_1543fe60aabae363.json                                     |              12 |                      11 |                        1 | planned  |
| news_channel                           | linear_svm | claude-opus-4.7 | cache/schemas/news_channel/linear_svm/claude-opus-4.7/schema_f32d635fb43d10a7.json                           |              12 |                      10 |                        2 | planned  |
| nursery                                | linear_svm | claude-opus-4.7 | cache/schemas/nursery/linear_svm/claude-opus-4.7/schema_2f0c203025f49c1a.json                                |              12 |                      11 |                        1 | planned  |
| online_shoppers                        | linear_svm | claude-opus-4.7 | cache/schemas/online_shoppers/linear_svm/claude-opus-4.7/schema_da4980c97c317bca.json                        |              12 |                      11 |                        1 | planned  |
| optdigits                              | linear_svm | claude-opus-4.7 | cache/schemas/optdigits/linear_svm/claude-opus-4.7/schema_764e4f4783592aef.json                              |              12 |                      11 |                        1 | planned  |
| phishingwebsites                       | linear_svm | claude-opus-4.7 | cache/schemas/phishingwebsites/linear_svm/claude-opus-4.7/schema_46a1fac2c28c302c.json                       |              12 |                      10 |                        2 | planned  |
| pol                                    | linear_svm | claude-opus-4.7 | cache/schemas/pol/linear_svm/claude-opus-4.7/schema_9dec6bfcce3bda67.json                                    |              12 |                      11 |                        1 | planned  |
| splice                                 | linear_svm | claude-opus-4.7 | cache/schemas/splice/linear_svm/claude-opus-4.7/schema_03c2650f0a76baad.json                                 |              12 |                      10 |                        2 | planned  |
| volcanoes_c1                           | linear_svm | claude-opus-4.7 | cache/schemas/volcanoes_c1/linear_svm/claude-opus-4.7/schema_4e9e8e972ee6983c.json                           |              12 |                      10 |                        2 | planned  |