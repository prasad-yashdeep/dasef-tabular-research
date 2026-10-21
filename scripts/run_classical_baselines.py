#!/usr/bin/env python3
"""Corrected classical AutoFE baselines for DASEF (cap-then-split, design-fit / eval-transform).

Differences from scripts/run_classical_baselines.py (the run behind paper Table 8):

  1. Row protocol matches the main DASEF benchmark (results/judgments, aggregated by
     scripts/aggregate_dataset_level.py): the FULL dataset is capped first with the run's
     recorded ``cap_rows`` (5000 for adult_income, bank_marketing, electricity; None for the
     other seven), then split 30/70 with seed 42 via ``schema_design_eval_split``. The
     evaluation rows are therefore identical to the stored DASEF matrices, which is asserted
     at runtime (``--no-verify-alignment`` disables the assertion). The old script split first
     and capped the eval split afterwards (5000 eval rows instead of 3500 on the three big
     datasets, with different rows).

  2. Every classical system is FIT on the DESIGN split only (labels allowed there, mirroring
     the LLM seeing a summary of the design split) and the fitted generator is APPLIED to the
     evaluation split. No evaluation-split label is used outside the CV training folds. The
     old script fit OpenFE / autofeat / the MI selector on the whole eval split before CV.

  3. The numeric encoder (category codes, median imputation) is fitted on the design split.

Usage (from the repo root, with .venv active):
  python run_classical_baselines_corrected.py --out-dir <dir> [--datasets a b ...]
        [--openfe-n-jobs N] [--top-k 12] [--variants poly openfe autofeat featuretools]
        [--models xgboost logistic_regression random_forest knn] [--resume]
        [--previous-dir results/statistics/classical_baselines] [--no-verify-alignment]

Outputs (same format as results/statistics/classical_baselines/):
  fold_scores.csv, dataset_model_summary.csv, run_metadata.json, summary.md,
  deltas_vs_dasef_formula.csv  (per dataset x model x metric x variant, with DASEF deltas)
  per_dataset_delta_vs_previous.csv (corrected vs previous classical delta, per dataset)
"""
from __future__ import annotations

import argparse
import contextlib
import functools
import json
import os
import sys
import time
import traceback
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.preprocessing import LabelEncoder, PolynomialFeatures

ROOT = Path(os.environ.get("DASEF_ROOT", Path.cwd())).resolve()
if not (ROOT / "src" / "dasef").exists():
    raise SystemExit(f"Run from the repo root (or set DASEF_ROOT); no src/dasef under {ROOT}")
sys.path.insert(0, str(ROOT / "src"))

from dasef.datasets import LoadedDataset, load_dataset, schema_design_eval_split, stratified_cap  # noqa: E402
from dasef.evaluate import evaluate_classifier  # noqa: E402

DATASETS = [
    "adult_income",
    "bank_marketing",
    "blood_transfusion",
    "car_evaluation",
    "credit_g",
    "electricity",
    "phoneme",
    "pima_diabetes",
    "qsar_biodegradation",
    "spambase",
]
# Recorded cap_rows of the canonical results/judgments runs (used only when no run is found).
CANONICAL_CAP_ROWS: dict[str, int | None] = {"adult_income": 5000, "bank_marketing": 5000, "electricity": 5000}
SCHEMA_DESIGN_FRACTION = 0.3
SPLIT_SEED = 42
DOWNSTREAM_MODELS = ["xgboost", "logistic_regression", "random_forest", "knn"]
METRICS = ["accuracy", "balanced_accuracy", "f1_macro", "roc_auc_ovr"]
ALL_VARIANTS = ["poly", "openfe", "autofeat", "featuretools"]
JUDGMENTS_DIR = ROOT / "results" / "judgments"
DASEF_DELTAS = ROOT / "results" / "statistics" / "dataset_level" / "per_dataset_deltas.csv"
PREVIOUS_DIR = ROOT / "results" / "statistics" / "classical_baselines"


# --------------------------------------------------------------------------- utilities
@contextmanager
def silence_fds():
    """Silence Python and native-library writes to stdout/stderr."""
    stdout_fd = os.dup(1)
    stderr_fd = os.dup(2)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull_fd, 1)
        os.dup2(devnull_fd, 2)
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                yield
    finally:
        os.dup2(stdout_fd, 1)
        os.dup2(stderr_fd, 2)
        os.close(stdout_fd)
        os.close(stderr_fd)
        os.close(devnull_fd)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


class DesignNumericEncoder:
    """Label-free dense numeric encoding fitted on the design split and applied to any split."""

    def fit(self, X: pd.DataFrame) -> "DesignNumericEncoder":
        self.columns = list(X.columns)
        self.numeric: dict[str, bool] = {}
        self.categories: dict[str, dict] = {}
        self.medians: dict[str, float] = {}
        for col in X.columns:
            s = X[col]
            if is_numeric_dtype(s):
                self.numeric[col] = True
                v = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)
            else:
                self.numeric[col] = False
                cats = sorted(set(s.dropna().astype(str)))
                self.categories[col] = {c: float(i) for i, c in enumerate(cats)}
                v = s.astype(str).map(self.categories[col]).where(s.notna())
            med = float(v.median()) if v.notna().any() else 0.0
            self.medians[col] = med if np.isfinite(med) else 0.0
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=range(len(X)))
        for col in self.columns:
            s = X[col].reset_index(drop=True)
            if self.numeric[col]:
                v = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)
            else:
                v = s.astype(str).map(self.categories[col]).where(s.notna())
            out[col] = v.astype(float).fillna(self.medians[col])
        return out.astype(float)


def clean_generated(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    df = df.reset_index(drop=True).apply(pd.to_numeric, errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    df.columns = [f"{prefix}__{i:02d}" for i in range(df.shape[1])]
    return df


def with_raw(X_eval: pd.DataFrame, generated: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([X_eval.reset_index(drop=True), generated.reset_index(drop=True)], axis=1)


# --------------------------------------------------------------------------- feature systems
def make_poly(Xd: pd.DataFrame, yd: pd.Series, Xe: pd.DataFrame, top_k: int) -> tuple[pd.DataFrame | None, str, dict]:
    """Pairwise interaction-only products; top-k by mutual information on the DESIGN labels."""
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False).fit(Xd)
    names = poly.get_feature_names_out(Xd.columns)
    mask = np.array([" " in n for n in names])
    if mask.sum() == 0:
        return None, "poly produced no interaction features", {}
    arr_d = poly.transform(Xd)[:, mask]
    y_enc = LabelEncoder().fit_transform(yd.astype(str))
    k = min(top_k, arr_d.shape[1])
    score_fn = functools.partial(mutual_info_classif, random_state=SPLIT_SEED)
    selector = SelectKBest(score_func=score_fn, k=k).fit(arr_d, y_enc)
    idx = selector.get_support(indices=True)
    selected_names = [str(names[mask][i]).replace(" ", "__x__") for i in idx]
    arr_e = poly.transform(Xe)[:, mask][:, idx]
    generated = clean_generated(pd.DataFrame(arr_e), "poly")
    return generated, f"poly selected {generated.shape[1]} interactions by MI on design split", {"poly_features": selected_names}


def make_openfe(Xd: pd.DataFrame, yd: pd.Series, Xe: pd.DataFrame, top_k: int, n_jobs: int, tmp_dir: Path) -> tuple[pd.DataFrame | None, str, dict]:
    """OpenFE fit on the design split; features materialised on the eval split via transform()."""
    try:
        from openfe import OpenFE, tree_to_formula
    except Exception as exc:  # pragma: no cover
        return None, f"OpenFE import failed: {exc}", {}
    yd_enc = pd.Series(LabelEncoder().fit_transform(yd.astype(str)), name="target")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = str(tmp_dir / f"openfe_{os.getpid()}_{int(time.time() * 1000)}.feather")
    try:
        ofe = OpenFE()
        with silence_fds():
            features = ofe.fit(
                data=Xd.reset_index(drop=True),
                label=yd_enc,
                task="classification",
                n_data_blocks=2,
                min_candidate_features=100,
                is_stage1=True,
                n_repeats=1,
                n_jobs=n_jobs,
                seed=SPLIT_SEED,
                verbose=False,
                tmp_save_path=tmp_path,
            )
        features = list(features or [])[:top_k]
        if not features:
            return None, "OpenFE produced no features (fit on design split)", {}
        # OpenFE's global operators (GroupByThen*) need train and test transformed together;
        # this uses feature values of both splits but no labels.
        with silence_fds():
            _, Xe_t = ofe.transform(Xd.reset_index(drop=True), Xe.reset_index(drop=True), features, n_jobs=n_jobs)
        generated = clean_generated(Xe_t.iloc[:, Xd.shape[1]:], "openfe")
        formulas = []
        for f in features:
            try:
                formulas.append(tree_to_formula(f))
            except Exception:
                formulas.append("<unprintable>")
        return generated, f"OpenFE generated {generated.shape[1]} features; fit on design split, transformed on eval split", {"openfe_features": formulas}
    except Exception as exc:
        return None, f"OpenFE failed: {type(exc).__name__}: {exc}", {"openfe_traceback": traceback.format_exc()}
    finally:
        with contextlib.suppress(OSError):
            os.remove(tmp_path)


def _patch_autofeat_check_array() -> None:
    """autofeat 2.1.1 calls sklearn's check_array(force_all_finite=...) in transform(); sklearn>=1.6
    renamed the argument to ensure_all_finite and sklearn 1.8 removed the alias. The old script only
    used fit_transform(), which avoids that call path; the separate transform() needs this shim."""
    import inspect

    import sklearn.utils.validation as _validation

    if "ensure_all_finite" not in inspect.signature(_validation.check_array).parameters:
        return
    original = _validation.check_array

    def compat_check_array(*args, **kwargs):
        if "force_all_finite" in kwargs:
            kwargs["ensure_all_finite"] = kwargs.pop("force_all_finite")
        return original(*args, **kwargs)

    for mod_name in ("autofeat.autofeat", "autofeat.featsel"):
        try:
            mod = __import__(mod_name, fromlist=["check_array"])
            if getattr(mod, "check_array", None) is original:
                mod.check_array = compat_check_array
        except Exception:
            pass


def make_autofeat(Xd: pd.DataFrame, yd: pd.Series, Xe: pd.DataFrame) -> tuple[pd.DataFrame | None, str, dict]:
    """autofeat fit on the design split; transform() applied to the eval split."""
    try:
        from autofeat import AutoFeatClassifier
    except Exception as exc:  # pragma: no cover
        return None, f"autofeat import failed: {exc}", {}
    if not hasattr(pd.Series, "ravel"):  # pandas>=3 removed Series.ravel, autofeat still calls it
        pd.Series.ravel = lambda self: self.to_numpy().ravel()  # type: ignore[attr-defined]
    _patch_autofeat_check_array()
    y_enc = LabelEncoder().fit_transform(yd.astype(str))
    try:
        model = AutoFeatClassifier(
            feateng_steps=1,
            featsel_runs=1,
            transformations=("log", "sqrt", "^2"),
            n_jobs=-1,
            verbose=0,
        )
        with silence_fds():
            model.fit(Xd.reset_index(drop=True), y_enc)
            Xe_t = model.transform(Xe.reset_index(drop=True))
        original = set(str(c) for c in model.original_columns_)
        gen_cols = [c for c in Xe_t.columns if str(c) not in original]
        if not gen_cols:
            return None, "autofeat produced no additional features (fit on design split)", {}
        generated = clean_generated(Xe_t[gen_cols], "autofeat")
        return generated, f"autofeat generated {generated.shape[1]} features; fit on design split, transformed on eval split", {"autofeat_features": [str(c) for c in gen_cols]}
    except Exception as exc:
        return None, f"autofeat failed: {type(exc).__name__}: {exc}", {"autofeat_traceback": traceback.format_exc()}


def make_featuretools(Xd: pd.DataFrame, yd: pd.Series, Xe: pd.DataFrame, top_k: int) -> tuple[pd.DataFrame | None, str, dict]:
    """OPTIONAL and UNTESTED (featuretools is not installed in .venv): single-table DFS with
    arithmetic transform primitives, top-k selected by MI on the design labels."""
    try:
        import featuretools as ft
    except Exception as exc:
        return None, f"featuretools import failed: {exc}", {}
    try:
        def entityset(X: pd.DataFrame):
            df = X.reset_index(drop=True).copy()
            df.insert(0, "_row_id", np.arange(len(df)))
            es = ft.EntitySet(id="dasef")
            es = es.add_dataframe(dataframe_name="rows", dataframe=df, index="_row_id")
            return es

        prims = ["multiply_numeric", "add_numeric", "subtract_numeric", "divide_numeric"]
        with silence_fds():
            fm_d, defs = ft.dfs(entityset=entityset(Xd), target_dataframe_name="rows", trans_primitives=prims, agg_primitives=[], max_depth=1)
        new_defs = [d for d in defs if d.get_name() not in set(Xd.columns)]
        if not new_defs:
            return None, "featuretools produced no additional features", {}
        arr_d = fm_d[[d.get_name() for d in new_defs]].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=float)
        y_enc = LabelEncoder().fit_transform(yd.astype(str))
        k = min(top_k, arr_d.shape[1])
        selector = SelectKBest(score_func=functools.partial(mutual_info_classif, random_state=SPLIT_SEED), k=k).fit(arr_d, y_enc)
        chosen = [new_defs[i] for i in selector.get_support(indices=True)]
        with silence_fds():
            fm_e = ft.calculate_feature_matrix(features=chosen, entityset=entityset(Xe))
        generated = clean_generated(fm_e[[d.get_name() for d in chosen]], "featuretools")
        return generated, f"featuretools generated {generated.shape[1]} features; fit/selected on design split", {"featuretools_features": [d.get_name() for d in chosen]}
    except Exception as exc:
        return None, f"featuretools failed: {type(exc).__name__}: {exc}", {"featuretools_traceback": traceback.format_exc()}


# --------------------------------------------------------------------------- protocol helpers
def canonical_run_for(dataset: str) -> tuple[dict | None, Path | None]:
    """First deepseek-reasoner run in results/judgments for this dataset (the Table 8 source)."""
    if not JUDGMENTS_DIR.exists():
        return None, None
    for run_dir in sorted(JUDGMENTS_DIR.iterdir()):
        rf = run_dir / "results.json"
        jd = run_dir / "judgments"
        if not rf.exists() or not jd.exists():
            continue
        try:
            files = list(jd.iterdir())
            if not files or json.loads(files[0].read_text()).get("model") != "deepseek-reasoner":
                continue
            data = json.loads(rf.read_text())
        except Exception:
            continue
        if data.get("dataset") == dataset:
            return data, run_dir
    return None, None


def load_design_eval(dataset: str) -> tuple[LoadedDataset, LoadedDataset, dict]:
    """Cap-then-split exactly like run_schema_evaluation with the recorded cap_rows."""
    run, run_dir = canonical_run_for(dataset)
    if run is not None:
        cap_rows = run.get("cap_rows")
        cap_source = f"recorded in {run_dir}"
    else:
        cap_rows = CANONICAL_CAP_ROWS.get(dataset)
        cap_source = "CANONICAL_CAP_ROWS fallback (no results/judgments run found)"
    ds = load_dataset(dataset)
    n_total = len(ds.X)
    if cap_rows:
        ds = stratified_cap(ds, int(cap_rows), random_state=SPLIT_SEED)
    design, evaluation = schema_design_eval_split(ds, SCHEMA_DESIGN_FRACTION, SPLIT_SEED)
    info = {
        "cap_rows": cap_rows,
        "cap_source": cap_source,
        "total_rows": n_total,
        "capped_rows": len(ds.X),
        "design_rows": len(design.X),
        "eval_rows": len(evaluation.X),
        "canonical_run": str(run_dir) if run_dir else None,
    }
    return design, evaluation, info


def verify_alignment(dataset: str, X_eval: pd.DataFrame, run: dict | None) -> dict:
    """Assert the eval split's raw columns are row-identical to the stored DASEF formula matrix."""
    if run is None:
        return {"alignment_verified": False, "alignment_note": "no canonical run found"}
    fm = run.get("artifacts", {}).get("formula_matrix")
    path = ROOT / fm if fm and not Path(fm).is_absolute() else Path(fm) if fm else None
    if path is None or not path.exists():
        return {"alignment_verified": False, "alignment_note": f"formula matrix missing: {fm}"}
    mat = pd.read_parquet(path)
    raw_cols = [c for c in X_eval.columns if c in mat.columns]
    if len(raw_cols) != X_eval.shape[1] or len(mat) != len(X_eval):
        raise RuntimeError(f"alignment: {dataset} eval has {len(X_eval)}x{X_eval.shape[1]} but stored matrix has {len(mat)} rows / {len(raw_cols)} matching raw cols")
    a = X_eval[raw_cols].reset_index(drop=True)
    b = mat[raw_cols].reset_index(drop=True)
    for c in raw_cols:
        if not (a[c].astype(str).values == b[c].astype(str).values).all():
            raise RuntimeError(f"alignment: {dataset} raw column {c!r} differs from stored matrix {path}")
    return {"alignment_verified": True, "alignment_note": f"raw columns identical to {path} ({len(mat)} rows)"}


# --------------------------------------------------------------------------- evaluation / outputs
def evaluate_matrix(dataset: str, variant: str, X: pd.DataFrame, y: pd.Series, models: list[str]) -> list[dict]:
    rows: list[dict] = []
    for model in models:
        start = time.time()
        result = evaluate_classifier(X, y, model, n_splits=5, n_repeats=2, random_state=SPLIT_SEED)
        elapsed = time.time() - start
        for metric, scores in result.raw_scores.items():
            for fold_idx, score in enumerate(scores):
                rows.append({
                    "dataset": dataset,
                    "variant": variant,
                    "downstream_model": model,
                    "metric": metric,
                    "fold": fold_idx,
                    "score": score,
                    "n_rows": len(X),
                    "n_columns": X.shape[1],
                    "elapsed_seconds_model": elapsed,
                })
    return rows


def load_dasef_formula_deltas(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df[(df["baseline"] == "raw") & (df["candidate"] == "raw_plus_formula")].copy()


def build_delta_table(summary_df: pd.DataFrame, dasef: pd.DataFrame, variants: list[str]) -> pd.DataFrame:
    rows = []
    for (dataset, model, metric), group in summary_df.groupby(["dataset", "downstream_model", "metric"]):
        raw = group[group["variant"] == "raw"]["mean_score"]
        if raw.empty:
            continue
        raw_score = float(raw.iloc[0])
        for variant in [f"raw+{v}" for v in variants]:
            cand = group[group["variant"] == variant]["mean_score"]
            if cand.empty:
                continue
            row = {"dataset": dataset, "model": model, "metric": metric, "variant": variant, "classical_delta": float(cand.iloc[0] - raw_score)}
            if not dasef.empty:
                match = dasef[(dasef["dataset"] == dataset) & (dasef["downstream_model"] == model) & (dasef["metric"] == metric)]
                if not match.empty:
                    row["dasef_formula_delta"] = float(match["delta"].mean())
                    row["classical_minus_dasef"] = row["classical_delta"] - row["dasef_formula_delta"]
            rows.append(row)
    return pd.DataFrame(rows)


def build_previous_comparison(delta_df: pd.DataFrame, previous_dir: Path, metadata: list[dict]) -> pd.DataFrame:
    prev_path = previous_dir / "deltas_vs_dasef_formula.csv"
    if delta_df.empty or not prev_path.exists():
        return pd.DataFrame()
    prev = pd.read_csv(prev_path)[["dataset", "model", "metric", "variant", "classical_delta"]].rename(columns={"classical_delta": "classical_delta_previous"})
    prev_rows = {}
    meta_path = previous_dir / "run_metadata.json"
    if meta_path.exists():
        prev_rows = {m["dataset"]: m.get("eval_rows") for m in json.loads(meta_path.read_text())}
    cur_rows = {m["dataset"]: m.get("eval_rows") for m in metadata}
    out = delta_df[["dataset", "model", "metric", "variant", "classical_delta"]].rename(columns={"classical_delta": "classical_delta_corrected"})
    out = out.merge(prev, on=["dataset", "model", "metric", "variant"], how="left")
    out["change_corrected_minus_previous"] = out["classical_delta_corrected"] - out["classical_delta_previous"]
    out["eval_rows_corrected"] = out["dataset"].map(cur_rows)
    out["eval_rows_previous"] = out["dataset"].map(prev_rows)
    return out


def write_summary(out_dir: Path, summary_df: pd.DataFrame, metadata: list[dict], delta_df: pd.DataFrame, prev_df: pd.DataFrame, variants: list[str], models: list[str]) -> None:
    lines = [
        "# Classical Feature Engineering Baselines (corrected protocol)",
        "",
        "Scope: cap-then-split identical to the main DASEF benchmark (`stratified_cap(ds, recorded cap_rows)` then",
        f"`schema_design_eval_split(ds, {SCHEMA_DESIGN_FRACTION}, {SPLIT_SEED})`); evaluation rows are row-identical to the stored DASEF matrices.",
        "Each classical system is fit on the design split only (labels allowed there) and applied to the evaluation split;",
        "no evaluation-split label is used outside the CV training folds.",
        f"CV: 5-fold x 2-repeat with {', '.join(f'`{m}`' for m in models)}.",
        "",
        "## Run Status",
        "",
    ]
    status_rows = []
    for item in metadata:
        row = {
            "dataset": item["dataset"],
            "cap_rows": item.get("cap_rows"),
            "design_rows": item.get("design_rows"),
            "eval_rows": item.get("eval_rows"),
            "raw_cols": item.get("raw_cols"),
            "aligned": item.get("alignment_verified"),
        }
        for v in variants:
            row[f"{v}_status"] = item.get(f"{v}_status", "")
            row[f"{v}_fit_s"] = round(item.get(f"{v}_fit_seconds", float("nan")), 1) if item.get(f"{v}_fit_seconds") is not None else None
        if item.get("error"):
            row["error"] = item["error"]
        status_rows.append(row)
    lines.append(pd.DataFrame(status_rows).to_markdown(index=False))
    lines.extend(["", "## Mean Deltas vs Raw", ""])
    if delta_df.empty:
        lines.append("_No deltas available._")
    else:
        compact = (
            delta_df.groupby(["variant", "metric", "model"], as_index=False)
            .agg(mean_classical_delta=("classical_delta", "mean"), mean_dasef_formula_delta=("dasef_formula_delta", "mean") if "dasef_formula_delta" in delta_df else ("classical_delta", "size"), n=("classical_delta", "count"))
            .sort_values(["metric", "model", "variant"])
        )
        lines.append(compact.to_markdown(index=False, floatfmt=".4f"))
        lines.extend(["", "Dataset-level comparison was also saved to `deltas_vs_dasef_formula.csv`.", ""])
    if not prev_df.empty:
        lines.extend(["## Change vs previous run (split-then-cap, label-selected on eval split)", ""])
        comp = (
            prev_df.groupby(["variant", "metric", "model"], as_index=False)
            .agg(mean_corrected=("classical_delta_corrected", "mean"), mean_previous=("classical_delta_previous", "mean"), mean_change=("change_corrected_minus_previous", "mean"), n=("classical_delta_corrected", "count"))
            .sort_values(["metric", "model", "variant"])
        )
        lines.append(comp.to_markdown(index=False, floatfmt=".4f"))
        lines.extend(["", "Per-dataset comparison saved to `per_dataset_delta_vs_previous.csv`.", ""])
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_outputs(out_dir: Path, all_rows: list[dict], metadata: list[dict], args: argparse.Namespace) -> None:
    fold_df = pd.DataFrame(all_rows)
    fold_df.to_csv(out_dir / "fold_scores.csv", index=False)
    (out_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    if fold_df.empty:
        return
    summary_df = fold_df.groupby(["dataset", "variant", "downstream_model", "metric"], as_index=False).agg(mean_score=("score", "mean"), std_score=("score", "std"), n_folds=("score", "count"))
    summary_df.to_csv(out_dir / "dataset_model_summary.csv", index=False)
    delta_df = build_delta_table(summary_df, load_dasef_formula_deltas(Path(args.dasef_deltas)), args.variants)
    if not delta_df.empty:
        delta_df.to_csv(out_dir / "deltas_vs_dasef_formula.csv", index=False)
    prev_df = build_previous_comparison(delta_df, Path(args.previous_dir), metadata)
    if not prev_df.empty:
        prev_df.to_csv(out_dir / "per_dataset_delta_vs_previous.csv", index=False)
    write_summary(out_dir, summary_df, metadata, delta_df, prev_df, args.variants, args.models)


# --------------------------------------------------------------------------- main
def run_dataset(name: str, args: argparse.Namespace, out_dir: Path) -> tuple[list[dict], dict]:
    item: dict = {"dataset": name, "started_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    rows: list[dict] = []
    t0 = time.time()
    design, evaluation, info = load_design_eval(name)
    item.update(info)
    item["raw_cols"] = evaluation.X.shape[1]
    log(f"{name}: total={info['total_rows']} cap_rows={info['cap_rows']} design={info['design_rows']} eval={info['eval_rows']} cols={item['raw_cols']}")
    run, _ = canonical_run_for(name)
    if args.verify_alignment:
        item.update(verify_alignment(name, evaluation.X, run))
        log(f"{name}: {item.get('alignment_note')}")

    encoder = DesignNumericEncoder().fit(design.X)
    Xd, Xe = encoder.transform(design.X), encoder.transform(evaluation.X)
    yd, ye = design.y.reset_index(drop=True), evaluation.y.reset_index(drop=True)
    X_eval_raw = evaluation.X.reset_index(drop=True)

    matrices: dict[str, pd.DataFrame] = {"raw": X_eval_raw}
    for variant in args.variants:
        start = time.time()
        if variant == "poly":
            generated, status, extra = make_poly(Xd, yd, Xe, args.top_k)
        elif variant == "openfe":
            generated, status, extra = make_openfe(Xd, yd, Xe, args.top_k, args.openfe_n_jobs, out_dir / "tmp")
        elif variant == "autofeat":
            generated, status, extra = make_autofeat(Xd, yd, Xe)
        elif variant == "featuretools":
            generated, status, extra = make_featuretools(Xd, yd, Xe, args.top_k)
        else:
            raise ValueError(variant)
        item[f"{variant}_fit_seconds"] = round(time.time() - start, 2)
        item[f"{variant}_status"] = status
        item.update(extra)
        log(f"{name}: {variant}: {status} ({item[f'{variant}_fit_seconds']}s)")
        if generated is not None:
            if len(generated) != len(X_eval_raw):
                raise RuntimeError(f"{variant} returned {len(generated)} rows for {len(X_eval_raw)} eval rows")
            matrices[f"raw+{variant}"] = with_raw(X_eval_raw, generated)
            item[f"{variant}_cols"] = matrices[f"raw+{variant}"].shape[1]

    for variant, X_mat in matrices.items():
        start = time.time()
        rows.extend(evaluate_matrix(name, variant, X_mat, ye, args.models))
        item[f"eval_seconds_{variant}"] = round(time.time() - start, 2)
        log(f"{name}: evaluated {variant} {X_mat.shape[0]}x{X_mat.shape[1]} in {item[f'eval_seconds_{variant}']}s")
    item["total_seconds"] = round(time.time() - t0, 2)
    return rows, item


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", required=True, help="output directory (created)")
    p.add_argument("--datasets", nargs="+", default=DATASETS)
    p.add_argument("--variants", nargs="+", default=["poly", "openfe", "autofeat"], choices=ALL_VARIANTS)
    p.add_argument("--models", nargs="+", default=DOWNSTREAM_MODELS)
    p.add_argument("--top-k", type=int, default=12)
    p.add_argument("--openfe-n-jobs", type=int, default=1)
    p.add_argument("--previous-dir", default=str(PREVIOUS_DIR), help="old classical_baselines dir for the change-vs-previous CSV")
    p.add_argument("--dasef-deltas", default=str(DASEF_DELTAS))
    p.add_argument("--no-verify-alignment", dest="verify_alignment", action="store_false")
    p.add_argument("--resume", action="store_true", help="skip datasets already present in out-dir/run_metadata.json")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    metadata: list[dict] = []
    if args.resume and (out_dir / "run_metadata.json").exists():
        metadata = [m for m in json.loads((out_dir / "run_metadata.json").read_text()) if not m.get("error")]
        done = {m["dataset"] for m in metadata}
        if (out_dir / "fold_scores.csv").exists():
            prev = pd.read_csv(out_dir / "fold_scores.csv")
            all_rows = prev[prev["dataset"].isin(done)].to_dict("records")
        log(f"resume: {sorted(done)} already done")
    else:
        done = set()

    (out_dir / "run_args.json").write_text(json.dumps({**vars(args), "root": str(ROOT), "started_at": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=2), encoding="utf-8")
    run_start = time.time()
    for name in args.datasets:
        if name in done:
            continue
        log(f"=== {name} ===")
        try:
            rows, item = run_dataset(name, args, out_dir)
            all_rows.extend(rows)
        except Exception as exc:
            item = {"dataset": name, "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}
            log(f"ERROR {name}: {item['error']}")
        metadata.append(item)
        write_outputs(out_dir, all_rows, metadata, args)
    log(f"done in {time.time() - run_start:.1f}s; outputs in {out_dir}")


if __name__ == "__main__":
    main()
