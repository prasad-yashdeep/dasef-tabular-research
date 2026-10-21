#!/usr/bin/env python
"""Parallel schema generation runner for a single model.

Usage:
  python run_schema_gen_single_model.py <model_id> [--datasets ds1,ds2,...] [--families f1,f2,...]

Generates schemas for all dataset×family combinations, then evaluates.
Saves to results/full_suite_expanded/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dasef.config import load_llm_models, load_model_families
from dasef.datasets import load_dataset, schema_design_eval_split, dataset_summary
from dasef.schema_generation import generate_schema
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation
from dasef.hash_utils import stable_hash
from dasef.io_utils import write_json

# Configuration
SCHEMA_DESIGN_FRACTION = 0.2
SCHEMA_DESIGN_SEED = 42
N_SPLITS = 5
N_REPEATS = 2
RANDOM_CONTROL_SEED = 42
DOWNSTREAM_MODELS = ["xgboost", "random_forest", "logistic_regression", "knn"]
N_FEATURES = 12

ALL_DATASETS = [
    "blood_transfusion", "pima_diabetes", "credit_g", "qsar_biodegradation",
    "car_evaluation", "phoneme", "electricity", "spambase", "adult_income", "bank_marketing",
]
ALL_FAMILIES = ["tree", "linear_svm", "distance_knn"]

OUT_DIR = Path("results/full_suite_expanded")
SCHEMA_ROOT = Path("cache/schemas")


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_schema_gen_single_model.py <model_id>")
        sys.exit(1)
    
    model_id = sys.argv[1]
    
    # Parse optional filters
    datasets = ALL_DATASETS
    families = ALL_FAMILIES
    for arg in sys.argv[2:]:
        if arg.startswith("--datasets="):
            datasets = arg.split("=")[1].split(",")
        elif arg.startswith("--families="):
            families = arg.split("=")[1].split(",")
    
    # Find model config
    models = load_llm_models()
    model_config = None
    for m in models.schema_generators:
        if m.id == model_id:
            model_config = m
            break
    if model_config is None:
        print(f"ERROR: Model '{model_id}' not found in configs/llm_models.yaml")
        sys.exit(1)
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    completed_path = OUT_DIR / f"completed_{model_id.replace('.', '_').replace('-', '_')}.json"
    completed_runs: list[dict] = []
    if completed_path.exists():
        completed_runs = json.loads(completed_path.read_text()).get("runs", [])
    completed_keys = {(r["dataset"], r["family"]) for r in completed_runs if r.get("status") == "completed"}
    
    total = len(datasets) * len(families)
    print(f"\n{'='*60}")
    print(f"  Schema Generator: {model_id}")
    print(f"  Datasets: {len(datasets)} | Families: {len(families)}")
    print(f"  Total: {total} | Already done: {len(completed_keys)}")
    print(f"{'='*60}\n")
    
    count = 0
    for dataset_name in datasets:
        for family in families:
            key = (dataset_name, family)
            if key in completed_keys:
                continue
            
            count += 1
            print(f"[{count}/{total-len(completed_keys)}] {dataset_name}/{family}/{model_id}")
            
            # Check existing schema
            schema_dir = SCHEMA_ROOT / dataset_name / family / model_id
            schema_path = None
            if schema_dir.exists():
                schemas = [s for s in schema_dir.glob("schema_*.json") if not s.name.endswith(".raw.json")]
                if schemas:
                    # Validate
                    for sp in schemas:
                        try:
                            data = json.loads(sp.read_text())
                            if "features" in data:
                                schema_path = sp
                                break
                        except Exception:
                            continue
            
            # Generate if needed
            if schema_path is None:
                try:
                    loaded = load_dataset(dataset_name)
                    design_ds, _ = schema_design_eval_split(loaded, schema_design_fraction=SCHEMA_DESIGN_FRACTION, random_state=SCHEMA_DESIGN_SEED)
                    summary = dataset_summary(design_ds)
                    
                    result = generate_schema(
                        dataset_summary=summary,
                        model_family=family,
                        model_config=model_config,
                        n_features=N_FEATURES,
                    )
                    
                    # Find saved file
                    schemas = [s for s in schema_dir.glob("schema_*.json") if not s.name.endswith(".raw.json")]
                    if schemas:
                        schema_path = schemas[-1]
                    elif hasattr(result, 'prompt_hash'):
                        schema_path = schema_dir / f"schema_{result.prompt_hash}.json"
                    
                    if not (schema_path and schema_path.exists()):
                        print(f"  ✗ Schema file not found after generation")
                        completed_runs.append({"dataset": dataset_name, "family": family, "schema_model": model_id, "status": "schema_failed"})
                        write_json(completed_path, {"runs": completed_runs})
                        continue
                    
                    print(f"  ✓ Schema: {schema_path.name}")
                except Exception as exc:
                    print(f"  ✗ Schema generation failed: {str(exc)[:100]}")
                    completed_runs.append({"dataset": dataset_name, "family": family, "schema_model": model_id, "status": "schema_failed", "error": str(exc)[:200]})
                    write_json(completed_path, {"runs": completed_runs})
                    continue
            else:
                print(f"  ✓ Schema cached: {schema_path.name}")
            
            # Evaluate
            run_id = stable_hash({
                "block": "full_suite_expanded",
                "dataset": dataset_name,
                "schema_path": str(schema_path),
                "schema_design_fraction": SCHEMA_DESIGN_FRACTION,
            })
            run_dir = OUT_DIR / "runs" / run_id
            
            try:
                plan = EvaluationPlan(
                    n_splits=N_SPLITS, n_repeats=N_REPEATS,
                    random_state=SCHEMA_DESIGN_SEED, downstream_models=DOWNSTREAM_MODELS,
                )
                run_schema_evaluation(
                    dataset_name=dataset_name, schema_path=schema_path, plan=plan,
                    out_dir=run_dir, schema_design_fraction=SCHEMA_DESIGN_FRACTION,
                    schema_design_seed=SCHEMA_DESIGN_SEED, include_random_controls=True,
                    random_control_seed=RANDOM_CONTROL_SEED,
                )
                result_path = next(run_dir.rglob("results.json"), run_dir / "results.json")
                completed_runs.append({
                    "dataset": dataset_name, "family": family, "schema_model": model_id,
                    "schema_path": str(schema_path), "run_id": run_id,
                    "result_path": str(result_path), "status": "completed",
                })
                write_json(completed_path, {"runs": completed_runs})
                completed_keys.add(key)
                print(f"  ✓ Evaluation done")
            except Exception as exc:
                print(f"  ✗ Eval failed: {str(exc)[:100]}")
                completed_runs.append({"dataset": dataset_name, "family": family, "schema_model": model_id, "status": "eval_failed", "error": str(exc)[:200]})
                write_json(completed_path, {"runs": completed_runs})
    
    n_ok = sum(1 for r in completed_runs if r.get("status") == "completed")
    n_fail = sum(1 for r in completed_runs if "failed" in r.get("status", ""))
    print(f"\n{'='*60}")
    print(f"  DONE: {model_id}")
    print(f"  Completed: {n_ok} | Failed: {n_fail}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
