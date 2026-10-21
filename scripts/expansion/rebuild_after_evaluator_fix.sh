#!/usr/bin/env bash
# After scripts/expansion/rematerialize_after_evaluator_fix.py has re-evaluated the runs whose
# formula columns changed, rebuild every derived statistic that depends on them:
#   1. the permuted-formula control of the changed runs (core: results/statistics/permuted_control;
#      expansion: results/expansion_offline/<gen>/<batch>/permuted), reusing the untouched runs;
#   2. the core-tier statistics (dataset_level, downstream awareness, leakage check);
#   3. the two-tier benchmark aggregates, tables and figures (rebuild_benchmark44.sh).
# The anonymized control is re-scored separately (scripts/rescore_anonymized_control_offline.py).
# Usage: bash scripts/expansion/rebuild_after_evaluator_fix.sh <report.csv from rematerialize_after_evaluator_fix.py>
set -euo pipefail
cd "$(dirname "$0")/../.."
REPORT=${1:?report csv}
export PYTHONPATH=src:scripts PYTHONUNBUFFERED=1

echo "[$(date '+%T')] deleting permuted controls of updated runs"
python - "$REPORT" <<'EOF'
import sys, pandas as pd
from pathlib import Path
rep = pd.read_csv(sys.argv[1]); upd = rep[rep.status == "updated"]
n = 0
for run in upd.run:
    p = Path(run); rid = p.name
    if run.startswith("results/judgments/"):
        f = Path("results/statistics/permuted_control") / f"{rid}_permuted.json"
    elif run.startswith("results/expansion_offline/"):
        f = p.parents[1] / "permuted" / "runs" / f"{rid}_permuted.json"
    else:
        continue  # prospective/leakage roots have no permuted control
    if f.exists():
        f.unlink(); n += 1
print(f"deleted {n} stale permuted-control files for {len(upd)} updated runs")
EOF

echo "[$(date '+%T')] core permuted control (recompute deleted runs only)"
python scripts/build_permuted_control.py --skip-existing > results/statistics/permuted_control/rebuild.log 2>&1
tail -3 results/statistics/permuted_control/rebuild.log

echo "[$(date '+%T')] expansion permuted controls"
for gen in gpt-5.5-pro gemini-3.1-pro-preview claude-opus-4.7 claude-sonnet-4.6; do
  for batch in raw_names safe_names; do
    d=results/expansion_offline/$gen/$batch
    [ -d "$d/runs" ] || continue
    extra=""; [ "$batch" = safe_names ] && extra="--safe-columns"
    python scripts/expansion/permuted_control_capped.py --runs-dir "$d/runs" --out-dir "$d/permuted" --skip-existing $extra > "$d/permuted/rebuild.log" 2>&1
    echo "  $gen/$batch: $(grep -c '^run ' "$d/permuted/rebuild.log") recomputed, $(grep -c '^reuse ' "$d/permuted/rebuild.log") reused, $(grep -c '^SKIP' "$d/permuted/rebuild.log") skipped"
  done
done

echo "[$(date '+%T')] core-tier statistics"
python scripts/aggregate_dataset_level.py > results/statistics/dataset_level/rebuild.log 2>&1
for metric in roc_auc_ovr balanced_accuracy; do
  python scripts/analyze_existing_results.py results/judgments --metric $metric --out-dir results/statistics/awareness_full > /dev/null
  python scripts/analyze_downstream_awareness.py --stats-csv results/statistics/awareness_full/existing_result_stats_$metric.csv --out-dir results/statistics/awareness_full > /dev/null
  python scripts/analyze_downstream_awareness.py --stats-csv results/statistics/awareness_full/existing_result_stats_$metric.csv --out-dir results/statistics/awareness_full \
    --downstream-models logistic_regression,random_forest,knn --suffix primary_models > /dev/null
done
python scripts/leakage_equivalence_check.py > /dev/null

echo "[$(date '+%T')] two-tier benchmark"
bash scripts/expansion/rebuild_benchmark44.sh
python scripts/expansion/scan_formula_columns.py --out results/statistics/benchmark44/formula_column_scan.csv > /dev/null
echo "[$(date '+%T')] ALL_REBUILT"
