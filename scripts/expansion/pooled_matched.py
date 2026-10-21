"""Matched-configuration pooling: GPT-5.5 Pro linear/SVM schemas on the 10 main datasets
(from results/judgments + results/statistics/permuted_control) plus the offline expansion.

Writes main10_matched_run_level.csv in the same format as permuted_control_capped.py's
run_level_scores.csv so aggregate_expansion.py can pool them (N = 10 + expansion).
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--schema-substring", default="linear_svm/gpt-5.5-pro")
    args = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(str(ROOT / "results/judgments/*/results.json"))):
        r = json.load(open(f))
        if args.schema_substring not in r["artifacts"]["schema"]:
            continue
        perm_path = ROOT / "results/statistics/permuted_control" / f"{r['run_id']}_permuted.json"
        if not perm_path.exists():
            print("no permuted control for", r["run_id"], r["dataset"])
            continue
        perm = json.load(open(perm_path))
        ev = {e["matrix_name"]: e for e in r["evaluations"]}
        for model in MODELS:
            for metric in METRICS:
                rows.append({
                    "dataset": r["dataset"], "run_id": r["run_id"], "model": model, "metric": metric,
                    "raw": ev["raw"]["models"][model][metric],
                    "raw_plus_formula": ev["raw_plus_formula"]["models"][model][metric],
                    "raw_plus_random_formula": ev["raw_plus_random_formula"]["models"][model][metric],
                    "raw_plus_random_all": ev["raw_plus_random_all"]["models"][model][metric],
                    "raw_plus_permuted_formula": perm["models"][model]["permuted_metrics"][metric],
                })
    df = pd.DataFrame(rows)
    df["direct_delta"] = df.raw_plus_formula - df.raw
    df["vs_random_delta"] = df.raw_plus_formula - df.raw_plus_random_formula
    df["semantic_delta"] = df.raw_plus_formula - df.raw_plus_permuted_formula
    df.to_csv(args.out, index=False)
    print(df.groupby("dataset").run_id.nunique().to_string())
    print("datasets:", df.dataset.nunique(), "rows:", len(df))


if __name__ == "__main__":
    main()
