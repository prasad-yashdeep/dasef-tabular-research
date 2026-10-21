#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_EXPECTED_FAMILY = {
    "xgboost": "tree",
    "random_forest": "tree",
    "logistic_regression": "linear_svm",
    "linear_svm": "linear_svm",
    "rbf_svm": "linear_svm",
    "knn": "distance_knn",
}


def write_markdown_report(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        out_path.write_text("# Downstream-Awareness Diagnostic\n\nNo matched comparisons found.\n")
        return

    wins = int((df["matched_minus_best_mismatch"] > 0).sum())
    losses = int((df["matched_minus_best_mismatch"] < 0).sum())
    ties = len(df) - wins - losses

    strongest = df.sort_values("matched_minus_best_mismatch", ascending=False).head(12)
    weakest = df.sort_values("matched_minus_best_mismatch").head(12)

    def compact_table(frame: pd.DataFrame) -> str:
        rows = []
        for _, row in frame.iterrows():
            rows.append({
                "dataset": row["dataset"],
                "schema_model": row["schema_model"],
                "model": row["downstream_model"],
                "matched": row["expected_family"],
                "matched_delta": f"{row['matched_delta']:+.4f}",
                "best_mismatch": row["best_mismatch_family"],
                "best_mismatch_delta": f"{row['best_mismatch_delta']:+.4f}",
                "matched-best": f"{row['matched_minus_best_mismatch']:+.4f}",
            })
        return pd.DataFrame(rows).to_markdown(index=False)

    lines = [
        "# Downstream-Awareness Diagnostic",
        "",
        "This report asks whether the schema family matched to a downstream model",
        "beats the best mismatched schema family for the same dataset, schema generator,",
        "downstream model, matrix pair, and metric.",
        "",
        "## Scope",
        "",
        f"- Matched comparisons: {len(df)}",
        f"- Matched family beats best mismatch: {wins}",
        f"- Matched family loses to best mismatch: {losses}",
        f"- Ties: {ties}",
        "",
        "## Strongest Matched Wins",
        "",
        compact_table(strongest),
        "",
        "## Strongest Matched Losses",
        "",
        compact_table(weakest),
        "",
        "## Guardrail",
        "",
        "This is a diagnostic over existing runs, not a final statistical test.",
        "Use it to decide whether downstream-awareness is a headline claim or a secondary characterization.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def build_downstream_awareness(df: pd.DataFrame) -> pd.DataFrame:
    formula = df[
        (df["baseline_matrix"] == "raw")
        & (df["candidate_matrix"] == "raw_plus_formula")
    ].copy()
    formula["expected_family"] = formula["downstream_model"].map(DEFAULT_EXPECTED_FAMILY)
    formula = formula[formula["expected_family"].notna()]

    rows = []
    group_cols = ["dataset", "schema_model", "downstream_model", "metric"]
    for group_key, group in formula.groupby(group_cols, dropna=False):
        dataset, schema_model, downstream_model, metric = group_key
        expected_family = DEFAULT_EXPECTED_FAMILY[downstream_model]
        matched = group[group["model_family"] == expected_family]
        mismatched = group[group["model_family"] != expected_family]
        if matched.empty or mismatched.empty:
            continue
        matched_row = matched.sort_values("delta_mean", ascending=False).iloc[0]
        best_mismatch = mismatched.sort_values("delta_mean", ascending=False).iloc[0]
        rows.append({
            "dataset": dataset,
            "schema_model": schema_model,
            "downstream_model": downstream_model,
            "metric": metric,
            "expected_family": expected_family,
            "matched_delta": matched_row["delta_mean"],
            "matched_ci_low": matched_row["ci_low"],
            "matched_ci_high": matched_row["ci_high"],
            "best_mismatch_family": best_mismatch["model_family"],
            "best_mismatch_delta": best_mismatch["delta_mean"],
            "best_mismatch_ci_low": best_mismatch["ci_low"],
            "best_mismatch_ci_high": best_mismatch["ci_high"],
            "matched_minus_best_mismatch": matched_row["delta_mean"] - best_mismatch["delta_mean"],
        })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze DASEF matched-vs-mismatched schema behavior.")
    parser.add_argument("--stats-csv", default="results/statistics/existing_result_stats_roc_auc_ovr.csv")
    parser.add_argument("--out-dir", default="results/statistics/awareness_full")
    parser.add_argument(
        "--downstream-models",
        default="",
        help="Optional comma-separated downstream-model filter, e.g. logistic_regression,random_forest,knn",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Optional output filename suffix inserted after the metric, e.g. primary_models",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.stats_csv)
    if args.downstream_models.strip():
        keep = {m.strip() for m in args.downstream_models.split(",") if m.strip()}
        df = df[df["downstream_model"].isin(keep)].copy()
    out = build_downstream_awareness(df)
    metric = df["metric"].iloc[0] if not df.empty else "metric"
    out_dir = Path(args.out_dir)
    suffix = f"_{args.suffix.strip()}" if args.suffix.strip() else ""
    csv_path = out_dir / f"downstream_awareness_{metric}{suffix}.csv"
    md_path = out_dir / f"downstream_awareness_{metric}{suffix}.md"
    out.to_csv(csv_path, index=False)
    write_markdown_report(out, md_path)
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
