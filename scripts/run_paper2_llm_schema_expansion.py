from __future__ import annotations

import glob
import json
import re
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dasef.config import load_llm_models  # noqa: E402
from dasef.datasets import LoadedDataset, dataset_summary, load_dataset, schema_design_eval_split  # noqa: E402
from dasef.features.formula import materialize_formula_features  # noqa: E402
from dasef.io_utils import read_json  # noqa: E402
from dasef.schema import SchemaSpec  # noqa: E402
from dasef.schema_generation import generate_schema  # noqa: E402
from dasef.settings import ENV_PATH  # noqa: F401,E402 - loads project-local .env

warnings.filterwarnings("ignore")

INPUT = ROOT / "results" / "paper2_expansion_datasets.csv"
PROXY = ROOT / "results" / "paper2_full_ground_truth.csv"
OUT_LLM = ROOT / "results" / "paper2_llm_generated_ground_truth.csv"
OUT_COMPARISON = ROOT / "results" / "paper2_proxy_vs_llm_comparison.csv"
OUT_FAILURES = ROOT / "results" / "paper2_llm_generated_ground_truth_failures.json"

FAMILY = "linear_svm"
GENERATORS = ("gpt-5.5-pro", "gemini-3.1-pro-preview")
MAX_EVAL_ROWS = 10_000
CV = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)


def snake_name(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_]+", "_", str(value).strip())
    text = re.sub(r"_+", "_", text).strip("_").lower()
    if not text:
        text = "col"
    return text


def safe_identifier(value: str) -> str:
    text = snake_name(value)
    if text[0].isdigit():
        text = f"f_{text}"
    return text


def safe_columns(dataset: LoadedDataset) -> LoadedDataset:
    mapping: dict[str, str] = {}
    seen: set[str] = set()
    for col in dataset.X.columns:
        base = safe_identifier(str(col))
        name = base
        suffix = 2
        while name in seen:
            name = f"{base}_{suffix}"
            suffix += 1
        seen.add(name)
        mapping[col] = name

    X = dataset.X.rename(columns=mapping).copy()
    categorical = [mapping[c] for c in dataset.categorical_columns if c in mapping]
    numeric = [mapping[c] for c in dataset.numeric_columns if c in mapping]
    return LoadedDataset(dataset.name, X, dataset.y.reset_index(drop=True), categorical, numeric, dataset.target_name)


def latest_schema_path(dataset: str, model_id: str) -> Path | None:
    paths = [
        Path(p)
        for p in glob.glob(str(ROOT / "cache" / "schemas" / dataset / FAMILY / model_id / "schema_*.json"))
        if not p.endswith(".raw.json") and not p.endswith(".prompt.json")
    ]
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


def load_cached_schema(dataset: str, model_id: str) -> SchemaSpec | None:
    path = latest_schema_path(dataset, model_id)
    if path is None:
        return None
    return SchemaSpec.model_validate(read_json(path))


def salvage_schema_from_raw(dataset: str, model_id: str) -> SchemaSpec | None:
    raw_paths = [
        Path(p)
        for p in glob.glob(str(ROOT / "cache" / "schemas" / dataset / FAMILY / model_id / "schema_*.raw.json"))
    ]
    if not raw_paths:
        return None
    raw_path = max(raw_paths, key=lambda p: p.stat().st_mtime)
    raw = read_json(raw_path)
    text = raw.get("text") or ""
    if not text.strip():
        return None

    decoder = json.JSONDecoder()
    features: list[dict] = []
    marker = '"features"'
    pos = text.find(marker)
    if pos < 0:
        return None
    pos = text.find("[", pos)
    if pos < 0:
        return None
    pos += 1
    while pos < len(text):
        while pos < len(text) and text[pos] in " \n\r\t,":
            pos += 1
        if pos >= len(text) or text[pos] == "]":
            break
        if text[pos] != "{":
            pos += 1
            continue
        try:
            obj, end = decoder.raw_decode(text[pos:])
        except json.JSONDecodeError:
            break
        if isinstance(obj, dict):
            features.append(obj)
        pos += end

    if not features:
        return None
    data = {
        "dataset_name": dataset,
        "model_family": FAMILY,
        "schema_generator": model_id,
        "schema_version": "v1",
        "features": features,
        "prompt_hash": raw.get("prompt_hash"),
        "metadata": {"salvaged_from_partial_raw": str(raw_path), "n_salvaged_features": len(features)},
    }
    try:
        schema = SchemaSpec.model_validate(data)
    except Exception:
        return None
    schema_path = raw_path.with_suffix("").with_suffix(".json")
    schema_path.write_text(schema.model_dump_json(indent=2), encoding="utf-8")
    print(f"  salvaged {len(schema.features)} complete features from partial raw response: {schema_path}", flush=True)
    return schema


def generate_or_load_schema(
    dataset_name: str,
    summary: dict,
    model_id: str,
    model_cfg,
    ordinal: int,
    total_datasets: int,
) -> tuple[SchemaSpec | None, bool, str | None]:
    cached = load_cached_schema(dataset_name, model_id)
    if cached is not None:
        print(f"[{ordinal}/{total_datasets}] cached schema for {dataset_name} with {model_id}", flush=True)
        return cached, False, None
    salvaged = salvage_schema_from_raw(dataset_name, model_id)
    if salvaged is not None:
        print(f"[{ordinal}/{total_datasets}] salvaged cached raw schema for {dataset_name} with {model_id}", flush=True)
        return salvaged, False, None

    for attempt in range(1, 3):
        print(
            f"[{ordinal}/{total_datasets}] generating schema for {dataset_name} with {model_id} "
            f"(attempt {attempt}/2)...",
            flush=True,
        )
        try:
            schema = generate_schema(summary, FAMILY, model_cfg, n_features=12)
            return schema, True, None
        except Exception as exc:
            error = str(exc)
            print(f"  schema generation failed: {error[:240]}", flush=True)
            salvaged = salvage_schema_from_raw(dataset_name, model_id)
            if salvaged is not None:
                return salvaged, True, None
            if attempt == 1:
                time.sleep(3)
    return None, False, error


def make_preprocessor(X: pd.DataFrame, scale_numeric: bool) -> ColumnTransformer:
    numeric = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in numeric]
    num_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler()))
    return ColumnTransformer(
        [
            ("num", Pipeline(num_steps), numeric),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
        ],
        remainder="drop",
    )


def score_models(X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    y_encoded = LabelEncoder().fit_transform(y.astype(str).fillna("__missing__"))
    n_classes = len(np.unique(y_encoded))
    if n_classes < 2:
        raise ValueError("target has fewer than two classes")
    scoring = "roc_auc_ovr_weighted" if n_classes > 2 else "roc_auc"
    models = {
        "lr": LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42),
        "rf": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight="balanced_subsample"),
        "knn": KNeighborsClassifier(n_neighbors=5),
    }
    scores: dict[str, float] = {}
    for short, model in models.items():
        scale = short in {"lr", "knn"}
        pipe = Pipeline([("preprocess", make_preprocessor(X, scale)), ("model", model)])
        values = cross_val_score(pipe, X, y_encoded, cv=CV, scoring=scoring, n_jobs=-1, error_score=np.nan)
        mean = float(np.nanmean(values))
        if not np.isfinite(mean):
            raise ValueError(f"{short} produced non-finite CV scores")
        scores[short] = mean
    return scores


def evaluation_subset(dataset: LoadedDataset) -> LoadedDataset:
    if len(dataset.X) <= MAX_EVAL_ROWS:
        return dataset
    stratify = dataset.y if dataset.y.nunique() > 1 else None
    X_sub, _, y_sub, _ = train_test_split(
        dataset.X,
        dataset.y,
        train_size=MAX_EVAL_ROWS,
        stratify=stratify,
        random_state=42,
    )
    return LoadedDataset(
        dataset.name,
        X_sub.reset_index(drop=True),
        y_sub.reset_index(drop=True),
        dataset.categorical_columns,
        dataset.numeric_columns,
        dataset.target_name,
    )


def evaluate_schema(dataset_eval: LoadedDataset, schema: SchemaSpec) -> dict[str, float | int]:
    eval_ds = evaluation_subset(dataset_eval)
    X_raw = eval_ds.X.reset_index(drop=True).copy()
    y = eval_ds.y.reset_index(drop=True)
    raw = score_models(X_raw, y)

    formula_features = materialize_formula_features(X_raw, schema)
    formula_features = formula_features.replace([np.inf, -np.inf], np.nan)
    X_formula = pd.concat([X_raw, formula_features.add_prefix("formula_")], axis=1)
    formula = score_models(X_formula, y)

    return {
        "n_instances": int(len(X_raw)),
        "n_formula_features": int(len(schema.formula_features)),
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


def compare_with_proxy(llm_results: pd.DataFrame) -> pd.DataFrame:
    proxy = pd.read_csv(PROXY)
    proxy["openml_id"] = pd.to_numeric(proxy["openml_id"], errors="coerce")
    merged = llm_results.merge(
        proxy[["dataset", "openml_id", "lr_delta", "rf_delta", "knn_delta"]].rename(
            columns={
                "dataset": "proxy_dataset",
                "lr_delta": "proxy_lr_delta",
                "rf_delta": "proxy_rf_delta",
                "knn_delta": "proxy_knn_delta",
            }
        ),
        on="openml_id",
        how="left",
    )
    merged["llm_minus_proxy_lr_delta"] = merged["lr_delta"] - merged["proxy_lr_delta"]
    merged["llm_beats_proxy_lr"] = merged["llm_minus_proxy_lr_delta"] > 0
    return merged


def verdict(corr: float, mean_abs_gap: float) -> str:
    if not np.isfinite(corr):
        return "Inconclusive: not enough overlapping proxy/LLM deltas."
    if corr >= 0.5 and mean_abs_gap <= 0.03:
        return "Yes, directionally reasonable."
    if corr >= 0.25:
        return "Partly: useful as a rough directional proxy, but noisy."
    return "Weak: the brute-force proxy is not a reliable approximation for these LLM schemas."


def main() -> None:
    rows = pd.read_csv(INPUT)
    model_registry = load_llm_models()
    model_cfgs = {m.id: m for m in model_registry.schema_generators if m.id in GENERATORS}
    missing = [m for m in GENERATORS if m not in model_cfgs]
    if missing:
        raise ValueError(f"Missing model configs: {missing}")

    results: list[dict] = []
    failures: list[dict] = []
    generated_count = 0
    schema_success_count = 0

    for idx, input_row in rows.iterrows():
        dataset_name = snake_name(str(input_row["name"]))
        display_name = str(input_row["name"])
        openml_id = int(input_row["openml_id"])
        ordinal = idx + 1
        try:
            dataset = safe_columns(load_dataset(dataset_name))
            design, evaluation = schema_design_eval_split(dataset, 0.3, 42)
            summary = dataset_summary(design)
        except Exception as exc:
            print(f"[{ordinal}/{len(rows)}] skipping {dataset_name}: load failed: {str(exc)[:240]}", flush=True)
            failures.append({"dataset": dataset_name, "openml_id": openml_id, "stage": "load", "error": str(exc)})
            continue

        for generator in GENERATORS:
            schema, generated, error = generate_or_load_schema(
                dataset_name,
                summary,
                generator,
                model_cfgs[generator],
                ordinal,
                len(rows),
            )
            if schema is None:
                failures.append(
                    {"dataset": dataset_name, "openml_id": openml_id, "schema_generator": generator, "stage": "schema", "error": error}
                )
                continue
            schema_success_count += 1
            generated_count += int(generated)

            try:
                metrics = evaluate_schema(evaluation, schema)
            except Exception as exc:
                print(f"  evaluation failed for {dataset_name}/{generator}: {str(exc)[:240]}", flush=True)
                failures.append(
                    {"dataset": dataset_name, "openml_id": openml_id, "schema_generator": generator, "stage": "evaluation", "error": str(exc)}
                )
                continue

            result = {
                "dataset": dataset_name,
                "source_dataset": display_name,
                "openml_id": openml_id,
                "n_features": int(dataset.X.shape[1]),
                "n_classes": int(dataset.y.astype(str).nunique()),
                "cat_ratio": float(len(dataset.categorical_columns) / dataset.X.shape[1]) if dataset.X.shape[1] else 0.0,
                "schema_generator": generator,
                **metrics,
            }
            results.append(result)
            pd.DataFrame(results).to_csv(OUT_LLM, index=False)
            print(
                f"  ok {dataset_name}/{generator}: "
                f"n_formula={result['n_formula_features']} lr_delta={result['lr_delta']:.4f} "
                f"rf_delta={result['rf_delta']:.4f} knn_delta={result['knn_delta']:.4f}",
                flush=True,
            )

    result_df = pd.DataFrame(results)
    result_df.to_csv(OUT_LLM, index=False)
    OUT_FAILURES.write_text(json.dumps(failures, indent=2), encoding="utf-8")

    if result_df.empty:
        print("\nNo successful LLM schema evaluations.")
        print(f"Saved failures: {OUT_FAILURES}")
        return

    comparison = compare_with_proxy(result_df)
    comparison.to_csv(OUT_COMPARISON, index=False)
    overlap = comparison.dropna(subset=["proxy_lr_delta", "lr_delta"]).copy()
    corr = float(overlap["lr_delta"].corr(overlap["proxy_lr_delta"])) if len(overlap) >= 2 else float("nan")
    mean_llm_lr = float(result_df["lr_delta"].mean())
    mean_proxy_lr = float(overlap["proxy_lr_delta"].mean()) if not overlap.empty else float("nan")
    mean_abs_gap = float((overlap["lr_delta"] - overlap["proxy_lr_delta"]).abs().mean()) if not overlap.empty else float("nan")
    llm_beats = comparison[comparison["llm_beats_proxy_lr"]].sort_values("llm_minus_proxy_lr_delta", ascending=False)
    proxy_beats = comparison[~comparison["llm_beats_proxy_lr"].fillna(False)].sort_values("llm_minus_proxy_lr_delta", ascending=True)

    print("\nSummary")
    print(f"1. Schemas generated successfully: {schema_success_count}/{len(rows) * len(GENERATORS)} ({generated_count} new, rest cached)")
    print(f"2. Mean LR delta from LLM formulas: {mean_llm_lr:.4f}; brute-force proxy overlap mean: {mean_proxy_lr:.4f}")
    print(f"3. Correlation between LLM and proxy LR deltas: {corr:.4f}")
    print("4. Top 5 datasets where LLM formulas beat brute-force:")
    if llm_beats.empty:
        print("   none")
    else:
        for _, row in llm_beats.head(5).iterrows():
            print(
                f"   {row['dataset']} / {row['schema_generator']}: "
                f"LLM {row['lr_delta']:.4f}, proxy {row['proxy_lr_delta']:.4f}, gap {row['llm_minus_proxy_lr_delta']:.4f}"
            )
    print("5. Top 5 datasets where brute-force beats LLM:")
    if proxy_beats.empty:
        print("   none")
    else:
        for _, row in proxy_beats.head(5).iterrows():
            print(
                f"   {row['dataset']} / {row['schema_generator']}: "
                f"LLM {row['lr_delta']:.4f}, proxy {row['proxy_lr_delta']:.4f}, gap {row['llm_minus_proxy_lr_delta']:.4f}"
            )
    print(f"Verdict: {verdict(corr, mean_abs_gap)}")
    print(f"\nSaved LLM results: {OUT_LLM}")
    print(f"Saved comparison: {OUT_COMPARISON}")
    if failures:
        print(f"Saved failures: {OUT_FAILURES} ({len(failures)} failures)")


if __name__ == "__main__":
    main()
