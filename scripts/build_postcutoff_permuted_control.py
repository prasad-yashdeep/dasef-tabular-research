#!/usr/bin/env python3
"""Build the permuted-formula (row-alignment) control for the post-cutoff runs.

The post-cutoff runs under results/postcutoff_real/runs were produced by
scripts/run_prospective_formula_controls.py with schema_design_fraction=0.2,
schema_design_seed=42 and no row cap, and contain only the matrices
raw / raw_plus_formula / raw_plus_random_formula / raw_plus_random_all.
This script adds raw_plus_permuted_formula for each run: every generated
formula column is independently permuted across the evaluation rows (seed 42),
the permuted matrix is evaluated with the same downstream models and 5x2 CV,
and the result is paired with the stored raw_plus_formula fold scores.

Alignment is self-validating: the reconstructed evaluation split must match the
stored matrix in row count and raw columns, otherwise the run is skipped.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from dasef.datasets import load_dataset, schema_design_eval_split  # noqa: E402
from dasef.evaluate import evaluate_classifier  # noqa: E402

MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default="results/postcutoff_real/runs")
    ap.add_argument("--out-dir", default="results/statistics/postcutoff_real/permuted_control")
    ap.add_argument("--schema-design-fraction", type=float, default=0.2)
    ap.add_argument("--schema-design-seed", type=int, default=42)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--n-repeats", type=int, default=2)
    args = ap.parse_args()

    runs_dir = ROOT / args.runs_dir
    out_dir = ROOT / args.out_dir
    (out_dir / "runs").mkdir(parents=True, exist_ok=True)
    ds_cache: dict[str, tuple[pd.DataFrame, pd.Series]] = {}
    rows: list[dict] = []
    skipped: list[str] = []

    for rp in sorted(runs_dir.glob("*/results.json")):
        res = json.loads(rp.read_text())
        run_id, name = res["run_id"], res["dataset"]
        out_file = out_dir / "runs" / f"{run_id}_permuted.json"
        if out_file.exists():
            out = json.loads(out_file.read_text())
            print(f"cached {run_id} {name}", flush=True)
        else:
            if res.get("cap_rows"):
                raise SystemExit(f"{run_id}: unexpected cap_rows={res['cap_rows']}")
            if name not in ds_cache:
                ds = load_dataset(name)
                _, ds_eval = schema_design_eval_split(ds, args.schema_design_fraction, args.schema_design_seed)
                ds_cache[name] = (ds_eval.X.reset_index(drop=True), ds_eval.y.reset_index(drop=True))
            X_eval, y_eval = ds_cache[name]
            fdf = pd.read_parquet(rp.parent / "matrices" / "formula.parquet").reset_index(drop=True)
            raw_cols = list(X_eval.columns)
            formula_cols = [c for c in fdf.columns if c not in raw_cols]
            if len(fdf) != len(y_eval) or not fdf[raw_cols].equals(X_eval[raw_cols]) or not formula_cols:
                print(f"SKIP {run_id} {name}: rows {len(fdf)} vs {len(y_eval)}, formula_cols={len(formula_cols)}", flush=True)
                skipped.append(run_id)
                continue
            rng = np.random.default_rng(args.seed)
            Xp = fdf.copy()
            for c in formula_cols:
                Xp[c] = rng.permutation(Xp[c].values)
            y_enc = pd.Series(LabelEncoder().fit_transform(y_eval.astype(str)), index=y_eval.index)
            out = {
                "run_id": run_id, "dataset": name, "schema": res["artifacts"]["schema"],
                "n_rows": int(len(Xp)), "n_formula_features": len(formula_cols), "formula_cols": formula_cols,
                "schema_design_fraction": args.schema_design_fraction, "schema_design_seed": args.schema_design_seed,
                "permutation_seed": args.seed, "models": {},
            }
            print(f"run {run_id} {name} rows={len(Xp)} formula_cols={len(formula_cols)}", flush=True)
            for m in MODELS:
                r = evaluate_classifier(Xp, y_enc, m, n_splits=args.n_splits, n_repeats=args.n_repeats, random_state=args.seed)
                out["models"][m] = {"permuted_metrics": r.metrics, "permuted_raw_scores": r.raw_scores}
                print(f"  {m}: permuted roc_auc_ovr={r.metrics.get('roc_auc_ovr', float('nan')):.4f}", flush=True)
            out_file.write_text(json.dumps(out, indent=1))
        ev = {e["matrix_name"]: e for e in res["evaluations"]}
        for m in MODELS:
            for met in METRICS:
                f_scores = ev["raw_plus_formula"]["raw_scores"][m][met]
                p_scores = out["models"][m]["permuted_raw_scores"][met]
                rows.append({
                    "dataset": name, "run_id": run_id, "model": m, "metric": met,
                    "formula": float(np.mean(f_scores)), "permuted": float(np.mean(p_scores)),
                    "delta_formula_minus_permuted": float(np.mean(f_scores) - np.mean(p_scores)),
                })

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "run_level.csv", index=False)
    ds_level = df.groupby(["metric", "model", "dataset"], as_index=False)["delta_formula_minus_permuted"].mean()
    ds_level.to_csv(out_dir / "formula_vs_permuted_dataset_level.csv", index=False)
    lines = [
        "# Post-cutoff: formula vs permuted-formula (dataset-level)", "",
        f"Runs: {df.run_id.nunique()} (skipped: {len(skipped)}); datasets: {df.dataset.nunique()}. "
        "semantic = raw+formula minus raw+permuted-formula (each generated column independently "
        f"row-permuted, seed {args.seed}); design fraction {args.schema_design_fraction}, seed {args.schema_design_seed}, no cap. "
        "Wilcoxon (two-sided, exact) across datasets.", "",
    ]
    for met in METRICS:
        lines += [f"## {met}", "", "| Model | N | mean Δ | W/L | p |", "|---|---|---|---|---|"]
        for m in MODELS:
            x = ds_level[(ds_level.metric == met) & (ds_level.model == m)]["delta_formula_minus_permuted"].values
            p = stats.wilcoxon(x, alternative="two-sided", method="exact").pvalue if len(x) >= 2 and np.any(x != 0) else float("nan")
            lines.append(f"| {m} | {len(x)} | {x.mean():+.4f} | {(x > 0).sum()}/{(x < 0).sum()} | {p:.4f} |")
        lines.append("")
    (out_dir / "formula_vs_permuted_summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
