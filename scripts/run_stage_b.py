"""Stage B: Formula-only evaluation for all Gemini schemas."""
import sys
import json
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

DATASETS = ["blood_transfusion", "pima_diabetes", "credit_g", "qsar_biodegradation"]
FAMILIES = ["tree", "linear_svm", "distance_knn"]
MODEL = "gemini-3-pro"
CACHE_DIR = ROOT / "cache" / "schemas"
RESULTS_DIR = ROOT / "results" / "model_sweeps"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DASEF_BIN = str(ROOT / ".venv" / "bin" / "dasef")

completed = []
failed = []

for dataset in DATASETS:
    for family in FAMILIES:
        schema_dir = CACHE_DIR / dataset / family / MODEL
        schemas = [p for p in schema_dir.glob("schema_*.json") if ".raw." not in p.name]
        if not schemas:
            print(f"NO SCHEMA: {dataset}/{family}/{MODEL}", flush=True)
            failed.append(f"{dataset}/{family}/{MODEL} - no schema")
            continue
        
        schema_path = str(schemas[0])
        out_file = RESULTS_DIR / f"{dataset}_{family}_{MODEL}_formula_eval.json"
        combo = f"{dataset}/{family}/{MODEL}"
        
        print(f"EVAL {combo}...", flush=True)
        start = time.time()
        
        cmd = [
            DASEF_BIN, "run-schema-eval",
            dataset, schema_path,
            "--downstream-models", "xgboost,random_forest,logistic_regression,knn",
            "--n-splits", "5",
            "--n-repeats", "2",
            "--dry-run-judgments",
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(ROOT))
            elapsed = time.time() - start
            
            if result.returncode == 0:
                # Extract JSON from stdout (skip log lines)
                stdout_lines = result.stdout.strip().split('\n')
                json_start = None
                for i, line in enumerate(stdout_lines):
                    if line.strip().startswith('{'):
                        json_start = i
                        break
                
                if json_start is not None:
                    json_text = '\n'.join(stdout_lines[json_start:])
                    out_file.write_text(json_text)
                    print(f"  OK in {elapsed:.1f}s -> {out_file.name}", flush=True)
                else:
                    out_file.write_text(result.stdout)
                    print(f"  OK in {elapsed:.1f}s (no JSON found, saved raw)", flush=True)
                completed.append(combo)
            else:
                print(f"  FAIL in {elapsed:.1f}s: {result.stderr[-200:]}", flush=True)
                failed.append(f"{combo} - exit {result.returncode}")
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT after 300s", flush=True)
            failed.append(f"{combo} - timeout")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {str(e)[:200]}", flush=True)
            failed.append(f"{combo} - {type(e).__name__}")

print(f"\n=== STAGE B COMPLETE ===", flush=True)
print(f"Completed: {len(completed)} | Failed: {len(failed)}", flush=True)
if failed:
    print("Failures:", flush=True)
    for f in failed:
        print(f"  - {f}", flush=True)
