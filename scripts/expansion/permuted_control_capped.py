#!/usr/bin/env python
"""Permuted-formula (row-alignment) control for run_schema_evaluation outputs.

Scratch adaptation of scripts/build_postcutoff_permuted_control.py with two changes:
  1. cap-then-split: honours the run's recorded cap_rows (stratified_cap BEFORE the
     design/eval split), matching run_schema_evaluation; the original raises on cap_rows.
  2. optional --safe-columns: applies the same column renaming as
     scripts/run_paper2_llm_schema_expansion.safe_columns, for schemas generated with
     renamed columns.
Alignment is self-validating (row count + raw-column equality) exactly as in the original.
No LLM calls.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)
from dasef.datasets import load_dataset, raw_block_equal, schema_design_eval_split, stratified_cap  # noqa: E402
from dasef.evaluate import evaluate_classifier  # noqa: E402

MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--schema-design-fraction", type=float, default=0.3)
    ap.add_argument("--schema-design-seed", type=int, default=42)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--n-repeats", type=int, default=2)
    ap.add_argument("--safe-columns", action="store_true")
    ap.add_argument("--skip-existing", action="store_true",
                    help="reuse <out-dir>/runs/<run_id>_permuted.json when it already exists (only new or deleted runs are recomputed); run_level_scores.csv is still rebuilt for every run")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    (out_dir / "runs").mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for rp in sorted(runs_dir.glob("**/results.json")):
        res = json.loads(rp.read_text())
        if res.get("experiment_name") != "schema_evaluation":
            continue
        run_id, name = res["run_id"], res["dataset"]
        out_file = out_dir / "runs" / f"{run_id}_permuted.json"
        if args.skip_existing and out_file.exists():
            out = json.loads(out_file.read_text())
            print(f"reuse {run_id} {name} (existing permuted control)", flush=True)
            ev = {e["matrix_name"]: e for e in res["evaluations"]}
            for m in MODELS:
                for met in METRICS:
                    rec = {"dataset": name, "run_id": run_id, "model": m, "metric": met}
                    for mat in ["raw", "raw_plus_formula", "raw_plus_random_formula", "raw_plus_random_all"]:
                        if mat in ev:
                            rec[mat] = float(np.mean(ev[mat]["raw_scores"][m][met]))
                    rec["raw_plus_permuted_formula"] = float(np.mean(out["models"][m]["permuted_raw_scores"][met]))
                    rec["direct_delta"] = rec["raw_plus_formula"] - rec["raw"]
                    rec["vs_random_delta"] = rec["raw_plus_formula"] - rec.get("raw_plus_random_formula", np.nan)
                    rec["semantic_delta"] = rec["raw_plus_formula"] - rec["raw_plus_permuted_formula"]
                    rows.append(rec)
            continue
        t0 = time.time()
        ds = load_dataset(name)
        if args.safe_columns:
            from run_paper2_llm_schema_expansion import safe_columns
            ds = safe_columns(ds)
        cap_rows = res.get("cap_rows")
        if cap_rows:
            ds = stratified_cap(ds, cap_rows)
        _, ds_eval = schema_design_eval_split(ds, args.schema_design_fraction, args.schema_design_seed)
        X_eval = ds_eval.X.reset_index(drop=True)
        y_eval = ds_eval.y.reset_index(drop=True)
        fdf = pd.read_parquet(rp.parent / "matrices" / "formula.parquet").reset_index(drop=True)
        raw_cols = list(X_eval.columns)
        formula_cols = [c for c in fdf.columns if c not in raw_cols]
        if len(fdf) != len(y_eval) or not raw_block_equal(fdf[raw_cols], X_eval[raw_cols]) or not formula_cols:
            print(f"SKIP {run_id} {name}: rows {len(fdf)} vs {len(y_eval)}, formula_cols={len(formula_cols)}, "
                  f"raw_equal={fdf[raw_cols].equals(X_eval[raw_cols]) if len(fdf) == len(y_eval) else 'n/a'}", flush=True)
            continue
        nan_rate = {c: float(fdf[c].isna().mean()) for c in formula_cols}
        const_cols = [c for c in formula_cols if fdf[c].nunique(dropna=True) <= 1]
        rng = np.random.default_rng(args.seed)
        Xp = fdf.copy()
        for c in formula_cols:
            Xp[c] = rng.permutation(Xp[c].values)
        y_enc = pd.Series(LabelEncoder().fit_transform(y_eval.astype(str)), index=y_eval.index)
        out = {
            "run_id": run_id, "dataset": name, "schema": res["artifacts"]["schema"], "cap_rows": cap_rows,
            "n_rows": int(len(Xp)), "n_formula_features": len(formula_cols), "formula_cols": formula_cols,
            "formula_nan_rate": nan_rate, "formula_constant_cols": const_cols,
            "schema_design_fraction": args.schema_design_fraction, "schema_design_seed": args.schema_design_seed,
            "permutation_seed": args.seed, "safe_columns": args.safe_columns, "models": {},
        }
        print(f"run {run_id} {name} rows={len(Xp)} formula_cols={len(formula_cols)} "
              f"all-NaN cols={sum(1 for v in nan_rate.values() if v >= 1.0)} constant cols={len(const_cols)}", flush=True)
        for m in MODELS:
            tm = time.time()
            r = evaluate_classifier(Xp, y_enc, m, n_splits=args.n_splits, n_repeats=args.n_repeats, random_state=args.seed)
            out["models"][m] = {"permuted_metrics": r.metrics, "permuted_raw_scores": r.raw_scores, "seconds": round(time.time() - tm, 1)}
            print(f"  {m}: permuted roc_auc_ovr={r.metrics['roc_auc_ovr']:.4f} ({time.time() - tm:.1f}s)", flush=True)
        out["seconds_total"] = round(time.time() - t0, 1)
        out_file.write_text(json.dumps(out, indent=1))
        ev = {e["matrix_name"]: e for e in res["evaluations"]}
        for m in MODELS:
            for met in METRICS:
                rec = {"dataset": name, "run_id": run_id, "model": m, "metric": met}
                for mat in ["raw", "raw_plus_formula", "raw_plus_random_formula", "raw_plus_random_all"]:
                    if mat in ev:
                        rec[mat] = float(np.mean(ev[mat]["raw_scores"][m][met]))
                rec["raw_plus_permuted_formula"] = float(np.mean(out["models"][m]["permuted_raw_scores"][met]))
                rec["direct_delta"] = rec["raw_plus_formula"] - rec["raw"]
                rec["vs_random_delta"] = rec["raw_plus_formula"] - rec.get("raw_plus_random_formula", np.nan)
                rec["semantic_delta"] = rec["raw_plus_formula"] - rec["raw_plus_permuted_formula"]
                rows.append(rec)
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "run_level_scores.csv", index=False)
    if not df.empty:
        print(df[df.metric == "roc_auc_ovr"][["dataset", "model", "raw", "raw_plus_formula", "raw_plus_permuted_formula",
                                              "raw_plus_random_formula", "direct_delta", "semantic_delta"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
