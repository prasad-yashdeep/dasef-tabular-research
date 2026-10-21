"""Core-benchmark run-level rows for the linear/SVM schema of each generator on the 10 main
datasets, in the same format as the expansion run_level_scores.csv (plus a generator column).

Sources: results/judgments/*/results.json (raw, formula, random controls) and
results/statistics/permuted_control/<run>_permuted.json (permuted control, deepseek-filtered
runs). One run per (dataset, generator) is expected; duplicates are averaged.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GENERATORS = ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-4.7", "claude-sonnet-4.6"]
MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--family", default="linear_svm")
    args = ap.parse_args()
    rows = []
    missing = []
    for f in sorted(glob.glob(str(ROOT / "results/judgments/*/results.json"))):
        r = json.load(open(f))
        schema = r["artifacts"]["schema"]
        gen = next((g for g in GENERATORS if f"/{args.family}/{g}/" in schema), None)
        if gen is None:
            continue
        perm_path = ROOT / "results/statistics/permuted_control" / f"{r['run_id']}_permuted.json"
        if not perm_path.exists():
            missing.append((r["run_id"], r["dataset"], gen))
            continue
        perm = json.load(open(perm_path))
        ev = {e["matrix_name"]: e for e in r["evaluations"]}
        for model in MODELS:
            for metric in METRICS:
                rows.append({
                    "dataset": r["dataset"], "run_id": r["run_id"], "generator": gen, "model": model, "metric": metric,
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
    print(df.groupby(["generator"]).dataset.nunique().to_string())
    print("runs without permuted control (skipped, expected for non-deepseek duplicates):", len(missing))
    dup = df.groupby(["dataset", "generator"]).run_id.nunique()
    print("dataset x generator cells with >1 run:", int((dup > 1).sum()))


if __name__ == "__main__":
    main()
