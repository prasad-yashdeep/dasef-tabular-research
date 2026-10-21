#!/usr/bin/env python
"""Full 10-dataset DASEF pipeline runner.

Runs the complete prospective formula-control pipeline:
1. Schema generation (Claude Sonnet 4.6 + Gemini 3.1 Pro) × 3 families
2. Formula-only evaluation with random controls (leakage-safe split)
3. Statistics generation

For the 4 pilot datasets, skips schema generation (schemas already exist).
For the 6 new datasets, generates schemas first, then evaluates.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dasef.config import load_llm_models
from dasef.datasets import load_dataset, schema_design_eval_split
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation
from dasef.hash_utils import stable_hash
from dasef.io_utils import write_json
from dasef.prompts import build_schema_prompt
from dasef.schema_generation import generate_schema


# --- Configuration ---
SCHEMA_DESIGN_FRACTION = 0.2
SCHEMA_DESIGN_SEED = 42
N_SPLITS = 5
N_REPEATS = 2
RANDOM_CONTROL_SEED = 42
DOWNSTREAM_MODELS = ["xgboost", "random_forest", "logistic_regression", "knn"]
N_FEATURES = 12

SCHEMA_MODELS = ["claude-sonnet-4.6", "gemini-3.1-pro-preview"]
FAMILIES = ["tree", "linear_svm", "distance_knn"]

# New datasets (need schema generation)
NEW_DATASETS = [
    "car_evaluation",
    "phoneme",
    "electricity",
    "spambase",
    "adult_income",
    "bank_marketing",
]

# Pilot datasets (schemas already cached)
PILOT_DATASETS = [
    "blood_transfusion",
    "pima_diabetes",
    "credit_g",
    "qsar_biodegradation",
]

ALL_DATASETS = PILOT_DATASETS + NEW_DATASETS

OUT_DIR = Path("results/full_suite_prospective")
SCHEMA_ROOT = Path("cache/schemas")


def find_or_generate_schema(dataset_name: str, family: str, schema_model: str) -> Path | None:
    """Find existing schema or generate a new one."""
    schema_dir = SCHEMA_ROOT / dataset_name / family / schema_model
    
    # Check for existing schemas
    if schema_dir.exists():
        schemas = list(schema_dir.glob("schema_*.json"))
        if schemas:
            for sp in schemas:
                try:
                    data = json.loads(sp.read_text())
                    if "features" in data:
                        return sp
                except Exception:
                    continue
    
    # Generate new schema
    print(f"    Generating schema: {dataset_name}/{family}/{schema_model}...")
    try:
        from dasef.datasets import dataset_summary as get_ds_summary
        from dasef.config import load_llm_models
        
        loaded = load_dataset(dataset_name)
        design_ds, _ = schema_design_eval_split(
            loaded, schema_design_fraction=SCHEMA_DESIGN_FRACTION, random_state=SCHEMA_DESIGN_SEED
        )
        summary = get_ds_summary(design_ds)
        
        # Find model config
        models = load_llm_models()
        model_config = None
        for m in models.schema_generators:
            if m.id == schema_model:
                model_config = m
                break
        if model_config is None:
            print(f"    ✗ Model config not found for {schema_model}")
            return None
        
        result = generate_schema(
            dataset_summary=summary,
            model_family=family,
            model_config=model_config,
            n_features=N_FEATURES,
        )
        # Schema is saved to cache dir; find the file
        schema_dir.mkdir(parents=True, exist_ok=True)
        schemas_after = [s for s in schema_dir.glob("schema_*.json") if not s.name.endswith(".raw.json")]
        if schemas_after:
            schema_path = schemas_after[-1]
        elif hasattr(result, 'prompt_hash'):
            schema_path = schema_dir / f"schema_{result.prompt_hash}.json"
        else:
            schema_path = None
        
        if schema_path and schema_path.exists():
            print(f"    ✓ Generated: {schema_path}")
            return schema_path
        else:
            print(f"    ✗ Schema file not found after generation")
            return None
    except Exception as exc:
        print(f"    ✗ Schema generation failed: {exc}")
        return None


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Track completions
    completed_path = OUT_DIR / "completed_runs.json"
    completed_runs: list[dict] = []
    if completed_path.exists():
        completed_runs = json.loads(completed_path.read_text()).get("runs", [])
    completed_keys = {
        (r["dataset"], r["family"], r["schema_model"]) for r in completed_runs
        if r.get("status") == "completed"
    }
    
    total_combos = len(ALL_DATASETS) * len(FAMILIES) * len(SCHEMA_MODELS)
    print(f"\n{'='*70}")
    print(f"  DASEF Full Suite — Prospective Formula Controls")
    print(f"  Datasets: {len(ALL_DATASETS)} | Families: {len(FAMILIES)} | Schema models: {len(SCHEMA_MODELS)}")
    print(f"  Total combinations: {total_combos}")
    print(f"  Already completed: {len(completed_keys)}")
    print(f"  Remaining: {total_combos - len(completed_keys)}")
    print(f"{'='*70}\n")
    
    run_count = 0
    for dataset_name in ALL_DATASETS:
        print(f"\n{'─'*60}")
        print(f"  Dataset: {dataset_name}")
        print(f"{'─'*60}")
        
        for family in FAMILIES:
            for schema_model in SCHEMA_MODELS:
                key = (dataset_name, family, schema_model)
                if key in completed_keys:
                    continue
                
                run_count += 1
                print(f"\n  [{run_count}] {dataset_name} / {family} / {schema_model}")
                
                # Find or generate schema
                schema_path = find_or_generate_schema(dataset_name, family, schema_model)
                if schema_path is None:
                    run_record = {
                        "dataset": dataset_name, "family": family,
                        "schema_model": schema_model, "status": "schema_failed",
                    }
                    completed_runs.append(run_record)
                    write_json(completed_path, {"runs": completed_runs})
                    continue
                
                # Run evaluation
                run_id = stable_hash({
                    "block": "full_suite_prospective",
                    "dataset": dataset_name,
                    "schema_path": str(schema_path),
                    "schema_design_fraction": SCHEMA_DESIGN_FRACTION,
                })
                run_dir = OUT_DIR / "runs" / run_id
                
                try:
                    plan = EvaluationPlan(
                        n_splits=N_SPLITS,
                        n_repeats=N_REPEATS,
                        random_state=SCHEMA_DESIGN_SEED,
                        downstream_models=DOWNSTREAM_MODELS,
                    )
                    
                    summary = run_schema_evaluation(
                        dataset_name=dataset_name,
                        schema_path=schema_path,
                        plan=plan,
                        out_dir=run_dir,
                        schema_design_fraction=SCHEMA_DESIGN_FRACTION,
                        schema_design_seed=SCHEMA_DESIGN_SEED,
                        include_random_controls=True,
                        random_control_seed=RANDOM_CONTROL_SEED,
                    )
                    
                    run_record = {
                        "dataset": dataset_name,
                        "family": family,
                        "schema_model": schema_model,
                        "schema_path": str(schema_path),
                        "run_id": run_id,
                        "result_path": str(next(run_dir.rglob("results.json"), run_dir / "results.json")),
                        "status": "completed",
                    }
                    completed_runs.append(run_record)
                    write_json(completed_path, {"runs": completed_runs})
                    completed_keys.add(key)
                    print(f"    ✓ Evaluation complete")
                    
                except Exception as exc:
                    print(f"    ✗ Evaluation failed: {exc}")
                    run_record = {
                        "dataset": dataset_name, "family": family,
                        "schema_model": schema_model, "status": "eval_failed",
                        "error": str(exc)[:200],
                    }
                    completed_runs.append(run_record)
                    write_json(completed_path, {"runs": completed_runs})
    
    # --- Final statistics ---
    print(f"\n{'='*70}")
    print(f"  Generating statistics...")
    print(f"{'='*70}\n")
    
    result_paths = []
    for r in completed_runs:
        if r.get("status") == "completed" and "result_path" in r:
            p = Path(r["result_path"])
            if p.exists():
                result_paths.append(p)
            else:
                # Try rglob
                alt = list(Path(f"results/full_suite_prospective/runs/{r.get('run_id', '')}").rglob("results.json"))
                if alt:
                    result_paths.append(alt[0])
    
    if result_paths:
        import pandas as pd_
        from analyze_existing_results import write_markdown_report as write_stats_md
        from analyze_downstream_awareness import build_downstream_awareness, write_markdown_report as write_awareness_md
        from dasef.statistics import comparisons_for_paths
        
        stats_dir = OUT_DIR / "statistics"
        stats_dir.mkdir(parents=True, exist_ok=True)
        
        for metric in ["roc_auc_ovr", "balanced_accuracy"]:
            print(f"  Computing {metric}...")
            comparisons = comparisons_for_paths(result_paths, metric=metric, n_bootstrap=10000)
            df = pd_.DataFrame([c.as_dict() for c in comparisons])
            write_stats_md(df, stats_dir / f"full_suite_stats_{metric}.md", metric=metric, result_count=len(result_paths))
            awareness = build_downstream_awareness(df)
            write_awareness_md(awareness, stats_dir / f"full_suite_downstream_awareness_{metric}.md")
            print(f"    → {stats_dir / f'full_suite_stats_{metric}.md'}")
    
    print(f"\n{'='*70}")
    print(f"  DONE. Results: {OUT_DIR}")
    n_ok = sum(1 for r in completed_runs if r.get("status") == "completed")
    n_fail = sum(1 for r in completed_runs if "failed" in r.get("status", ""))
    print(f"  Completed: {n_ok} | Failed: {n_fail} | Total: {len(completed_runs)}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
