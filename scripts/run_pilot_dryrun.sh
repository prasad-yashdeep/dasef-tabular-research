#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate 2>/dev/null || true
export PYTHONPATH="${PYTHONPATH:-src}"

python3 -m dasef.cli list-datasets
python3 -m dasef.cli summarize-dataset blood_transfusion --cap 100 --out results/raw/blood_summary.json --max-chars 2000
python3 -m dasef.cli generate-schema blood_transfusion tree claude-sonnet-4.6 --cap 100 --dry-run
python3 -m dasef.cli paper1-pilot-dryrun --datasets blood_transfusion,pima_diabetes --cap 100
