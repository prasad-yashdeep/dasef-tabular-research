#!/usr/bin/env bash
# Rebuild every derived statistic after scripts/expansion/reevaluate_onehot_core.py re-scored the runs of the
# three cached core datasets with one-hot categorical raw blocks (adult_income, bank_marketing, car_evaluation).
# Run from the repo root with the virtualenv active. Offline; no LLM call.
#   1. permuted-formula control of the affected core runs (others reused)
#   2. classical AutoFE baselines of the three datasets, merged into the core summary
#   3. anonymized-column control re-scored for all ten core datasets (same encoding)
#   4. core-tier statistics (judgments, families, awareness, leakage), two-tier benchmark, tables, figures
#   5. random-expression control aggregate and table (requires the draws to be evaluated first)
set -euo pipefail
cd "$(dirname "$0")/../.."
DATASETS="adult_income bank_marketing car_evaluation"
STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="results/statistics/_pre_onehot_backup_$STAMP"; mkdir -p "$BACKUP"

START=${START_STEP:-1}
if [ "$START" -le 1 ]; then
echo "[$(date '+%T')] 1. permuted control of the affected core runs"
python - <<'PY'
import glob, json, os, shutil, pathlib
ROOT = pathlib.Path('.'); DS = {'adult_income', 'bank_marketing', 'car_evaluation'}
removed = 0
for f in glob.glob('results/judgments/*/results.json'):
    d = json.load(open(f)); rd = os.path.dirname(f)
    js = glob.glob(rd + '/judgments/*.json')
    if d['dataset'] in DS and js and json.load(open(js[0])).get('model') == 'deepseek-reasoner':
        p = pathlib.Path(f'results/statistics/permuted_control/{d["run_id"]}_permuted.json')
        if p.exists():
            bak = pathlib.Path(os.environ.get('BACKUP_DIR', 'results/statistics/_pre_onehot_backup')) / 'permuted_control'; bak.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(bak / p.name)); removed += 1
print('permuted-control files moved to backup:', removed)
PY
python scripts/build_permuted_control.py --skip-existing > "$BACKUP/build_permuted_control.log" 2>&1
echo "   reused: $(grep -c " reuse" "$BACKUP/build_permuted_control.log" || true) | skipped: $(grep -c "SKIP" "$BACKUP/build_permuted_control.log" || true)"

fi
if [ "$START" -le 2 ]; then
echo "[$(date '+%T')] 2. classical baselines for the three datasets"
cp results/statistics/classical_baselines/dataset_model_summary.csv "$BACKUP/classical_dataset_model_summary.csv"
python scripts/run_classical_baselines.py --out-dir results/statistics/classical_baselines_onehot --datasets $DATASETS > "$BACKUP/classical_onehot.log" 2>&1
python - <<'PY'
import pandas as pd
DS = {'adult_income', 'bank_marketing', 'car_evaluation'}
old = pd.read_csv('results/statistics/classical_baselines/dataset_model_summary.csv')
new = pd.read_csv('results/statistics/classical_baselines_onehot/dataset_model_summary.csv')
assert set(new.dataset) == DS, set(new.dataset)
merged = pd.concat([old[~old.dataset.isin(DS)], new], ignore_index=True)
merged.to_csv('results/statistics/classical_baselines/dataset_model_summary.csv', index=False)
print('classical summary rows:', len(old), '->', len(merged), '| variants for the three datasets:', sorted(new.variant.unique()))
PY

fi
echo "[$(date '+%T')] 3. anonymized control (all ten core datasets, offline re-score)"
cp results/anonymized_control/anonymized_per_run.csv "$BACKUP/anonymized_per_run.csv"
python scripts/rescore_anonymized_control_offline.py > "$BACKUP/anonymized_rescore.log" 2>&1
echo "   cells re-scored: $(grep -c "  OK " "$BACKUP/anonymized_rescore.log" || true)"

echo "[$(date '+%T')] 4. core-tier statistics and two-tier benchmark"
python scripts/aggregate_dataset_level.py > results/statistics/dataset_level/rebuild.log 2>&1
for metric in roc_auc_ovr balanced_accuracy; do
  python scripts/analyze_existing_results.py results/judgments --metric $metric --out-dir results/statistics/awareness_full > /dev/null
  python scripts/analyze_downstream_awareness.py --stats-csv results/statistics/awareness_full/existing_result_stats_$metric.csv --out-dir results/statistics/awareness_full > /dev/null
  python scripts/analyze_downstream_awareness.py --stats-csv results/statistics/awareness_full/existing_result_stats_$metric.csv --out-dir results/statistics/awareness_full \
    --downstream-models logistic_regression,random_forest,knn --suffix primary_models > /dev/null
done
python scripts/leakage_equivalence_check.py > /dev/null
bash scripts/expansion/rebuild_benchmark44.sh > "$BACKUP/rebuild_benchmark44.log" 2>&1
tail -1 "$BACKUP/rebuild_benchmark44.log" || true
python scripts/expansion/scan_formula_columns.py --out results/statistics/benchmark44/formula_column_scan.csv > /dev/null
python scripts/expansion/make_core_tables.py --out-dir paper/tables > /dev/null
python scripts/expansion/judgment_second_model.py > /dev/null
PYTHONWARNINGS=ignore python scripts/audit_judgment_signal.py > "$BACKUP/judgment_signal.log" 2>&1
python scripts/expansion/make_dataset_table.py --inventory results/statistics/benchmark44/dataset_inventory.csv --coverage results/statistics/benchmark44/coverage.csv \
  --core-inventory results/statistics/benchmark44/core_dataset_inventory.csv --provenance results/statistics/benchmark44/dataset_provenance.csv --style table --out paper/dmlr/tables/datasets.tex > /dev/null

if [ "${1:-}" != "--no-rfc" ]; then
  echo "[$(date '+%T')] 5. random-expression control aggregate and table"
  python scripts/expansion/random_formula_control.py aggregate > "$BACKUP/rfc_aggregate.log" 2>&1
  python scripts/expansion/random_formula_control.py table > /dev/null
fi
echo "[$(date '+%T')] ALL_REBUILT (backups in $BACKUP)"
