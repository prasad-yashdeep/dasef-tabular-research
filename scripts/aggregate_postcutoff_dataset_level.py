#!/usr/bin/env python
"""Dataset-level aggregation of the post-cutoff never-seen runs.

For each downstream model and metric, average run-level deltas within each
dataset, then run Wilcoxon across datasets (the publication unit). Reports:
  semantic  = raw+formula  -  raw+random_formula  (formula beats matched noise)
  direct    = raw+formula  -  raw
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

RUNS = Path("results/postcutoff_real/runs")
OUT = Path("results/statistics/postcutoff_real")
MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def mean_score(ev, matrix, model, metric):
    rs = ev.get(matrix, {}).get("raw_scores", {}).get(model, {}).get(metric)
    return float(np.mean(rs)) if rs else None


def main() -> None:
    # dataset -> model -> metric -> {semantic:[], direct:[]}
    acc = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"semantic": [], "direct": []})))
    n_runs = 0
    for p in sorted(RUNS.glob("*/results.json")):
        d = json.loads(p.read_text())
        ds = d["dataset"]
        ev = {e["matrix_name"]: e for e in d.get("evaluations", [])}
        if not {"raw", "raw_plus_formula", "raw_plus_random_formula"} <= set(ev):
            continue
        n_runs += 1
        for model in MODELS:
            for metric in METRICS:
                f = mean_score(ev, "raw_plus_formula", model, metric)
                r = mean_score(ev, "raw", model, metric)
                rf = mean_score(ev, "raw_plus_random_formula", model, metric)
                if None in (f, r, rf):
                    continue
                acc[ds][model][metric]["semantic"].append(f - rf)
                acc[ds][model][metric]["direct"].append(f - r)

    datasets = sorted(acc.keys())
    rows = []
    lines = ["# Post-Cutoff Never-Seen: Dataset-Level Aggregation", "",
             f"Runs aggregated: {n_runs}; datasets: {len(datasets)} ({', '.join(datasets)}).",
             "semantic = formula - random_formula; direct = formula - raw. Wilcoxon across datasets.", ""]
    for metric in METRICS:
        lines += [f"## {metric}", "",
                  "| Model | contrast | N | mean Δ | W/L | p |", "|---|---|---|---|---|---|"]
        for model in MODELS:
            for contrast in ("semantic", "direct"):
                vals = [np.mean(acc[ds][model][metric][contrast]) for ds in datasets
                        if acc[ds][model][metric][contrast]]
                vals = np.array(vals)
                n = len(vals)
                if n == 0:
                    continue
                wins = int((vals > 0).sum())
                losses = int((vals < 0).sum())
                try:
                    p = wilcoxon(vals).pvalue if np.any(vals != 0) else float("nan")
                except Exception:
                    p = float("nan")
                lines.append(f"| {model} | {contrast} | {n} | {vals.mean():+.4f} | {wins}/{losses} | {p:.4f} |")
                rows.append({"metric": metric, "model": model, "contrast": contrast,
                             "n_datasets": n, "mean_delta": vals.mean(),
                             "wins": wins, "losses": losses, "p": p})
        lines.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "dataset_level_summary.csv", index=False)
    (OUT / "dataset_level_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
