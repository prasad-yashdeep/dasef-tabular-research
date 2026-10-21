#!/usr/bin/env python
"""Block 3: Judgment shortlist under prospective leakage-safe protocol.

Fills judgment features with DeepSeek R1 for the formula-positive schemas
identified in the Block 1 prospective formula-control run. Evaluates on the
disjoint evaluation split only (schema-design-fraction 0.2, seed 42).

Selection criteria: schemas where formula features beat random controls with
95% bootstrap CI excluding zero in at least one meaningful downstream model.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_downstream_awareness import (
    build_downstream_awareness,
    write_markdown_report as write_awareness_markdown,
)
from analyze_existing_results import write_markdown_report as write_stats_markdown
from dasef.config import load_llm_models
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation
from dasef.hash_utils import stable_hash
from dasef.io_utils import read_json, write_json
from dasef.statistics import comparisons_for_paths


# --- Configuration ---

SCHEMA_DESIGN_FRACTION = 0.2
SCHEMA_DESIGN_SEED = 42
DOWNSTREAM_MODELS = ["xgboost", "random_forest", "logistic_regression", "knn"]
N_SPLITS = 5
N_REPEATS = 2
RANDOM_CONTROL_SEED = 42

# Judgment filler configuration
JUDGMENT_MODEL = "deepseek-r1"
JUDGMENT_PROVIDER = "deepseek"

# Output directory
OUT_DIR = Path("results/prospective_judgment_shortlist")

# --- Shortlist ---
# Selected based on Block 1 prospective formula-control results:
# Schemas where formula beat random controls with CI excluding zero on KNN/RF/XGB.
# Focusing on blood_transfusion (strongest), pima_diabetes (solid), credit_g (moderate).
# Excluding qsar_biodegradation (neutral/negative in formula-only, no value adding judgment).

SHORTLIST = [
    # blood_transfusion — strongest formula gains, all schema variants strong on KNN
    {
        "dataset": "blood_transfusion",
        "family": "distance_knn",
        "schema_model": "claude-sonnet-4.6",
        "schema_path": "cache/schemas/blood_transfusion/distance_knn/claude-sonnet-4.6/schema_7019cd525482bf23.json",
        "rationale": "Prospective BA CI +0.14 (KNN), +0.08 (RF) vs random",
    },
    {
        "dataset": "blood_transfusion",
        "family": "linear_svm",
        "schema_model": "claude-sonnet-4.6",
        "schema_path": "cache/schemas/blood_transfusion/linear_svm/claude-sonnet-4.6/schema_e5ee48e95b4740b4.json",
        "rationale": "Prospective BA CI +0.13 (KNN), +0.07 (RF) vs random",
    },
    {
        "dataset": "blood_transfusion",
        "family": "tree",
        "schema_model": "claude-sonnet-4.6",
        "schema_path": "cache/schemas/blood_transfusion/tree/claude-sonnet-4.6/schema_3231ffc7380c7a44.json",
        "rationale": "Prospective BA CI +0.09 (KNN) vs random",
    },
    {
        "dataset": "blood_transfusion",
        "family": "distance_knn",
        "schema_model": "gemini-3.1-pro-preview",
        "schema_path": "cache/schemas/blood_transfusion/distance_knn/gemini-3.1-pro-preview/schema_3341515dc3e2ce10.json",
        "rationale": "Prospective BA CI +0.13 (KNN) vs random; Gemini cross-model check",
    },
    # pima_diabetes — solid formula gains on KNN
    {
        "dataset": "pima_diabetes",
        "family": "distance_knn",
        "schema_model": "claude-sonnet-4.6",
        "schema_path": "cache/schemas/pima_diabetes/distance_knn/claude-sonnet-4.6/schema_0610ce00140b737f.json",
        "rationale": "Prospective BA CI +0.06 (KNN) vs random; prior shortlist top performer",
    },
    {
        "dataset": "pima_diabetes",
        "family": "distance_knn",
        "schema_model": "gemini-3.1-pro-preview",
        "schema_path": "cache/schemas/pima_diabetes/distance_knn/gemini-3.1-pro-preview/schema_50264ade25c8c2d2.json",
        "rationale": "Prospective BA CI +0.07 (KNN) vs random; Gemini cross-model",
    },
    {
        "dataset": "pima_diabetes",
        "family": "tree",
        "schema_model": "claude-sonnet-4.6",
        "schema_path": "cache/schemas/pima_diabetes/tree/claude-sonnet-4.6/schema_6d8554e2adc614fd.json",
        "rationale": "Prospective BA CI +0.07 (KNN) vs random",
    },
    # credit_g — moderate formula gains, interesting because judgment helped here before
    {
        "dataset": "credit_g",
        "family": "distance_knn",
        "schema_model": "gemini-3.1-pro-preview",
        "schema_path": "cache/schemas/credit_g/distance_knn/gemini-3.1-pro-preview/schema_adb28d4c0a00a65f.json",
        "rationale": "Prospective ROC-AUC CI +0.03 (XGB, RF) vs random; 4 judgment features",
    },
    {
        "dataset": "credit_g",
        "family": "tree",
        "schema_model": "claude-sonnet-4.6",
        "schema_path": "cache/schemas/credit_g/tree/claude-sonnet-4.6/schema_5f941a93db4be64b.json",
        "rationale": "Prior shortlist: judgment KNN Δ BA +0.03; 2 judgment features",
    },
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build the plan manifest
    plan_path = OUT_DIR / "run_plan.json"
    completed_path = OUT_DIR / "completed_runs.json"

    # Load prior completions if resuming
    completed_runs: list[dict] = []
    if completed_path.exists():
        completed_runs = json.loads(completed_path.read_text()).get("runs", [])
    completed_keys = {
        (r["dataset"], r["family"], r["schema_model"]) for r in completed_runs
    }

    total = len(SHORTLIST)
    print(f"\n{'='*60}")
    print(f"Block 3: Prospective Judgment Shortlist")
    print(f"Judgment filler: {JUDGMENT_MODEL} ({JUDGMENT_PROVIDER})")
    print(f"Schemas to process: {total}")
    print(f"Already completed: {len(completed_keys)}")
    print(f"{'='*60}\n")

    for i, entry in enumerate(SHORTLIST, 1):
        key = (entry["dataset"], entry["family"], entry["schema_model"])
        if key in completed_keys:
            print(f"[{i}/{total}] SKIP (already done): {key}")
            continue

        schema_path = Path(entry["schema_path"])
        if not schema_path.exists():
            print(f"[{i}/{total}] ERROR: schema not found: {schema_path}")
            continue

        print(f"\n[{i}/{total}] Running: {entry['dataset']} / {entry['family']} / {entry['schema_model']}")
        print(f"  Schema: {schema_path}")
        print(f"  Rationale: {entry['rationale']}")

        run_id = stable_hash({
            "block": "judgment_shortlist",
            "dataset": entry["dataset"],
            "schema_path": str(schema_path),
            "judgment_model": JUDGMENT_MODEL,
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
                dataset_name=entry["dataset"],
                schema_path=schema_path,
                plan=plan,
                out_dir=run_dir,
                judgment_model_id=JUDGMENT_MODEL,
                judgment_provider=JUDGMENT_PROVIDER,
                dry_run_judgments=False,
                schema_design_fraction=SCHEMA_DESIGN_FRACTION,
                schema_design_seed=SCHEMA_DESIGN_SEED,
                include_random_controls=True,
                random_control_seed=RANDOM_CONTROL_SEED,
            )

            run_record = {
                "dataset": entry["dataset"],
                "family": entry["family"],
                "schema_model": entry["schema_model"],
                "schema_path": str(schema_path),
                "run_id": run_id,
                "result_path": str(run_dir / "results.json"),
                "judgment_model": JUDGMENT_MODEL,
                "judgment_provider": JUDGMENT_PROVIDER,
                "status": "completed",
                "rationale": entry["rationale"],
            }
            completed_runs.append(run_record)
            write_json(completed_path, {"runs": completed_runs})
            print(f"  ✓ Completed: {run_dir / 'results.json'}")

        except Exception as exc:
            print(f"  ✗ FAILED: {exc}")
            run_record = {
                "dataset": entry["dataset"],
                "family": entry["family"],
                "schema_model": entry["schema_model"],
                "schema_path": str(schema_path),
                "run_id": run_id,
                "status": "failed",
                "error": str(exc),
            }
            completed_runs.append(run_record)
            write_json(completed_path, {"runs": completed_runs})
            continue

    # --- Generate statistics reports ---
    print(f"\n{'='*60}")
    print("Generating statistics reports...")
    print(f"{'='*60}\n")

    result_paths = []
    for r in completed_runs:
        if r["status"] == "completed" and Path(r["result_path"]).exists():
            result_paths.append(Path(r["result_path"]))

    if not result_paths:
        print("No completed results to analyze.")
        return

    stats_dir = OUT_DIR / "statistics"
    stats_dir.mkdir(parents=True, exist_ok=True)

    for metric in ["roc_auc_ovr", "balanced_accuracy"]:
        print(f"  Computing {metric} statistics...")
        try:
            comparisons = comparisons_for_paths(result_paths, metric=metric, n_bootstrap=10000)
            csv_path = stats_dir / f"judgment_shortlist_stats_{metric}.csv"
            md_path = stats_dir / f"judgment_shortlist_stats_{metric}.md"
            comparisons.to_csv(csv_path, index=False)
            write_stats_markdown(comparisons, md_path, metric=metric, n_files=len(result_paths))
            print(f"    → {md_path}")
        except Exception as exc:
            print(f"    ✗ Failed: {exc}")

    # Downstream-awareness diagnostic
    for metric in ["roc_auc_ovr", "balanced_accuracy"]:
        print(f"  Computing downstream-awareness diagnostic ({metric})...")
        try:
            comparisons = comparisons_for_paths(result_paths, metric=metric, n_bootstrap=10000)
            awareness = build_downstream_awareness(comparisons)
            md_path = stats_dir / f"judgment_shortlist_downstream_awareness_{metric}.md"
            write_awareness_markdown(awareness, md_path, metric=metric)
            print(f"    → {md_path}")
        except Exception as exc:
            print(f"    ✗ Failed: {exc}")

    print(f"\n{'='*60}")
    print(f"Block 3 complete. Results in: {OUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
