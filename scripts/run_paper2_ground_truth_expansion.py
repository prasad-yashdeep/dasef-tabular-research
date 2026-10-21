from __future__ import annotations

import json
import warnings
from itertools import combinations
from io import StringIO
from pathlib import Path

import numpy as np
import openml
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler


warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
INPUT = RESULTS / "paper2_expansion_datasets.csv"
OUT_EXPANSION = RESULTS / "paper2_ground_truth_expansion.csv"
OUT_FULL = RESULTS / "paper2_full_ground_truth.csv"
OUT_FAILURES = RESULTS / "paper2_ground_truth_expansion_failures.json"

CV = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)


EXISTING_17 = """dataset,n_features,lr_delta,rf_delta,knn_delta
adult_income,15,0.0188,-0.0039,0.0041
bank_marketing,17,0.0001,-0.0019,0.0078
blood_transfusion,5,-0.0011,-0.0025,-0.0015
car_evaluation,7,0.1038,-0.0002,-0.0061
credit_g,21,-0.0004,-0.0005,-0.0122
electricity,9,0.0030,-0.0116,-0.0058
phoneme,6,0.0361,-0.0006,-0.0073
pima_diabetes,9,0.0005,0.0035,0.0091
qsar_biodegradation,42,-0.0015,-0.0015,-0.0058
spambase,58,0.0054,-0.0020,0.0102
tic-tac-toe,9,0.2589,0.0040,-0.0123
monks-problems-1,6,0.2146,0.0000,-0.0709
ionosphere,34,0.0501,-0.0020,-0.0285
glass,9,0.0203,-0.0187,-0.0132
haberman,3,0.0202,0.0002,0.0146
balance-scale,4,0.0171,0.0208,0.0005
vehicle,18,0.0089,0.0067,-0.0036
"""


def _is_categorical(series: pd.Series) -> bool:
    return series.dtype == "object" or series.dtype.name == "category" or str(series.dtype) == "bool"


def _encode_frame(X: pd.DataFrame) -> tuple[np.ndarray, int, int, float]:
    X = X.copy()
    n_features = len(X.columns)
    categorical_cols = [col for col in X.columns if _is_categorical(X[col])]
    n_categorical = len(categorical_cols)

    for col in categorical_cols:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str).fillna("__missing__"))

    for col in X.columns:
        if col not in categorical_cols:
            X[col] = pd.to_numeric(X[col], errors="coerce")

    X_np = X.to_numpy(dtype=float)
    X_np = SimpleImputer(strategy="median").fit_transform(X_np)
    X_np = np.nan_to_num(X_np, nan=0.0, posinf=0.0, neginf=0.0)
    cat_ratio = n_categorical / n_features if n_features else 0.0
    return X_np, n_features, n_categorical, cat_ratio


def _generate_formula_features(
    X_raw: np.ndarray,
    max_formula_features: int = 200,
) -> tuple[np.ndarray, int]:
    interactions: list[np.ndarray] = []
    n_feat = X_raw.shape[1]

    def add(values: np.ndarray) -> bool:
        if len(interactions) >= max_formula_features:
            return False
        interactions.append(values)
        return len(interactions) < max_formula_features

    # Pairwise products first, matching the paper-2 proof-of-concept definition.
    for i in range(n_feat):
        for j in range(i + 1, n_feat):
            if not add(X_raw[:, i] * X_raw[:, j]):
                break
        if len(interactions) >= max_formula_features:
            break

    if n_feat <= 50:
        for i in range(n_feat):
            if not add(X_raw[:, i] ** 2):
                break

        # A small deterministic ratio set, guarded against zero denominators.
        for i in range(n_feat):
            for j in range(n_feat):
                if i == j:
                    continue
                denom = X_raw[:, j]
                values = np.divide(
                    X_raw[:, i],
                    denom,
                    out=np.zeros_like(X_raw[:, i], dtype=float),
                    where=np.abs(denom) > 1e-12,
                )
                values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
                if not add(values):
                    break
            if len(interactions) >= max_formula_features:
                break

    if n_feat <= 10:
        for i, j, k in combinations(range(n_feat), 3):
            if not add(X_raw[:, i] * X_raw[:, j] * X_raw[:, k]):
                break

    if interactions:
        return np.column_stack([X_raw] + interactions), len(interactions)
    return X_raw.copy(), 0


def _score_models(X: np.ndarray, y: np.ndarray, n_classes: int, formula: bool = False) -> dict[str, float]:
    scoring = "roc_auc_ovr_weighted" if n_classes > 2 else "roc_auc"
    X_scaled = StandardScaler().fit_transform(X)
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    models = {
        "lr": LogisticRegression(max_iter=3000 if formula else 2000, random_state=42),
        "rf": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "knn": KNeighborsClassifier(n_neighbors=5),
    }
    scores = {}
    for name, model in models.items():
        values = cross_val_score(
            model,
            X_scaled,
            y,
            cv=CV,
            scoring=scoring,
            n_jobs=-1,
            error_score="raise",
        )
        mean = float(values.mean())
        if not np.isfinite(mean):
            raise ValueError(f"{name} produced non-finite CV score")
        scores[name] = mean
    return scores


def evaluate_dataset(openml_id: int, name: str, max_rows: int = 10000) -> dict[str, float | int | str]:
    ds = openml.datasets.get_dataset(openml_id)
    X, y, _, _ = ds.get_data(target=ds.default_target_attribute)

    if len(X) > max_rows:
        idx = np.random.RandomState(42).choice(len(X), max_rows, replace=False)
        X = X.iloc[idx].reset_index(drop=True)
        y = pd.Series(y).iloc[idx].reset_index(drop=True)

    X_raw, n_features, n_categorical, cat_ratio = _encode_frame(X)
    y_enc = LabelEncoder().fit_transform(pd.Series(y).astype(str).fillna("__missing__"))
    n_classes = int(len(np.unique(y_enc)))
    if n_classes < 2:
        raise ValueError("target has fewer than two classes after encoding")

    raw = _score_models(X_raw, y_enc, n_classes, formula=False)
    X_formula, n_formula_features = _generate_formula_features(X_raw)
    formula = _score_models(X_formula, y_enc, n_classes, formula=True)

    return {
        "dataset": name,
        "openml_id": int(openml_id),
        "n_features": int(n_features),
        "n_instances": int(len(X_raw)),
        "n_classes": int(n_classes),
        "n_categorical": int(n_categorical),
        "cat_ratio": float(cat_ratio),
        "n_formula_features": int(n_formula_features),
        "lr_raw": raw["lr"],
        "rf_raw": raw["rf"],
        "knn_raw": raw["knn"],
        "lr_formula": formula["lr"],
        "rf_formula": formula["rf"],
        "knn_formula": formula["knn"],
        "lr_delta": formula["lr"] - raw["lr"],
        "rf_delta": formula["rf"] - raw["rf"],
        "knn_delta": formula["knn"] - raw["knn"],
        "rf_lr_gap_raw": raw["rf"] - raw["lr"],
    }


def write_full_ground_truth(expansion: pd.DataFrame) -> pd.DataFrame:
    existing = pd.read_csv(StringIO(EXISTING_17))
    for col in expansion.columns:
        if col not in existing.columns:
            existing[col] = np.nan
    full = pd.concat([existing[expansion.columns], expansion], ignore_index=True)
    full.to_csv(OUT_FULL, index=False)
    return full


def print_summary(results: pd.DataFrame) -> None:
    if results.empty:
        print("No successful datasets.")
        return

    summary_cols = [
        "dataset",
        "openml_id",
        "n_features",
        "n_instances",
        "n_classes",
        "cat_ratio",
        "lr_delta",
        "rf_delta",
        "knn_delta",
        "rf_lr_gap_raw",
    ]
    print("\nResults:")
    print(results[summary_cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    lr_benefit_count = int((results["lr_delta"] > 0.02).sum())
    cat_corr = float(results["cat_ratio"].corr(results["lr_delta"]))
    gap_corr = float(results["rf_lr_gap_raw"].corr(results["lr_delta"]))

    predictors = {
        "cat_ratio": abs(cat_corr),
        "rf_lr_gap_raw": abs(gap_corr),
        "n_features": abs(float(results["n_features"].corr(results["lr_delta"]))),
        "n_categorical": abs(float(results["n_categorical"].corr(results["lr_delta"]))),
    }
    best_predictor = max(predictors, key=lambda key: -1 if np.isnan(predictors[key]) else predictors[key])

    print("\nKey finding:")
    print(f"- LR benefit > 0.02: {lr_benefit_count}/{len(results)} datasets")
    print(f"- corr(cat_ratio, lr_delta): {cat_corr:.4f}")
    print(f"- corr(rf_lr_gap_raw, lr_delta): {gap_corr:.4f}")
    print(f"- best single predictor of DASEF benefit: {best_predictor} (|r|={predictors[best_predictor]:.4f})")


def main() -> None:
    inputs = pd.read_csv(INPUT)
    rows = []
    failures = []

    for idx, row in inputs.iterrows():
        openml_id = int(row["openml_id"])
        name = str(row["name"])
        print(f"[{idx + 1}/{len(inputs)}] {name} (OpenML {openml_id})", flush=True)
        try:
            result = evaluate_dataset(openml_id, name)
        except Exception as exc:
            msg = str(exc)
            print(f"  FAILED {name} (ID={openml_id}): {msg[:160]}", flush=True)
            failures.append({"dataset": name, "openml_id": openml_id, "error": msg})
            continue

        rows.append(result)
        pd.DataFrame(rows).to_csv(OUT_EXPANSION, index=False)
        print(
            "  ok "
            f"lr_delta={result['lr_delta']:.4f} "
            f"rf_delta={result['rf_delta']:.4f} "
            f"knn_delta={result['knn_delta']:.4f}",
            flush=True,
        )

    results = pd.DataFrame(rows)
    results.to_csv(OUT_EXPANSION, index=False)
    OUT_FAILURES.write_text(json.dumps(failures, indent=2), encoding="utf-8")
    write_full_ground_truth(results)

    print(f"\nSaved expansion results: {OUT_EXPANSION}")
    print(f"Saved full ground truth: {OUT_FULL}")
    if failures:
        print(f"Saved failures: {OUT_FAILURES} ({len(failures)} failures)")
    print_summary(results)


if __name__ == "__main__":
    main()
