#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_downstream_awareness import build_downstream_awareness, write_markdown_report as write_awareness_markdown
from analyze_existing_results import write_markdown_report as write_stats_markdown
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation
from dasef.io_utils import read_json, write_json
from dasef.schema import SchemaSpec
from dasef.statistics import comparisons_for_paths


DEFAULT_DATASETS = "blood_transfusion,pima_diabetes,credit_g,qsar_biodegradation"
DEFAULT_FAMILIES = "tree,linear_svm,distance_knn"
DEFAULT_SCHEMA_MODELS = "claude-sonnet-4.6,gemini-3-pro"
DEFAULT_DOWNSTREAM = "xgboost,random_forest,logistic_regression,knn"


def csv_arg(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def latest_schema(schema_root: Path, dataset: str, family: str, schema_model: str) -> Path | None:
    root = schema_root / dataset / family / schema_model
    if not root.exists():
        return None
    candidates = [
        path
        for path in root.glob("schema_*.json")
        if ".raw." not in path.name and ".prompt." not in path.name
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime, path.name))


def build_plan(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    schema_root = Path(args.schema_root)
    for dataset in csv_arg(args.datasets):
        for family in csv_arg(args.families):
            for schema_model in csv_arg(args.schema_models):
                schema_path = latest_schema(schema_root, dataset, family, schema_model)
                if schema_path is None:
                    rows.append(
                        {
                            "dataset": dataset,
                            "family": family,
                            "schema_model": schema_model,
                            "schema_path": None,
                            "status": "missing_schema",
                        }
                    )
                    continue
                schema = SchemaSpec.model_validate(read_json(schema_path))
                rows.append(
                    {
                        "dataset": dataset,
                        "family": family,
                        "schema_model": schema_model,
                        "schema_path": str(schema_path),
                        "feature_count": len(schema.features),
                        "formula_feature_count": len(schema.formula_features),
                        "judgment_feature_count": len(schema.judgment_features),
                        "status": "planned",
                    }
                )
    planned = [row for row in rows if row["status"] == "planned"]
    if args.max_runs is not None:
        keep = {(row["dataset"], row["family"], row["schema_model"]) for row in planned[: args.max_runs]}
        for row in rows:
            if row["status"] == "planned" and (
                row["dataset"],
                row["family"],
                row["schema_model"],
            ) not in keep:
                row["status"] = "skipped_by_max_runs"
    return rows


def write_plan_markdown(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    lines = [
        "# Clean Formula-Control Run Plan",
        "",
        "This plan evaluates existing cached DASEF schemas with leakage-safe evaluation rows,",
        "formula-only DASEF features, and random-control matrices. It does not call LLM APIs.",
        "",
        "Important: cached schemas are publishable under the leakage-safe protocol only if",
        "they were generated from the same schema-design split. Otherwise this is rehearsal",
        "evidence for pipeline validation and screening.",
        "",
        "## Summary",
        "",
        f"- Planned runs: {int((df['status'] == 'planned').sum()) if not df.empty else 0}",
        f"- Missing schemas: {int((df['status'] == 'missing_schema').sum()) if not df.empty else 0}",
        f"- Skipped by max-runs: {int((df['status'] == 'skipped_by_max_runs').sum()) if not df.empty else 0}",
        "",
        "## Runs",
        "",
    ]
    lines.append(df.to_markdown(index=False) if not df.empty else "_No runs._")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_stats(result_paths: list[Path], out_dir: Path, *, n_bootstrap: int, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for metric in ["roc_auc_ovr", "balanced_accuracy"]:
        comparisons = comparisons_for_paths(
            result_paths,
            metric=metric,
            n_bootstrap=n_bootstrap,
            seed=seed,
        )
        df = pd.DataFrame([comparison.as_dict() for comparison in comparisons])
        csv_path = out_dir / f"clean_formula_controls_stats_{metric}.csv"
        md_path = out_dir / f"clean_formula_controls_stats_{metric}.md"
        df.to_csv(csv_path, index=False)
        write_stats_markdown(df, md_path, metric=metric, result_count=len(result_paths))

        awareness = build_downstream_awareness(df) if not df.empty else pd.DataFrame()
        awareness_csv = out_dir / f"clean_formula_controls_downstream_awareness_{metric}.csv"
        awareness_md = out_dir / f"clean_formula_controls_downstream_awareness_{metric}.md"
        awareness.to_csv(awareness_csv, index=False)
        write_awareness_markdown(awareness, awareness_md)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run leakage-split formula-only controls for cached DASEF schemas.")
    parser.add_argument("--datasets", default=DEFAULT_DATASETS)
    parser.add_argument("--families", default=DEFAULT_FAMILIES)
    parser.add_argument("--schema-models", default=DEFAULT_SCHEMA_MODELS)
    parser.add_argument("--schema-root", default="cache/schemas")
    parser.add_argument("--out-dir", default="results/clean_formula_controls")
    parser.add_argument("--stats-out-dir", default="results/statistics")
    parser.add_argument("--downstream-models", default=DEFAULT_DOWNSTREAM)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-repeats", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cap", type=int)
    parser.add_argument("--schema-design-fraction", type=float, default=0.2)
    parser.add_argument("--schema-design-seed", type=int, default=42)
    parser.add_argument("--random-control-seed", type=int, default=42)
    parser.add_argument("--n-bootstrap", type=int, default=10_000)
    parser.add_argument("--max-runs", type=int)
    parser.add_argument("--plan-only", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = build_plan(args)
    write_json(out_dir / "run_plan.json", {"runs": rows, "args": vars(args)})
    write_plan_markdown(rows, out_dir / "run_plan.md")

    if args.plan_only:
        print(f"Wrote {out_dir / 'run_plan.json'}")
        print(f"Wrote {out_dir / 'run_plan.md'}")
        return

    plan = EvaluationPlan(
        downstream_models=csv_arg(args.downstream_models),
        n_splits=args.n_splits,
        n_repeats=args.n_repeats,
        random_state=args.seed,
    )
    completed: list[dict[str, Any]] = []
    result_paths: list[Path] = []
    for row in rows:
        if row["status"] != "planned":
            continue
        try:
            summary = run_schema_evaluation(
                row["dataset"],
                row["schema_path"],
                out_dir=out_dir / "runs",
                cap_rows=args.cap,
                plan=plan,
                schema_design_fraction=args.schema_design_fraction,
                schema_design_seed=args.schema_design_seed,
                include_random_controls=True,
                random_control_seed=args.random_control_seed,
            )
            result_path = Path(summary.artifacts["results"])
            result_paths.append(result_path)
            completed.append(
                {
                    **row,
                    "status": "completed",
                    "run_id": summary.run_id,
                    "result_path": str(result_path),
                }
            )
            print(f"completed {row['dataset']} {row['family']} {row['schema_model']} -> {result_path}", flush=True)
        except Exception as exc:
            completed.append({**row, "status": "failed", "error": repr(exc)})
            print(f"failed {row['dataset']} {row['family']} {row['schema_model']}: {exc!r}", flush=True)

    write_json(out_dir / "completed_runs.json", {"runs": completed, "args": vars(args)})
    if result_paths:
        write_stats(result_paths, Path(args.stats_out_dir), n_bootstrap=args.n_bootstrap, seed=args.seed)
    print(f"Wrote {out_dir / 'completed_runs.json'}")


if __name__ == "__main__":
    main()
