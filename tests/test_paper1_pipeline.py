from __future__ import annotations

import pandas as pd

from dasef.datasets import LoadedDataset
from dasef.experiments import paper1_pipeline
from dasef.experiments.paper1_pipeline import (
    EvaluationPlan,
    evaluate_matrix,
    run_direct_risk_control,
    run_schema_evaluation,
)
from dasef.io_utils import write_model
from dasef.schema import FeatureSpec, FeatureType, SchemaSpec


def _toy_dataset() -> LoadedDataset:
    X = pd.DataFrame({
        "age": [20, 25, 30, 35, 45, 50, 55, 60],
        "income": [30, 35, 45, 50, 65, 70, 80, 90],
        "segment": ["a", "a", "b", "b", "a", "b", "a", "b"],
    })
    y = pd.Series([0, 0, 0, 0, 1, 1, 1, 1], name="target")
    return LoadedDataset(
        name="toy",
        X=X,
        y=y,
        categorical_columns=["segment"],
        numeric_columns=["age", "income"],
        target_name="target",
    )


def _toy_schema() -> SchemaSpec:
    return SchemaSpec(
        dataset_name="toy",
        model_family="tree",
        schema_generator="unit-test",
        features=[
            FeatureSpec(
                name="age_income_ratio",
                type=FeatureType.formula,
                description="Ratio of age to income.",
                value_range=(0.0, 10.0),
                feature_family="interaction",
                expected_model_benefit="Captures nonlinear row-level interaction.",
                leakage_risk="low",
                formula="age / income",
            ),
            FeatureSpec(
                name="risk_judgment",
                type=FeatureType.judgment,
                description="Semantic risk score.",
                value_range=(0.0, 1.0),
                feature_family="semantic_risk",
                expected_model_benefit="Adds expert-like row interpretation.",
                leakage_risk="low",
            ),
        ],
    )


def test_evaluate_matrix_smoke() -> None:
    ds = _toy_dataset()
    evaluation = evaluate_matrix(
        ds.X,
        ds.y,
        "raw",
        EvaluationPlan(downstream_models=["logistic_regression"], n_splits=2, n_repeats=1),
    )
    assert evaluation.matrix_name == "raw"
    assert "logistic_regression" in evaluation.models
    assert "balanced_accuracy" in evaluation.models["logistic_regression"]


def test_schema_evaluation_formula_and_judgment_dryrun(monkeypatch, tmp_path) -> None:
    ds = _toy_dataset()
    monkeypatch.setattr(paper1_pipeline, "load_dataset_for_experiment", lambda dataset_name, cap_rows=None: ds)
    schema_path = tmp_path / "schema.json"
    write_model(schema_path, _toy_schema())

    summary = run_schema_evaluation(
        "toy",
        schema_path,
        out_dir=tmp_path / "runs",
        plan=EvaluationPlan(downstream_models=["logistic_regression"], n_splits=2, n_repeats=1),
        judgment_model_id="deepseek-r1",
        judgment_provider="deepseek",
        dry_run_judgments=True,
    )

    assert [e.matrix_name for e in summary.evaluations] == ["raw", "raw_plus_formula"]
    assert "formula_matrix" in summary.artifacts
    assert "judgment_dir" in summary.artifacts
    assert any("hybrid evaluation skipped" in note for note in summary.notes)


def test_schema_evaluation_can_add_random_controls(monkeypatch, tmp_path) -> None:
    ds = _toy_dataset()
    monkeypatch.setattr(paper1_pipeline, "load_dataset_for_experiment", lambda dataset_name, cap_rows=None: ds)
    schema_path = tmp_path / "schema.json"
    write_model(schema_path, _toy_schema())

    summary = run_schema_evaluation(
        "toy",
        schema_path,
        out_dir=tmp_path / "runs",
        plan=EvaluationPlan(downstream_models=["logistic_regression"], n_splits=2, n_repeats=1),
        include_random_controls=True,
        random_control_seed=9,
    )

    assert [e.matrix_name for e in summary.evaluations] == [
        "raw",
        "raw_plus_random_formula",
        "raw_plus_formula",
        "raw_plus_random_all",
    ]
    assert "random_formula_matrix" in summary.artifacts
    assert "random_all_schema_features_matrix" in summary.artifacts


def test_direct_risk_control_dryrun_generates_prompts(monkeypatch, tmp_path) -> None:
    ds = _toy_dataset()
    monkeypatch.setattr(paper1_pipeline, "load_dataset_for_experiment", lambda dataset_name, cap_rows=None: ds)

    summary = run_direct_risk_control(
        "toy",
        target_class="1",
        filler_model_id="deepseek-r1",
        filler_provider="deepseek",
        out_dir=tmp_path / "direct_risk",
        plan=EvaluationPlan(downstream_models=["logistic_regression"], n_splits=2, n_repeats=1),
        dry_run=True,
    )

    assert [e.matrix_name for e in summary.evaluations] == ["raw"]
    assert "direct_risk_dir" in summary.artifacts
    assert any("dry-run mode" in note for note in summary.notes)
    assert list((tmp_path / "direct_risk").rglob("*.prompt.json"))


def test_schema_evaluation_can_exclude_schema_design_split(monkeypatch, tmp_path) -> None:
    ds = _toy_dataset()
    monkeypatch.setattr(paper1_pipeline, "load_dataset_for_experiment", lambda dataset_name, cap_rows=None: ds)
    schema_path = tmp_path / "schema.json"
    write_model(schema_path, _toy_schema())

    summary = run_schema_evaluation(
        "toy",
        schema_path,
        out_dir=tmp_path / "runs",
        plan=EvaluationPlan(downstream_models=["logistic_regression"], n_splits=2, n_repeats=1),
        schema_design_fraction=0.25,
        schema_design_seed=7,
    )

    assert summary.evaluations[0].rows == 6
    assert any("schema-design split" in note for note in summary.notes)
