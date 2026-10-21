#!/usr/bin/env python3
"""Dataset-level statistical aggregation for DASEF Paper 1.

Fixes the fold-level bootstrap problem by:
1. For each (dataset, downstream_model, matrix_pair): average fold deltas → 1 number per run
2. If multiple runs exist per dataset (different schema_models/families), average across them → 1 dataset-level delta
3. Run Wilcoxon signed-rank across datasets (N=10)
4. Report Friedman + post-hoc Nemenyi for multi-treatment comparison
5. Apply Holm-Bonferroni correction for primary hypotheses, BH-FDR for exploratory

Outputs:
  results/statistics/dataset_level/
    primary_hypotheses.md          — headline tests (formula>raw, judgment>formula)
    primary_hypotheses.csv
    per_dataset_deltas.csv         — the actual dataset-level observations
    friedman_nemenyi.md            — multi-treatment ranking
    exploratory_pockets.csv        — per schema_model/family breakdown (FDR-corrected)
    win_loss_tie.md                — counts at dataset level
    effect_sizes.csv               — Cliff's delta per hypothesis
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon, rankdata

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from dasef.io_utils import read_json

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results" / "judgments"
OUTPUT_DIR = ROOT / "results" / "statistics" / "dataset_level"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

METRICS = ["roc_auc_ovr", "balanced_accuracy"]

# Primary matrix pairs for headline claims
PRIMARY_PAIRS = [
    ("raw", "raw_plus_formula"),                          # Formula adds value over raw?
    ("raw", "raw_plus_formula_plus_judgment"),             # Full DASEF over raw?
    ("raw_plus_formula", "raw_plus_formula_plus_judgment"),# Judgment adds over formula?
    ("raw_plus_random_formula", "raw_plus_formula"),       # Formula > random (same dims)?
    ("raw_plus_random_all", "raw_plus_formula_plus_judgment"),  # Full > random-all?
]

# Filter to R1 filler only
def get_filler_model(run_dir: Path) -> str | None:
    judgment_dir = run_dir / "judgments"
    if not judgment_dir.exists():
        return None
    files = list(judgment_dir.iterdir())
    if not files:
        return None
    try:
        data = json.loads(files[0].read_text())
        return data.get("model")
    except:
        return None


def load_all_r1_results() -> list[dict]:
    """Load all R1 judgment run results."""
    results = []
    for run_dir in sorted(RESULTS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        results_file = run_dir / "results.json"
        if not results_file.exists():
            continue
        filler = get_filler_model(run_dir)
        if filler != "deepseek-reasoner":
            continue
        data = json.loads(results_file.read_text())
        data["_run_dir"] = str(run_dir)
        results.append(data)
    return results


def extract_cell_delta(result: dict, baseline_matrix: str, candidate_matrix: str,
                       downstream_model: str, metric: str) -> float | None:
    """Extract mean fold delta for one cell (one run, one downstream model, one pair)."""
    evals_by_name = {e["matrix_name"]: e for e in result.get("evaluations", [])}
    if baseline_matrix not in evals_by_name or candidate_matrix not in evals_by_name:
        return None
    base_eval = evals_by_name[baseline_matrix]
    cand_eval = evals_by_name[candidate_matrix]
    base_scores = base_eval.get("raw_scores", {}).get(downstream_model, {}).get(metric)
    cand_scores = cand_eval.get("raw_scores", {}).get(downstream_model, {}).get(metric)
    if not base_scores or not cand_scores:
        return None
    base = np.array(base_scores, dtype=float)
    cand = np.array(cand_scores, dtype=float)
    finite = np.isfinite(base) & np.isfinite(cand)
    if finite.sum() == 0:
        return None
    return float(np.mean(cand[finite] - base[finite]))


def schema_model_from_result(result: dict) -> str | None:
    schema_path = result.get("artifacts", {}).get("schema", "")
    parts = Path(schema_path).parts
    if "schemas" in parts:
        idx = parts.index("schemas")
        try:
            return parts[idx + 3]  # cache/schemas/dataset/family/model/...
        except IndexError:
            pass
    return None


def model_family_from_result(result: dict) -> str | None:
    schema_path = result.get("artifacts", {}).get("schema", "")
    parts = Path(schema_path).parts
    if "schemas" in parts:
        idx = parts.index("schemas")
        try:
            return parts[idx + 2]
        except IndexError:
            pass
    return None


def cliffs_delta(x: np.ndarray) -> float:
    """Cliff's delta for one-sample: proportion positive minus proportion negative."""
    n = len(x)
    if n == 0:
        return 0.0
    pos = np.sum(x > 0)
    neg = np.sum(x < 0)
    return float((pos - neg) / n)


def holm_bonferroni(p_values: list[float | None]) -> list[float | None]:
    """Apply Holm-Bonferroni correction."""
    n = len(p_values)
    indexed = [(i, p) for i, p in enumerate(p_values) if p is not None]
    indexed.sort(key=lambda x: x[1])
    corrected = [None] * n
    for rank, (idx, p) in enumerate(indexed):
        corrected[idx] = min(1.0, p * (n - rank))
    # Enforce monotonicity
    prev = 0.0
    for rank, (idx, _) in enumerate(indexed):
        corrected[idx] = max(corrected[idx], prev)
        prev = corrected[idx]
    return corrected


def bh_fdr(p_values: list[float | None]) -> list[float | None]:
    """Benjamini-Hochberg FDR correction."""
    n = len(p_values)
    indexed = [(i, p) for i, p in enumerate(p_values) if p is not None]
    indexed.sort(key=lambda x: x[1])
    corrected = [None] * n
    for rank, (idx, p) in enumerate(indexed, 1):
        corrected[idx] = p * len(indexed) / rank
    # Enforce monotonicity (step-down)
    prev = 1.0
    for rank in range(len(indexed) - 1, -1, -1):
        idx = indexed[rank][0]
        corrected[idx] = min(corrected[idx], prev)
        prev = corrected[idx]
    return corrected


def nemenyi_cd(k: int, n: int, alpha: float = 0.05) -> float:
    """Critical difference for Nemenyi post-hoc test."""
    from scipy.stats import studentized_range
    # Demsar (2006) Nemenyi critical values q_alpha are the studentized-range
    # quantiles divided by sqrt(2); scipy's studentized_range gives the raw
    # (Tukey) quantile, so divide here. For k=5, N=10 this yields CD=1.929
    # (the previous code returned 2.728, which is q_alpha itself).
    q = studentized_range.ppf(1 - alpha, k, np.inf) / np.sqrt(2)
    return q * np.sqrt(k * (k + 1) / (6 * n))


def main():
    print("Loading R1 results...", flush=True)
    results = load_all_r1_results()
    print(f"  Loaded {len(results)} R1 runs", flush=True)

    datasets = sorted(set(r["dataset"] for r in results))
    downstream_models = ["xgboost", "logistic_regression", "random_forest", "knn"]
    print(f"  Datasets: {datasets}")
    print(f"  Downstream models: {downstream_models}")

    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Build per-dataset deltas for each primary hypothesis
    # ═══════════════════════════════════════════════════════════════
    print("\n=== STEP 1: Dataset-level deltas ===", flush=True)

    all_rows = []
    for metric in METRICS:
        for base_mat, cand_mat in PRIMARY_PAIRS:
            for dm in downstream_models:
                # For each dataset: average across all runs (schema_models × families)
                dataset_deltas = {}
                for dataset in datasets:
                    ds_results = [r for r in results if r["dataset"] == dataset]
                    deltas_for_ds = []
                    for r in ds_results:
                        d = extract_cell_delta(r, base_mat, cand_mat, dm, metric)
                        if d is not None:
                            deltas_for_ds.append(d)
                    if deltas_for_ds:
                        dataset_deltas[dataset] = float(np.mean(deltas_for_ds))

                for ds, delta in dataset_deltas.items():
                    all_rows.append({
                        "metric": metric,
                        "baseline": base_mat,
                        "candidate": cand_mat,
                        "downstream_model": dm,
                        "dataset": ds,
                        "delta": delta,
                        "n_runs": len([r for r in results if r["dataset"] == ds]),
                    })

    df_deltas = pd.DataFrame(all_rows)
    df_deltas.to_csv(OUTPUT_DIR / "per_dataset_deltas.csv", index=False)
    print(f"  Saved {len(df_deltas)} dataset-level observations")

    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Primary hypothesis tests (Wilcoxon across datasets)
    # ═══════════════════════════════════════════════════════════════
    print("\n=== STEP 2: Primary hypothesis tests ===", flush=True)

    hypothesis_rows = []
    for metric in METRICS:
        for base_mat, cand_mat in PRIMARY_PAIRS:
            for dm in downstream_models:
                subset = df_deltas[
                    (df_deltas["metric"] == metric) &
                    (df_deltas["baseline"] == base_mat) &
                    (df_deltas["candidate"] == cand_mat) &
                    (df_deltas["downstream_model"] == dm)
                ]
                deltas = subset["delta"].values
                n = len(deltas)
                if n < 5:
                    continue

                mean_delta = float(np.mean(deltas))
                std_delta = float(np.std(deltas, ddof=1)) if n > 1 else 0.0
                wins = int(np.sum(deltas > 0))
                losses = int(np.sum(deltas < 0))
                ties = n - wins - losses

                # Wilcoxon signed-rank (two-sided)
                try:
                    if np.allclose(deltas, 0):
                        p_val = 1.0
                    else:
                        stat, p_val = wilcoxon(deltas, zero_method="wilcox")
                        p_val = float(p_val)
                except ValueError:
                    p_val = None

                cd = cliffs_delta(deltas)

                hypothesis_rows.append({
                    "metric": metric,
                    "baseline": base_mat,
                    "candidate": cand_mat,
                    "downstream_model": dm,
                    "n_datasets": n,
                    "mean_delta": mean_delta,
                    "std_delta": std_delta,
                    "wins": wins,
                    "losses": losses,
                    "ties": ties,
                    "p_value": p_val,
                    "cliffs_delta": cd,
                })

    df_hyp = pd.DataFrame(hypothesis_rows)

    # Apply Holm-Bonferroni correction
    p_vals = df_hyp["p_value"].tolist()
    corrected = holm_bonferroni(p_vals)
    df_hyp["p_corrected_holm"] = corrected

    # Also BH-FDR
    fdr = bh_fdr(p_vals)
    df_hyp["p_corrected_bh"] = fdr

    # Significance flag
    df_hyp["sig_holm_05"] = df_hyp["p_corrected_holm"].apply(
        lambda x: x is not None and x < 0.05
    )
    df_hyp["sig_bh_05"] = df_hyp["p_corrected_bh"].apply(
        lambda x: x is not None and x < 0.05
    )

    df_hyp = df_hyp.sort_values("p_value")
    df_hyp.to_csv(OUTPUT_DIR / "primary_hypotheses.csv", index=False)

    # Write markdown report
    lines = [
        "# DASEF Paper 1 — Dataset-Level Primary Hypotheses",
        "",
        "Statistical unit: **dataset** (N=10). Each dataset-level delta is the mean",
        "of all available runs (across schema generators and model families) for that dataset.",
        "",
        "Test: Wilcoxon signed-rank (two-sided). Correction: Holm-Bonferroni (primary),",
        "Benjamini-Hochberg FDR (exploratory).",
        "",
        f"Total hypotheses tested: {len(df_hyp)}",
        f"Significant after Holm (α=0.05): {int(df_hyp['sig_holm_05'].sum())}",
        f"Significant after BH-FDR (α=0.05): {int(df_hyp['sig_bh_05'].sum())}",
        "",
        "## Key Results",
        "",
    ]

    # Group by pair for readability
    for (base, cand), group in df_hyp.groupby(["baseline", "candidate"]):
        lines.append(f"### {base} → {cand}")
        lines.append("")
        for metric in METRICS:
            mg = group[group["metric"] == metric]
            if mg.empty:
                continue
            lines.append(f"**Metric: {metric}**")
            lines.append("")
            lines.append("| Downstream | N | Mean Δ | W/L/T | p (raw) | p (Holm) | Cliff's δ | Sig? |")
            lines.append("|---|---|---|---|---|---|---|---|")
            for _, row in mg.iterrows():
                p_raw = f"{row['p_value']:.4f}" if row['p_value'] is not None else "n/a"
                p_holm = f"{row['p_corrected_holm']:.4f}" if row['p_corrected_holm'] is not None else "n/a"
                sig = "✅" if row["sig_holm_05"] else "❌"
                lines.append(
                    f"| {row['downstream_model']} | {row['n_datasets']} | "
                    f"{row['mean_delta']:+.4f} | {row['wins']}/{row['losses']}/{row['ties']} | "
                    f"{p_raw} | {p_holm} | {row['cliffs_delta']:+.2f} | {sig} |"
                )
            lines.append("")

    # Win/Loss/Tie summary
    lines.append("## Aggregate Win/Loss/Tie Summary")
    lines.append("")
    lines.append("| Pair | Metric | Total W | Total L | Total T | Net |")
    lines.append("|---|---|---|---|---|---|")
    for (base, cand), group in df_hyp.groupby(["baseline", "candidate"]):
        for metric in METRICS:
            mg = group[group["metric"] == metric]
            if mg.empty:
                continue
            tw = int(mg["wins"].sum())
            tl = int(mg["losses"].sum())
            tt = int(mg["ties"].sum())
            lines.append(f"| {base}→{cand} | {metric} | {tw} | {tl} | {tt} | {tw-tl:+d} |")
    lines.append("")

    (OUTPUT_DIR / "primary_hypotheses.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved primary_hypotheses.md + .csv ({len(df_hyp)} tests)")

    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Exploratory breakdown by schema_model and family
    # ═══════════════════════════════════════════════════════════════
    print("\n=== STEP 3: Exploratory per-schema-model breakdown ===", flush=True)

    exploratory_rows = []
    for metric in METRICS:
        for base_mat, cand_mat in PRIMARY_PAIRS[:3]:  # Focus on top 3 pairs
            for dm in downstream_models:
                # Get per-schema-model results
                for schema_model in ["claude-sonnet-4.6", "claude-opus-4.7", "gpt-5.5-pro", "gemini-3.1-pro-preview"]:
                    dataset_deltas = {}
                    for dataset in datasets:
                        ds_results = [r for r in results
                                      if r["dataset"] == dataset
                                      and schema_model_from_result(r) == schema_model]
                        deltas_for_ds = []
                        for r in ds_results:
                            d = extract_cell_delta(r, base_mat, cand_mat, dm, metric)
                            if d is not None:
                                deltas_for_ds.append(d)
                        if deltas_for_ds:
                            dataset_deltas[dataset] = float(np.mean(deltas_for_ds))

                    deltas = np.array(list(dataset_deltas.values()))
                    n = len(deltas)
                    if n < 5:
                        continue

                    try:
                        if np.allclose(deltas, 0):
                            p_val = 1.0
                        else:
                            _, p_val = wilcoxon(deltas, zero_method="wilcox")
                            p_val = float(p_val)
                    except ValueError:
                        p_val = None

                    exploratory_rows.append({
                        "metric": metric,
                        "baseline": base_mat,
                        "candidate": cand_mat,
                        "downstream_model": dm,
                        "schema_model": schema_model,
                        "n_datasets": n,
                        "mean_delta": float(np.mean(deltas)),
                        "wins": int(np.sum(deltas > 0)),
                        "losses": int(np.sum(deltas < 0)),
                        "p_value": p_val,
                    })

    df_exp = pd.DataFrame(exploratory_rows)
    if not df_exp.empty:
        fdr_exp = bh_fdr(df_exp["p_value"].tolist())
        df_exp["p_corrected_bh"] = fdr_exp
        df_exp = df_exp.sort_values("p_value")
        df_exp.to_csv(OUTPUT_DIR / "exploratory_pockets.csv", index=False)
        print(f"  Saved exploratory_pockets.csv ({len(df_exp)} tests)")

    # ═══════════════════════════════════════════════════════════════
    # STEP 4: Friedman test (multi-treatment ranking)
    # ═══════════════════════════════════════════════════════════════
    print("\n=== STEP 4: Friedman + ranking ===", flush=True)

    treatments = ["raw", "raw_plus_formula", "raw_plus_formula_plus_judgment",
                  "raw_plus_random_formula", "raw_plus_random_all"]

    friedman_lines = [
        "# Friedman Test — Multi-Treatment Ranking",
        "",
        "Treatments: raw, raw+formula, raw+formula+judgment, raw+random_formula, raw+random_all",
        "",
    ]

    for metric in METRICS:
        for dm in downstream_models:
            # Build matrix: rows=datasets, cols=treatments
            matrix = []
            ds_used = []
            for dataset in datasets:
                ds_results = [r for r in results if r["dataset"] == dataset]
                row = []
                skip = False
                for treatment in treatments:
                    scores = []
                    for r in ds_results:
                        evals = {e["matrix_name"]: e for e in r.get("evaluations", [])}
                        if treatment in evals:
                            raw_sc = evals[treatment].get("raw_scores", {}).get(dm, {}).get(metric)
                            if raw_sc:
                                scores.append(float(np.mean(raw_sc)))
                    if scores:
                        row.append(float(np.mean(scores)))
                    else:
                        skip = True
                        break
                if not skip and len(row) == len(treatments):
                    matrix.append(row)
                    ds_used.append(dataset)

            if len(matrix) < 5:
                continue

            matrix = np.array(matrix)
            # Friedman test
            try:
                stat, p = friedmanchisquare(*[matrix[:, i] for i in range(len(treatments))])
            except Exception:
                continue

            # Average ranks (lower = worse, higher = better)
            ranks = np.zeros_like(matrix)
            for i in range(matrix.shape[0]):
                ranks[i] = rankdata(matrix[i])
            avg_ranks = ranks.mean(axis=0)

            friedman_lines.append(f"## {metric} / {dm}")
            friedman_lines.append(f"- N = {len(matrix)} datasets")
            friedman_lines.append(f"- Friedman χ² = {stat:.3f}, p = {p:.4f}")
            friedman_lines.append("")
            friedman_lines.append("| Treatment | Avg Rank | Mean Score |")
            friedman_lines.append("|---|---|---|")
            sorted_idx = np.argsort(-avg_ranks)
            for idx in sorted_idx:
                friedman_lines.append(
                    f"| {treatments[idx]} | {avg_ranks[idx]:.2f} | {matrix[:, idx].mean():.4f} |"
                )
            friedman_lines.append("")

            # Nemenyi CD
            k = len(treatments)
            n = len(matrix)
            try:
                cd = nemenyi_cd(k, n, alpha=0.05)
                friedman_lines.append(f"Nemenyi CD (α=0.05): {cd:.3f}")
                friedman_lines.append("")
            except:
                pass

    (OUTPUT_DIR / "friedman_nemenyi.md").write_text("\n".join(friedman_lines), encoding="utf-8")
    print("  Saved friedman_nemenyi.md")

    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Effect size summary
    # ═══════════════════════════════════════════════════════════════
    print("\n=== STEP 5: Effect sizes ===", flush=True)

    effect_rows = []
    for _, row in df_hyp.iterrows():
        effect_rows.append({
            "pair": f"{row['baseline']} → {row['candidate']}",
            "metric": row["metric"],
            "downstream_model": row["downstream_model"],
            "mean_delta": row["mean_delta"],
            "cliffs_delta": row["cliffs_delta"],
            "effect_magnitude": (
                "large" if abs(row["cliffs_delta"]) >= 0.474 else
                "medium" if abs(row["cliffs_delta"]) >= 0.33 else
                "small" if abs(row["cliffs_delta"]) >= 0.147 else
                "negligible"
            ),
            "direction": "positive" if row["mean_delta"] > 0 else "negative",
            "sig_holm": row["sig_holm_05"],
        })

    df_effect = pd.DataFrame(effect_rows)
    df_effect.to_csv(OUTPUT_DIR / "effect_sizes.csv", index=False)
    print(f"  Saved effect_sizes.csv ({len(df_effect)} entries)")

    # Final summary
    print("\n" + "=" * 60)
    print("DONE. Key files:")
    print(f"  {OUTPUT_DIR / 'primary_hypotheses.md'}")
    print(f"  {OUTPUT_DIR / 'primary_hypotheses.csv'}")
    print(f"  {OUTPUT_DIR / 'per_dataset_deltas.csv'}")
    print(f"  {OUTPUT_DIR / 'friedman_nemenyi.md'}")
    print(f"  {OUTPUT_DIR / 'exploratory_pockets.csv'}")
    print(f"  {OUTPUT_DIR / 'effect_sizes.csv'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
