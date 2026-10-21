#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from dasef.statistics import DEFAULT_METRIC, comparisons_for_paths


DEFAULT_RESULT_DIRS = (
    "results/judgment_shortlist",
    "results/deepseek_judgment_shortlist",
    "results/schema_runs",
)


def find_result_files(paths: list[str]) -> list[Path]:
    result_files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file():
            result_files.append(path)
        elif path.exists():
            result_files.extend(path.rglob("results.json"))
    return sorted(set(result_files))


def _format_p(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if value < 0.001:
        return "<0.001"
    return f"{value:.3f}"


def _format_delta(value: float) -> str:
    return f"{value:+.4f}"


def _format_ci(row: pd.Series) -> str:
    return f"[{row.ci_low:+.4f}, {row.ci_high:+.4f}]"


def write_markdown_report(df: pd.DataFrame, out_path: Path, *, metric: str, result_count: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        out_path.write_text("# DASEF Existing Result Statistics\n\nNo comparisons found.\n", encoding="utf-8")
        return

    formula = df[
        (df["baseline_matrix"] == "raw")
        & (df["candidate_matrix"] == "raw_plus_formula")
    ].copy()
    judgment_vs_raw = df[
        (df["baseline_matrix"] == "raw")
        & (df["candidate_matrix"] == "raw_plus_formula_plus_judgment")
    ].copy()
    judgment_increment = df[
        (df["baseline_matrix"] == "raw_plus_formula")
        & (df["candidate_matrix"] == "raw_plus_formula_plus_judgment")
    ].copy()

    positive_ci = df[df["ci_low"] > 0].sort_values("delta_mean", ascending=False)
    negative_ci = df[df["ci_high"] < 0].sort_values("delta_mean")

    strongest = df.sort_values("delta_mean", ascending=False).head(12).copy()
    weakest = df.sort_values("delta_mean").head(8).copy()

    def compact_table(frame: pd.DataFrame, limit: int = 12) -> str:
        if frame.empty:
            return "_None._"
        rows = []
        for _, row in frame.head(limit).iterrows():
            rows.append({
                "dataset": row["dataset"],
                "schema": f"{row['schema_model']}/{row['model_family']}",
                "model": row["downstream_model"],
                "pair": f"{row['baseline_matrix']} -> {row['candidate_matrix']}",
                "delta": _format_delta(row["delta_mean"]),
                "95% CI": _format_ci(row),
                "p": _format_p(row["p_value"]),
            })
        return pd.DataFrame(rows).to_markdown(index=False)

    lines = [
        "# DASEF Existing Result Statistics",
        "",
        "Generated from stored fold-level `raw_scores`; no external API calls were made.",
        "",
        "## Scope",
        "",
        f"- Result files scanned: {result_count}",
        f"- Matrix comparisons analyzed: {len(df)}",
        f"- Metric: `{metric}`",
        "- Statistical unit here is the stored CV fold delta. Treat these as descriptive diagnostics;",
        "  final paper claims still need dataset-level aggregation once the larger suite is run.",
        "",
        "## Headline",
        "",
        f"- Comparisons with 95% bootstrap CI entirely above zero: {int((df['ci_low'] > 0).sum())}",
        f"- Comparisons with 95% bootstrap CI entirely below zero: {int((df['ci_high'] < 0).sum())}",
        f"- Formula-vs-raw comparisons: {len(formula)}",
        f"- Judgment-vs-raw comparisons: {len(judgment_vs_raw)}",
        f"- Judgment incremental-over-formula comparisons: {len(judgment_increment)}",
        "",
        "## Positive CI Excluding Zero",
        "",
        compact_table(positive_ci, limit=20),
        "",
        "## Negative CI Excluding Zero",
        "",
        compact_table(negative_ci, limit=20),
        "",
        "## Largest Positive Deltas, Regardless Of CI",
        "",
        compact_table(strongest, limit=12),
        "",
        "## Largest Negative Deltas",
        "",
        compact_table(weakest, limit=8),
        "",
        "## Interpretation Guardrails",
        "",
        "- A positive mean delta is not enough for a claim; require confidence intervals and dataset-level replication.",
        "- Repeated CV folds are not independent publication units. Use this report to triage, not to overclaim.",
        "- The strongest next claim to test is matched-vs-mismatched downstream-awareness, not another broad sweep.",
        "- Judgment features should be reported separately from formula features; they are costlier and currently mixed.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze existing DASEF result JSON files.")
    parser.add_argument("paths", nargs="*", default=list(DEFAULT_RESULT_DIRS))
    parser.add_argument("--metric", default=DEFAULT_METRIC)
    parser.add_argument("--out-dir", default="results/statistics/awareness_full")
    parser.add_argument("--n-bootstrap", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result_files = find_result_files(args.paths)
    comparisons = comparisons_for_paths(
        result_files,
        metric=args.metric,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
    )
    df = pd.DataFrame([comparison.as_dict() for comparison in comparisons])
    if not df.empty:
        dedupe_cols = [
            "dataset",
            "schema_model",
            "model_family",
            "downstream_model",
            "metric",
            "baseline_matrix",
            "candidate_matrix",
            "baseline_mean",
            "candidate_mean",
            "delta_mean",
        ]
        df = df.drop_duplicates(subset=dedupe_cols).reset_index(drop=True)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"existing_result_stats_{args.metric}.csv"
    md_path = out_dir / f"existing_result_stats_{args.metric}.md"
    df.to_csv(csv_path, index=False)
    write_markdown_report(df, md_path, metric=args.metric, result_count=len(result_files))
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
