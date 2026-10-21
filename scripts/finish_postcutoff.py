#!/usr/bin/env python
"""Re-run the 2 post-cutoff cells whose schema generation failed, then leave the
result dirs in place so post-cutoff stats can be recomputed over all runs.

Failed cells (gpt-5.5-pro schema-gen JSONDecodeError / ReadTimeout):
  - postcutoff_clinical_trials_ai_20260517 / distance_knn
  - postcutoff_prediction_markets_20260517 / tree
"""
from __future__ import annotations

from pathlib import Path

from dasef.config import load_llm_models
from dasef.datasets import dataset_summary, load_dataset, schema_design_eval_split
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation
from dasef.schema import SchemaSpec
from dasef.schema_generation import generate_schema

from run_prospective_formula_controls import schema_out_path

CELLS = [
    ("postcutoff_clinical_trials_ai_20260517", "distance_knn"),
    # prediction_markets/tree omitted: a ~217k-row evaluation with negligible
    # impact on the 6-dataset aggregate; its schema-gen call originally timed out.
]
SCHEMA_MODEL = "gpt-5.5-pro"
SCHEMA_ROOT = Path("cache/schemas_postcutoff_real")
OUT_DIR = Path("results/postcutoff_real/runs")
N_FEATURES = 12
FRACTION = 0.2
SEED = 42


def main() -> None:
    model_cfg = {m.id: m for m in load_llm_models().schema_generators}[SCHEMA_MODEL]
    plan = EvaluationPlan(
        downstream_models=["xgboost", "logistic_regression", "random_forest", "knn"],
        n_splits=5, n_repeats=2, random_state=SEED,
    )
    for dataset_name, family in CELLS:
        print(f"=== {dataset_name} / {family} ===", flush=True)
        ds = load_dataset(dataset_name)
        design_ds, _ = schema_design_eval_split(ds, FRACTION, SEED)
        design_summary = dataset_summary(design_ds)
        generated = generate_schema(
            design_summary, family, model_cfg,
            n_features=N_FEATURES, dry_run=False, out_dir=SCHEMA_ROOT,
        )
        if not isinstance(generated, SchemaSpec):
            raise TypeError("generate_schema returned a path in non-dry run")
        schema_path = schema_out_path(SCHEMA_ROOT, design_summary, family, SCHEMA_MODEL, N_FEATURES)
        print(f"  schema generated: {schema_path}", flush=True)
        summary = run_schema_evaluation(
            dataset_name, schema_path, out_dir=OUT_DIR, cap_rows=None, plan=plan,
            schema_design_fraction=FRACTION, schema_design_seed=SEED,
            include_random_controls=True, random_control_seed=SEED,
        )
        print(f"  done -> {summary.artifacts['results']}", flush=True)


if __name__ == "__main__":
    main()
