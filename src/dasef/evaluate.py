from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.svm import SVC

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvalResult:
    model_name: str
    metrics: dict[str, float]
    raw_scores: dict[str, list[float]]


def infer_column_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = [c for c in X.columns if is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in numeric]
    return categorical, numeric


def build_preprocessor(X: pd.DataFrame, scale_numeric: bool = False) -> ColumnTransformer:
    cat_cols, num_cols = infer_column_types(X)
    num_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler()))
    num_pipe = Pipeline(num_steps)
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", num_pipe, num_cols),
        ("cat", cat_pipe, cat_cols),
    ], remainder="drop")


def classifier_for(name: str):
    if name == "logistic_regression":
        return LogisticRegression(max_iter=2000, class_weight="balanced")
    if name == "random_forest":
        return RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1, class_weight="balanced_subsample")
    if name == "knn":
        return KNeighborsClassifier(n_neighbors=15)
    if name == "linear_svm":
        return SVC(kernel="linear", probability=True, class_weight="balanced")
    if name == "rbf_svm":
        return SVC(kernel="rbf", probability=True, class_weight="balanced")
    if name == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss", n_jobs=-1, random_state=42)
    if name == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(n_estimators=300, learning_rate=0.05, random_state=42, n_jobs=-1, verbose=-1)
    if name == "catboost":
        from catboost import CatBoostClassifier
        return CatBoostClassifier(iterations=300, learning_rate=0.05, depth=6, verbose=False, random_seed=42)
    raise ValueError(f"Unknown classifier: {name}")


def evaluate_classifier(X: pd.DataFrame, y: pd.Series, model_name: str, n_splits: int = 5, n_repeats: int = 2, random_state: int = 42) -> EvalResult:
    y_encoded = pd.Series(LabelEncoder().fit_transform(y.astype(str)), index=y.index, name=y.name)
    scale = model_name in {"logistic_regression", "knn", "linear_svm", "rbf_svm"}
    pipe = Pipeline([
        ("preprocess", build_preprocessor(X, scale_numeric=scale)),
        ("model", classifier_for(model_name)),
    ])
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    scoring = {"accuracy": "accuracy", "balanced_accuracy": "balanced_accuracy", "f1_macro": "f1_macro", "roc_auc_ovr": "roc_auc_ovr"}
    scores = cross_validate(pipe, X, y_encoded, cv=cv, scoring=scoring, n_jobs=1, error_score=np.nan)
    raw = {k.replace("test_", ""): [float(v) for v in vals] for k, vals in scores.items() if k.startswith("test_")}
    metrics = {k: float(np.nanmean(v)) for k, v in raw.items()}
    logger.info("Evaluation done model=%s metrics=%s", model_name, metrics)
    return EvalResult(model_name, metrics, raw)
