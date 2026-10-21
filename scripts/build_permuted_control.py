#!/usr/bin/env python3
"""Build permuted-formula control and re-evaluate.

For each existing R1 judgment run:
1. Load the formula matrix (raw_plus_formula columns minus raw columns = formula features)
2. Shuffle each formula column independently within the evaluation fold
3. Evaluate the permuted matrix with the same downstream models
4. Save as a new matrix comparison: raw_plus_permuted_formula

This isolates semantic row-alignment: if formula > permuted-formula,
the gain comes from meaningful value-to-row mapping, not just marginal distribution.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from dasef.datasets import load_dataset, raw_block_equal, schema_design_eval_split, stratified_cap
from dasef.evaluate import evaluate_classifier, EvalResult
from dasef.io_utils import read_json, read_model
from dasef.schema import SchemaSpec

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results" / "judgments"
OUTPUT_DIR = ROOT / "results" / "statistics" / "permuted_control"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DOWNSTREAM_MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]
N_SPLITS = 5
N_REPEATS = 2
RANDOM_STATE = 42


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


def load_r1_runs() -> list[tuple[Path, dict]]:
    """Load R1 runs that have formula matrices."""
    runs = []
    for run_dir in sorted(RESULTS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        results_file = run_dir / "results.json"
        if not results_file.exists():
            continue
        if get_filler_model(run_dir) != "deepseek-reasoner":
            continue
        formula_matrix = run_dir / "matrices" / "formula.parquet"
        if not formula_matrix.exists():
            continue
        data = json.loads(results_file.read_text())
        runs.append((run_dir, data))
    return runs


def permuted_evaluation(
    run_dir: Path, result: dict, seed: int = 42
) -> dict | None:
    """Run permuted-formula evaluation for one run.
    
    Returns dict with per-model fold-level scores for the permuted matrix.
    """
    dataset_name = result["dataset"]
    schema_path = result.get("artifacts", {}).get("schema")
    if not schema_path:
        return None

    # Resolve schema path
    schema_full = ROOT / schema_path if not Path(schema_path).is_absolute() else Path(schema_path)
    if not schema_full.exists():
        return None

    try:
        schema = read_model(str(schema_full), SchemaSpec)
    except:
        return None

    # Reproduce the canonical pipeline's eval split EXACTLY: cap the FULL dataset
    # to the run's cap_rows FIRST, then take the (0.3, seed=42) split. Splitting
    # WITHOUT capping (the previous behaviour) produced a y vector up to ~10x
    # longer than the cached matrices for capped datasets (adult_income,
    # bank_marketing, electricity); the downstream length-trim then paired the
    # permuted matrix with mis-ordered labels, collapsing the permuted score to
    # ~0.5 and inflating the semantic-control delta (~+0.40 instead of ~+0.01).
    cap_rows = result.get("cap_rows")
    try:
        ds = load_dataset(dataset_name)
        if cap_rows:
            ds = stratified_cap(ds, cap_rows)
        _, ds_eval = schema_design_eval_split(ds, 0.3, 42)
    except Exception:
        return None

    # Load the raw and formula matrices
    raw_matrix = run_dir / "matrices" / "formula.parquet"  # This is actually raw+formula
    if not raw_matrix.exists():
        return None

    # We need the raw X and the formula columns
    # The formula matrix in the pipeline is the raw columns + formula features
    # Let's load both and compute the formula-only columns
    X_eval = ds_eval.X.reset_index(drop=True)
    y_eval = ds_eval.y.reset_index(drop=True)
    
    # Load the formula parquet to get the formula feature names
    formula_df = pd.read_parquet(run_dir / "matrices" / "formula.parquet")
    raw_cols = list(X_eval.columns)
    formula_cols = [c for c in formula_df.columns if c not in raw_cols]
    
    if not formula_cols:
        return None

    # Build raw_plus_formula matrix: the raw block comes from the freshly loaded evaluation split (so the
    # integer-coded categorical columns of the cached core datasets carry their category dtype and are
    # one-hot encoded exactly as in the re-evaluated raw and raw+formula matrices), the formula columns
    # from the stored parquet. Row alignment of the two is asserted below.
    formula_df = formula_df.reset_index(drop=True)
    X_with_formula = pd.concat([X_eval[raw_cols], formula_df[formula_cols]], axis=1)
    
    # Create permuted version: shuffle each formula column independently
    rng = np.random.default_rng(seed)
    X_permuted = X_with_formula.copy()
    for col in formula_cols:
        X_permuted[col] = rng.permutation(X_permuted[col].values)

    # Evaluate both raw_plus_formula and raw_plus_permuted_formula
    # with the same CV folds for proper pairing
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE)
    
    from sklearn.preprocessing import LabelEncoder
    y_encoded = pd.Series(LabelEncoder().fit_transform(y_eval.astype(str)), index=y_eval.index)
    
    # Self-validating alignment (NO silent trimming). After the cap-then-split
    # fix above, the cached matrix and the reconstructed labels must match exactly
    # in row count, and the matrix's raw columns must equal the reconstructed raw
    # features row-for-row. If not, skip this run rather than emit misaligned data.
    if len(formula_df) != len(y_encoded) or len(X_with_formula) != len(y_encoded):
        print(f" MISALIGN(len {len(X_with_formula)}!={len(y_encoded)})", end="", flush=True)
        return None
    if not raw_block_equal(formula_df[raw_cols].reset_index(drop=True), X_eval[raw_cols].reset_index(drop=True)):
        print(" MISALIGN(raw-cols)", end="", flush=True)
        return None

    results_out = {
        "run_id": result.get("run_id", run_dir.name),
        "dataset": dataset_name,
        "schema_path": schema_path,
        "formula_cols": formula_cols,
        "n_formula_features": len(formula_cols),
        "n_rows": len(X_permuted),
        "models": {},
    }

    for model_name in DOWNSTREAM_MODELS:
        try:
            # Evaluate permuted
            perm_result = evaluate_classifier(
                X_permuted, y_encoded, model_name,
                n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE
            )
            results_out["models"][model_name] = {
                "permuted_metrics": perm_result.metrics,
                "permuted_raw_scores": perm_result.raw_scores,
            }
        except Exception as e:
            results_out["models"][model_name] = {"error": str(e)}

    return results_out


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-existing", action="store_true",
                    help="reuse results/statistics/permuted_control/<run_id>_permuted.json when it exists "
                         "(delete the files of runs whose formula matrix changed to recompute only those); "
                         "the dataset-level summary is still rebuilt over every run")
    args = ap.parse_args()
    print("Loading R1 runs with formula matrices...", flush=True)
    runs = load_r1_runs()
    print(f"  Found {len(runs)} R1 runs with formula matrices", flush=True)

    all_results = []
    failed = 0

    for i, (run_dir, result) in enumerate(runs):
        dataset = result["dataset"]
        run_id = result.get("run_id", run_dir.name)
        print(f"  [{i+1}/{len(runs)}] {dataset} / {run_id}...", end="", flush=True)

        existing = OUTPUT_DIR / f"{run_id}_permuted.json"
        if args.skip_existing and existing.exists():
            all_results.append(json.loads(existing.read_text()))
            print(" reuse", flush=True)
            continue

        out = permuted_evaluation(run_dir, result)
        if out is None:
            print(" SKIP", flush=True)
            failed += 1
            continue

        errors = [m for m, v in out["models"].items() if "error" in v]
        if errors:
            print(f" PARTIAL ({len(errors)} errors)", flush=True)
        else:
            print(" OK", flush=True)

        all_results.append(out)

        # Save individual result
        out_file = OUTPUT_DIR / f"{run_id}_permuted.json"
        out_file.write_text(json.dumps(out, indent=2, default=str))

    print(f"\n  Completed: {len(all_results)} | Failed/Skipped: {failed}")

    # ═══════════════════════════════════════════════════════════════
    # Aggregate: formula vs permuted-formula at dataset level
    # ═══════════════════════════════════════════════════════════════
    print("\n=== Dataset-level: formula vs permuted-formula ===", flush=True)

    # Load the original formula scores from the judgment runs
    datasets = sorted(set(r["dataset"] for r in all_results))
    
    comparison_rows = []
    for metric in METRICS:
        for dm in DOWNSTREAM_MODELS:
            for dataset in datasets:
                ds_results = [r for r in all_results if r["dataset"] == dataset]
                deltas = []
                for r in ds_results:
                    model_data = r["models"].get(dm, {})
                    if "error" in model_data:
                        continue
                    perm_scores = model_data.get("permuted_raw_scores", {}).get(metric)
                    if not perm_scores:
                        continue
                    
                    # Load original formula scores from the main results
                    run_id = r["run_id"]
                    orig_results_file = RESULTS_DIR / run_id / "results.json"
                    if not orig_results_file.exists():
                        continue
                    orig_data = json.loads(orig_results_file.read_text())
                    orig_evals = {e["matrix_name"]: e for e in orig_data.get("evaluations", [])}
                    
                    formula_eval = orig_evals.get("raw_plus_formula")
                    if not formula_eval:
                        continue
                    formula_scores = formula_eval.get("raw_scores", {}).get(dm, {}).get(metric)
                    if not formula_scores:
                        continue
                    
                    # Delta: formula - permuted (positive = formula wins)
                    f_arr = np.array(formula_scores)
                    p_arr = np.array(perm_scores)
                    min_len = min(len(f_arr), len(p_arr))
                    delta = float(np.mean(f_arr[:min_len] - p_arr[:min_len]))
                    deltas.append(delta)
                
                if deltas:
                    comparison_rows.append({
                        "metric": metric,
                        "downstream_model": dm,
                        "dataset": dataset,
                        "mean_delta_formula_minus_permuted": float(np.mean(deltas)),
                        "n_runs": len(deltas),
                    })

    df_comp = pd.DataFrame(comparison_rows)
    if not df_comp.empty:
        df_comp.to_csv(OUTPUT_DIR / "formula_vs_permuted_dataset_level.csv", index=False)
        
        # Wilcoxon per (metric, downstream_model)
        summary_lines = [
            "# Formula vs Permuted-Formula (Dataset-Level)",
            "",
            "If formula > permuted consistently, the gain is from semantic row-alignment,",
            "not just the marginal distribution of feature values.",
            "",
        ]
        
        from scipy.stats import wilcoxon as wilcoxon_test
        for metric in METRICS:
            summary_lines.append(f"## {metric}")
            summary_lines.append("")
            summary_lines.append("| Downstream | N | Mean Δ | W/L/T | p (Wilcoxon) |")
            summary_lines.append("|---|---|---|---|---|")
            for dm in DOWNSTREAM_MODELS:
                subset = df_comp[(df_comp["metric"] == metric) & (df_comp["downstream_model"] == dm)]
                deltas = subset["mean_delta_formula_minus_permuted"].values
                n = len(deltas)
                if n < 5:
                    continue
                wins = int(np.sum(deltas > 0))
                losses = int(np.sum(deltas < 0))
                ties = n - wins - losses
                try:
                    _, p = wilcoxon_test(deltas, zero_method="wilcox")
                    p_str = f"{p:.4f}"
                except:
                    p_str = "n/a"
                summary_lines.append(
                    f"| {dm} | {n} | {np.mean(deltas):+.4f} | {wins}/{losses}/{ties} | {p_str} |"
                )
            summary_lines.append("")
        
        (OUTPUT_DIR / "formula_vs_permuted_summary.md").write_text("\n".join(summary_lines))
        print("  Saved formula_vs_permuted_summary.md")

    print("\nDONE.")


if __name__ == "__main__":
    main()
