from __future__ import annotations

import os

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.model_selection import train_test_split

from .config import DatasetConfig, load_datasets
from .paths import DATA_DIR

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadedDataset:
    name: str
    X: pd.DataFrame
    y: pd.Series
    categorical_columns: list[str]
    numeric_columns: list[str]
    target_name: str
    onehot_override_columns: list[str] = field(default_factory=list)  # integer-coded categoricals cast to category


# Integer-coded categorical columns of the locally cached core datasets (OpenML nominal attributes).
LOCAL_CACHE_CATEGORICAL: dict[str, list[str]] = {
    "adult_income": ["workclass", "education", "marital_status", "occupation", "relationship", "race", "sex", "native_country"],
    "bank_marketing": ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "day_of_week", "poutcome"],
    "car_evaluation": ["buying", "maint", "doors", "persons", "lug_boot", "safety"],
}


def raw_block_equal(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    """Row-alignment check that ignores the category-versus-integer dtype of override columns."""
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return False
    for col in a.columns:
        x, y = a[col], b[col]
        if str(x.dtype) == "category" or str(y.dtype) == "category" or (pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y)):
            try:
                xv = pd.to_numeric(x.astype(object), errors="coerce").to_numpy(dtype=float)
                yv = pd.to_numeric(y.astype(object), errors="coerce").to_numpy(dtype=float)
            except (TypeError, ValueError):
                return False
            if not np.allclose(np.nan_to_num(xv, nan=-1e300), np.nan_to_num(yv, nan=-1e300), rtol=0, atol=1e-9):
                return False
        elif not x.astype(str).equals(y.astype(str)):
            return False
    return True


def _infer_columns(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = [c for c in X.columns if is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in numeric]
    return categorical, numeric


def load_openml_dataset(config: DatasetConfig, cache: bool = True) -> LoadedDataset:
    if config.openml_id is None:
        raise ValueError(f"Dataset {config.name} has no OpenML id configured")
    logger.info("Fetching OpenML dataset %s (%s)", config.name, config.openml_id)
    try:
        import openml
    except ModuleNotFoundError as exc:
        raise RuntimeError("OpenML support requires dependency `openml`. Install project deps with `pip install -e .`.") from exc
    ds = openml.datasets.get_dataset(config.openml_id, download_data=cache, download_qualities=False, download_features_meta_data=True)
    X, y, categorical_indicator, attribute_names = ds.get_data(dataset_format="dataframe", target=ds.default_target_attribute)
    if y is None:
        raise ValueError(f"OpenML dataset {config.name} returned no target")
    X = X.copy()
    y = pd.Series(y, name=ds.default_target_attribute)
    categorical = [col for col, is_cat in zip(attribute_names, categorical_indicator, strict=False) if is_cat and col in X.columns]
    inferred_cat, numeric = _infer_columns(X)
    categorical = sorted(set(categorical) | set(inferred_cat))
    numeric = [c for c in X.columns if c not in categorical]
    return LoadedDataset(config.name, X, y, categorical, numeric, ds.default_target_attribute or "target")


def _load_from_local_cache(name: str) -> LoadedDataset | None:
    """Fallback: load from data/local_cache/<name>/data.parquet + meta.json."""
    import json
    cache_dir = DATA_DIR / "local_cache" / name
    if not (cache_dir / "data.parquet").exists():
        return None
    meta = json.loads((cache_dir / "meta.json").read_text())
    df = pd.read_parquet(cache_dir / "data.parquet")
    target_name = meta["target_name"]
    y = df[target_name].astype(str)
    X = df.drop(columns=[target_name])
    # Encode remaining categoricals
    for col in X.select_dtypes(include=["object", "category", "str"]).columns:
        X[col] = X[col].astype("category").cat.codes.astype(float)
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)
    # Three cached core datasets store their categorical columns as integer codes. Those codes are
    # what the schema generators saw (and what the formulas operate on), but the downstream RAW block
    # must treat them as categories, so they are cast to ``category`` dtype here: the evaluator then
    # one-hot encodes them, while the formula evaluator still exposes the numeric codes (every category
    # label parses as a number). Set DASEF_RAW_ONEHOT=0 to reproduce the pre-October-2026 behaviour.
    override = [c for c in LOCAL_CACHE_CATEGORICAL.get(name, []) if c in X.columns]
    if override and os.environ.get("DASEF_RAW_ONEHOT", "1") != "0":
        for col in override:
            X[col] = X[col].astype("int64").astype("category")
    else:
        override = []
    categorical, numeric = _infer_columns(X)
    logger.info("Loaded %s from local cache: %d rows × %d features (%d integer-coded categoricals one-hot)", name, len(X), X.shape[1], len(override))
    return LoadedDataset(name, X, y, categorical, numeric, target_name, onehot_override_columns=override)


def load_dataset(name: str) -> LoadedDataset:
    registry = load_datasets()
    config = registry.get(name)
    # Try local cache first (avoids OpenML network timeout when API is down)
    cached = _load_from_local_cache(name)
    if cached is not None:
        return cached
    return load_openml_dataset(config)


def stratified_cap(dataset: LoadedDataset, cap_rows: int | None, random_state: int = 42) -> LoadedDataset:
    if cap_rows is None or len(dataset.X) <= cap_rows:
        return dataset
    X_sub, _, y_sub, _ = train_test_split(
        dataset.X,
        dataset.y,
        train_size=cap_rows,
        stratify=dataset.y if dataset.y.nunique() > 1 else None,
        random_state=random_state,
    )
    return LoadedDataset(dataset.name, X_sub.reset_index(drop=True), y_sub.reset_index(drop=True), dataset.categorical_columns, dataset.numeric_columns, dataset.target_name, dataset.onehot_override_columns)


def schema_design_eval_split(
    dataset: LoadedDataset,
    schema_design_fraction: float,
    random_state: int = 42,
) -> tuple[LoadedDataset, LoadedDataset]:
    """Split rows into schema-design and evaluation subsets.

    The schema-design subset may be summarized for LLM schema generation. The
    evaluation subset should be the only data used for downstream CV metrics.
    """
    if not 0.0 < schema_design_fraction < 1.0:
        raise ValueError("schema_design_fraction must be between 0 and 1")
    stratify = dataset.y if dataset.y.nunique() > 1 else None
    X_design, X_eval, y_design, y_eval = train_test_split(
        dataset.X,
        dataset.y,
        train_size=schema_design_fraction,
        stratify=stratify,
        random_state=random_state,
    )
    design = LoadedDataset(
        dataset.name,
        X_design.reset_index(drop=True),
        y_design.reset_index(drop=True),
        dataset.categorical_columns,
        dataset.numeric_columns,
        dataset.target_name,
        dataset.onehot_override_columns,
    )
    evaluation = LoadedDataset(
        dataset.name,
        X_eval.reset_index(drop=True),
        y_eval.reset_index(drop=True),
        dataset.categorical_columns,
        dataset.numeric_columns,
        dataset.target_name,
        dataset.onehot_override_columns,
    )
    return design, evaluation


def dataset_summary(dataset: LoadedDataset, max_categories: int = 10) -> dict:
    X = dataset.X
    summary: dict = {
        "name": dataset.name,
        "rows": int(len(X)),
        "n_features": int(X.shape[1]),
        "target_name": dataset.target_name,
        "target_distribution": dataset.y.astype(str).value_counts(dropna=False).to_dict(),
        "columns": [],
    }
    for col in X.columns:
        item = {
            "name": col,
            "dtype": str(X[col].dtype),
            "missing_rate": float(X[col].isna().mean()),
        }
        if col in dataset.numeric_columns:
            s = pd.to_numeric(X[col], errors="coerce")
            item.update({
                "kind": "numeric",
                "mean": float(np.nanmean(s)) if s.notna().any() else None,
                "std": float(np.nanstd(s)) if s.notna().any() else None,
                "min": float(np.nanmin(s)) if s.notna().any() else None,
                "max": float(np.nanmax(s)) if s.notna().any() else None,
            })
        else:
            item.update({
                "kind": "categorical",
                "n_unique": int(X[col].nunique(dropna=True)),
                "top_values": X[col].astype(str).value_counts(dropna=False).head(max_categories).to_dict(),
            })
        summary["columns"].append(item)
    return summary


def save_dataset_snapshot(dataset: LoadedDataset, out_dir: Path = DATA_DIR / "processed") -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset.X.to_parquet(out_dir / f"{dataset.name}_X.parquet")
    dataset.y.to_frame().to_parquet(out_dir / f"{dataset.name}_y.parquet")
