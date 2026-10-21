from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .config import load_datasets, load_llm_models
from .datasets import dataset_summary, load_dataset, schema_design_eval_split, stratified_cap
from .features.augment import augment_with_formula
from .io_utils import read_model, write_json
from .logging_utils import configure_logging
from .schema import SchemaSpec
from .schema_generation import generate_schema
from .experiments.paper1_pipeline import (
    EvaluationPlan,
    run_pilot_dryrun,
    run_direct_risk_control,
    run_raw_baselines,
    run_schema_evaluation,
)
from .experiments.tracking import RunManifest, write_manifest

logger = logging.getLogger(__name__)


def cmd_list_datasets(_: argparse.Namespace) -> None:
    reg = load_datasets()
    for ds in reg.datasets:
        print(f"{ds.name}\topenml_id={ds.openml_id}\ttier={ds.tier}")


def cmd_summarize_dataset(args: argparse.Namespace) -> None:
    ds = load_dataset(args.dataset)
    if args.cap:
        ds = stratified_cap(ds, args.cap)
    summary = dataset_summary(ds)
    if args.out:
        write_json(args.out, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False)[: args.max_chars])


def cmd_generate_schema(args: argparse.Namespace) -> None:
    ds = load_dataset(args.dataset)
    if args.cap:
        ds = stratified_cap(ds, args.cap)
    if args.schema_design_fraction:
        ds, _ = schema_design_eval_split(ds, args.schema_design_fraction, args.schema_design_seed)
    summary = dataset_summary(ds)
    llm_reg = load_llm_models()
    models = [m for m in llm_reg.schema_generators if m.id == args.model]
    if not models:
        raise SystemExit(f"Unknown schema model: {args.model}")
    result = generate_schema(summary, args.model_family, models[0], n_features=args.n_features, dry_run=args.dry_run)
    print(result if isinstance(result, Path) else result.model_dump_json(indent=2))


def cmd_formula_only(args: argparse.Namespace) -> None:
    ds = load_dataset(args.dataset)
    schema = read_model(args.schema, SchemaSpec)
    X_aug = augment_with_formula(ds.X, schema)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    X_aug.to_parquet(out)
    logger.info("Formula-only augmented matrix written to %s shape=%s", out, X_aug.shape)
    print(out)


def cmd_init_run(args: argparse.Namespace) -> None:
    manifest = RunManifest(
        experiment_name=args.experiment_name,
        dataset=args.dataset,
        model_family=args.model_family,
        schema_model=args.schema_model,
        judgment_model=args.judgment_model,
        seed=args.seed,
    )
    path = write_manifest(args.out_dir, manifest)
    print(path)


def _csv_arg(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _evaluation_plan_from_args(args: argparse.Namespace) -> EvaluationPlan:
    return EvaluationPlan(
        downstream_models=_csv_arg(args.downstream_models)
        or ["xgboost", "logistic_regression", "random_forest", "knn"],
        n_splits=args.n_splits,
        n_repeats=args.n_repeats,
        random_state=args.seed,
    )


def cmd_run_raw_baselines(args: argparse.Namespace) -> None:
    summary = run_raw_baselines(
        args.dataset,
        out_dir=args.out_dir,
        cap_rows=args.cap,
        plan=_evaluation_plan_from_args(args),
        save_snapshot=not args.no_snapshot,
    )
    print(summary.model_dump_json(indent=2))


def cmd_run_direct_risk_control(args: argparse.Namespace) -> None:
    summary = run_direct_risk_control(
        args.dataset,
        target_class=args.target_class,
        filler_model_id=args.filler_model,
        filler_provider=args.filler_provider,
        out_dir=args.out_dir,
        cap_rows=args.cap,
        plan=_evaluation_plan_from_args(args),
        dry_run=args.dry_run,
    )
    print(summary.model_dump_json(indent=2))


def cmd_run_schema_eval(args: argparse.Namespace) -> None:
    summary = run_schema_evaluation(
        args.dataset,
        args.schema,
        out_dir=args.out_dir,
        cap_rows=args.cap,
        plan=_evaluation_plan_from_args(args),
        judgment_model_id=args.judgment_model,
        judgment_provider=args.judgment_provider,
        dry_run_judgments=args.dry_run_judgments,
        schema_design_fraction=args.schema_design_fraction,
        schema_design_seed=args.schema_design_seed,
        include_random_controls=args.include_random_controls,
        random_control_seed=args.random_control_seed,
    )
    print(summary.model_dump_json(indent=2))


def cmd_paper1_pilot_dryrun(args: argparse.Namespace) -> None:
    report = run_pilot_dryrun(
        datasets=_csv_arg(args.datasets),
        model_families=_csv_arg(args.model_families),
        schema_models=_csv_arg(args.schema_models),
        cap_rows=args.cap,
        n_features=args.n_features,
        out_dir=args.out_dir,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dasef")
    p.add_argument("--log-level", default="INFO")
    sub = p.add_subparsers(required=True)

    s = sub.add_parser("list-datasets")
    s.set_defaults(func=cmd_list_datasets)

    s = sub.add_parser("summarize-dataset")
    s.add_argument("dataset")
    s.add_argument("--cap", type=int)
    s.add_argument("--out")
    s.add_argument("--max-chars", type=int, default=6000)
    s.set_defaults(func=cmd_summarize_dataset)

    s = sub.add_parser("generate-schema")
    s.add_argument("dataset")
    s.add_argument("model_family", choices=["tree", "linear_svm", "distance_knn"])
    s.add_argument("model")
    s.add_argument("--n-features", type=int, default=20)
    s.add_argument("--cap", type=int)
    s.add_argument("--schema-design-fraction", type=float)
    s.add_argument("--schema-design-seed", type=int, default=42)
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=cmd_generate_schema)


    s = sub.add_parser("init-run")
    s.add_argument("experiment_name")
    s.add_argument("--dataset")
    s.add_argument("--model-family")
    s.add_argument("--schema-model")
    s.add_argument("--judgment-model")
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--out-dir", default="results/raw")
    s.set_defaults(func=cmd_init_run)

    s = sub.add_parser("formula-only")
    s.add_argument("dataset")
    s.add_argument("schema")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_formula_only)

    s = sub.add_parser("run-raw-baselines")
    s.add_argument("dataset")
    s.add_argument("--cap", type=int)
    s.add_argument("--downstream-models", default="xgboost,logistic_regression,random_forest,knn")
    s.add_argument("--n-splits", type=int, default=5)
    s.add_argument("--n-repeats", type=int, default=2)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--out-dir", default="results/raw")
    s.add_argument("--no-snapshot", action="store_true")
    s.set_defaults(func=cmd_run_raw_baselines)

    s = sub.add_parser("run-direct-risk-control")
    s.add_argument("dataset")
    s.add_argument("--target-class", required=True)
    s.add_argument("--filler-model", required=True)
    s.add_argument("--filler-provider", required=True)
    s.add_argument("--cap", type=int)
    s.add_argument("--downstream-models", default="xgboost,logistic_regression,random_forest,knn")
    s.add_argument("--n-splits", type=int, default=5)
    s.add_argument("--n-repeats", type=int, default=2)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--out-dir", default="results/direct_risk_controls")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=cmd_run_direct_risk_control)

    s = sub.add_parser("run-schema-eval")
    s.add_argument("dataset")
    s.add_argument("schema")
    s.add_argument("--cap", type=int)
    s.add_argument("--downstream-models", default="xgboost,logistic_regression,random_forest,knn")
    s.add_argument("--n-splits", type=int, default=5)
    s.add_argument("--n-repeats", type=int, default=2)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--out-dir", default="results/schema_runs")
    s.add_argument("--judgment-model")
    s.add_argument("--judgment-provider")
    s.add_argument("--dry-run-judgments", action="store_true")
    s.add_argument("--schema-design-fraction", type=float)
    s.add_argument("--schema-design-seed", type=int, default=42)
    s.add_argument("--include-random-controls", action="store_true")
    s.add_argument("--random-control-seed", type=int)
    s.set_defaults(func=cmd_run_schema_eval)

    s = sub.add_parser("paper1-pilot-dryrun")
    s.add_argument("--datasets", default="blood_transfusion,heart_disease")
    s.add_argument("--model-families", default="tree,linear_svm,distance_knn")
    s.add_argument("--schema-models", default="claude-sonnet-4.6,gpt-5.5,deepseek-r1,gemini-3-pro-latest")
    s.add_argument("--cap", type=int, default=100)
    s.add_argument("--n-features", type=int, default=20)
    s.add_argument("--out-dir", default="results/pilot_dryrun")
    s.set_defaults(func=cmd_paper1_pilot_dryrun)
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(level=args.log_level)
    args.func(args)


if __name__ == "__main__":
    main()
