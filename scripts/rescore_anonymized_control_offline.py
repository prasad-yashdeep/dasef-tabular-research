#!/usr/bin/env python
"""Re-score the anonymized-column control from the cached anonymized schemas, offline.

scripts/run_anonymized_controls.py always calls the schema generator (the cache under
cache/schemas_anonymized is written, never read), so it cannot be re-run without API
access. This script reproduces its evaluation exactly from the cached schema files:
the same cap-then-split evaluation rows (cap 5000, 30% design split, seed 42), the same
generic column renaming (x001, x002, ...), the same four matrices (raw, raw+formula,
raw+random-formula, raw+permuted-formula; random seed 42, permutation seed 42), the same
5x2 CV with the four downstream models, and the same per-run CSV and dataset-level
summary formats. It is used whenever the formula evaluator changes (the credit_g
category fix and the integer-overflow fix both touch anonymized datasets).

Usage: python scripts/rescore_anonymized_control_offline.py [--families linear_svm]
       [--schema-model gpt-5.5-pro] [--out-dir results/anonymized_control]
       [--stats-out-dir results/statistics/anonymized_control]
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from dasef.datasets import dataset_summary, load_dataset, raw_block_equal, schema_design_eval_split, stratified_cap  # noqa: E402
from dasef.features.augment import augment_with_formula  # noqa: E402
from dasef.features.random_control import augment_with_random_control  # noqa: E402
from dasef.config import load_llm_models  # noqa: E402
from dasef.hash_utils import stable_hash  # noqa: E402
from dasef.io_utils import read_model  # noqa: E402
from dasef.prompts import build_schema_prompt  # noqa: E402
from dasef.schema import SchemaSpec  # noqa: E402
from run_anonymized_controls import (  # noqa: E402
    DEFAULT_DATASETS, DEFAULT_DOWNSTREAM, METRICS, all_metric_means, anonymize_summary, csv_arg, permute_formula_cols,
)


def cached_schema(schema_root: Path, anon_summary: dict, family: str, model_cfg, n_features: int) -> Path:
    """The cached schema file generate_schema() would have written for this exact prompt:
    same prompt builder, same n_features, same prompt-hash rule (so a stale cache entry
    from an earlier prompt version is never picked up silently)."""
    prompt = build_schema_prompt(anon_summary, family, model_cfg.id, n_features=n_features)
    prompt_hash = stable_hash({"prompt": prompt, "model": model_cfg.id})
    path = schema_root / anon_summary["name"] / family / model_cfg.id / f"schema_{prompt_hash}.json"
    if not path.exists():
        others = sorted(Path(q).name for q in glob.glob(str(path.parent / "schema_*.json")) if not q.endswith((".raw.json", ".prompt.json")))
        raise FileNotFoundError(f"no cached schema for the current prompt of {anon_summary['name']}/{family}/{model_cfg.id} "
                                f"(expected {path.name}; cached: {others})")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--datasets", default=DEFAULT_DATASETS)
    ap.add_argument("--families", default="linear_svm")
    ap.add_argument("--schema-model", default="gpt-5.5-pro")
    ap.add_argument("--schema-root", default="cache/schemas_anonymized")
    ap.add_argument("--out-dir", default="results/anonymized_control")
    ap.add_argument("--stats-out-dir", default="results/statistics/anonymized_control")
    ap.add_argument("--cap", type=int, default=5000)
    ap.add_argument("--schema-design-fraction", type=float, default=0.3)
    ap.add_argument("--schema-design-seed", type=int, default=42)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-features", type=int, default=12)
    args = ap.parse_args()
    model_cfg = {m.id: m for m in load_llm_models().schema_generators}[args.schema_model]
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    schema_root = ROOT / args.schema_root
    rows: list[dict] = []
    datasets = csv_arg(args.datasets)
    for idx, dataset_name in enumerate(datasets):
        ds = load_dataset(dataset_name)
        if args.cap:
            ds = stratified_cap(ds, args.cap)
        design_ds, eval_ds = schema_design_eval_split(ds, args.schema_design_fraction, args.schema_design_seed)
        # the cached anonymized schemas were generated from summaries of the local cache, whose categorical
        # columns are int8 codes; reproduce that summary (and hence the prompt hash) from a load with the
        # one-hot override disabled, on the same capped design rows (asserted below)
        design_for_summary = design_ds
        if getattr(design_ds, "onehot_override_columns", []):
            previous = os.environ.get("DASEF_RAW_ONEHOT")
            os.environ["DASEF_RAW_ONEHOT"] = "0"
            try:
                ds_num = load_dataset(dataset_name)
            finally:
                if previous is None:
                    os.environ.pop("DASEF_RAW_ONEHOT", None)
                else:
                    os.environ["DASEF_RAW_ONEHOT"] = previous
            if args.cap:
                ds_num = stratified_cap(ds_num, args.cap)
            design_for_summary, _ = schema_design_eval_split(ds_num, args.schema_design_fraction, args.schema_design_seed)
            assert raw_block_equal(design_for_summary.X, design_ds.X), f"{dataset_name}: numeric and one-hot design splits differ"
        anon_summary, mapping = anonymize_summary(dataset_summary(design_for_summary), idx)
        X_eval = eval_ds.X.rename(columns=mapping).reset_index(drop=True)
        y_eval = eval_ds.y.reset_index(drop=True)
        for family in csv_arg(args.families):
            tag = f"{dataset_name}/{family}/{args.schema_model}"
            path = cached_schema(schema_root, anon_summary, family, model_cfg, args.n_features)
            schema = read_model(path, SchemaSpec)
            formula_specs = schema.formula_features
            X_formula = augment_with_formula(X_eval, schema)
            formula_cols = [c for c in X_formula.columns if c not in X_eval.columns]
            X_random = augment_with_random_control(X_eval, formula_specs, seed=args.seed, prefix="random_formula")
            X_permuted = permute_formula_cols(X_formula, formula_cols, seed=args.seed)
            n_const = sum(int(X_formula[c].nunique(dropna=True) <= 1) for c in formula_cols)
            n_nan = sum(int(X_formula[c].isna().all()) for c in formula_cols)
            for model in DEFAULT_DOWNSTREAM:
                sc_raw = all_metric_means(X_eval, y_eval, model, args.seed)
                sc_formula = all_metric_means(X_formula, y_eval, model, args.seed)
                sc_random = all_metric_means(X_random, y_eval, model, args.seed)
                sc_permuted = all_metric_means(X_permuted, y_eval, model, args.seed)
                for metric in METRICS:
                    rows.append({
                        "dataset": dataset_name, "family": family, "downstream_model": model, "metric": metric,
                        "raw": sc_raw[metric], "formula": sc_formula[metric], "random_formula": sc_random[metric],
                        "permuted_formula": sc_permuted[metric],
                        "direct_delta": sc_formula[metric] - sc_raw[metric],
                        "vs_random_delta": sc_formula[metric] - sc_random[metric],
                        "semantic_delta": sc_formula[metric] - sc_permuted[metric],
                        "n_formula_cols": len(formula_cols), "n_constant_formula_cols": n_const, "n_all_nan_formula_cols": n_nan,
                        "schema_path": str(path.relative_to(ROOT)),
                    })
            print(f"  OK {tag} ({len(formula_cols)} formula cols, {n_const} constant, {n_nan} all-NaN) <- {path.name}", flush=True)
            pd.DataFrame(rows).to_csv(out_dir / "anonymized_per_run.csv", index=False)
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "anonymized_per_run.csv", index=False)
    stats_dir = ROOT / args.stats_out_dir
    stats_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Anonymized-Column Memorization Control", "",
             f"Schema generator: {args.schema_model}; column names -> x001..xNNN, dataset identity removed, distributional stats preserved.",
             "Dataset-level means (families averaged), Wilcoxon across datasets.", "",
             "Re-scored offline from the cached anonymized schemas by scripts/rescore_anonymized_control_offline.py.", ""]
    agg_rows = []
    for metric in METRICS:
        lines += [f"## {metric}", "", "| Downstream | N | direct Δ | vs-random Δ | semantic Δ | semantic W/L | semantic p |", "|---|---|---|---|---|---|---|"]
        for model in DEFAULT_DOWNSTREAM:
            sub = df[(df.metric == metric) & (df.downstream_model == model)]
            by_ds = sub.groupby("dataset")[["direct_delta", "vs_random_delta", "semantic_delta"]].mean()
            sem = by_ds.semantic_delta.values
            wins, losses = int((sem > 0).sum()), int((sem < 0).sum())
            p = float(wilcoxon(sem).pvalue) if np.any(sem != 0) else float("nan")
            lines.append(f"| {model} | {len(sem)} | {by_ds.direct_delta.mean():+.4f} | {by_ds.vs_random_delta.mean():+.4f} | "
                         f"{by_ds.semantic_delta.mean():+.4f} | {wins}/{losses} | {p:.4f} |")
            agg_rows.append({"metric": metric, "downstream_model": model, "n": len(sem), "direct_delta": by_ds.direct_delta.mean(),
                             "vs_random_delta": by_ds.vs_random_delta.mean(), "semantic_delta": by_ds.semantic_delta.mean(),
                             "semantic_wins": wins, "semantic_losses": losses, "semantic_p": p})
        lines.append("")
    (stats_dir / "anonymized_summary.md").write_text("\n".join(lines))
    pd.DataFrame(agg_rows).to_csv(stats_dir / "anonymized_summary.csv", index=False)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
