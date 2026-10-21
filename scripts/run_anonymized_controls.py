#!/usr/bin/env python
"""Anonymized-column memorization control for Paper 1.

Memorization concern: because the 10 OpenML datasets are public, an LLM might be
retrieving *dataset-specific* feature recipes it has seen, rather than reasoning
from the schema. This control removes the two cues that enable such retrieval:

  1. the dataset identity (name -> generic token), and
  2. the semantic column names (age, capital_gain, ... -> x001, x002, ...).

Distributional structure (dtype, kind, mean/std/min/max, missing rate, target
class balance) is preserved, so the generator can still propose ratios /
thresholds / interactions from *statistics*, but cannot look up "the known good
features for adult_income".

For each (dataset, family) we generate an anonymized schema with the configured
generator, materialize its formulas on the (column-renamed) evaluation split, and
compute the same three contrasts used in the main paper:

  * direct        : raw            -> raw+formula
  * vs random     : raw+random     -> raw+formula     (dimensionality control)
  * semantic      : raw+permuted   -> raw+formula     (row-alignment control)

If the SEMANTIC contrast stays positive under anonymization, the formula signal
cannot be pure dataset-specific retrieval. Interpretation caveat (stated in the
paper): anonymization also removes *domain* semantics, so a shrunk effect is
expected; the post-cutoff benchmark is the complementary never-seen test.

No judgment features are generated. Schema-generation calls hit the configured
provider unless the prompt hash is already cached under --schema-root.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from dasef.config import load_llm_models
from dasef.datasets import (
    dataset_summary,
    load_dataset,
    schema_design_eval_split,
    stratified_cap,
)
from dasef.evaluate import evaluate_classifier
from dasef.features.augment import augment_with_formula
from dasef.features.random_control import augment_with_random_control
from dasef.schema_generation import generate_schema

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DATASETS = (
    "adult_income,bank_marketing,blood_transfusion,car_evaluation,credit_g,"
    "electricity,phoneme,pima_diabetes,qsar_biodegradation,spambase"
)
DEFAULT_FAMILIES = "linear_svm,tree,distance_knn"
DEFAULT_DOWNSTREAM = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def csv_arg(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def anonymize_summary(summary: dict[str, Any], idx: int) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (anonymized_summary, original->generic column mapping).

    Keeps every distributional field; replaces only identity/semantics.
    """
    mapping: dict[str, str] = {}
    new_cols = []
    for i, col in enumerate(summary["columns"], start=1):
        generic = f"x{i:03d}"
        mapping[col["name"]] = generic
        new_col = dict(col)
        new_col["name"] = generic
        new_cols.append(new_col)
    anon = dict(summary)
    anon["name"] = f"anon_dataset_{idx:02d}"
    anon["target_name"] = "target"
    anon["columns"] = new_cols
    return anon, mapping


def permute_formula_cols(X: pd.DataFrame, formula_cols: list[str], seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = X.copy()
    for col in formula_cols:
        out[col] = rng.permutation(out[col].values)
    return out


def all_metric_means(X: pd.DataFrame, y: pd.Series, model: str, seed: int) -> dict[str, float]:
    """One CV pass per (matrix, model); return the mean for every metric."""
    res = evaluate_classifier(X, y, model, n_splits=5, n_repeats=2, random_state=seed)
    return {m: float(np.mean(res.raw_scores[m])) for m in METRICS}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--datasets", default=DEFAULT_DATASETS)
    ap.add_argument("--families", default=DEFAULT_FAMILIES)
    ap.add_argument("--schema-model", default="gpt-5.5-pro")
    ap.add_argument("--schema-root", default="cache/schemas_anonymized")
    ap.add_argument("--out-dir", default="results/anonymized_control")
    ap.add_argument("--stats-out-dir", default="results/statistics/anonymized_control")
    ap.add_argument("--n-features", type=int, default=12)
    ap.add_argument("--cap", type=int, default=5000)
    ap.add_argument("--schema-design-fraction", type=float, default=0.3)
    ap.add_argument("--schema-design-seed", type=int, default=42)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force-regenerate", action="store_true")
    args = ap.parse_args()

    out_dir = ROOT / args.out_dir
    runs_dir = out_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    schema_root = ROOT / args.schema_root

    model_by_id = {m.id: m for m in load_llm_models().schema_generators}
    if args.schema_model not in model_by_id:
        raise KeyError(f"Unknown schema model {args.schema_model}")
    model_cfg = model_by_id[args.schema_model]

    per_run_rows: list[dict[str, Any]] = []
    datasets = csv_arg(args.datasets)
    for idx, dataset_name in enumerate(datasets):
        ds = load_dataset(dataset_name)
        if args.cap:
            ds = stratified_cap(ds, args.cap)
        design_ds, eval_ds = schema_design_eval_split(
            ds, args.schema_design_fraction, args.schema_design_seed
        )
        design_summary = dataset_summary(design_ds)
        anon_summary, mapping = anonymize_summary(design_summary, idx)

        # Evaluation features, columns renamed to the SAME generic mapping.
        X_eval = eval_ds.X.rename(columns=mapping).reset_index(drop=True)
        y_eval = eval_ds.y.reset_index(drop=True)

        for family in csv_arg(args.families):
            tag = f"{dataset_name}/{family}/{args.schema_model}"
            try:
                schema = generate_schema(
                    anon_summary,
                    family,
                    model_cfg,
                    n_features=args.n_features,
                    dry_run=False,
                    out_dir=schema_root,
                )
                formula_specs = schema.formula_features
                if not formula_specs:
                    print(f"  SKIP {tag}: no formula features", flush=True)
                    continue

                X_formula = augment_with_formula(X_eval, schema)
                formula_cols = [c for c in X_formula.columns if c not in X_eval.columns]
                if not formula_cols:
                    print(f"  SKIP {tag}: no materialized formula cols", flush=True)
                    continue
                X_random = augment_with_random_control(
                    X_eval, formula_specs, seed=args.seed, prefix="random_formula"
                )
                X_permuted = permute_formula_cols(X_formula, formula_cols, seed=args.seed)

                for model in DEFAULT_DOWNSTREAM:
                    sc_raw = all_metric_means(X_eval, y_eval, model, args.seed)
                    sc_formula = all_metric_means(X_formula, y_eval, model, args.seed)
                    sc_random = all_metric_means(X_random, y_eval, model, args.seed)
                    sc_permuted = all_metric_means(X_permuted, y_eval, model, args.seed)
                    for metric in METRICS:
                        s_raw, s_formula = sc_raw[metric], sc_formula[metric]
                        s_random, s_permuted = sc_random[metric], sc_permuted[metric]
                        per_run_rows.append({
                            "dataset": dataset_name,
                            "family": family,
                            "downstream_model": model,
                            "metric": metric,
                            "raw": s_raw,
                            "formula": s_formula,
                            "random_formula": s_random,
                            "permuted_formula": s_permuted,
                            "direct_delta": s_formula - s_raw,
                            "vs_random_delta": s_formula - s_random,
                            "semantic_delta": s_formula - s_permuted,
                            "n_formula_cols": len(formula_cols),
                        })
                print(f"  OK {tag} ({len(formula_cols)} formula cols)", flush=True)
                # Incremental checkpoint so partial results survive interruption.
                runs_dir.mkdir(parents=True, exist_ok=True)
                pd.DataFrame(per_run_rows).to_csv(runs_dir.parent / "anonymized_per_run.csv", index=False)
            except Exception as exc:  # noqa: BLE001
                print(f"  FAIL {tag}: {type(exc).__name__}: {exc}", flush=True)
                per_run_rows.append({
                    "dataset": dataset_name, "family": family,
                    "downstream_model": None, "metric": None,
                    "error": f"{type(exc).__name__}: {exc}",
                })

    df = pd.DataFrame(per_run_rows)
    df.to_csv(runs_dir.parent / "anonymized_per_run.csv", index=False)

    # Dataset-level aggregation: average families per (dataset, model, metric),
    # then Wilcoxon across datasets — same unit as the main paper.
    stats_dir = ROOT / args.stats_out_dir
    stats_dir.mkdir(parents=True, exist_ok=True)
    ok = df[df["downstream_model"].notna()].copy()
    lines = [
        "# Anonymized-Column Memorization Control",
        "",
        f"Schema generator: {args.schema_model}; column names -> x001..xNNN, "
        "dataset identity removed, distributional stats preserved.",
        "Dataset-level means (families averaged), Wilcoxon across datasets.",
        "",
    ]
    agg_rows = []
    for metric in METRICS:
        lines += [f"## {metric}", "",
                  "| Downstream | N | direct Δ | vs-random Δ | semantic Δ | semantic W/L | semantic p |",
                  "|---|---|---|---|---|---|---|"]
        for model in DEFAULT_DOWNSTREAM:
            sub = ok[(ok["metric"] == metric) & (ok["downstream_model"] == model)]
            if sub.empty:
                continue
            by_ds = sub.groupby("dataset")[["direct_delta", "vs_random_delta", "semantic_delta"]].mean()
            sem = by_ds["semantic_delta"].values
            n = len(sem)
            wins = int(np.sum(sem > 0))
            losses = int(np.sum(sem < 0))
            try:
                p = wilcoxon(sem).pvalue if n >= 1 and np.any(sem != 0) else float("nan")
            except Exception:
                p = float("nan")
            lines.append(
                f"| {model} | {n} | {by_ds['direct_delta'].mean():+.4f} | "
                f"{by_ds['vs_random_delta'].mean():+.4f} | {by_ds['semantic_delta'].mean():+.4f} | "
                f"{wins}/{losses} | {p:.4f} |"
            )
            agg_rows.append({
                "metric": metric, "downstream_model": model, "n_datasets": n,
                "direct_delta": by_ds["direct_delta"].mean(),
                "vs_random_delta": by_ds["vs_random_delta"].mean(),
                "semantic_delta": by_ds["semantic_delta"].mean(),
                "semantic_wins": wins, "semantic_losses": losses, "semantic_p": p,
            })
        lines.append("")
    pd.DataFrame(agg_rows).to_csv(stats_dir / "anonymized_summary.csv", index=False)
    (stats_dir / "anonymized_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {stats_dir / 'anonymized_summary.md'}")


if __name__ == "__main__":
    main()
