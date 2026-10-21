# Changelog

All notable changes to the DASEF benchmark, code and released artifacts. Corrections to reported numbers
are listed with the affected tables so that readers of a given paper version can trace them.

## v1.1-dmlr-submission (12 October 2026)

First public release (tag `v1.1-dmlr-submission`). Corrections applied before the DMLR submission; every number in the
paper was regenerated from the stored runs.

- **Categorical encoding of three cached core datasets (adult income, bank marketing, car evaluation).** The local
  cache stores their categorical columns as 8-bit integer codes, and the earlier evaluation passed those codes to the
  downstream models as ordinal integers, which weakened the raw logistic-regression and KNN baselines and inflated the
  formula gains on these datasets (most visibly car evaluation, whose LR direct gain was +0.072). The loader now
  restores these columns to categoricals (`LOCAL_CACHE_CATEGORICAL` in `src/dasef/datasets.py`; `DASEF_RAW_ONEHOT=0`
  reproduces the old loading), so the raw block is one-hot encoded as for every other dataset, while the stored
  formulas are still computed on the codes the generators referenced. Re-scored offline by
  `scripts/expansion/reevaluate_onehot_core.py` (79 runs: 67 under `results/judgments`, 12 prospective; the previous
  `results.json` of each run is kept as `results.json.pre-onehot.bak`) and `scripts/expansion/rebuild_after_onehot.sh`
  (permuted control of the 36 affected core runs, classical baselines of the three datasets, anonymized control of all
  ten core datasets, every derived statistic, table and figure). Affected tables: semantic/direct, random-expression, per-generator, judgments,
  classical baselines, anonymized control, core families, per-dataset deltas, raw scores, dataset table (categorical
  counts 8, 10 and 6), Figures 2 and 3. Headline changes: semantic ROC-AUC LR +0.0156 to +0.0140, KNN +0.0512 to +0.0510,
  RF +0.0086 to +0.0085 (XGBoost unchanged); direct LR +0.0112 to +0.0096; car evaluation LR direct gain +0.072 to
  +0.003; anonymized LR semantic +0.016 to +0.011; autofeat now returns features on 19 datasets (none on bank
  marketing with one-hot inputs); OpenFE's KNN ROC-AUC advantage is no longer significant (p = 0.056; it remains so on
  balanced accuracy).
- **Permuted-formula control rebuilt its matrix from the stored parquet**, whose raw block holds the integer codes;
  after the re-encoding this compared a one-hot `raw+formula` score with an integer-coded permuted score on the three
  datasets. `scripts/build_permuted_control.py` now takes the raw block from the freshly loaded evaluation split and
  only the formula columns from the parquet (row alignment asserted); the 36 affected runs were recomputed.
- **Random-expression control averaged over five random draws per cell** (`random_formula_control.py evaluate
  --draws 5`; 855 cell evaluations, 68,400 extra fold evaluations; draw-level scores in `draw_level_scores.csv`).
  Section 5.2 and Table 3 rewritten: random expressions reproduce 59% (LR), 77% (KNN), 36% (RF) and 57% (XGBoost) of
  the LLM semantic gap; LLM minus random expression is +0.0064 (LR), +0.0135 (KNN), +0.0036 (RF, now significant after
  Holm, p = 0.005) and +0.0007 (XGBoost, not significant); 29 of the 8,400 random columns were constant.
- Minor: leakage-equivalence check 0.0050 mean absolute / +0.0023 signed (was 0.0038 / +0.0003); downstream-awareness
  tally 57 of 160 (was 59); judgment wins 9 of 40 ROC-AUC and 11 of 40 balanced-accuracy cells (were 10 and 12).

## v1.0-dmlr-submission (11 October 2026; internal, superseded by v1.1 before anything was published)

Release candidate accompanying the DMLR submission draft.

- Two-tier benchmark (10 core + 39 expansion OpenML datasets, four schema generators, linear/SVM family
  benchmark-wide, all three families on the core tier), post-cutoff replication (six Hugging Face tables),
  anonymized-column control, per-row judgment evaluation (DeepSeek-Reasoner, with DeepSeek-V4-Pro as a second
  judgment model), classical AutoFE baselines, and the count-matched random-expression control.
- Formula evaluator fixes applied before the reported numbers (documented in the paper's Appendix H and
  in this changelog): numpy-name shadowing of column names; category-typed columns
  coerced to constants; numeric-looking category labels versus string literals; narrow-integer overflow in sums and
  products. Every stored run was re-materialized with the corrected evaluator.
- Dataset provenance (`results/statistics/benchmark44/dataset_provenance.csv`, fetched from the OpenML API on
  11 October 2026) with OpenML identifier, version, licence string, upload date and source URL per dataset.
- Figures regenerated from the checked-in scripts with Type 1 fonts (`DASEF_FIG_PGF=1`).
