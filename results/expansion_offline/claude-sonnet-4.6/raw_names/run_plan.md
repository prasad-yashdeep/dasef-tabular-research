# Clean Formula-Control Run Plan

This plan evaluates existing cached DASEF schemas with leakage-safe evaluation rows,
formula-only DASEF features, and random-control matrices. It does not call LLM APIs.

Important: cached schemas are publishable under the leakage-safe protocol only if
they were generated from the same schema-design split. Otherwise this is rehearsal
evidence for pipeline validation and screening.

## Summary

- Planned runs: 30
- Missing schemas: 0
- Skipped by max-runs: 0

## Runs

| dataset                                | family     | schema_model      | schema_path                                                                                                    |   feature_count |   formula_feature_count |   judgment_feature_count | status   |
|:---------------------------------------|:-----------|:------------------|:---------------------------------------------------------------------------------------------------------------|----------------:|------------------------:|-------------------------:|:---------|
| 2dplanes                               | linear_svm | claude-sonnet-4.6 | cache/schemas/2dplanes/linear_svm/claude-sonnet-4.6/schema_f3c325115bf60255.json                               |              12 |                      10 |                        2 | planned  |
| ailerons                               | linear_svm | claude-sonnet-4.6 | cache/schemas/ailerons/linear_svm/claude-sonnet-4.6/schema_eb77d10057bc130e.json                               |              12 |                      10 |                        2 | planned  |
| airlines                               | linear_svm | claude-sonnet-4.6 | cache/schemas/airlines/linear_svm/claude-sonnet-4.6/schema_f231c55c248e5199.json                               |              12 |                       9 |                        3 | planned  |
| bitcoinheist_ransomware                | linear_svm | claude-sonnet-4.6 | cache/schemas/bitcoinheist_ransomware/linear_svm/claude-sonnet-4.6/schema_dec8451cd252fc1e.json                |              12 |                      10 |                        2 | planned  |
| bng_breast_w                           | linear_svm | claude-sonnet-4.6 | cache/schemas/bng_breast_w/linear_svm/claude-sonnet-4.6/schema_29f7812881212344.json                           |              12 |                      10 |                        2 | planned  |
| click_prediction_small                 | linear_svm | claude-sonnet-4.6 | cache/schemas/click_prediction_small/linear_svm/claude-sonnet-4.6/schema_2a29916d3ff134f2.json                 |              12 |                      11 |                        1 | planned  |
| coil2000_insurance_policies            | linear_svm | claude-sonnet-4.6 | cache/schemas/coil2000_insurance_policies/linear_svm/claude-sonnet-4.6/schema_e14e54310de12d3c.json            |              12 |                      10 |                        2 | planned  |
| compass                                | linear_svm | claude-sonnet-4.6 | cache/schemas/compass/linear_svm/claude-sonnet-4.6/schema_cdd305e6edd52ab5.json                                |              12 |                      11 |                        1 | planned  |
| customer_churn_classification_nominal  | linear_svm | claude-sonnet-4.6 | cache/schemas/customer_churn_classification_nominal/linear_svm/claude-sonnet-4.6/schema_62818d4fc1a0151d.json  |              12 |                      10 |                        2 | planned  |
| employee_turnover_at_techco            | linear_svm | claude-sonnet-4.6 | cache/schemas/employee_turnover_at_techco/linear_svm/claude-sonnet-4.6/schema_8823b7d4dc5a4a98.json            |              12 |                      10 |                        2 | planned  |
| first_order_theorem_proving            | linear_svm | claude-sonnet-4.6 | cache/schemas/first_order_theorem_proving/linear_svm/claude-sonnet-4.6/schema_9812ea1e518e1942.json            |              12 |                      11 |                        1 | planned  |
| fried                                  | linear_svm | claude-sonnet-4.6 | cache/schemas/fried/linear_svm/claude-sonnet-4.6/schema_2c0f3c9b0e015de2.json                                  |              12 |                      11 |                        1 | planned  |
| house_16h                              | linear_svm | claude-sonnet-4.6 | cache/schemas/house_16h/linear_svm/claude-sonnet-4.6/schema_d02dfd74a96d2040.json                              |              12 |                      11 |                        1 | planned  |
| house_8l                               | linear_svm | claude-sonnet-4.6 | cache/schemas/house_8l/linear_svm/claude-sonnet-4.6/schema_6c68c317498b7590.json                               |              12 |                      10 |                        2 | planned  |
| jungle_chess_2pcs_raw_endgame_complete | linear_svm | claude-sonnet-4.6 | cache/schemas/jungle_chess_2pcs_raw_endgame_complete/linear_svm/claude-sonnet-4.6/schema_5a24ecce82ffca7b.json |              12 |                      11 |                        1 | planned  |
| kr_vs_kp                               | linear_svm | claude-sonnet-4.6 | cache/schemas/kr_vs_kp/linear_svm/claude-sonnet-4.6/schema_b36b9137f640e222.json                               |              12 |                      10 |                        2 | planned  |
| law_school_admission_bianry            | linear_svm | claude-sonnet-4.6 | cache/schemas/law_school_admission_bianry/linear_svm/claude-sonnet-4.6/schema_a965fb746e4d4c72.json            |              12 |                      10 |                        2 | planned  |
| loan_approval_status_classification    | linear_svm | claude-sonnet-4.6 | cache/schemas/loan_approval_status_classification/linear_svm/claude-sonnet-4.6/schema_e485bcfef55efcf2.json    |              12 |                      11 |                        1 | planned  |
| loan_status                            | linear_svm | claude-sonnet-4.6 | cache/schemas/loan_status/linear_svm/claude-sonnet-4.6/schema_f09cd9c1c8d4cb15.json                            |              12 |                      10 |                        2 | planned  |
| microaggregation2                      | linear_svm | claude-sonnet-4.6 | cache/schemas/microaggregation2/linear_svm/claude-sonnet-4.6/schema_f10b6e6264839296.json                      |              12 |                      10 |                        2 | planned  |
| mozilla4                               | linear_svm | claude-sonnet-4.6 | cache/schemas/mozilla4/linear_svm/claude-sonnet-4.6/schema_eb6b88032d9f0791.json                               |              12 |                      11 |                        1 | planned  |
| mv                                     | linear_svm | claude-sonnet-4.6 | cache/schemas/mv/linear_svm/claude-sonnet-4.6/schema_e0b044634ea0c992.json                                     |              12 |                      11 |                        1 | planned  |
| news_channel                           | linear_svm | claude-sonnet-4.6 | cache/schemas/news_channel/linear_svm/claude-sonnet-4.6/schema_f356d9111677be4d.json                           |              12 |                      10 |                        2 | planned  |
| nursery                                | linear_svm | claude-sonnet-4.6 | cache/schemas/nursery/linear_svm/claude-sonnet-4.6/schema_566b6022cf14f38b.json                                |              12 |                      10 |                        2 | planned  |
| online_shoppers                        | linear_svm | claude-sonnet-4.6 | cache/schemas/online_shoppers/linear_svm/claude-sonnet-4.6/schema_3a094272a918cc12.json                        |              12 |                      10 |                        2 | planned  |
| optdigits                              | linear_svm | claude-sonnet-4.6 | cache/schemas/optdigits/linear_svm/claude-sonnet-4.6/schema_f7cc4ed22fd8c1b7.json                              |              12 |                      11 |                        1 | planned  |
| phishingwebsites                       | linear_svm | claude-sonnet-4.6 | cache/schemas/phishingwebsites/linear_svm/claude-sonnet-4.6/schema_dd81e15bd0595974.json                       |              12 |                      10 |                        2 | planned  |
| pol                                    | linear_svm | claude-sonnet-4.6 | cache/schemas/pol/linear_svm/claude-sonnet-4.6/schema_9d2b912add0cb9ff.json                                    |              12 |                      10 |                        2 | planned  |
| taiwanese_bankruptcy_prediction        | linear_svm | claude-sonnet-4.6 | cache/schemas/taiwanese_bankruptcy_prediction/linear_svm/claude-sonnet-4.6/schema_453739705b55b973.json        |              12 |                      11 |                        1 | planned  |
| volcanoes_c1                           | linear_svm | claude-sonnet-4.6 | cache/schemas/volcanoes_c1/linear_svm/claude-sonnet-4.6/schema_3f73cd5221c88192.json                           |              12 |                      10 |                        2 | planned  |