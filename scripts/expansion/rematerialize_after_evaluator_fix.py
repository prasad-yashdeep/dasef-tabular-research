"""Re-materialize every stored formula matrix with the current evaluator and re-evaluate
the runs whose formula columns changed.

Used after each fix to src/dasef/features/formula.py (the ``floor`` shadowing fix, the two
category-dtype fixes, and the string-literal comparison fix). For every run directory
under the given roots it recomputes ``matrices/formula.parquet`` from the stored raw
columns and the cached schema and compares it with the stored formula columns. Runs with
no change are left untouched. For runs with a changed column it re-evaluates BOTH
``raw`` and ``raw_plus_formula`` in the same pass (so the two scores that enter the
direct and semantic deltas are always computed together; KNN's probability-based ROC-AUC
can drift by up to ~0.02 between passes on datasets with many near-duplicate one-hot
rows, which a strict raw-reproduction gate would otherwise flag), replaces those two
evaluations in results.json, writes the new formula matrix, and keeps the originals as
``*.pre-<suffix>.*.bak``. Non-KNN raw scores must still reproduce the stored ones to
1e-6, otherwise the run is reported and skipped (a real problem, not drift).

The permuted-formula control must then be rebuilt for the changed runs (delete their
``permuted/runs/<run_id>_permuted.json`` and re-run permuted_control_capped.py with
--skip-existing); this script prints the list.

Roots are given as ``<runs_glob>[:safe]`` where the optional ``:safe`` marker applies the
scripts/run_paper2_llm_schema_expansion.safe_columns() renaming before loading (for the
safe_names batches).

Usage:
  python rematerialize_after_evaluator_fix.py --suffix categorical-fix3 --report <csv> [--dry-run] \
      --roots 'results/judgments/*' 'results/expansion_offline/*/raw_names/runs/*' \
              'results/expansion_offline/*/safe_names/runs/*:safe' ...
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import dasef.experiments.paper1_pipeline as p1  # noqa: E402
from dasef.experiments.paper1_pipeline import EvaluationPlan, evaluate_matrix, schema_design_eval_split  # noqa: E402
from dasef.features.formula import materialize_formula_features  # noqa: E402
from dasef.io_utils import read_model  # noqa: E402
from dasef.schema import SchemaSpec  # noqa: E402

_ORIG_LOAD_DATASET = p1.load_dataset


def _install_safe_columns() -> None:
    from run_paper2_llm_schema_expansion import safe_columns

    p1.load_dataset = lambda name: safe_columns(_ORIG_LOAD_DATASET(name))


def _restore_load_dataset() -> None:
    p1.load_dataset = _ORIG_LOAD_DATASET


def _split_params(results: dict) -> tuple[float | None, int | None]:
    frac = seed = None
    for note in results.get("notes", []):
        m = re.search(r"fraction=([0-9.]+), seed=(\d+)", note)
        if m:
            frac, seed = float(m.group(1)), int(m.group(2))
    return frac, seed


def _same(a: pd.Series, b: pd.Series) -> bool:
    x = a.to_numpy(dtype=float)
    y = b.to_numpy(dtype=float)
    return np.array_equal(np.isnan(x), np.isnan(y)) and np.allclose(np.nan_to_num(x), np.nan_to_num(y), atol=1e-9)


def process_run(run_dir: Path, suffix: str, dry_run: bool) -> dict:
    res_path = run_dir / "results.json"
    fm_path = run_dir / "matrices" / "formula.parquet"
    results = json.loads(res_path.read_text())
    schema = read_model(run_dir / "schema.normalized.json", SchemaSpec)
    stored = pd.read_parquet(fm_path)
    names = [f.name for f in schema.formula_features]
    raw_cols = [c for c in stored.columns if c not in set(names)]
    remat = materialize_formula_features(stored[raw_cols], schema)
    changed = [n for n in names if n in stored.columns and not _same(stored[n], remat[n])]
    rec = {"run": str(run_dir.relative_to(ROOT)), "dataset": results["dataset"], "n_formula": len(names),
           "n_changed": len(changed), "changed": ";".join(changed)}
    if not changed:
        rec["status"] = "unchanged"
        return rec
    if dry_run:
        rec["status"] = "would update"
        return rec
    frac, seed = _split_params(results)
    ds = p1.load_dataset_for_experiment(results["dataset"], results.get("cap_rows"))
    if frac is not None:
        _, ds = schema_design_eval_split(ds, frac, seed)
    X_raw = ds.X.reset_index(drop=True)
    y = ds.y.reset_index(drop=True)
    if list(X_raw.columns) != raw_cols or len(X_raw) != len(stored):
        rec["status"] = "SKIPPED raw columns/rows do not match the stored matrix"
        return rec
    ev = {e["matrix_name"]: e for e in results["evaluations"]}
    models = list(ev["raw"]["models"].keys())
    plan = EvaluationPlan(downstream_models=models)
    raw_eval = evaluate_matrix(X_raw, y, "raw", plan)
    non_knn_ok = all(
        np.allclose(raw_eval.raw_scores[m][k], ev["raw"]["raw_scores"][m][k], atol=1e-6)
        for m in models if m != "knn" for k in raw_eval.raw_scores[m]
    )
    rec["non_knn_raw_reproduces"] = non_knn_ok
    if not non_knn_ok:
        rec["status"] = "SKIPPED non-KNN raw scores do not reproduce (investigate)"
        return rec
    X_new = pd.concat([X_raw, materialize_formula_features(X_raw, schema).reset_index(drop=True)], axis=1)
    assert list(X_new.columns) == list(stored.columns)
    fm_eval = evaluate_matrix(X_new, y, "raw_plus_formula", plan)
    for m in models:
        rec[f"{m}.roc_auc.formula.old"] = ev["raw_plus_formula"]["models"][m]["roc_auc_ovr"]
        rec[f"{m}.roc_auc.formula.new"] = fm_eval.models[m]["roc_auc_ovr"]
    # Core runs also hold a hybrid matrix (raw + formula + per-row judgment columns) that
    # embeds the same formula columns; rebuild it with the new formula values and
    # re-evaluate raw_plus_formula_plus_judgment so the judgment increment stays matched.
    hybrid_path = run_dir / "matrices" / "hybrid.parquet"
    hybrid_eval = None
    X_hybrid = None
    if hybrid_path.exists() and "raw_plus_formula_plus_judgment" in ev:
        stored_hybrid = pd.read_parquet(hybrid_path)
        judgment_cols = [c for c in stored_hybrid.columns if c not in stored.columns]
        assert list(stored_hybrid.columns) == list(stored.columns) + judgment_cols, run_dir
        assert len(stored_hybrid) == len(X_new), run_dir
        X_hybrid = pd.concat([X_new, stored_hybrid[judgment_cols].reset_index(drop=True)], axis=1)
        hybrid_eval = evaluate_matrix(X_hybrid, y, "raw_plus_formula_plus_judgment", plan)
        for m in models:
            rec[f"{m}.roc_auc.hybrid.old"] = ev["raw_plus_formula_plus_judgment"]["models"][m]["roc_auc_ovr"]
            rec[f"{m}.roc_auc.hybrid.new"] = hybrid_eval.models[m]["roc_auc_ovr"]
    bak_res = res_path.with_name(f"results.pre-{suffix}.json.bak")
    bak_fm = fm_path.with_name(f"formula.pre-{suffix}.parquet.bak")
    if not bak_res.exists():
        shutil.copy2(res_path, bak_res)
    if not bak_fm.exists():
        shutil.copy2(fm_path, bak_fm)
    replacements = [("raw", raw_eval), ("raw_plus_formula", fm_eval)]
    if hybrid_eval is not None:
        bak_h = hybrid_path.with_name(f"hybrid.pre-{suffix}.parquet.bak")
        if not bak_h.exists():
            shutil.copy2(hybrid_path, bak_h)
        replacements.append(("raw_plus_formula_plus_judgment", hybrid_eval))
    for name, ev_obj in replacements:
        idx = [i for i, e in enumerate(results["evaluations"]) if e["matrix_name"] == name][0]
        results["evaluations"][idx] = ev_obj.model_dump(mode="json")
    results.setdefault("notes", []).append(
        f"raw, raw_plus_formula{' and raw_plus_formula_plus_judgment' if hybrid_eval is not None else ''} re-evaluated together on {time.strftime('%Y-%m-%d')} after the formula-evaluator fix "
        f"'{suffix}' changed formula columns: {', '.join(changed)}. Originals kept as *.pre-{suffix}.*.bak."
    )
    res_path.write_text(json.dumps(results, indent=2))
    X_new.index = stored.index
    X_new.to_parquet(fm_path)
    if X_hybrid is not None:
        X_hybrid.index = stored.index
        X_hybrid.to_parquet(hybrid_path)
    rec["status"] = "updated"
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", required=True)
    ap.add_argument("--suffix", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    targets: list[tuple[Path, bool]] = []
    for spec in args.roots:
        pattern, safe = (spec[:-5], True) if spec.endswith(":safe") else (spec, False)
        for d in sorted(glob.glob(str(ROOT / pattern), recursive=True)):
            d = Path(d)
            if (d / "results.json").exists() and (d / "matrices" / "formula.parquet").exists() and (d / "schema.normalized.json").exists():
                targets.append((d, safe))
    rows: list[dict] = []
    cur_safe = None
    t0 = time.time()
    for i, (run_dir, safe) in enumerate(targets):
        if safe != cur_safe:
            (_install_safe_columns if safe else _restore_load_dataset)()
            cur_safe = safe
        try:
            rows.append(process_run(run_dir, args.suffix, args.dry_run))
        except Exception as exc:  # noqa: BLE001
            rows.append({"run": str(run_dir.relative_to(ROOT)), "status": f"ERROR {type(exc).__name__}: {exc}"})
        if rows[-1].get("status") != "unchanged":
            print(f"[{i + 1}/{len(targets)}] {rows[-1]}", flush=True)
        elif (i + 1) % 50 == 0:
            print(f"[{i + 1}/{len(targets)}] {time.time() - t0:.0f}s", flush=True)
    _restore_load_dataset()
    df = pd.DataFrame(rows)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.report, index=False)
    print("runs scanned:", len(df))
    print(df.status.value_counts().to_string())
    ch = df[df.status != "unchanged"]
    if len(ch):
        print(ch[["run", "dataset", "n_changed", "status"]].to_string())


if __name__ == "__main__":
    main()
