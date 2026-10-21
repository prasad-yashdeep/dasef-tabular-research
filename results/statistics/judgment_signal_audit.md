# Judgment-feature signal audit (DeepSeek-Reasoner runs, core tier)

runs: 120 | judgment features: 226 | missing values: 0
judgments-only LR ROC-AUC: mean 0.663, median 0.651, range 0.47 to 0.83; runs above 0.60: 93
distinct values per feature: median 109 (quartiles 16 to 402); binary features: 1; near-constant (dominant value >= 80%): 3; more than half of values at a declared bound: 14; more than 90%: 4

per dataset (mean judgments-only LR AUC, raw LR AUC):
  adult_income: 0.719 (raw 0.912)
  bank_marketing: 0.612 (raw 0.937)
  blood_transfusion: 0.620 (raw 0.764)
  car_evaluation: 0.615 (raw 0.981)
  credit_g: 0.641 (raw 0.793)
  electricity: 0.627 (raw 0.819)
  phoneme: 0.690 (raw 0.805)
  pima_diabetes: 0.690 (raw 0.823)
  qsar_biodegradation: 0.681 (raw 0.914)
  spambase: 0.738 (raw 0.972)
