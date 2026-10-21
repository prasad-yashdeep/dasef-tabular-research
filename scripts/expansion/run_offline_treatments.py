#!/usr/bin/env python
"""Offline evaluation of one cached schema under the main-benchmark protocol.

Thin wrapper around dasef.experiments.paper1_pipeline.run_schema_evaluation
(the same function scripts/run_clean_formula_controls.py calls). Adds ONE thing the
repo runner lacks: --safe-columns, which applies scripts/run_paper2_llm_schema_expansion
.safe_columns() to the loaded dataset so schemas generated with renamed columns can be
materialized. Produces raw / raw_plus_random_formula / raw_plus_formula /
raw_plus_random_all; then permuted_control_capped.py adds raw_plus_permuted_formula.
No LLM calls: judgment_model_id is never passed, so fill_judgment_features is not reached.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

import dasef.experiments.paper1_pipeline as p1  # noqa: E402
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--cap", type=int, default=5000)
    ap.add_argument("--schema-design-fraction", type=float, default=0.3)
    ap.add_argument("--schema-design-seed", type=int, default=42)
    ap.add_argument("--random-control-seed", type=int, default=42)
    ap.add_argument("--downstream", default="xgboost,random_forest,logistic_regression,knn")
    ap.add_argument("--safe-columns", action="store_true")
    args = ap.parse_args()

    if args.safe_columns:
        from run_paper2_llm_schema_expansion import safe_columns
        _orig = p1.load_dataset

        def _renamed(name: str):
            return safe_columns(_orig(name))

        p1.load_dataset = _renamed  # run_schema_evaluation resolves load_dataset from this module namespace

    plan = EvaluationPlan(downstream_models=args.downstream.split(","), n_splits=5, n_repeats=2, random_state=42)
    t0 = time.time()
    summary = run_schema_evaluation(
        args.dataset,
        args.schema,
        out_dir=Path(args.out_dir) / "runs",
        cap_rows=args.cap,
        plan=plan,
        schema_design_fraction=args.schema_design_fraction,
        schema_design_seed=args.schema_design_seed,
        include_random_controls=True,
        random_control_seed=args.random_control_seed,
    )
    elapsed = time.time() - t0
    print(f"run_id={summary.run_id} results={summary.artifacts['results']} elapsed={elapsed:.1f}s")
    for ev in summary.evaluations:
        print(f"  {ev.matrix_name:28s} rows={ev.rows} cols={ev.columns} " +
              " ".join(f"{m}={v['roc_auc_ovr']:.4f}" for m, v in ev.models.items()))
    for note in summary.notes:
        print("  note:", note)


if __name__ == "__main__":
    main()
