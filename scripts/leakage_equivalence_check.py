#!/usr/bin/env python3
"""Compare prospective vs cached-schema formula effects."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROSPECTIVE_DIR = ROOT / "results" / "full_suite_prospective"
CACHED_DIR = ROOT / "results" / "judgments"
OUT = ROOT / "results" / "statistics" / "dataset_level" / "leakage_equivalence.md"
MATRIX_BASE = "raw"
MATRIX_CAND = "raw_plus_formula"
METRICS = ["roc_auc_ovr", "balanced_accuracy"]
MODELS = ["logistic_regression", "random_forest", "knn"]


def mean_fold_delta(result: dict, model: str, metric: str) -> float | None:
    evals = {e.get("matrix_name"): e for e in result.get("evaluations", [])}
    if MATRIX_BASE not in evals or MATRIX_CAND not in evals:
        return None
    base = evals[MATRIX_BASE].get("raw_scores", {}).get(model, {}).get(metric)
    cand = evals[MATRIX_CAND].get("raw_scores", {}).get(model, {}).get(metric)
    if not base or not cand:
        return None
    b = np.asarray(base, dtype=float)
    c = np.asarray(cand, dtype=float)
    mask = np.isfinite(b) & np.isfinite(c)
    if mask.sum() == 0:
        return None
    return float(np.mean(c[mask] - b[mask]))


def collect(root: Path, label: str) -> pd.DataFrame:
    rows = []
    for path in sorted(root.rglob("results.json")):
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        dataset = result.get("dataset")
        if not dataset:
            continue
        for model in MODELS:
            for metric in METRICS:
                delta = mean_fold_delta(result, model, metric)
                if delta is not None:
                    rows.append(
                        {
                            "source": label,
                            "dataset": dataset,
                            "downstream_model": model,
                            "metric": metric,
                            "delta": delta,
                            "path": str(path.relative_to(ROOT)),
                        }
                    )
    return pd.DataFrame(rows)


def main() -> None:
    prospective = collect(PROSPECTIVE_DIR, "prospective")
    cached = collect(CACHED_DIR, "cached_full_data")
    if prospective.empty or cached.empty:
        raise SystemExit("Missing prospective or cached rows; cannot compare leakage equivalence.")

    all_rows = pd.concat([prospective, cached], ignore_index=True)
    grouped = (
        all_rows.groupby(["source", "dataset", "downstream_model", "metric"], as_index=False)
        .agg(mean_delta=("delta", "mean"), std_delta=("delta", "std"), n_runs=("delta", "count"))
    )
    wide = grouped.pivot_table(
        index=["dataset", "downstream_model", "metric"],
        columns="source",
        values=["mean_delta", "n_runs"],
        aggfunc="first",
    )
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide = wide.dropna(subset=["mean_delta_prospective", "mean_delta_cached_full_data"])
    wide["difference_cached_minus_prospective"] = (
        wide["mean_delta_cached_full_data"] - wide["mean_delta_prospective"]
    )
    wide["abs_difference"] = wide["difference_cached_minus_prospective"].abs()

    summary = (
        wide.groupby(["metric", "downstream_model"], as_index=False)
        .agg(
            n_datasets=("dataset", "nunique"),
            prospective_mean_delta=("mean_delta_prospective", "mean"),
            cached_mean_delta=("mean_delta_cached_full_data", "mean"),
            mean_difference_cached_minus_prospective=("difference_cached_minus_prospective", "mean"),
            mean_abs_difference=("abs_difference", "mean"),
        )
        .sort_values(["metric", "downstream_model"])
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wide.to_csv(OUT.with_suffix(".csv"), index=False)

    lines = [
        "# Leakage Equivalence Check",
        "",
        "Question: did cached full-data schema generation inflate `raw -> raw_plus_formula` effects relative to prospective schema generation?",
        "",
        f"- Prospective result files: {prospective['path'].nunique()}",
        f"- Cached judgment result files: {cached['path'].nunique()}",
        f"- Overlapping dataset/model/metric cells: {len(wide)}",
        "",
        "## Summary By Metric And Downstream Model",
        "",
        summary.to_markdown(index=False, floatfmt=".5f"),
        "",
        "## Dataset-Level Comparison",
        "",
        wide.sort_values(["metric", "downstream_model", "dataset"]).to_markdown(index=False, floatfmt=".5f"),
        "",
        "## Interpretation",
        "",
    ]
    mean_abs = float(wide["abs_difference"].mean()) if not wide.empty else float("nan")
    mean_signed = float(wide["difference_cached_minus_prospective"].mean()) if not wide.empty else float("nan")
    if np.isfinite(mean_abs) and mean_abs < 0.02:
        lines.append(
            f"Mean absolute difference is {mean_abs:.4f} with signed cached-minus-prospective difference {mean_signed:+.4f}; "
            "the two schema-generation modes look broadly similar at this aggregation level."
        )
    else:
        lines.append(
            f"Mean absolute difference is {mean_abs:.4f} with signed cached-minus-prospective difference {mean_signed:+.4f}; "
            "inspect the dataset-level rows before claiming leakage equivalence."
        )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT.with_suffix('.csv')}")


if __name__ == "__main__":
    main()
