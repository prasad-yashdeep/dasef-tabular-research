"""Friedman/Nemenyi ranking over the five treatments on the restructured benchmark, written in
the same markdown format that scripts/make_cd_diagram.py parses, plus the CD diagrams.

Usage: python friedman_cd44.py --dataset-level <agg>/dataset_level.csv --out-md <path.md> --fig-dir <dir>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, rankdata, studentized_range

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import make_cd_diagram as cdd  # noqa: E402

TREATMENTS = ["raw", "raw_plus_formula", "raw_plus_permuted_formula", "raw_plus_random_formula", "raw_plus_random_all"]
MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def nemenyi_cd(k: int, n: int, alpha: float = 0.05) -> float:
    q = studentized_range.ppf(1 - alpha, k, np.inf) / np.sqrt(2)
    return q * np.sqrt(k * (k + 1) / (6 * n))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-level", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--fig-dir", required=True)
    args = ap.parse_args()
    dl = pd.read_csv(args.dataset_level)
    lines = ["# Friedman Test — Multi-Treatment Ranking (restructured benchmark)", "",
             "Treatments: " + ", ".join(t.replace("raw_plus_", "raw+") for t in TREATMENTS), ""]
    for metric in METRICS:
        for model in MODELS:
            sub = dl[(dl.metric == metric) & (dl.model == model)].set_index("dataset")
            matrix = sub[TREATMENTS].to_numpy(dtype=float)
            n = matrix.shape[0]
            # rank within each dataset, higher score = higher rank (as in aggregate_dataset_level.py)
            ranks = np.vstack([rankdata(row) for row in matrix])
            avg = ranks.mean(axis=0)
            stat, p = friedmanchisquare(*[matrix[:, i] for i in range(len(TREATMENTS))])
            cd = nemenyi_cd(len(TREATMENTS), n)
            lines += [f"## {metric} / {model}", f"- N = {n} datasets", f"- Friedman χ² = {stat:.3f}, p = {p:.4f}", "",
                      "| Treatment | Avg Rank | Mean Score |", "|---|---|---|"]
            order = np.argsort(-avg)
            for i in order:
                lines.append(f"| {TREATMENTS[i]} | {avg[i]:.2f} | {matrix[:, i].mean():.4f} |")
            lines += ["", f"Nemenyi CD (α=0.05): {cd:.3f}", ""]
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")
    cdd.TREATMENT_LABELS["raw_plus_permuted_formula"] = "raw+permuted-formula"
    cdd.OUT_DIR = Path(args.fig_dir)
    items = cdd.parse_report(Path(args.out_md))
    for item in items:
        cdd.draw_diagram(item)
    print("\n".join(lines[:40])); print(f"wrote {len(items)} CD diagrams to {args.fig_dir}")


if __name__ == "__main__":
    main()
