#!/usr/bin/env python
"""Random-formula control for the two-tier benchmark (no LLM calls).

For every (dataset, generator) cell of the linear/SVM benchmark, build a schema of k random but
syntactically valid formulas over the dataset's own columns, where k is the number of formula
features in that cell's LLM schema. The random generator sees exactly what the LLM generators
saw (the design-split column statistics: mean, std, min, max, top categories) and draws from the
same vocabulary the LLM formulas use (log1p, z-scores, min-max scaling, ratios, products, sums,
differences, threshold and two-way indicators, three-way buckets, category indicators). The random
formulas are materialized on the evaluation rows with the same evaluator (``materialize_formula_
features``, including range clipping), scored with the same repeated stratified folds (seed 42)
and the same four downstream models, and their columns are then independently row-permuted
(seed 42) exactly as in the paper's column-permutation control.

Three questions the output answers, at the dataset level (generator-averaged, exact Wilcoxon,
Holm over the four models, bootstrap CIs, same code as aggregate_benchmark44.py):
  random_formula_vs_raw       do random valid formulas help at all?
  random_formula_semantic     do random formulas beat their own permuted copies (how much of the
                              paper's semantic contrast is generic to any row-aligned function)?
  llm_vs_random_formula       do the LLM's formula choices beat random choices of the same size
                              and vocabulary?  (the control a sceptical reviewer asks for)

Usage
  python scripts/expansion/random_formula_control.py evaluate  [--workers 8] [--limit N] [--skip-existing]
  python scripts/expansion/random_formula_control.py aggregate
Outputs under results/statistics/random_formula_control/.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "expansion"))
os.chdir(ROOT)

GENERATORS = ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-4.7", "claude-sonnet-4.6"]
MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]
OUT_DIR = ROOT / "results/statistics/random_formula_control"
SCHEMA_VERSION = "random-formula-control-v2"


# ----------------------------------------------------------------------------- cells
def list_cells() -> list[dict]:
    cells = []
    core = pd.read_csv(ROOT / "results/statistics/benchmark44_core_run_level.csv")
    for (dataset, run_id, gen), _ in core.groupby(["dataset", "run_id", "generator"]):
        cells.append({"dataset": dataset, "run_id": run_id, "generator": gen, "tier": "core",
                      "run_dir": str(ROOT / "results/judgments" / run_id), "safe_columns": False})
    for gen in GENERATORS:
        for batch in ["raw_names", "safe_names"]:
            f = ROOT / f"results/expansion_offline/{gen}/{batch}/permuted/run_level_scores_gen.csv"
            if not f.exists():
                continue
            used = pd.read_csv(f)[["dataset", "run_id"]].drop_duplicates()
            for dataset, run_id in used.itertuples(index=False):
                cells.append({"dataset": dataset, "run_id": run_id, "generator": gen, "tier": "expansion",
                              "run_dir": str(ROOT / f"results/expansion_offline/{gen}/{batch}/runs/{run_id}"),
                              "safe_columns": batch == "safe_names"})
    return cells


def stable_seed(*parts: str) -> int:
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:8], 16)


# ----------------------------------------------------------------------------- random schema
def _ref(col: str) -> str:
    return col if col.isidentifier() else f"`{col}`"


def _f(x: float) -> str:
    return f"{float(x):.6g}"


def random_schema(X_design: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str], k: int,
                  rng: np.random.Generator, dataset: str, generator: str):
    """k random formulas drawn from the LLM formulas' vocabulary using only design-split statistics."""
    from dasef.features.formula import materialize_formula_features
    from dasef.schema import FeatureSpec, FeatureType, SchemaSpec

    num = [c for c in numeric_cols if c in X_design.columns and pd.api.types.is_numeric_dtype(X_design[c])]
    cat = [c for c in categorical_cols if c in X_design.columns and c not in num]
    stats = {}
    for c in num:
        s = pd.to_numeric(X_design[c], errors="coerce")
        stats[c] = {"mean": float(s.mean()), "std": float(s.std(ddof=0)) if s.notna().sum() > 1 else 0.0,
                    "min": float(s.min()), "max": float(s.max())}
    tops = {c: [str(v) for v in X_design[c].astype(str).value_counts().index[:10]] for c in cat}

    def unary(t: str, a: str) -> str:
        m, sd, lo, hi = stats[a]["mean"], stats[a]["std"], stats[a]["min"], stats[a]["max"]
        r = _ref(a)
        return {
            "log1p": f"np.log1p(np.abs({r}))",
            "zscore": f"({r} - {_f(m)}) / ({_f(sd)} + 1e-6)",
            "minmax": f"np.clip(({r} - {_f(lo)}) / ({_f(hi - lo)} + 1e-6), 0.0, 1.0)",
            "square": f"{r} ** 2",
            "sqrt_abs": f"np.sqrt(np.abs({r}))",
            "threshold": f"np.where({r} > {_f(m)}, 1, 0)",
            "bucket3": f"np.where({r} < {_f(m - sd)}, 0, np.where({r} > {_f(m + sd)}, 2, 1))",
        }[t]

    def binary(t: str, a: str, b: str) -> str:
        ra, rb = _ref(a), _ref(b)
        ma, mb, sa, sb = stats[a]["mean"], stats[b]["mean"], stats[a]["std"], stats[b]["std"]
        return {
            "ratio": f"{ra} / (np.abs({rb}) + 1e-6)",
            "product": f"{ra} * {rb}",
            "difference": f"{ra} - {rb}",
            "sum": f"{ra} + {rb}",
            "share": f"{ra} / (np.abs({ra}) + np.abs({rb}) + 1e-6)",
            "both_high": f"np.where(({ra} > {_f(ma)}) & ({rb} > {_f(mb)}), 1, 0)",
            "zsum": f"(({ra} - {_f(ma)}) / ({_f(sa)} + 1e-6)) + (({rb} - {_f(mb)}) / ({_f(sb)} + 1e-6))",
        }[t]

    UNARY = ["log1p", "zscore", "minmax", "square", "sqrt_abs", "threshold", "bucket3"]
    BINARY = ["ratio", "product", "difference", "sum", "share", "both_high", "zsum"]
    p_cat = (len(cat) / (len(cat) + len(num))) if (cat and num) else (1.0 if cat else 0.0)

    features: list[FeatureSpec] = []
    used_names: set[str] = set()
    used_exprs: set[str] = set()
    attempts = 0
    while len(features) < k and attempts < 40 * k:
        attempts += 1
        if cat and (not num or rng.random() < p_cat):
            if len(cat) >= 2 and rng.random() < 0.25:
                c1, c2 = rng.choice(cat, size=2, replace=False)
                if set(tops[c1]) & set(tops[c2]):
                    template, expr = "cat_match", f"np.where({_ref(c1)} == {_ref(c2)}, 1, 0)"
                else:
                    continue
            else:
                c = str(rng.choice(cat))
                if not tops[c]:
                    continue
                v = str(rng.choice(tops[c]))
                template, expr = "cat_indicator", f"np.where({_ref(c)} == {v!r}, 1, 0)"
        else:
            if len(num) >= 2 and rng.random() < 0.6:
                a, b = (str(x) for x in rng.choice(num, size=2, replace=False))
                template = str(rng.choice(BINARY))
                expr = binary(template, a, b)
            else:
                a = str(rng.choice(num))
                template = str(rng.choice(UNARY))
                expr = unary(template, a)
        if expr in used_exprs:
            continue  # no duplicate formulas within a schema (LLM schemas never repeat a formula)
        name = f"rf{len(features) + 1:02d}_{template}"
        if name in used_names:
            continue
        probe = FeatureSpec(name=name, type=FeatureType.formula, description=f"random {template} formula", value_range=(-1e12, 1e12),
                            feature_family="random_control", expected_model_benefit="none (control)", leakage_risk="low", formula=expr)
        probe_schema = SchemaSpec(dataset_name=dataset, model_family="linear_svm", schema_generator="random-formula-control",
                                  schema_version=SCHEMA_VERSION, features=[probe])
        col = materialize_formula_features(X_design, probe_schema)[name]
        finite = col.replace([np.inf, -np.inf], np.nan).dropna()
        if finite.empty or finite.nunique() <= 1:
            continue  # all-NaN or constant on the design split: redraw, as a careful generator would
        lo, hi = float(finite.min()), float(finite.max())
        if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
            continue
        features.append(FeatureSpec(name=name, type=FeatureType.formula, description=f"random {template} formula over the dataset's own columns",
                                    value_range=(lo, hi), feature_family="random_control", expected_model_benefit="none (control)",
                                    leakage_risk="low", formula=expr))
        used_names.add(name)
        used_exprs.add(expr)
    return SchemaSpec(dataset_name=dataset, model_family="linear_svm", schema_generator="random-formula-control",
                      schema_version=SCHEMA_VERSION, features=features,
                      metadata={"matched_generator": generator, "design_statistics_only": True, "attempts": attempts})


# ----------------------------------------------------------------------------- one cell
def evaluate_cell(cell: dict, out_dir: str, skip_existing: bool = True, n_splits: int = 5, n_repeats: int = 2,
                  cv_seed: int = 42, perm_seed: int = 42, draw: int = 0) -> str:
    out_file = Path(out_dir) / "cells" / (f"{cell['run_id']}.json" if draw == 0 else f"{cell['run_id']}.d{draw}.json")
    if skip_existing and out_file.exists():
        return f"skip {cell['run_id']} {cell['dataset']} ({cell['generator']}) draw {draw}: exists"
    t0 = time.time()
    try:
        from dasef.datasets import load_dataset, raw_block_equal, schema_design_eval_split, stratified_cap
        from dasef.evaluate import evaluate_classifier
        from dasef.features.formula import materialize_formula_features

        run_dir = Path(cell["run_dir"])
        res = json.loads((run_dir / "results.json").read_text())
        llm_schema = json.loads((run_dir / "schema.normalized.json").read_text())
        k = sum(1 for f in llm_schema["features"] if f["type"] == "formula")
        ds = load_dataset(cell["dataset"])
        if cell["safe_columns"]:
            from run_paper2_llm_schema_expansion import safe_columns
            ds = safe_columns(ds)
        if res.get("cap_rows"):
            ds = stratified_cap(ds, res["cap_rows"])
        design, evald = schema_design_eval_split(ds, 0.3, 42)
        X_eval = evald.X.reset_index(drop=True)
        y_eval = evald.y.reset_index(drop=True)
        fdf = pd.read_parquet(run_dir / "matrices" / "formula.parquet").reset_index(drop=True)
        raw_cols = list(X_eval.columns)
        if len(fdf) != len(y_eval) or not raw_block_equal(fdf[raw_cols], X_eval[raw_cols]):
            raise RuntimeError("evaluation rows do not match the stored formula matrix")
        seed_parts = (cell["dataset"], cell["generator"], SCHEMA_VERSION) + (() if draw == 0 else (f"draw{draw}",))
        rng = np.random.default_rng(stable_seed(*seed_parts))
        # integer-coded categoricals were shown to the generators as numbers, so the random generator sees them as numbers too
        override = list(getattr(design, "onehot_override_columns", []))
        X_design = design.X.reset_index(drop=True).copy()
        for c in override:
            X_design[c] = X_design[c].astype(float)
        schema = random_schema(X_design, design.numeric_columns + override, [c for c in design.categorical_columns if c not in override], k, rng,
                               cell["dataset"], cell["generator"])
        formula_df = materialize_formula_features(X_eval, schema)
        rf_cols = list(formula_df.columns)
        nan_rate = {c: float(formula_df[c].isna().mean()) for c in rf_cols}
        const_cols = [c for c in rf_cols if formula_df[c].nunique(dropna=True) <= 1]
        X_rf = pd.concat([X_eval, formula_df], axis=1)
        prng = np.random.default_rng(perm_seed)
        X_rfp = X_rf.copy()
        for c in rf_cols:
            X_rfp[c] = prng.permutation(X_rfp[c].values)
        out = {"cell": cell, "draw": draw, "k_llm_formulas": k, "k_random_formulas": len(rf_cols), "n_rows": int(len(X_rf)),
               "schema": json.loads(schema.model_dump_json()), "formula_nan_rate": nan_rate, "formula_constant_cols": const_cols,
               "cv": {"n_splits": n_splits, "n_repeats": n_repeats, "seed": cv_seed}, "permutation_seed": perm_seed, "models": {}}
        ev = {e["matrix_name"]: e for e in res["evaluations"]}
        for m in MODELS:
            tm = time.time()
            r1 = evaluate_classifier(X_rf, y_eval, m, n_splits=n_splits, n_repeats=n_repeats, random_state=cv_seed)
            r2 = evaluate_classifier(X_rfp, y_eval, m, n_splits=n_splits, n_repeats=n_repeats, random_state=cv_seed)
            out["models"][m] = {
                "raw_plus_random_formula_fx": r1.metrics, "raw_plus_random_formula_fx_raw_scores": r1.raw_scores,
                "raw_plus_permuted_random_formula_fx": r2.metrics, "raw_plus_permuted_random_formula_fx_raw_scores": r2.raw_scores,
                "stored_raw": ev["raw"]["models"][m], "stored_raw_plus_formula": ev["raw_plus_formula"]["models"][m],
                "stored_raw_plus_random_noise": ev.get("raw_plus_random_formula", {}).get("models", {}).get(m),
                "seconds": round(time.time() - tm, 1),
            }
        out["seconds_total"] = round(time.time() - t0, 1)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(out, indent=1))
        lr = out["models"]["logistic_regression"]
        return (f"done {cell['run_id']} {cell['dataset']} ({cell['generator']}, {cell['tier']}) draw {draw}: k={k}->{len(rf_cols)} "
                f"const={len(const_cols)} LR raw={lr['stored_raw']['roc_auc_ovr']:.4f} llm={lr['stored_raw_plus_formula']['roc_auc_ovr']:.4f} "
                f"randfx={lr['raw_plus_random_formula_fx']['roc_auc_ovr']:.4f} randfx_perm={lr['raw_plus_permuted_random_formula_fx']['roc_auc_ovr']:.4f} "
                f"{out['seconds_total']}s")
    except Exception as exc:  # keep the pool alive; record the failure
        err = Path(out_dir) / "cells" / f"{cell['run_id']}.d{draw}.error.txt"
        err.parent.mkdir(parents=True, exist_ok=True)
        err.write_text(traceback.format_exc())
        return f"ERROR {cell['run_id']} {cell['dataset']} ({cell['generator']}): {type(exc).__name__}: {exc}"


def _worker(args):
    return evaluate_cell(*args)


# ----------------------------------------------------------------------------- aggregate
def aggregate(out_dir: Path) -> None:
    from aggregate_benchmark44 import boot_ci, exact_p, holm  # same tests as the paper

    draw_rows = []
    for f in sorted((out_dir / "cells").glob("*.json")):
        if f.name.endswith(".error.txt"):
            continue
        d = json.loads(f.read_text())
        c = d["cell"]
        for m in MODELS:
            for met in METRICS:
                mm = d["models"][m]
                draw_rows.append({"dataset": c["dataset"], "run_id": c["run_id"], "generator": c["generator"], "tier": c["tier"],
                                  "draw": int(d.get("draw", 0)), "model": m, "metric": met, "k_llm": d["k_llm_formulas"],
                                  "k_random": d["k_random_formulas"], "n_constant_random_cols": len(d["formula_constant_cols"]),
                                  "raw": mm["stored_raw"][met], "raw_plus_formula": mm["stored_raw_plus_formula"][met],
                                  "raw_plus_random_formula_fx": mm["raw_plus_random_formula_fx"][met],
                                  "raw_plus_permuted_random_formula_fx": mm["raw_plus_permuted_random_formula_fx"][met]})
    dr = pd.DataFrame(draw_rows)
    dr.to_csv(out_dir / "draw_level_scores.csv", index=False)
    # one row per cell x model x metric: random-expression scores averaged over the draws, plus the share of draws the LLM beats
    key = ["dataset", "run_id", "generator", "tier", "model", "metric"]
    dr["llm_beats"] = (dr.raw_plus_formula > dr.raw_plus_random_formula_fx).astype(float)
    rl = dr.groupby(key, as_index=False).agg(k_llm=("k_llm", "first"), k_random=("k_random", "first"),
                                             n_constant_random_cols=("n_constant_random_cols", "sum"), n_draws=("draw", "nunique"),
                                             raw=("raw", "first"), raw_plus_formula=("raw_plus_formula", "first"),
                                             raw_plus_random_formula_fx=("raw_plus_random_formula_fx", "mean"),
                                             raw_plus_permuted_random_formula_fx=("raw_plus_permuted_random_formula_fx", "mean"),
                                             llm_beats_frac=("llm_beats", "mean"))
    rl.to_csv(out_dir / "run_level_scores.csv", index=False)
    # bring in the LLM permuted control and the noise control from the benchmark aggregation
    bench = pd.read_csv(ROOT / "results/statistics/benchmark44/dataset_generator_level.csv")
    keep = ["dataset", "generator", "model", "metric", "raw_plus_permuted_formula", "raw_plus_random_formula"]
    TREAT = ["raw", "raw_plus_formula", "raw_plus_random_formula_fx", "raw_plus_permuted_random_formula_fx"]
    dg = rl.groupby(["dataset", "tier", "generator", "model", "metric"], as_index=False)[TREAT].mean()
    dg = dg.merge(bench[keep], on=["dataset", "generator", "model", "metric"], how="left")
    dl = dg.groupby(["dataset", "tier", "model", "metric"], as_index=False)[TREAT + ["raw_plus_permuted_formula", "raw_plus_random_formula"]].mean()
    CONTRASTS = {
        "random_formula_vs_raw": ("raw_plus_random_formula_fx", "raw"),
        "random_formula_semantic": ("raw_plus_random_formula_fx", "raw_plus_permuted_random_formula_fx"),
        "llm_vs_random_formula": ("raw_plus_formula", "raw_plus_random_formula_fx"),
        "llm_semantic": ("raw_plus_formula", "raw_plus_permuted_formula"),
        "llm_direct": ("raw_plus_formula", "raw"),
        "random_formula_vs_noise": ("raw_plus_random_formula_fx", "raw_plus_random_formula"),
    }
    for name, (a, b) in CONTRASTS.items():
        dg[name] = dg[a] - dg[b]
        dl[name] = dl[a] - dl[b]
    for frame in (dg, dl):
        frame["semantic_excess"] = frame["llm_semantic"] - frame["random_formula_semantic"]
    dg.to_csv(out_dir / "dataset_generator_level.csv", index=False)
    dl.to_csv(out_dir / "dataset_level.csv", index=False)

    def summarize(df: pd.DataFrame, label: str) -> pd.DataFrame:
        out = []
        for metric in METRICS:
            for model in MODELS:
                sub = df[(df.metric == metric) & (df.model == model)]
                for name in list(CONTRASTS) + ["semantic_excess"]:
                    x = sub[name].dropna().to_numpy(dtype=float)
                    if len(x) == 0:
                        continue
                    lo, hi = boot_ci(x)
                    out.append({"subset": label, "metric": metric, "model": model, "contrast": name, "n_datasets": len(x),
                                "mean_delta": x.mean(), "median_delta": float(np.median(x)), "wins": int((x > 0).sum()),
                                "losses": int((x < 0).sum()), "ties": int((x == 0).sum()), "p_wilcoxon_exact": exact_p(x),
                                "cliffs_delta": ((x > 0).sum() - (x < 0).sum()) / len(x), "ci95_lo": lo, "ci95_hi": hi})
        s = pd.DataFrame(out)
        s["p_holm_models"] = np.nan
        for (_, _), idx in s.groupby(["metric", "contrast"]).groups.items():
            s.loc[idx, "p_holm_models"] = holm(s.loc[idx, "p_wilcoxon_exact"].tolist())
        return s

    n_all, n_core, n_exp = dl.dataset.nunique(), dl[dl.tier == "core"].dataset.nunique(), dl[dl.tier == "expansion"].dataset.nunique()
    summ = pd.concat([summarize(dl, f"all datasets, generator-averaged (N={n_all}: {n_core} core + {n_exp} expansion)"),
                      summarize(dl[dl.tier == "expansion"], f"expansion only (N={n_exp})"),
                      summarize(dl[dl.tier == "core"], f"core only (N={n_core})")] +
                     [summarize(dg[dg.generator == g], f"{g} (N={dg[dg.generator == g].dataset.nunique()})") for g in sorted(dg.generator.unique())],
                     ignore_index=True)
    summ.to_csv(out_dir / "summary.csv", index=False)
    cells = rl.drop_duplicates("run_id")
    beats = rl[rl.metric == "roc_auc_ovr"].groupby("model").llm_beats_frac.agg(["mean", lambda v: float((v > 0.5).mean()), lambda v: float((v >= 1.0).mean())])
    lines = ["# Random-expression control (count-matched random valid expressions over the dataset's own columns)", "",
             f"cells: {rl.run_id.nunique()} | datasets: {n_all} | draws per cell: {int(cells.n_draws.min())} to {int(cells.n_draws.max())} | "
             f"random expression columns constant on evaluation rows (summed over draws): {int(cells.n_constant_random_cols.sum())}", "",
             "share of draws the LLM schema beats (ROC-AUC), per model: mean fraction | cells with LLM above the median draw | cells with LLM above every draw",
             *(f"  {m}: {r['mean']:.2f} | {r['<lambda_0>']:.2f} | {r['<lambda_1>']:.2f}" for m, r in beats.iterrows()), ""]
    for label in summ.subset.unique():
        lines += [f"## {label}", ""]
        for metric in METRICS:
            lines += [f"### {metric}", "", "| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | 95% CI |", "|---|---|---|---|---|---|---|---|---|"]
            s = summ[(summ.subset == label) & (summ.metric == metric)]
            for _, r in s.iterrows():
                lines.append(f"| {r.model} | {r.contrast} | {r.n_datasets} | {r.mean_delta:+.4f} | {r.median_delta:+.4f} | {r.wins}/{r.losses}/{r.ties} | {r.p_wilcoxon_exact:.2g} | {r.p_holm_models:.2g} | [{r.ci95_lo:+.4f}, {r.ci95_hi:+.4f}] |")
            lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines[:120]))


def write_table(out_dir: Path, tex_out: Path) -> None:
    """LaTeX table of the random-formula control (pooled, generator-averaged, N datasets)."""
    summ = pd.read_csv(out_dir / "summary.csv")
    summ = summ[summ.subset.str.startswith("all datasets")]
    LAB = {"logistic_regression": "Logistic regression", "knn": "KNN", "random_forest": "Random forest", "xgboost": "XGBoost"}
    MET = {"roc_auc_ovr": "ROC-AUC", "balanced_accuracy": "Bal. accuracy"}
    COLS = ["random_formula_vs_raw", "random_formula_semantic", "llm_vs_random_formula", "semantic_excess"]

    def cell(r) -> str:
        p = r.p_holm_models
        ps = "$<$0.001" if p < 0.001 else f"{p:.3f}"
        return f"{r.mean_delta:+.4f} & {int(r.wins)}/{int(r.losses)} & {ps}"

    lines = ["\\begin{table}[tbp]",
             "\\caption{Random-expression control on all 49 datasets (ROC-AUC and balanced accuracy, generator-averaged). Each (dataset, generator) cell receives $k$ random but valid expressions over the dataset's own columns, drawn from the LLM formulas' vocabulary with design-split statistics only, where $k$ is the cell's number of LLM formula features (Section~\\ref{sec:controls}); they are materialized, scored, and column-permuted exactly like the LLM formulas, and the random-expression columns of the table are averaged over five independent random schemas per cell. ``Random expr.\\ $-$ raw'': \\texttt{raw+random-expression} minus \\texttt{raw}; ``Random expr.\\ vs permuted'': random expressions minus their own permuted copy; ``LLM $-$ random expr.'': \\texttt{raw+formula} minus \\texttt{raw+random-expression}; ``Excess semantic'': the LLM semantic contrast of Table~\\ref{tab:semantic-direct} minus the random-expression semantic contrast. W/L counts datasets (ties excluded); $p_{\\mathrm{Holm}}$ is the exact Wilcoxon test over datasets, Holm-corrected over the four models.}\\label{tab:random-expression}",
             "\\centering", "\\small", "\\begin{adjustbox}{max width=\\linewidth}", "\\begin{tabular}{llrrrrrrrrrrrr}", "\\toprule",
             "& & \\multicolumn{3}{c}{Random expr. $-$ raw} & \\multicolumn{3}{c}{Random expr. vs permuted} & \\multicolumn{3}{c}{LLM $-$ random expr.} & \\multicolumn{3}{c}{Excess semantic} \\\\",
             "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\\cmidrule(lr){9-11}\\cmidrule(lr){12-14}",
             "Metric & Model & $\\Delta$ & W/L & $p_{\\mathrm{Holm}}$ & $\\Delta$ & W/L & $p_{\\mathrm{Holm}}$ & $\\Delta$ & W/L & $p_{\\mathrm{Holm}}$ & $\\Delta$ & W/L & $p_{\\mathrm{Holm}}$ \\\\",
             "\\midrule"]
    for mi, metric in enumerate(MET):
        if mi:
            lines.append("\\midrule")
        for model in LAB:
            parts = []
            for c in COLS:
                r = summ[(summ.metric == metric) & (summ.model == model) & (summ.contrast == c)].iloc[0]
                parts.append(cell(r))
            lines.append(f"{MET[metric]} & {LAB[model]} & " + " & ".join(parts) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\end{table}"]
    tex_out.parent.mkdir(parents=True, exist_ok=True)
    tex_out.write_text("\n".join(lines) + "\n")
    print("wrote", tex_out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["list", "evaluate", "aggregate", "table"])
    ap.add_argument("--table-out", default="paper/dmlr/tables/random_expression.tex")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--tier", choices=["core", "expansion"], default=None)
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--draws", type=int, default=1, help="number of random schemas per cell (draw 0 is the original seed)")
    ap.add_argument("--only-draws", default=None, help="comma-separated draw indices to run")
    ap.add_argument("--datasets", default=None, help="comma-separated datasets to include")
    ap.add_argument("--exclude-datasets", default=None, help="comma-separated datasets to exclude")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    if args.command == "aggregate":
        aggregate(out_dir)
        return
    if args.command == "table":
        write_table(out_dir, Path(args.table_out))
        return
    cells = list_cells()
    if args.tier:
        cells = [c for c in cells if c["tier"] == args.tier]
    if args.datasets:
        keep = set(args.datasets.split(","))
        cells = [c for c in cells if c["dataset"] in keep]
    if args.exclude_datasets:
        drop = set(args.exclude_datasets.split(","))
        cells = [c for c in cells if c["dataset"] not in drop]
    if args.limit:
        cells = cells[: args.limit]
    print(f"{len(cells)} cells ({sum(c['tier'] == 'core' for c in cells)} core, {sum(c['tier'] == 'expansion' for c in cells)} expansion)", flush=True)
    if args.command == "list":
        for c in cells:
            print(c["tier"], c["dataset"], c["generator"], c["run_id"], "safe" if c["safe_columns"] else "raw")
        return
    from multiprocessing import get_context
    t0 = time.time()
    draws = [int(x) for x in args.only_draws.split(",")] if args.only_draws else list(range(args.draws))
    tasks = [(c, str(out_dir), args.skip_existing, 5, 2, 42, 42, dr) for dr in draws for c in cells]
    print(f"{len(tasks)} cell-draw evaluations (draws {draws})", flush=True)
    with get_context("spawn").Pool(args.workers) as pool:
        for i, msg in enumerate(pool.imap_unordered(_worker, tasks), 1):
            print(f"[{i}/{len(tasks)} {time.time() - t0:.0f}s] {msg}", flush=True)
    print("EVALUATE_DONE", flush=True)


if __name__ == "__main__":
    main()
