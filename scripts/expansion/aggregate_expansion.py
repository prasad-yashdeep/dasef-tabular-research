"""Dataset-level aggregation of the offline 34-dataset expansion (GPT-5.5 Pro, linear/SVM schemas).

Inputs: the permuted-control run_level_scores.csv files written by permuted_control_capped.py
for the raw-name and safe-name batches. Each row holds, per (dataset, model, metric), the
five treatment scores: raw, raw+formula, raw+random-formula, raw+random-all, raw+permuted-formula.

Outputs (in --out-dir): dataset_level.csv (one row per dataset/model/metric with all deltas),
summary.csv and summary.md (mean delta, W/L, exact two-sided Wilcoxon p, Cliff's delta,
percentile-bootstrap CI over datasets) for the contrasts
  semantic  = formula - permuted
  direct    = formula - raw
  vs_random = formula - random_formula
  random_formula_vs_raw, random_all_vs_raw (dimensionality controls)
for the full set and for the subset excluding thin schemas (< --min-formulas usable formulas).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

CONTRASTS = {
    "semantic": ("raw_plus_formula", "raw_plus_permuted_formula"),
    "direct": ("raw_plus_formula", "raw"),
    "vs_random": ("raw_plus_formula", "raw_plus_random_formula"),
    "random_formula_vs_raw": ("raw_plus_random_formula", "raw"),
    "random_all_vs_raw": ("raw_plus_random_all", "raw"),
}
MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def exact_wilcoxon(x: np.ndarray) -> float:
    x = x[x != 0]
    if len(x) == 0:
        return 1.0
    try:
        return float(wilcoxon(x, alternative="two-sided", method="exact").pvalue)
    except Exception:
        return float(wilcoxon(x, alternative="two-sided").pvalue)


def boot_ci(x: np.ndarray, n: int = 10000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(df: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        for model in MODELS:
            sub = df[(df.metric == metric) & (df.model == model)]
            for name, (a, b) in CONTRASTS.items():
                x = (sub[a] - sub[b]).to_numpy(dtype=float)
                lo, hi = boot_ci(x)
                rows.append({
                    "subset": label, "metric": metric, "model": model, "contrast": name,
                    "n_datasets": len(x), "mean_delta": x.mean(), "median_delta": float(np.median(x)),
                    "wins": int((x > 0).sum()), "losses": int((x < 0).sum()), "ties": int((x == 0).sum()),
                    "p_wilcoxon_exact": exact_wilcoxon(x),
                    "cliffs_delta": ((x > 0).sum() - (x < 0).sum()) / len(x),
                    "ci95_lo": lo, "ci95_hi": hi,
                })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-level", nargs="+", required=True, help="run_level_scores.csv files")
    ap.add_argument("--schema-inventory", required=True, help="schema_inventory.csv with usable formula counts")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--min-formulas", type=int, default=5)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.concat([pd.read_csv(f) for f in args.run_level], ignore_index=True)
    # one run per dataset expected; average if several
    per = df.groupby(["dataset", "model", "metric"], as_index=False)[
        ["raw", "raw_plus_formula", "raw_plus_random_formula", "raw_plus_random_all", "raw_plus_permuted_formula"]
    ].mean()
    for name, (a, b) in CONTRASTS.items():
        per[name] = per[a] - per[b]
    per.to_csv(out / "dataset_level.csv", index=False)

    inv = pd.read_csv(args.schema_inventory)
    thin = set()
    if "n_formula_materialized_nondegenerate" in inv.columns:
        gpt = inv[inv.generator.astype(str).str.contains("gpt", case=False)] if "generator" in inv.columns else inv
        thin = set(gpt[gpt.n_formula_materialized_nondegenerate < args.min_formulas].dataset.astype(str))
    datasets = sorted(per.dataset.unique())
    kept = [d for d in datasets if d not in thin]
    summ = pd.concat([
        summarize(per, f"all (N={len(datasets)})"),
        summarize(per[per.dataset.isin(kept)], f"schemas with >= {args.min_formulas} usable formulas (N={len(kept)})"),
    ], ignore_index=True)
    summ.to_csv(out / "summary.csv", index=False)

    lines = ["# Offline expansion: dataset-level summary", "",
             f"Datasets: {len(datasets)}; thin schemas excluded in the second block: {sorted(thin & set(datasets))}", ""]
    for label in summ.subset.unique():
        lines += [f"## {label}", ""]
        for metric in METRICS:
            lines += [f"### {metric}", "", "| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | Cliff | 95% CI |", "|---|---|---|---|---|---|---|---|---|"]
            s = summ[(summ.subset == label) & (summ.metric == metric)]
            for _, r in s.iterrows():
                lines.append(f"| {r.model} | {r.contrast} | {r.n_datasets} | {r.mean_delta:+.4f} | {r.median_delta:+.4f} | {r.wins}/{r.losses}/{r.ties} | {r.p_wilcoxon_exact:.2g} | {r.cliffs_delta:+.2f} | [{r.ci95_lo:+.4f}, {r.ci95_hi:+.4f}] |")
            lines.append("")
    (out / "summary.md").write_text("\n".join(lines))
    (out / "datasets.json").write_text(json.dumps({"all": datasets, "kept": kept, "thin": sorted(thin & set(datasets))}, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
