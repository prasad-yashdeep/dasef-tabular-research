#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from analyze_downstream_awareness import (
    build_downstream_awareness,
    write_markdown_report as write_awareness_markdown,
)
from analyze_existing_results import write_markdown_report as write_stats_markdown
from dasef.config import load_llm_models
from dasef.datasets import dataset_summary, load_dataset, schema_design_eval_split, stratified_cap
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation
from dasef.hash_utils import stable_hash
from dasef.io_utils import read_json, write_json
from dasef.prompts import build_schema_prompt
from dasef.schema import SchemaSpec
from dasef.schema_generation import generate_schema
from dasef.statistics import comparisons_for_paths


DEFAULT_DATASETS = "blood_transfusion,pima_diabetes,credit_g,qsar_biodegradation"
DEFAULT_FAMILIES = "tree,linear_svm,distance_knn"
DEFAULT_SCHEMA_MODELS = "claude-sonnet-4.6,gemini-3.1-pro-preview"
DEFAULT_DOWNSTREAM = "xgboost,random_forest,logistic_regression,knn"


def csv_arg(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def schema_out_path(
    schema_root: Path,
    dataset_summary_payload: dict[str, Any],
    family: str,
    schema_model: str,
    n_features: int,
) -> Path:
    prompt = build_schema_prompt(
        dataset_summary_payload,
        family,
        schema_model,
        n_features=n_features,
    )
    prompt_hash = stable_hash({"prompt": prompt, "model": schema_model})
    return (
        schema_root
        / dataset_summary_payload["name"]
        / family
        / schema_model
        / f"schema_{prompt_hash}.json"
    )


def schema_feature_counts(schema_path: Path) -> dict[str, int]:
    schema = SchemaSpec.model_validate(read_json(schema_path))
    return {
        "feature_count": len(schema.features),
        "formula_feature_count": len(schema.formula_features),
        "judgment_feature_count": len(schema.judgment_features),
    }


def build_plan(args: argparse.Namespace) -> list[dict[str, Any]]:
    llm_registry = load_llm_models()
    known_models = {model.id for model in llm_registry.schema_generators}
    rows: list[dict[str, Any]] = []
    schema_root = Path(args.schema_root)
    for dataset_name in csv_arg(args.datasets):
        ds = load_dataset(dataset_name)
        if args.cap:
            ds = stratified_cap(ds, args.cap)
        design_ds, eval_ds = schema_design_eval_split(
            ds,
            args.schema_design_fraction,
            args.schema_design_seed,
        )
        design_summary = dataset_summary(design_ds)
        for family in csv_arg(args.families):
            for schema_model in csv_arg(args.schema_models):
                if schema_model not in known_models:
                    rows.append(
                        {
                            "dataset": dataset_name,
                            "family": family,
                            "schema_model": schema_model,
                            "status": "unknown_schema_model",
                        }
                    )
                    continue
                schema_path = schema_out_path(
                    schema_root,
                    design_summary,
                    family,
                    schema_model,
                    args.n_features,
                )
                row: dict[str, Any] = {
                    "dataset": dataset_name,
                    "family": family,
                    "schema_model": schema_model,
                    "schema_path": str(schema_path),
                    "design_rows": len(design_ds.X),
                    "eval_rows": len(eval_ds.X),
                    "schema_design_fraction": args.schema_design_fraction,
                    "schema_design_seed": args.schema_design_seed,
                    "status": "planned",
                }
                if schema_path.exists():
                    row.update(schema_feature_counts(schema_path))
                    row["status"] = "schema_cached"
                rows.append(row)

    runnable = [row for row in rows if row["status"] in {"planned", "schema_cached"}]
    if args.max_runs is not None:
        keep = {
            (row["dataset"], row["family"], row["schema_model"])
            for row in runnable[: args.max_runs]
        }
        for row in rows:
            if row["status"] in {"planned", "schema_cached"} and (
                row["dataset"],
                row["family"],
                row["schema_model"],
            ) not in keep:
                row["status"] = "skipped_by_max_runs"
    return rows


def write_plan_markdown(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    status_counts = df["status"].value_counts().to_dict() if not df.empty else {}
    lines = [
        "# Prospective Split-Generated Formula-Control Run Plan",
        "",
        "This run generates schemas from the schema-design split only, then evaluates",
        "raw, random-control, and formula-only matrices on the disjoint evaluation split.",
        "It performs schema-generator API calls unless the exact split prompt hash is cached.",
        "",
        "## Summary",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Runs", ""])
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
        prefix = "prospective_formula_controls"
        csv_path = out_dir / f"{prefix}_stats_{metric}.csv"
        md_path = out_dir / f"{prefix}_stats_{metric}.md"
        df.to_csv(csv_path, index=False)
        write_stats_markdown(df, md_path, metric=metric, result_count=len(result_paths))

        awareness = build_downstream_awareness(df) if not df.empty else pd.DataFrame()
        awareness_csv = out_dir / f"{prefix}_downstream_awareness_{metric}.csv"
        awareness_md = out_dir / f"{prefix}_downstream_awareness_{metric}.md"
        awareness.to_csv(awareness_csv, index=False)
        write_awareness_markdown(awareness, awareness_md)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run prospective split-generated formula-only DASEF controls."
    )
    parser.add_argument("--datasets", default=DEFAULT_DATASETS)
    parser.add_argument("--families", default=DEFAULT_FAMILIES)
    parser.add_argument("--schema-models", default=DEFAULT_SCHEMA_MODELS)
    parser.add_argument("--schema-root", default="cache/schemas")
    parser.add_argument("--out-dir", default="results/prospective_formula_controls")
    parser.add_argument("--stats-out-dir", default="results/statistics")
    parser.add_argument("--downstream-models", default=DEFAULT_DOWNSTREAM)
    parser.add_argument("--n-features", type=int, default=12)
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
    parser.add_argument("--force-regenerate", action="store_true")
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

    llm_registry = load_llm_models()
    model_by_id = {model.id: model for model in llm_registry.schema_generators}
    plan = EvaluationPlan(
        downstream_models=csv_arg(args.downstream_models),
        n_splits=args.n_splits,
        n_repeats=args.n_repeats,
        random_state=args.seed,
    )
    completed: list[dict[str, Any]] = []
    result_paths: list[Path] = []
    schema_root = Path(args.schema_root)

    for row in rows:
        if row["status"] not in {"planned", "schema_cached"}:
            completed.append(row)
            continue
        dataset_name = row["dataset"]
        family = row["family"]
        schema_model = row["schema_model"]
        schema_path = Path(row["schema_path"])
        try:
            ds = load_dataset(dataset_name)
            if args.cap:
                ds = stratified_cap(ds, args.cap)
            design_ds, _ = schema_design_eval_split(
                ds,
                args.schema_design_fraction,
                args.schema_design_seed,
            )
            design_summary = dataset_summary(design_ds)

            if args.force_regenerate or not schema_path.exists():
                generated = generate_schema(
                    design_summary,
                    family,
                    model_by_id[schema_model],
                    n_features=args.n_features,
                    dry_run=False,
                    out_dir=schema_root,
                )
                if not isinstance(generated, SchemaSpec):
                    raise TypeError("generate_schema returned a path during non-dry run")
                schema_path = schema_out_path(
                    schema_root,
                    design_summary,
                    family,
                    schema_model,
                    args.n_features,
                )
                schema_status = "schema_generated"
            else:
                schema_status = "schema_reused"

            counts = schema_feature_counts(schema_path)
            summary = run_schema_evaluation(
                dataset_name,
                schema_path,
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
            done = {
                **row,
                **counts,
                "status": "completed",
                "schema_status": schema_status,
                "schema_path": str(schema_path),
                "run_id": summary.run_id,
                "result_path": str(result_path),
            }
            completed.append(done)
            print(
                f"completed {dataset_name} {family} {schema_model} "
                f"schema={schema_status} -> {result_path}",
                flush=True,
            )
        except Exception as exc:
            failed = {**row, "status": "failed", "error": repr(exc)}
            completed.append(failed)
            print(f"failed {dataset_name} {family} {schema_model}: {exc!r}", flush=True)

    write_json(out_dir / "completed_runs.json", {"runs": completed, "args": vars(args)})
    if result_paths:
        write_stats(result_paths, Path(args.stats_out_dir), n_bootstrap=args.n_bootstrap, seed=args.seed)
    print(f"Wrote {out_dir / 'completed_runs.json'}")


if __name__ == "__main__":
    main()
