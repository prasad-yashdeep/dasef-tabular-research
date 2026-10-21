#!/usr/bin/env bash
# Rebuild every aggregate, table and figure of the two-tier (core + expansion) benchmark
# from the stored runs. Run from the repo root with .venv active. No LLM calls.
#
# Inputs (must already exist):
#   results/judgments/*                                  core runs (4 generators x 3 families x 10 datasets)
#   results/statistics/permuted_control/<run>_permuted.json   core permuted control (scripts/build_permuted_control.py)
#   results/expansion_offline/<gen>/{raw_names,safe_names}/permuted/run_level_scores.csv
#                                                        expansion run-level scores incl. permuted control
#                                                        (scripts/expansion/permuted_control_capped.py)
#   results/statistics/classical_baselines{,_expansion}/dataset_model_summary.csv
#   results/statistics/benchmark44/dataset_inventory.csv and results/statistics/benchmark44/core_dataset_inventory.csv
set -euo pipefail
cd "$(dirname "$0")/../.."
AGG=results/statistics/benchmark44
EXP=results/expansion_offline
mkdir -p "$AGG" paper/tables results/figures/cd_diagrams44

# 1. tag each expansion run-level file with its generator
python - <<'EOF'
import pandas as pd
from pathlib import Path
for gen in ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-4.7", "claude-sonnet-4.6"]:
    for batch in ["raw_names", "safe_names"]:
        f = Path(f"results/expansion_offline/{gen}/{batch}/permuted/run_level_scores.csv")
        if f.exists():
            df = pd.read_csv(f); df["generator"] = gen
            df.to_csv(f.with_name("run_level_scores_gen.csv"), index=False)
            print(f"tagged {f} ({df.dataset.nunique()} datasets)")
EOF
EXP_FILES=$(ls $EXP/*/raw_names/permuted/run_level_scores_gen.csv $EXP/*/safe_names/permuted/run_level_scores_gen.csv 2>/dev/null)

# 2. core tier: linear/SVM schema of each generator on the 10 core datasets
python scripts/expansion/core_matched_all_generators.py --out results/statistics/benchmark44_core_run_level.csv

# 3. dataset-level aggregation, contrasts, tests
python scripts/expansion/aggregate_benchmark44.py \
  --core-run-level results/statistics/benchmark44_core_run_level.csv \
  --expansion-run-level $EXP_FILES --out-dir "$AGG" > "$AGG/aggregate.log"

# 4. tables, Friedman/CD, figures
python scripts/expansion/make_tables44.py --agg-dir "$AGG" --out-dir paper/tables
python scripts/expansion/friedman_cd44.py --dataset-level "$AGG/dataset_level.csv" --out-md "$AGG/friedman_nemenyi.md" --fig-dir results/figures/cd_diagrams44 > /dev/null
python scripts/expansion/make_semantic_dotplot.py --dataset-level "$AGG/dataset_level.csv" --summary "$AGG/summary_pooled.csv" --out results/figures/semantic_dotplot.pdf
python scripts/expansion/make_dataset_table.py --inventory results/statistics/benchmark44/dataset_inventory.csv \
  --coverage "$AGG/coverage.csv" --core-inventory "$AGG/core_dataset_inventory.csv" --out paper/tables/datasets.tex > /dev/null
python scripts/expansion/classical_table44.py \
  --classical-dirs results/statistics/classical_baselines results/statistics/classical_baselines_expansion \
  --dataset-level "$AGG/dataset_level.csv" --out-dir results/statistics/benchmark44_classical > /dev/null
cp results/statistics/benchmark44_classical/classical.tex paper/tables/classical.tex
# the paper includes these three figures under fixed names (regenerate with DASEF_FIG_PGF=1 for Type 1 fonts)
cp results/figures/semantic_dotplot.pdf paper/dmlr/figures/fig2_semantic_deltas.pdf
cp results/figures/cd_diagrams44/roc_auc_ovr__logistic_regression.pdf paper/dmlr/figures/fig3a_cd_lr.pdf
cp results/figures/cd_diagrams44/roc_auc_ovr__xgboost.pdf paper/dmlr/figures/fig3b_cd_xgboost.pdf
echo "REBUILD_DONE"
