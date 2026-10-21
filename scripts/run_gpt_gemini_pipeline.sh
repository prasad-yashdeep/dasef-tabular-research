#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

DATASETS=(blood_transfusion pima_diabetes credit_g qsar_biodegradation)
FAMILIES=(tree linear_svm distance_knn)
MODELS=(gpt-5.5-pro gemini-3-pro)

SCHEMA_LOG="results/model_sweeps/schema_generation_log.txt"
> "$SCHEMA_LOG"

echo "=== STAGE A: Schema Generation ==="
GENERATED=0
FAILED=0
SKIPPED=0

for dataset in "${DATASETS[@]}"; do
  for family in "${FAMILIES[@]}"; do
    for model in "${MODELS[@]}"; do
      schema_dir="cache/schemas/${dataset}/${family}/${model}"
      # Check if valid schema already exists (non-raw json)
      existing=$(find "$schema_dir" -name "schema_*.json" ! -name "*.raw.json" 2>/dev/null | head -1)
      if [ -n "$existing" ]; then
        echo "SKIP: ${dataset}/${family}/${model} — already exists: $existing" | tee -a "$SCHEMA_LOG"
        SKIPPED=$((SKIPPED + 1))
        continue
      fi

      success=false
      for attempt in 1 2 3; do
        echo "GEN (attempt $attempt): ${dataset}/${family}/${model}" | tee -a "$SCHEMA_LOG"
        if dasef generate-schema "$dataset" "$family" "$model" --n-features 12 2>&1 | tee -a "$SCHEMA_LOG"; then
          # Verify a valid schema was written
          new_schema=$(find "$schema_dir" -name "schema_*.json" ! -name "*.raw.json" 2>/dev/null | head -1)
          if [ -n "$new_schema" ]; then
            echo "  SUCCESS: $new_schema" | tee -a "$SCHEMA_LOG"
            GENERATED=$((GENERATED + 1))
            success=true
            break
          fi
        fi
        echo "  RETRY needed for ${dataset}/${family}/${model} (attempt $attempt failed)" | tee -a "$SCHEMA_LOG"
        sleep 2
      done

      if [ "$success" = false ]; then
        echo "  FAILED after 3 attempts: ${dataset}/${family}/${model}" | tee -a "$SCHEMA_LOG"
        FAILED=$((FAILED + 1))
      fi
    done
  done
done

echo ""
echo "=== STAGE A COMPLETE ==="
echo "Generated: $GENERATED | Skipped: $SKIPPED | Failed: $FAILED"
echo "Generated: $GENERATED | Skipped: $SKIPPED | Failed: $FAILED" >> "$SCHEMA_LOG"
