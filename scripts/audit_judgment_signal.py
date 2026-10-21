#!/usr/bin/env python
"""Do the per-row judgment features carry row-level signal on their own?

For every DeepSeek-Reasoner judgment run on the core tier, score logistic regression on the judgment
columns ALONE (same 5x2 stratified folds, seed 42, as the paper) and summarise the value distribution of
each judgment feature (distinct values, dominant-value rate, share of values at a declared bound).
Writes results/statistics/judgment_signal_audit.csv (one row per run) and judgment_signal_features.csv
(one row per feature) plus a markdown summary. Offline; no LLM call.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dasef.datasets import load_dataset, schema_design_eval_split, stratified_cap  # noqa: E402
from dasef.evaluate import evaluate_classifier  # noqa: E402


def main() -> None:
    rows, feats = [], []
    for rd in sorted(glob.glob(str(ROOT / "results/judgments/*"))):
        rd = Path(rd)
        js = glob.glob(str(rd / "judgments" / "*.json"))
        if not js or not (rd / "results.json").exists():
            continue
        if json.load(open(js[0])).get("model") != "deepseek-reasoner":
            continue
        res = json.load(open(rd / "results.json"))
        schema = json.load(open(rd / "schema.normalized.json"))
        jspecs = {f["name"]: f for f in schema["features"] if f["type"] == "judgment"}
        jm = pd.read_parquet(rd / "matrices" / "judgment.parquet").reset_index(drop=True)
        jcols = [c for c in jm.columns if c in jspecs]
        if not jcols:
            continue
        ds = load_dataset(res["dataset"])
        if res.get("cap_rows"):
            ds = stratified_cap(ds, res["cap_rows"])
        _, ev = schema_design_eval_split(ds, 0.3, 42)
        y = ev.y.reset_index(drop=True)
        if len(jm) != len(y):
            print("SKIP", rd.name, res["dataset"], "rows", len(jm), len(y)); continue
        X = jm[jcols].apply(pd.to_numeric, errors="coerce")
        r = evaluate_classifier(X, y, "logistic_regression", n_splits=5, n_repeats=2, random_state=42)
        ev_stored = {e["matrix_name"]: e for e in res["evaluations"]}
        rows.append({"run_id": rd.name, "dataset": res["dataset"], "schema": res["artifacts"]["schema"], "n_judgment_features": len(jcols),
                     "lr_auc_judgments_only": r.metrics["roc_auc_ovr"], "lr_auc_raw": ev_stored["raw"]["models"]["logistic_regression"]["roc_auc_ovr"],
                     "lr_auc_raw_plus_formula": ev_stored["raw_plus_formula"]["models"]["logistic_regression"]["roc_auc_ovr"],
                     "lr_auc_raw_plus_formula_plus_judgment": ev_stored["raw_plus_formula_plus_judgment"]["models"]["logistic_regression"]["roc_auc_ovr"]})
        for c in jcols:
            v = X[c]; lo, hi = jspecs[c]["value_range"]
            vc = v.value_counts(dropna=True)
            feats.append({"run_id": rd.name, "dataset": res["dataset"], "feature": c, "n_missing": int(v.isna().sum()), "n_distinct": int(v.nunique()),
                          "dominant_rate": float(vc.iloc[0] / v.notna().sum()) if len(vc) else np.nan,
                          "share_at_bounds": float(((v == lo) | (v == hi)).mean()), "declared_lo": lo, "declared_hi": hi})
        print(f"{res['dataset']:22s} {rd.name} judgments-only LR AUC={r.metrics['roc_auc_ovr']:.3f} (raw {rows[-1]['lr_auc_raw']:.3f})", flush=True)
    df, ff = pd.DataFrame(rows), pd.DataFrame(feats)
    out = ROOT / "results/statistics"
    df.to_csv(out / "judgment_signal_audit.csv", index=False); ff.to_csv(out / "judgment_signal_features.csv", index=False)
    lines = ["# Judgment-feature signal audit (DeepSeek-Reasoner runs, core tier)", "",
             f"runs: {len(df)} | judgment features: {len(ff)} | missing values: {int(ff.n_missing.sum())}",
             f"judgments-only LR ROC-AUC: mean {df.lr_auc_judgments_only.mean():.3f}, median {df.lr_auc_judgments_only.median():.3f}, "
             f"range {df.lr_auc_judgments_only.min():.2f} to {df.lr_auc_judgments_only.max():.2f}; runs above 0.60: {int((df.lr_auc_judgments_only > 0.6).sum())}",
             f"distinct values per feature: median {ff.n_distinct.median():.0f} (quartiles {ff.n_distinct.quantile(.25):.0f} to {ff.n_distinct.quantile(.75):.0f}); "
             f"binary features: {int((ff.n_distinct <= 2).sum())}; near-constant (dominant value >= 80%): {int((ff.dominant_rate >= 0.8).sum())}; "
             f"more than half of values at a declared bound: {int((ff.share_at_bounds > 0.5).sum())}; more than 90%: {int((ff.share_at_bounds > 0.9).sum())}",
             "", "per dataset (mean judgments-only LR AUC, raw LR AUC):"]
    for d, g in df.groupby("dataset"):
        lines.append(f"  {d}: {g.lr_auc_judgments_only.mean():.3f} (raw {g.lr_auc_raw.mean():.3f})")
    (out / "judgment_signal_audit.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
