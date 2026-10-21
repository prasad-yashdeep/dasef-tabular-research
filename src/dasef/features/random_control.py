from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from dasef.schema import FeatureSpec


def random_features_for_specs(
    index: pd.Index,
    feature_specs: Sequence[FeatureSpec],
    *,
    seed: int = 42,
    prefix: str = "random_control",
) -> pd.DataFrame:
    """Generate random numeric controls matching DASEF feature count and ranges."""
    rng = np.random.default_rng(seed)
    columns: dict[str, np.ndarray] = {}
    n_rows = len(index)
    for feature in feature_specs:
        lo, hi = feature.value_range
        if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
            lo, hi = 0.0, 1.0
        columns[f"{prefix}_{feature.name}"] = rng.uniform(lo, hi, size=n_rows)
    return pd.DataFrame(columns, index=index)


def augment_with_random_control(
    df: pd.DataFrame,
    feature_specs: Sequence[FeatureSpec],
    *,
    seed: int = 42,
    prefix: str = "random_control",
) -> pd.DataFrame:
    random_df = random_features_for_specs(df.index, feature_specs, seed=seed, prefix=prefix)
    return pd.concat([df.reset_index(drop=True), random_df.reset_index(drop=True)], axis=1)
