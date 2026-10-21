# DASEF: What Actually Helps in LLM Tabular Feature Engineering?

Code, cached LLM schemas, stored results and the scripts that regenerate every table and figure of

> Hasan Aljabbouli, Yashdeep Prasad and Bhumika Dinesh Shetty. *What Actually Helps in LLM Tabular Feature
> Engineering? A Controlled Decomposition of Deterministic Formulas vs. Per-Row Judgments.* Submitted to the
> Journal of Data-centric Machine Learning Research (DMLR), 2026.

DASEF (Downstream-Aware Semantic Feature Engineering) asks an LLM once per dataset for a schema of deterministic
formula features (and optional per-row judgment specifications), materializes the formulas on the evaluation rows,
and scores four downstream models under controls that separate signal from feature count (column permutation,
count-matched noise, random formulas over the dataset's own columns) and from memorization of public datasets
(column anonymization, post-cutoff tables). Everything in the paper is reproducible **offline** from the artifacts
in this repository and its release assets; no API key is needed unless you want to generate new schemas.

## Layout

| Path | Contents |
|---|---|
| `src/dasef/` | pipeline: dataset loading and splits (`datasets.py`), the formula evaluator (`features/formula.py`), noise controls (`features/random_control.py`), judgment filling and audit, downstream evaluation (`evaluate.py`), schema prompts and generation, LLM providers |
| `configs/` | `datasets.yaml` (OpenML dataset identifiers and tiers; the expansion pool carries its historical tag `paper2_expansion`), `llm_models.yaml` (API model identifiers), `model_families.yaml` |
| `cache/schemas/<dataset>/<family>/<generator>/` | cached LLM schemas (`schema_<prompthash>.json`) and raw responses (`*.raw.json`); the prompt behind each file is rebuilt by `src/dasef/prompts.py` from the dataset summary and identified by the hash in the file name; `cache/schemas_anonymized/`, `cache/schemas_postcutoff_real/` likewise |
| `results/judgments/<run_id>/` | 240 run directories: the 120 DeepSeek-R1 core runs (10 datasets x 4 generators x 3 families; scripts select them by the `model` field of `judgments/*.json`), 108 DeepSeek-V4-Pro runs (93 complete) behind Appendix G, and 12 incomplete directories; each holds `results.json` (per-fold scores of every matrix) and `schema.normalized.json`, plus `matrices/*.parquet` and `judgments/` from the release assets |
| `results/expansion_offline/<generator>/{raw_names,safe_names}/` | expansion-tier runs (39 datasets, linear/SVM family) and their permuted controls |
| `results/postcutoff_real/`, `results/anonymized_control/` | post-cutoff replication runs and the anonymized-column control |
| `results/full_suite_prospective/`, `results/schema_runs/` | prospective re-evaluations behind the leakage-equivalence check (48 runs) and 29 dry-run schema evaluations without judgments (not used by the paper's tables) |
| `results/statistics/` | every aggregate the paper quotes (`benchmark44/`, `benchmark44_classical/`, `dataset_level/`, `permuted_control/`, `anonymized_control/`, `awareness_full/`, `postcutoff_real/`, `random_formula_control/`, `mechanism_panel_poc.json`, `judgment_signal_audit.*`, `judgment_signal_features.csv`) |
| `results/figures/` | generated figures (not committed; `rebuild_benchmark44.sh` copies the three the paper uses into `paper/dmlr/figures/`) |
| `scripts/`, `scripts/expansion/` | run and aggregation scripts (see below) |
| `paper/dmlr/` | LaTeX source of the DMLR submission and the supplementary datasheet; the tables are inline in `sections/` and are refreshed from the generated `paper/tables/*.tex` and `paper/dmlr/tables/datasets.tex` by `scripts/release/splice_paper_tables.py` (only `random_expression.tex` and `judgment_v4pro.tex` are `\input` directly) |
| `tests/` | unit tests for the evaluator, schema validation, statistics and pipeline |

Large stored matrices (`results/**/matrices/*.parquet`), judgment outputs and the 74 MB prepared salmonella table
(`data/local_cache/postcutoff_salmonella_serovar_20260401/`) are published as release assets of this repository rather
than committed; the six cached core tables and the other five prepared post-cutoff tables are committed under
`data/local_cache/` (licences in `data/local_cache/NOTICE.md`), and the supplementary zip contains everything except the release assets. The matrices are regenerable from the cached schemas with the scripts
below, except the judgment matrices, which record LLM outputs and are stored verbatim.

## Release assets

The repository is https://github.com/prasad-yashdeep/dasef-tabular-research; the submitted state is the tag
`v1.1-dmlr-submission`. Files that git does not track are attached to that release as tarballs built from the repository
root, so they unpack in place:

```bash
gh release download v1.1-dmlr-submission -p '*.tar.gz' && for f in *.tar.gz; do tar -xzf "$f"; done && rm -f *.tar.gz
```

| Tarball | Contents | Needed by |
|---|---|---|
| `judgment_rows_core` | `results/judgments/<run>/judgments/*.json` (per-row judgment outputs; the scripts identify a run's judgment model from these) | every core-tier command below |
| `matrices_core_judgments` | `results/judgments/<run>/matrices/*.parquet` | core-tier tables, permuted control, one-hot re-evaluation |
| `matrices_expansion` | `results/expansion_offline/**/matrices/*.parquet` | random-expression control, expansion permuted control |
| `matrices_prospective` | `results/full_suite_prospective/**/*.parquet` | one-hot re-evaluation of the prospective runs |
| `matrices_postcutoff` | `results/postcutoff_real/**/*.parquet` (matrices derived from the two CC BY-NC tables keep those terms) | post-cutoff permuted control |
| `matrices_anonymized` | `results/anonymized_control/**/*.parquet` | anonymized-control rescore |
| `matrices_schema_runs` | `results/schema_runs/**` matrices and judgments (dry-run evaluations, not used by the paper's tables) | nothing in the paper |
| `local_cache_postcutoff_salmonella` | `data/local_cache/postcutoff_salmonella_serovar_20260401/` (74 MB, CC BY 4.0) | post-cutoff replication on the salmonella table |

The supplementary zip submitted with the paper (`dasef_supplement.zip`) is attached to the same release.

## Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt  # Python 3.11 to 3.14 (the paper's numbers were produced with 3.14.7); pins
pip install -e . --no-deps            # scikit-learn 1.8.0, xgboost 3.2.0, numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, OpenFE, autofeat
```

OpenML datasets are downloaded on first use by dataset identifier (`configs/datasets.yaml`; identifiers, versions
and licences are listed in `results/statistics/benchmark44/dataset_provenance.csv`). Six core datasets are served
from `data/local_cache/` (see Section 4.1 of the paper for the three local variants). API keys are only needed for
schema generation and judgment filling; copy `.env.example` to `.env` if you want to run those.

## Reproducing the paper

All commands run from the repository root with the virtual environment active. Every number quoted in the prose
is printed by one script so the text can be checked against disk:

```bash
python scripts/expansion/paper_numbers.py
```

| Paper item | Command | Output |
|---|---|---|
| Main benchmark tables and Figures 2 and 4 (two-tier benchmark: semantic and direct contrasts, noise controls, per-generator results, per-dataset deltas, raw scores, dot plot, critical-difference diagrams) | `DASEF_FIG_PGF=1 bash scripts/expansion/rebuild_benchmark44.sh` (also copies the three figure files into `paper/dmlr/figures/`) | `results/statistics/benchmark44/`, `paper/tables/*.tex`, `results/figures/semantic_dotplot.pdf`, `results/figures/cd_diagrams44/` |
| Core-tier tables (per-row judgments, three schema families, anonymized control) | `python scripts/aggregate_dataset_level.py && python scripts/build_permuted_control.py --skip-existing && python scripts/rescore_anonymized_control_offline.py && python scripts/expansion/make_core_tables.py --out-dir paper/tables`; then `python scripts/release/splice_paper_tables.py` refreshes the inline tables of the paper source from the generated files (`--dry-run` shows the row differences) | `results/statistics/dataset_level/`, `results/statistics/permuted_control/`, `results/statistics/anonymized_control/` |
| Classical AutoFE baseline table | `python scripts/run_classical_baselines.py --out-dir results/statistics/classical_baselines` (core; roughly 11 minutes). The expansion-tier run in `results/statistics/classical_baselines_expansion/` (39 datasets, about three hours) was produced by a variant of this script whose extra flags (5,000-row cap when a table exceeds 5,000 rows, alignment against the expansion run matrices, no DASEF join, dataset list file) are recorded in its `run_args.json`; the shipped script reproduces the core tier and the expansion outputs are shipped. Then `python scripts/expansion/classical_table44.py --classical-dirs results/statistics/classical_baselines results/statistics/classical_baselines_expansion --dataset-level results/statistics/benchmark44/dataset_level.csv --out-dir results/statistics/benchmark44_classical` | `results/statistics/benchmark44_classical/` |
| Post-cutoff replication table | `python scripts/build_postcutoff_permuted_control.py && python scripts/aggregate_postcutoff_dataset_level.py` | `results/statistics/postcutoff_real/` |
| Downstream-awareness diagnostic (Section 5.5, Appendix J) | `for m in roc_auc_ovr balanced_accuracy; do python scripts/analyze_existing_results.py results/judgments --metric $m --out-dir results/statistics/awareness_full; python scripts/analyze_downstream_awareness.py --stats-csv results/statistics/awareness_full/existing_result_stats_$m.csv --out-dir results/statistics/awareness_full; python scripts/analyze_downstream_awareness.py --stats-csv results/statistics/awareness_full/existing_result_stats_$m.csv --out-dir results/statistics/awareness_full --downstream-models logistic_regression,random_forest,knn --suffix primary_models; done` | `results/statistics/awareness_full/` |
| Leakage-equivalence check (Section 4.3) | `python scripts/leakage_equivalence_check.py` | `results/statistics/dataset_level/leakage_equivalence.md` |
| Judgment-feature signal audit (judgment columns alone, distinct values, bounds) | `python scripts/audit_judgment_signal.py` | `results/statistics/judgment_signal_audit.*`, `judgment_signal_features.csv` |
| Second judgment model (DeepSeek-V4-Pro appendix table) | `python scripts/expansion/judgment_second_model.py` | `results/statistics/judgment_v4pro/`, `paper/dmlr/tables/judgment_v4pro.tex` |
| Random-expression control (count-matched random but valid expressions over each dataset's own columns) | `python scripts/expansion/random_formula_control.py evaluate --workers 5 --draws 5 && python scripts/expansion/random_formula_control.py aggregate && python scripts/expansion/random_formula_control.py table` (five random draws per cell, averaged; about two hours on 5 cores; the random-expression table of the paper) | `results/statistics/random_formula_control/`, `paper/dmlr/tables/random_expression.tex` |
| One-hot re-encoding of the integer-coded categorical columns of the cached core datasets (adult income, bank marketing, car evaluation): re-score the stored core runs and rebuild every derived statistic | `python scripts/expansion/reevaluate_onehot_core.py && bash scripts/expansion/rebuild_after_onehot.sh` (offline; `DASEF_RAW_ONEHOT=0` restores the integer-coded loading) | `results/judgments/*/results.json` (backups `results.json.pre-onehot.bak`), `results/statistics/` |
| Appendix A, Figure 3 (mechanism case study) | `python scripts/run_mechanism_case_study.py --out results/statistics/mechanism_panel_poc.json && DASEF_FIG_PGF=1 python scripts/make_paper_figures.py && cp results/figures/mechanism_panel.pdf paper/dmlr/figures/fig4_mechanism.pdf` | `results/statistics/mechanism_panel_poc.json`, `results/figures/mechanism_panel.pdf` |
| Benchmark dataset table (OpenML version and licence per dataset) | `python scripts/expansion/fetch_openml_provenance.py && python scripts/expansion/make_dataset_table.py --inventory results/statistics/benchmark44/dataset_inventory.csv --coverage results/statistics/benchmark44/coverage.csv --core-inventory results/statistics/benchmark44/core_dataset_inventory.csv --provenance results/statistics/benchmark44/dataset_provenance.csv --style table --out paper/dmlr/tables/datasets.tex` | `paper/dmlr/tables/datasets.tex` |

Set `DASEF_FIG_PGF=1` to typeset figure text with pdflatex (Latin Modern Type 1 fonts, as in the paper); without it the
scripts embed TrueType outlines. The paper is built from clean with `cd paper/dmlr && rm -f main.aux main.bbl && pdflatex main && bibtex main && pdflatex main && pdflatex main && pdflatex main`
(official `dmlr2e.sty`, unchanged; the `adjustbox`, `collectbox`, `lastpage` and `cm-super` packages are required).

### Re-evaluating stored runs from the cached schemas (offline, no API)

```bash
# one cached schema under the main protocol (cap 5,000 rows, 30% design split, 5x2 CV, four models)
python scripts/expansion/run_offline_treatments.py --dataset <name> --schema cache/schemas/<name>/linear_svm/<generator>/schema_<hash>.json --out-dir <dir>
# column-permuted control for every run under <dir>
python scripts/expansion/permuted_control_capped.py --runs-dir <dir>/runs --out-dir <dir>/permuted
# re-materialize every stored run after a change to the formula evaluator
python scripts/expansion/rematerialize_after_evaluator_fix.py --help
```

### Generating new schemas or judgments (API keys required)

```bash
PYTHONPATH=src python -m dasef.cli generate-schema <dataset> <family> <generator> --cap 5000 --schema-design-fraction 0.3 --n-features 12
PYTHONPATH=src python -m dasef.cli run-schema-eval <dataset> <schema.json> --cap 5000 --schema-design-fraction 0.3 --include-random-controls   # writes results/schema_runs/<run_id>/
python run_judgments.py --help           # per-row judgments, 25 rows per call
python scripts/run_anonymized_controls.py --help
python scripts/run_prospective_formula_controls.py --datasets <six postcutoff_* names> --families tree,linear_svm,distance_knn --schema-models gpt-5.5-pro,gemini-3.1-pro-preview --schema-root cache/schemas_postcutoff_real --out-dir results/postcutoff_real --stats-out-dir results/statistics/postcutoff_real --schema-design-fraction 0.2   # post-cutoff runs; the exact invocation is in results/postcutoff_real/completed_runs.json
```

Schemas are cached by prompt hash, so repeated calls with the same prompt never hit the API twice.

## Protocol in one paragraph

Datasets larger than 5,000 rows are capped to a stratified sample (seed 42), then split into a 30% schema-design and
70% evaluation subset (seed 42). The generator receives only a column-level summary of the design split (names,
dtypes, missing rates, mean/std/min/max, ten most frequent categories, class balance) and returns 12 feature
specifications. Formula features are materialized on the evaluation rows with `src/dasef/features/formula.py` (an
AST-validated numpy/pandas subset, outputs clipped to the declared range). Downstream models (logistic regression,
k-NN with k=15, random forest, XGBoost) are scored with 5-fold x 2-repeat stratified cross-validation (seed 42) on one-vs-rest
ROC-AUC and balanced accuracy. Controls: each generated column independently row-permuted (seed 42), uniform noise matched
in count and declared range (seeds 42 and 43), and random formulas drawn from the same vocabulary over the dataset's own
columns. Statistics are dataset-level (generator-averaged), exact two-sided Wilcoxon tests, Holm correction over the four
models, percentile-bootstrap confidence intervals, Friedman/Nemenyi rankings. Full details are in Sections 3 and 4 of the paper
and in `CHANGELOG.md`, which lists every correction to the evaluator and to reported numbers.

## Tests

```bash
pytest -q
```

## Licence

Code: MIT (see `LICENSE`). Cached schemas, responses, result files and statistics: CC BY 4.0. Datasets remain under
their own licences (OpenML licence strings per dataset in `results/statistics/benchmark44/dataset_provenance.csv`;
Hugging Face licences in the post-cutoff provenance table of the paper; matrices derived from the two CC BY-NC tables are distributed under the
same non-commercial terms).
