# Clean Formula-Control Run Plan

This plan evaluates existing cached DASEF schemas with leakage-safe evaluation rows,
formula-only DASEF features, and random-control matrices. It does not call LLM APIs.

Important: cached schemas are publishable under the leakage-safe protocol only if
they were generated from the same schema-design split. Otherwise this is rehearsal
evidence for pipeline validation and screening.

## Summary

- Planned runs: 29
- Missing schemas: 0
- Skipped by max-runs: 0

## Runs

| dataset                               | family     | schema_model           | schema_path                                                                                                        |   feature_count |   formula_feature_count |   judgment_feature_count | status   |
|:--------------------------------------|:-----------|:-----------------------|:-------------------------------------------------------------------------------------------------------------------|----------------:|------------------------:|-------------------------:|:---------|
| ailerons                              | linear_svm | gemini-3.1-pro-preview | cache/schemas/ailerons/linear_svm/gemini-3.1-pro-preview/schema_55dd8a886caf428e.json                              |              12 |                       8 |                        4 | planned  |
| airlines                              | linear_svm | gemini-3.1-pro-preview | cache/schemas/airlines/linear_svm/gemini-3.1-pro-preview/schema_80ff89b5509d64a3.json                              |              12 |                       9 |                        3 | planned  |
| amazon_employee_access                | linear_svm | gemini-3.1-pro-preview | cache/schemas/amazon_employee_access/linear_svm/gemini-3.1-pro-preview/schema_8a148e7af780319f.json                |              12 |                       8 |                        4 | planned  |
| bitcoinheist_ransomware               | linear_svm | gemini-3.1-pro-preview | cache/schemas/bitcoinheist_ransomware/linear_svm/gemini-3.1-pro-preview/schema_c767e28c645ce7d8.json               |              12 |                      10 |                        2 | planned  |
| bng_breast_w                          | linear_svm | gemini-3.1-pro-preview | cache/schemas/bng_breast_w/linear_svm/gemini-3.1-pro-preview/schema_11292d8cdeb3706c.json                          |              12 |                      10 |                        2 | planned  |
| click_prediction_small                | linear_svm | gemini-3.1-pro-preview | cache/schemas/click_prediction_small/linear_svm/gemini-3.1-pro-preview/schema_c1d57b340b4f6daa.json                |              12 |                      10 |                        2 | planned  |
| codexglue                             | linear_svm | gemini-3.1-pro-preview | cache/schemas/codexglue/linear_svm/gemini-3.1-pro-preview/schema_cdfd8cbe097aea41.json                             |              12 |                       3 |                        9 | planned  |
| coil2000_insurance_policies           | linear_svm | gemini-3.1-pro-preview | cache/schemas/coil2000_insurance_policies/linear_svm/gemini-3.1-pro-preview/schema_fc1ef94385bb7509.json           |              12 |                       9 |                        3 | planned  |
| compass                               | linear_svm | gemini-3.1-pro-preview | cache/schemas/compass/linear_svm/gemini-3.1-pro-preview/schema_62e1a354dae3e017.json                               |              12 |                       9 |                        3 | planned  |
| customer_churn_classification_nominal | linear_svm | gemini-3.1-pro-preview | cache/schemas/customer_churn_classification_nominal/linear_svm/gemini-3.1-pro-preview/schema_93ab8d7e2c9d07b3.json |              12 |                      10 |                        2 | planned  |
| employee_turnover_at_techco           | linear_svm | gemini-3.1-pro-preview | cache/schemas/employee_turnover_at_techco/linear_svm/gemini-3.1-pro-preview/schema_a7ca767d251f458c.json           |              12 |                      11 |                        1 | planned  |
| first_order_theorem_proving           | linear_svm | gemini-3.1-pro-preview | cache/schemas/first_order_theorem_proving/linear_svm/gemini-3.1-pro-preview/schema_807d6a40c369bdfb.json           |              12 |                      10 |                        2 | planned  |
| fried                                 | linear_svm | gemini-3.1-pro-preview | cache/schemas/fried/linear_svm/gemini-3.1-pro-preview/schema_eb5c13acc9e8bd42.json                                 |              12 |                      10 |                        2 | planned  |
| house_16h                             | linear_svm | gemini-3.1-pro-preview | cache/schemas/house_16h/linear_svm/gemini-3.1-pro-preview/schema_657152b9e23fc502.json                             |              12 |                      10 |                        2 | planned  |
| house_8l                              | linear_svm | gemini-3.1-pro-preview | cache/schemas/house_8l/linear_svm/gemini-3.1-pro-preview/schema_7fd7808f748ef73f.json                              |              12 |                       9 |                        3 | planned  |
| kr_vs_kp                              | linear_svm | gemini-3.1-pro-preview | cache/schemas/kr_vs_kp/linear_svm/gemini-3.1-pro-preview/schema_7fdeab52013ea8aa.json                              |               8 |                       8 |                        0 | planned  |
| loan_approval_status_classification   | linear_svm | gemini-3.1-pro-preview | cache/schemas/loan_approval_status_classification/linear_svm/gemini-3.1-pro-preview/schema_3656543ef56f20d6.json   |              12 |                      10 |                        2 | planned  |
| loan_status                           | linear_svm | gemini-3.1-pro-preview | cache/schemas/loan_status/linear_svm/gemini-3.1-pro-preview/schema_ec180f979afcdb8f.json                           |              12 |                      10 |                        2 | planned  |
| microaggregation2                     | linear_svm | gemini-3.1-pro-preview | cache/schemas/microaggregation2/linear_svm/gemini-3.1-pro-preview/schema_690cf885d12acb62.json                     |              12 |                      10 |                        2 | planned  |
| mozilla4                              | linear_svm | gemini-3.1-pro-preview | cache/schemas/mozilla4/linear_svm/gemini-3.1-pro-preview/schema_686d777b63aa091e.json                              |              12 |                      10 |                        2 | planned  |
| mv                                    | linear_svm | gemini-3.1-pro-preview | cache/schemas/mv/linear_svm/gemini-3.1-pro-preview/schema_0f720596681265c9.json                                    |              12 |                      10 |                        2 | planned  |
| news_channel                          | linear_svm | gemini-3.1-pro-preview | cache/schemas/news_channel/linear_svm/gemini-3.1-pro-preview/schema_b0ae97964f385f08.json                          |              12 |                       9 |                        3 | planned  |
| nursery                               | linear_svm | gemini-3.1-pro-preview | cache/schemas/nursery/linear_svm/gemini-3.1-pro-preview/schema_980ce54cbc2fffbc.json                               |              12 |                       9 |                        3 | planned  |
| okcupid_stem                          | linear_svm | gemini-3.1-pro-preview | cache/schemas/okcupid_stem/linear_svm/gemini-3.1-pro-preview/schema_2908de87a6072335.json                          |              12 |                       8 |                        4 | planned  |
| online_shoppers                       | linear_svm | gemini-3.1-pro-preview | cache/schemas/online_shoppers/linear_svm/gemini-3.1-pro-preview/schema_db95d80f630193df.json                       |              12 |                       6 |                        6 | planned  |
| pol                                   | linear_svm | gemini-3.1-pro-preview | cache/schemas/pol/linear_svm/gemini-3.1-pro-preview/schema_2804915db89670d7.json                                   |              12 |                       9 |                        3 | planned  |
| splice                                | linear_svm | gemini-3.1-pro-preview | cache/schemas/splice/linear_svm/gemini-3.1-pro-preview/schema_6b435e1f2ded0432.json                                |               4 |                       4 |                        0 | planned  |
| taiwanese_bankruptcy_prediction       | linear_svm | gemini-3.1-pro-preview | cache/schemas/taiwanese_bankruptcy_prediction/linear_svm/gemini-3.1-pro-preview/schema_70950baf5ad6b82e.json       |              12 |                       9 |                        3 | planned  |
| volcanoes_c1                          | linear_svm | gemini-3.1-pro-preview | cache/schemas/volcanoes_c1/linear_svm/gemini-3.1-pro-preview/schema_1b2a598620585743.json                          |              12 |                      10 |                        2 | planned  |