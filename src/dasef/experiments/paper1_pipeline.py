from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from dasef.config import load_llm_models, load_model_families
from dasef.datasets import (
    LoadedDataset,
    dataset_summary,
    load_dataset,
    save_dataset_snapshot,
    schema_design_eval_split,
    stratified_cap,
)
from dasef.evaluate import EvalResult, evaluate_classifier
from dasef.features.augment import augment_hybrid, augment_with_formula
from dasef.features.direct_risk import fill_direct_risk_scores
from dasef.features.judgment import fill_judgment_features
from dasef.features.random_control import augment_with_random_control
from dasef.hash_utils import stable_hash
from dasef.io_utils import read_model, write_json, write_model
from dasef.schema import SchemaSpec
from dasef.schema_generation import generate_schema

logger = logging.getLogger(__name__)


def resolve_provider_model_id(model_id: str, provider: str | None = None) -> str:
    """Resolve a stable research model id to the provider-specific API model id."""
    registry = load_llm_models()
    candidates = [*registry.schema_generators, *registry.judgment_fillers]
    for model in candidates:
        if model.id == model_id and (provider is None or model.provider == provider):
            return model.provider_model or model.id
    return model_id


DEFAULT_PILOT_DATASETS = ["blood_transfusion", "heart_disease"]
DEFAULT_MODEL_FAMILIES = ["tree", "linear_svm", "distance_knn"]
DEFAULT_SCHEMA_MODELS = ["claude-sonnet-4.6", "gpt-5.5-pro", "deepseek-r1", "gemini-3-pro"]
DEFAULT_SAFE_DOWNSTREAM_MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]


class MatrixEvaluation(BaseModel):
    matrix_name: str
    rows: int
    columns: int
    models: dict[str, dict[str, float]]
    raw_scores: dict[str, dict[str, list[float]]] = Field(default_factory=dict)


class Paper1RunSummary(BaseModel):
    run_id: str
    experiment_name: str
    dataset: str
    cap_rows: int | None = None
    artifacts: dict[str, str] = Field(default_factory=dict)
    evaluations: list[MatrixEvaluation] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class EvaluationPlan:
    downstream_models: list[str] = field(default_factory=lambda: DEFAULT_SAFE_DOWNSTREAM_MODELS.copy())
    n_splits: int = 5
    n_repeats: int = 2
    random_state: int = 42


def _eval_result_to_dict(result: EvalResult) -> tuple[dict[str, float], dict[str, list[float]]]:
    return result.metrics, result.raw_scores


def evaluate_matrix(
    X: pd.DataFrame,
    y: pd.Series,
    matrix_name: str,
    plan: EvaluationPlan,
) -> MatrixEvaluation:
    metrics: dict[str, dict[str, float]] = {}
    raw_scores: dict[str, dict[str, list[float]]] = {}
    for model_name in plan.downstream_models:
        result = evaluate_classifier(
            X,
            y,
            model_name,
            n_splits=plan.n_splits,
            n_repeats=plan.n_repeats,
            random_state=plan.random_state,
        )
        metrics[model_name], raw_scores[model_name] = _eval_result_to_dict(result)
    return MatrixEvaluation(
        matrix_name=matrix_name,
        rows=int(X.shape[0]),
        columns=int(X.shape[1]),
        models=metrics,
        raw_scores=raw_scores,
    )


def generate_phase1_schema_prompts(
    dataset: LoadedDataset,
    model_families: list[str] | None = None,
    schema_models: list[str] | None = None,
    n_features: int = 20,
    out_dir: Path = Path("cache/schemas"),
) -> list[Path]:
    """Generate audit artifacts for schema prompts without calling external APIs."""
    model_families = model_families or DEFAULT_MODEL_FAMILIES
    schema_models = schema_models or DEFAULT_SCHEMA_MODELS
    llm_registry = load_llm_models()
    by_id = {m.id: m for m in llm_registry.schema_generators}
    missing = [m for m in schema_models if m not in by_id]
    if missing:
        raise KeyError(f"Unknown schema model(s): {missing}")

    summary = dataset_summary(dataset)
    prompt_paths: list[Path] = []
    for family in model_families:
        for model_id in schema_models:
            path_or_schema = generate_schema(
                summary,
                family,
                by_id[model_id],
                n_features=n_features,
                dry_run=True,
                out_dir=out_dir,
            )
            if not isinstance(path_or_schema, Path):
                raise TypeError("dry_run=True should return a prompt artifact Path")
            prompt_paths.append(path_or_schema)
    return prompt_paths


def load_dataset_for_experiment(dataset_name: str, cap_rows: int | None = None) -> LoadedDataset:
    ds = load_dataset(dataset_name)
    return stratified_cap(ds, cap_rows) if cap_rows else ds


def run_raw_baselines(
    dataset_name: str,
    out_dir: str | Path = "results/raw",
    cap_rows: int | None = None,
    plan: EvaluationPlan | None = None,
    save_snapshot: bool = True,
) -> Paper1RunSummary:
    plan = plan or EvaluationPlan()
    ds = load_dataset_for_experiment(dataset_name, cap_rows)
    run_id = stable_hash({
        "experiment": "raw_baselines",
        "dataset": dataset_name,
        "cap_rows": cap_rows,
        "plan": plan.__dict__,
    })
    root = Path(out_dir) / run_id
    root.mkdir(parents=True, exist_ok=True)
    if save_snapshot:
        save_dataset_snapshot(ds, root / "data")

    summary = Paper1RunSummary(
        run_id=run_id,
        experiment_name="raw_baselines",
        dataset=dataset_name,
        cap_rows=cap_rows,
        artifacts={},
    )
    dataset_summary_path = root / "dataset_summary.json"
    write_json(dataset_summary_path, dataset_summary(ds))
    summary.artifacts["dataset_summary"] = str(dataset_summary_path)

    evaluation = evaluate_matrix(ds.X, ds.y, "raw", plan)
    summary.evaluations.append(evaluation)
    result_path = root / "results.json"
    write_json(result_path, summary.model_dump(mode="json"))
    summary.artifacts["results"] = str(result_path)
    logger.info("Raw baseline run complete dataset=%s run_id=%s", dataset_name, run_id)
    return summary


def run_direct_risk_control(
    dataset_name: str,
    *,
    target_class: str,
    filler_model_id: str,
    filler_provider: str,
    out_dir: str | Path = "results/direct_risk_controls",
    cap_rows: int | None = None,
    plan: EvaluationPlan | None = None,
    dry_run: bool = False,
) -> Paper1RunSummary:
    """Evaluate a direct LLM risk-score baseline, or generate prompts in dry-run mode."""
    plan = plan or EvaluationPlan()
    ds = load_dataset_for_experiment(dataset_name, cap_rows)
    provider_model_id = resolve_provider_model_id(filler_model_id, filler_provider)
    ds_summary = dataset_summary(ds)
    run_id = stable_hash({
        "experiment": "direct_risk_control",
        "dataset": dataset_name,
        "target_class": target_class,
        "filler_model_id": filler_model_id,
        "filler_provider": filler_provider,
        "provider_model_id": provider_model_id,
        "cap_rows": cap_rows,
        "plan": plan.__dict__,
        "dry_run": dry_run,
    })
    root = Path(out_dir) / run_id
    root.mkdir(parents=True, exist_ok=True)
    summary = Paper1RunSummary(
        run_id=run_id,
        experiment_name="direct_risk_control",
        dataset=dataset_name,
        cap_rows=cap_rows,
        artifacts={},
        notes=[
            "Direct-risk-score baseline asks an LLM to score the target class directly; "
            "compare against DASEF to ensure schema features add value beyond direct prediction."
        ],
    )
    write_json(root / "dataset_summary.json", ds_summary)
    summary.evaluations.append(evaluate_matrix(ds.X, ds.y, "raw", plan))
    direct_risk_dir = root / "direct_risk"
    scores = fill_direct_risk_scores(
        ds.X,
        ds_summary,
        target_class=target_class,
        filler_model_id=provider_model_id,
        filler_provider=filler_provider,
        dry_run=dry_run,
        out_dir=direct_risk_dir,
    )
    summary.artifacts["direct_risk_dir"] = str(direct_risk_dir)
    if dry_run:
        summary.notes.append("Direct-risk prompts were generated in dry-run mode; matrix evaluation skipped.")
    else:
        score_path = root / "matrices" / "direct_risk.parquet"
        score_path.parent.mkdir(parents=True, exist_ok=True)
        scores.to_parquet(score_path)
        summary.artifacts["direct_risk_matrix"] = str(score_path)
        X_direct = pd.concat([ds.X.reset_index(drop=True), scores.reset_index(drop=True)], axis=1)
        hybrid_path = root / "matrices" / "raw_plus_direct_risk.parquet"
        X_direct.to_parquet(hybrid_path)
        summary.artifacts["raw_plus_direct_risk_matrix"] = str(hybrid_path)
        summary.evaluations.append(evaluate_matrix(X_direct, ds.y, "raw_plus_direct_risk", plan))
    result_path = root / "results.json"
    write_json(result_path, summary.model_dump(mode="json"))
    summary.artifacts["results"] = str(result_path)
    logger.info("Direct-risk control complete dataset=%s run_id=%s", dataset_name, run_id)
    return summary


def run_schema_evaluation(
    dataset_name: str,
    schema_path: str | Path,
    out_dir: str | Path = "results/schema_runs",
    cap_rows: int | None = None,
    plan: EvaluationPlan | None = None,
    judgment_model_id: str | None = None,
    judgment_provider: str | None = None,
    dry_run_judgments: bool = False,
    schema_design_fraction: float | None = None,
    schema_design_seed: int = 42,
    include_random_controls: bool = False,
    random_control_seed: int | None = None,
    judgment_batch_size: int = 25,
) -> Paper1RunSummary:
    """Evaluate raw, formula-only, and optionally hybrid matrices for one schema.

    Judgment filling is opt-in. With `dry_run_judgments=True`, prompt artifacts are written but
    hybrid evaluation is skipped because no numeric judgment values exist yet.
    """
    plan = plan or EvaluationPlan()
    ds = load_dataset_for_experiment(dataset_name, cap_rows)
    if schema_design_fraction is not None:
        design_ds, eval_ds = schema_design_eval_split(ds, schema_design_fraction, schema_design_seed)
        ds = eval_ds
        logger.info(
            "Using leakage-safe evaluation split dataset=%s design_rows=%s eval_rows=%s seed=%s",
            dataset_name,
            len(design_ds.X),
            len(eval_ds.X),
            schema_design_seed,
        )
    schema = read_model(schema_path, SchemaSpec)
    run_id = stable_hash({
        "experiment": "schema_evaluation",
        "dataset": dataset_name,
        "schema_path": str(schema_path),
        "schema_hash": schema.model_dump(mode="json"),
        "cap_rows": cap_rows,
        "plan": plan.__dict__,
        "judgment_model_id": judgment_model_id,
        "dry_run_judgments": dry_run_judgments,
        "schema_design_fraction": schema_design_fraction,
        "schema_design_seed": schema_design_seed,
        "include_random_controls": include_random_controls,
        "random_control_seed": random_control_seed,
    })
    root = Path(out_dir) / run_id
    root.mkdir(parents=True, exist_ok=True)

    summary = Paper1RunSummary(
        run_id=run_id,
        experiment_name="schema_evaluation",
        dataset=dataset_name,
        cap_rows=cap_rows,
        artifacts={"schema": str(schema_path)},
    )
    if schema_design_fraction is not None:
        summary.notes.append(
            "Evaluation excluded the schema-design split "
            f"(fraction={schema_design_fraction}, seed={schema_design_seed}); "
            "the schema must be generated with the same split for leakage-safe claims."
        )
    write_json(root / "dataset_summary.json", dataset_summary(ds))
    write_model(root / "schema.normalized.json", schema)

    summary.evaluations.append(evaluate_matrix(ds.X, ds.y, "raw", plan))

    random_seed = plan.random_state if random_control_seed is None else random_control_seed
    if include_random_controls and schema.formula_features:
        X_random_formula = augment_with_random_control(
            ds.X,
            schema.formula_features,
            seed=random_seed,
            prefix="random_formula",
        )
        random_formula_path = root / "matrices" / "random_formula.parquet"
        random_formula_path.parent.mkdir(parents=True, exist_ok=True)
        X_random_formula.to_parquet(random_formula_path)
        summary.artifacts["random_formula_matrix"] = str(random_formula_path)
        summary.evaluations.append(
            evaluate_matrix(X_random_formula, ds.y, "raw_plus_random_formula", plan)
        )

    X_formula = augment_with_formula(ds.X, schema)
    formula_path = root / "matrices" / "formula.parquet"
    formula_path.parent.mkdir(parents=True, exist_ok=True)
    X_formula.to_parquet(formula_path)
    summary.artifacts["formula_matrix"] = str(formula_path)
    summary.evaluations.append(evaluate_matrix(X_formula, ds.y, "raw_plus_formula", plan))

    if include_random_controls and schema.features:
        X_random_all = augment_with_random_control(
            ds.X,
            schema.features,
            seed=random_seed + 1,
            prefix="random_schema",
        )
        random_all_path = root / "matrices" / "random_all_schema_features.parquet"
        X_random_all.to_parquet(random_all_path)
        summary.artifacts["random_all_schema_features_matrix"] = str(random_all_path)
        summary.evaluations.append(evaluate_matrix(X_random_all, ds.y, "raw_plus_random_all", plan))
        summary.notes.append(
            "Random-control matrices were evaluated with uniform random features matching "
            "DASEF feature counts and declared value ranges."
        )

    if schema.judgment_features and judgment_model_id and judgment_provider:
        judgment_dir = root / "judgments"
        provider_model_id = resolve_provider_model_id(judgment_model_id, judgment_provider)
        judgments = fill_judgment_features(
            ds.X,
            schema,
            filler_model_id=provider_model_id,
            filler_provider=judgment_provider,
            batch_size=judgment_batch_size,
            dry_run=dry_run_judgments,
            out_dir=judgment_dir,
        )
        summary.artifacts["judgment_dir"] = str(judgment_dir)
        if dry_run_judgments:
            summary.notes.append("Judgment prompts were generated in dry-run mode; hybrid evaluation skipped.")
        else:
            judgment_path = root / "matrices" / "judgment.parquet"
            judgments.to_parquet(judgment_path)
            summary.artifacts["judgment_matrix"] = str(judgment_path)
            X_hybrid = augment_hybrid(ds.X, schema, judgments)
            hybrid_path = root / "matrices" / "hybrid.parquet"
            X_hybrid.to_parquet(hybrid_path)
            summary.artifacts["hybrid_matrix"] = str(hybrid_path)
            summary.evaluations.append(evaluate_matrix(X_hybrid, ds.y, "raw_plus_formula_plus_judgment", plan))
    elif schema.judgment_features:
        summary.notes.append("Schema has judgment features, but no judgment filler was configured.")

    result_path = root / "results.json"
    write_json(result_path, summary.model_dump(mode="json"))
    summary.artifacts["results"] = str(result_path)
    logger.info("Schema evaluation complete dataset=%s schema=%s run_id=%s", dataset_name, schema_path, run_id)
    return summary


def run_pilot_dryrun(
    datasets: list[str] | None = None,
    model_families: list[str] | None = None,
    schema_models: list[str] | None = None,
    cap_rows: int | None = 100,
    n_features: int = 20,
    out_dir: str | Path = "results/pilot_dryrun",
) -> dict[str, Any]:
    """Create Phase-1 prompt artifacts for the paper-1 pilot without external API calls."""
    datasets = datasets or DEFAULT_PILOT_DATASETS
    model_families = model_families or DEFAULT_MODEL_FAMILIES
    schema_models = schema_models or DEFAULT_SCHEMA_MODELS
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "datasets": datasets,
        "model_families": model_families,
        "schema_models": schema_models,
        "cap_rows": cap_rows,
        "n_features": n_features,
        "prompt_artifacts": [],
        "notes": [],
    }
    # Validate downstream model family config up front; catches config drift early.
    configured_families = load_model_families().model_families
    unknown_families = [f for f in model_families if f not in configured_families]
    if unknown_families:
        raise KeyError(f"Unknown model family/families: {unknown_families}")

    for dataset_name in datasets:
        ds = load_dataset_for_experiment(dataset_name, cap_rows)
        ds_dir = root / dataset_name
        write_json(ds_dir / "dataset_summary.json", dataset_summary(ds))
        paths = generate_phase1_schema_prompts(
            ds,
            model_families=model_families,
            schema_models=schema_models,
            n_features=n_features,
            out_dir=ds_dir / "schema_prompts",
        )
        report["prompt_artifacts"].extend(str(p) for p in paths)
    report_path = root / "pilot_dryrun_report.json"
    write_json(report_path, report)
    report["report_path"] = str(report_path)
    logger.info("Pilot dry-run created %s prompt artifacts", len(report["prompt_artifacts"]))
    return report
