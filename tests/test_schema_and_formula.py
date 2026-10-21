from __future__ import annotations

import pandas as pd

from dasef.features.formula import materialize_formula_features
from dasef.schema import SchemaSpec


def test_schema_and_formula_materialization():
    schema = SchemaSpec.model_validate({
        "dataset_name": "toy",
        "model_family": "tree",
        "schema_generator": "test",
        "features": [
            {
                "name": "age_gt_50",
                "type": "formula",
                "description": "Age over 50",
                "formula": "age > 50",
                "value_range": [0, 1],
                "feature_family": "threshold_indicator",
                "expected_model_benefit": "tree split",
                "leakage_risk": "low",
            },
            {
                "name": "risk_judgment",
                "type": "judgment",
                "description": "semantic risk",
                "value_range": [0, 1],
                "feature_family": "semantic_score",
                "expected_model_benefit": "smooth signal",
                "leakage_risk": "medium",
            },
        ],
    })
    df = pd.DataFrame({"age": [40, 60]})
    out = materialize_formula_features(df, schema)
    assert list(out.columns) == ["age_gt_50"]
    assert out["age_gt_50"].tolist() == [0, 1]


def test_formula_materialization_accepts_backtick_column_names():
    schema = SchemaSpec.model_validate({
        "dataset_name": "toy",
        "model_family": "tree",
        "schema_generator": "test",
        "features": [
            {
                "name": "band_mean",
                "type": "formula",
                "description": "Average nearby bands",
                "formula": "((`Band_74_W_544_90` + `Band_75_W_546_80`) / 2.0)",
                "value_range": [0, 10],
                "feature_family": "ratio_or_interaction",
                "expected_model_benefit": "tree split",
                "leakage_risk": "low",
            },
        ],
    })
    df = pd.DataFrame({
        "Band_74_W_544_90": [2.0, 4.0],
        "Band_75_W_546_80": [4.0, 8.0],
    })

    out = materialize_formula_features(df, schema)

    assert out["band_mean"].tolist() == [3.0, 6.0]


def _feature(name: str, formula: str, value_range=(-1e9, 1e9)) -> dict:
    return {
        "name": name,
        "type": "formula",
        "description": name,
        "formula": formula,
        "value_range": list(value_range),
        "feature_family": "interaction",
        "expected_model_benefit": "test",
        "leakage_risk": "low",
    }


def _schema(features: list[dict]) -> SchemaSpec:
    return SchemaSpec.model_validate({
        "dataset_name": "toy",
        "model_family": "linear_svm",
        "schema_generator": "test",
        "features": features,
    })


def test_numeric_looking_category_labels_support_arithmetic_and_string_comparison():
    # OpenML stores flag/code columns as ``category`` with string labels such as '-1'/'1'.
    df = pd.DataFrame({
        "flag": pd.Categorical(["1", "0", "1", "1"], categories=["0", "1"]),
        "code": pd.Categorical(["-1", "1", "-1", "1"], categories=["-1", "1"]),
        "x": [1.0, 2.0, 3.0, 4.0],
    })
    schema = _schema([
        _feature("arith", "flag + x"),
        _feature("str_cmp", "np.where(flag == '1', 1.0, 0.0) + np.where(code == '-1', 1.0, 0.0)"),
        _feature("num_cmp", "np.where((flag == 1) | (flag == '1'), 1.0, 0.0)"),
        _feature("neq", "(code != '1') * 1.0"),
        _feature("float_literal", "np.where(flag == '1.0', 1.0, 0.0)"),
    ])
    out = materialize_formula_features(df, schema)
    assert out["arith"].tolist() == [2.0, 2.0, 4.0, 5.0]
    assert out["str_cmp"].tolist() == [2.0, 0.0, 2.0, 1.0]
    assert out["num_cmp"].tolist() == [1.0, 0.0, 1.0, 1.0]
    assert out["neq"].tolist() == [1.0, 0.0, 1.0, 0.0]
    assert out["float_literal"].tolist() == [1.0, 0.0, 1.0, 1.0]


def test_textual_category_labels_keep_string_semantics():
    df = pd.DataFrame({
        "status": pd.Categorical(["no checking", "<0", ">=200", "no checking"]),
        "grade": pd.Categorical(["1", "A", "1", "2"]),  # mixed labels are not numeric-looking
        "x": [1.0, 2.0, 3.0, 4.0],
    })
    schema = _schema([
        _feature("no_check", "np.where(status == 'no checking', 1.0, 0.0)"),
        _feature("grade_one", "np.where(grade == '1', 1.0, 0.0)"),
        _feature("literal_not_numeric", "np.where(status == '7', 1.0, 0.0)"),
    ])
    out = materialize_formula_features(df, schema)
    assert out["no_check"].tolist() == [1.0, 0.0, 0.0, 1.0]
    assert out["grade_one"].tolist() == [1.0, 0.0, 1.0, 0.0]
    assert out["literal_not_numeric"].tolist() == [0.0, 0.0, 0.0, 0.0]


def test_narrow_integer_columns_do_not_overflow_in_formulas():
    import numpy as np

    df = pd.DataFrame({
        "a": np.array([200, 100, 250], dtype="uint8"),
        "b": np.array([100, 200, 250], dtype="uint8"),
        "c": np.array([3, -5, 7], dtype="int8"),
        "flag": np.array([True, False, True]),
    })
    schema = _schema([
        _feature("sum_ab", "a + b"),
        _feature("prod_ab", "a * b"),
        _feature("diff_ba", "b - a"),
        _feature("c_sq", "c * c * 100"),
        _feature("flag_and", "(flag & (a > 150)) * 1.0"),
    ])
    out = materialize_formula_features(df, schema)
    assert out["sum_ab"].tolist() == [300.0, 300.0, 500.0]
    assert out["prod_ab"].tolist() == [20000.0, 20000.0, 62500.0]
    assert out["diff_ba"].tolist() == [-100.0, 100.0, 0.0]
    assert out["c_sq"].tolist() == [900.0, 2500.0, 4900.0]
    assert out["flag_and"].tolist() == [1.0, 0.0, 1.0]
