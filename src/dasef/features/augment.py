from __future__ import annotations

import pandas as pd

from dasef.schema import SchemaSpec
from .formula import materialize_formula_features


def augment_with_formula(df: pd.DataFrame, schema: SchemaSpec) -> pd.DataFrame:
    formula_df = materialize_formula_features(df, schema)
    return pd.concat([df.reset_index(drop=True), formula_df.reset_index(drop=True)], axis=1)


def augment_hybrid(df: pd.DataFrame, schema: SchemaSpec, judgment_df: pd.DataFrame | None = None) -> pd.DataFrame:
    formula_df = materialize_formula_features(df, schema)
    parts = [df.reset_index(drop=True), formula_df.reset_index(drop=True)]
    if judgment_df is not None:
        parts.append(judgment_df.reset_index(drop=True))
    return pd.concat(parts, axis=1)
