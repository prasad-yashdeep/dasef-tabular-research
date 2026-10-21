#!/usr/bin/env python
"""Re-evaluate stored runs of the locally cached core datasets whose categorical columns are integer
codes, with those columns one-hot encoded in the RAW block (dasef.datasets.LOCAL_CACHE_CATEGORICAL).

The generated columns are left exactly as stored (the generators saw the integer codes and the formulas
operate on them; see the alignment check), only the downstream evaluation is repeated: every matrix of
each run (raw, raw+formula, raw+random-formula, raw+random-all, raw+formula+judgment when present) is
rebuilt from the re-encoded evaluation rows plus the stored generated columns and scored with the same
models and folds. results.json is replaced in place (backup *.pre-onehot.bak). Offline; no LLM call.

Usage: python scripts/expansion/reevaluate_onehot_core.py [--datasets a,b,c] [--workers 5] [--roots judgments,prospective]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)

MATRIX_SOURCES = {"raw": None, "raw_plus_formula": "formula_matrix", "raw_plus_random_formula": "random_formula_matrix",
                  "raw_plus_random_all": "random_all_schema_features_matrix", "raw_plus_formula_plus_judgment": "hybrid_matrix"}
DEFAULT_DATASETS = ["adult_income", "bank_marketing", "car_evaluation"]


def list_runs(datasets: list[str], roots: list[str]) -> list[dict]:
    runs = []
    if "judgments" in roots:
        for f in sorted(glob.glob(str(ROOT / "results/judgments/*/results.json"))):
            d = json.load(open(f))
            if d["dataset"] in datasets:
                runs.append({"results": f, "design_fraction": 0.3, "root": "judgments"})
    if "prospective" in roots:
        for f in sorted(glob.glob(str(ROOT / "results/full_suite_prospective/runs/*/*/results.json"))):
            d = json.load(open(f))
            if d["dataset"] in datasets:
                runs.append({"results": f, "design_fraction": 0.2, "root": "prospective"})
    return runs


def reevaluate(task: dict) -> str:
    from dasef.datasets import load_dataset, raw_block_equal, schema_design_eval_split, stratified_cap
    from dasef.evaluate import evaluate_classifier

    f = Path(task["results"]); t0 = time.time()
    try:
        res = json.loads(f.read_text())
        ds = load_dataset(res["dataset"])
        if not ds.onehot_override_columns:
            return f"skip {f.parent.name} {res['dataset']}: no override columns"
        if res.get("cap_rows"):
            ds = stratified_cap(ds, res["cap_rows"])
        _, ev = schema_design_eval_split(ds, task["design_fraction"], 42)
        X_eval = ev.X.reset_index(drop=True); y_eval = ev.y.reset_index(drop=True)
        raw_cols = list(X_eval.columns)
        arts = res["artifacts"]
        fdf = pd.read_parquet(ROOT / arts["formula_matrix"]).reset_index(drop=True)
        if len(fdf) != len(y_eval) or not raw_block_equal(fdf[raw_cols], X_eval[raw_cols]):
            return f"ERROR {f.parent.name} {res['dataset']}: stored formula matrix is not row-aligned with the reconstructed split"
        models = list(res["evaluations"][0]["models"].keys())
        new_evals = []
        for e in res["evaluations"]:
            name = e["matrix_name"]
            if name not in MATRIX_SOURCES:
                new_evals.append(e); continue
            src = MATRIX_SOURCES[name]
            if src is None:
                X = X_eval
            else:
                if src not in arts or not (ROOT / arts[src]).exists():
                    new_evals.append(e); continue
                m = pd.read_parquet(ROOT / arts[src]).reset_index(drop=True)
                extra = [c for c in m.columns if c not in raw_cols]
                if len(m) != len(X_eval):
                    return f"ERROR {f.parent.name}: {src} has {len(m)} rows, expected {len(X_eval)}"
                X = pd.concat([X_eval, m[extra]], axis=1)
            entry = {"matrix_name": name, "rows": int(len(X)), "columns": int(X.shape[1]), "models": {}, "raw_scores": {}}
            for model in models:
                r = evaluate_classifier(X, y_eval, model, n_splits=5, n_repeats=2, random_state=42)
                entry["models"][model] = r.metrics; entry["raw_scores"][model] = r.raw_scores
            new_evals.append(entry)
        bak = f.with_name("results.json.pre-onehot.bak")
        if not bak.exists():
            bak.write_text(f.read_text())
        res["evaluations"] = new_evals
        res.setdefault("notes", []).append(f"Raw block re-evaluated on 2026-10-12 with the {len(ds.onehot_override_columns)} integer-coded categorical columns one-hot encoded (dasef.datasets.LOCAL_CACHE_CATEGORICAL); generated columns unchanged.")
        f.write_text(json.dumps(res, indent=2))
        lr = {e["matrix_name"]: e["models"]["logistic_regression"]["roc_auc_ovr"] for e in new_evals if "logistic_regression" in e["models"]}
        return f"done {task['root']} {f.parent.name} {res['dataset']}: LR " + " ".join(f"{k}={v:.4f}" for k, v in lr.items()) + f" ({time.time() - t0:.0f}s)"
    except Exception as exc:  # noqa: BLE001
        import traceback
        return f"ERROR {f} {type(exc).__name__}: {exc}\n{traceback.format_exc()[-800:]}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default=",".join(DEFAULT_DATASETS))
    ap.add_argument("--roots", default="judgments,prospective")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    runs = list_runs(args.datasets.split(","), args.roots.split(","))
    if args.limit:
        runs = runs[: args.limit]
    print(f"{len(runs)} runs to re-evaluate", flush=True)
    from multiprocessing import get_context
    t0 = time.time()
    with get_context("spawn").Pool(args.workers) as pool:
        for i, msg in enumerate(pool.imap_unordered(reevaluate, runs), 1):
            print(f"[{i}/{len(runs)} {time.time() - t0:.0f}s] {msg}", flush=True)
    print("REEVAL_DONE", flush=True)


if __name__ == "__main__":
    main()
