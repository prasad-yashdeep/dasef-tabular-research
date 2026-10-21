#!/usr/bin/env python3
"""Backfill XGBoost scores into existing Paper 1 judgment result files.

The expensive LLM/schema work is already cached. This script reuses the stored
matrices for each run and evaluates the same matrix variants with XGBoost under
the same 5x2 CV protocol, then adds the missing `xgboost` entries to
`results.json`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dasef.datasets import load_dataset, schema_design_eval_split, stratified_cap
from dasef.evaluate import evaluate_classifier

RESULTS_DIR = ROOT / "results" / "judgments"
MODEL = "xgboost"

MATRIX_FILES = {
    "raw_plus_formula": "formula.parquet",
    "raw_plus_random_formula": "random_formula.parquet",
    "raw_plus_random_all": "random_all_schema_features.parquet",
    "raw_plus_formula_plus_judgment": "hybrid.parquet",
}


def load_raw_eval(dataset: str, cap_rows: int | None) -> tuple[pd.DataFrame, pd.Series]:
    """Reproduce the canonical pipeline's eval split EXACTLY.

    `run_schema_evaluation` caps the FULL dataset to `cap_rows` first, then takes
    the (0.3, seed=42) schema-design/eval split, and materializes the matrices
    from that eval portion. The previous version here split FIRST and capped
    SECOND, which produced a different row set (and order) for any dataset larger
    than the cap (adult_income, bank_marketing, electricity) -> labels were
    misaligned with the cached matrices and XGBoost collapsed to ~0.50 AUC.
    """
    ds = load_dataset(dataset)
    if cap_rows:
        ds = stratified_cap(ds, cap_rows)
    _, ds_eval = schema_design_eval_split(ds, 0.3, 42)
    return ds_eval.X.reset_index(drop=True), ds_eval.y.reset_index(drop=True)


def matrix_for(run_dir: Path, matrix_name: str, raw_X: pd.DataFrame) -> pd.DataFrame | None:
    if matrix_name == "raw":
        return raw_X
    file_name = MATRIX_FILES.get(matrix_name)
    if not file_name:
        return None
    path = run_dir / "matrices" / file_name
    if not path.exists():
        return None
    return pd.read_parquet(path).reset_index(drop=True)


def add_model_scores(evaluation: dict, result) -> None:
    evaluation.setdefault("raw_scores", {})[MODEL] = result.raw_scores
    evaluation.setdefault("models", {})[MODEL] = result.metrics


def needs_backfill(data: dict, include_existing: bool) -> bool:
    if include_existing:
        return True
    for evaluation in data.get("evaluations", []):
        if MODEL not in evaluation.get("raw_scores", {}):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill XGBoost scores into existing result JSON files.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--include-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--datasets", type=str, default="", help="comma-separated dataset filter")
    args = parser.parse_args()

    ds_filter = {d.strip() for d in args.datasets.split(",") if d.strip()}
    result_files = sorted(RESULTS_DIR.glob("*/results.json"))
    todo: list[Path] = []
    for path in result_files:
        data = json.loads(path.read_text())
        if ds_filter and data.get("dataset") not in ds_filter:
            continue
        if needs_backfill(data, args.include_existing):
            todo.append(path)
    if args.limit:
        todo = todo[: args.limit]

    print(f"Result files: {len(result_files)} | to backfill: {len(todo)}", flush=True)
    failures: list[dict] = []

    for idx, path in enumerate(todo, 1):
        run_dir = path.parent
        data = json.loads(path.read_text())
        dataset = data["dataset"]
        # Use the run's recorded cap verbatim (None = no cap). The old `or 5000`
        # fallback turned uncapped runs (e.g. phoneme, cap_rows=None) into 5000,
        # which only happened to be harmless under the old split-then-cap order;
        # under the correct cap-then-split order it changes the row set.
        cap_rows = data.get("cap_rows")
        print(f"[{idx}/{len(todo)}] {run_dir.name} / {dataset}", flush=True)
        start_run = time.time()

        try:
            raw_X, y = load_raw_eval(dataset, cap_rows)
            changed = False
            for evaluation in data.get("evaluations", []):
                matrix_name = evaluation.get("matrix_name")
                if not args.include_existing and MODEL in evaluation.get("raw_scores", {}):
                    continue
                X = matrix_for(run_dir, matrix_name, raw_X)
                if X is None:
                    print(f"  skip {matrix_name}: matrix unavailable", flush=True)
                    continue
                # Self-validating alignment: the reconstructed eval labels must have
                # the same row count as the cached matrix, AND the matrix's raw columns
                # must equal the reconstructed raw features row-for-row. If either check
                # fails, abort this run (recorded as a failure) rather than silently
                # truncating and producing misaligned ~0.50-AUC garbage.
                if len(X) != len(y):
                    raise ValueError(
                        f"alignment: {matrix_name} has {len(X)} rows but reconstructed y has {len(y)}"
                    )
                raw_cols = [c for c in raw_X.columns if c in X.columns]
                if len(raw_cols) != raw_X.shape[1] or not X[raw_cols].reset_index(drop=True).equals(
                    raw_X[raw_cols].reset_index(drop=True)
                ):
                    raise ValueError(
                        f"alignment: {matrix_name} raw columns do not match reconstructed eval"
                    )
                y_eval = y
                t0 = time.time()
                result = evaluate_classifier(
                    X,
                    y_eval,
                    MODEL,
                    n_splits=5,
                    n_repeats=2,
                    random_state=42,
                )
                add_model_scores(evaluation, result)
                changed = True
                print(f"  {matrix_name}: ok in {time.time() - t0:.1f}s", flush=True)

            if changed and not args.dry_run:
                backup = path.with_suffix(".json.bak_before_xgboost")
                if not backup.exists():
                    backup.write_text(path.read_text(), encoding="utf-8")
                path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  done in {time.time() - start_run:.1f}s", flush=True)
        except Exception as exc:
            failures.append({"run": run_dir.name, "dataset": dataset, "error": f"{type(exc).__name__}: {exc}"})
            print(f"  ERROR: {type(exc).__name__}: {exc}", flush=True)

    out_dir = ROOT / "results" / "statistics" / "xgboost_backfill"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
    print(f"Failures: {len(failures)}")
    print(f"Wrote {out_dir / 'failures.json'}")


if __name__ == "__main__":
    main()
