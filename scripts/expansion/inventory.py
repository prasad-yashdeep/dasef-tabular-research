#!/usr/bin/env python
"""Inventory of extra (non-main) datasets and their cached schemas.

Writes, into the scratch expansion dir:
  dataset_inventory.csv  - one row per non-main dataset in configs/datasets.yaml
  schema_inventory.csv   - one row per cached valid schema json under cache/schemas/<ds>/
  inventory_summary.txt  - counts

No LLM calls. Datasets load from data/local_cache or the OpenML on-disk cache.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from dasef.config import load_datasets  # noqa: E402
from dasef.datasets import dataset_summary, load_dataset, schema_design_eval_split, stratified_cap  # noqa: E402
from dasef.features.formula import UnsafeFormula, materialize_formula_features, validate_formula  # noqa: E402
import logging; logging.getLogger("dasef.features.formula").setLevel(logging.CRITICAL)
from dasef.hash_utils import stable_hash  # noqa: E402
from dasef.prompts import build_schema_prompt  # noqa: E402
from dasef.schema import SchemaSpec  # noqa: E402
from run_paper2_llm_schema_expansion import safe_columns  # noqa: E402  (pure function, no API)

MAIN = {
    "adult_income", "bank_marketing", "blood_transfusion", "car_evaluation", "credit_g",
    "electricity", "phoneme", "pima_diabetes", "qsar_biodegradation", "spambase",
}
OPENML_CACHE = Path.home() / ".openml" / "org" / "openml" / "www" / "datasets"
N_FEATURES = 12
CAP = 5000
FRACTIONS = (0.3, 0.2)


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def count_valid(schema: SchemaSpec, allowed: set[str]) -> tuple[int, list[str]]:
    ok = 0
    errs = []
    for f in schema.formula_features:
        try:
            validate_formula(f.formula or "", allowed)
            ok += 1
        except UnsafeFormula as exc:
            errs.append(f"{f.name}: {str(exc)[:60]}")
        except Exception as exc:  # syntax errors etc.
            errs.append(f"{f.name}: {type(exc).__name__}: {str(exc)[:50]}")
    return ok, errs


def main() -> None:
    registry = load_datasets()
    generators = ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-4.7", "claude-sonnet-4.6"]
    ds_rows = []
    schema_rows = []
    signal.signal(signal.SIGALRM, _alarm)

    for cfg in registry.datasets:
        if cfg.name in MAIN:
            continue
        row = {
            "dataset": cfg.name,
            "openml_id": cfg.openml_id,
            "tier": cfg.tier,
            "in_local_cache": (ROOT / "data" / "local_cache" / cfg.name / "data.parquet").exists(),
            "in_data_raw": bool(glob.glob(str(ROOT / "data" / "raw" / f"{cfg.name}*"))),
            "openml_cache_has_data": bool(cfg.openml_id) and (OPENML_CACHE / str(cfg.openml_id) / f"dataset_{cfg.openml_id}.pq").exists(),
        }
        schema_files = [
            p for p in glob.glob(str(ROOT / "cache" / "schemas" / cfg.name / "*" / "*" / "schema_*.json"))
            if not p.endswith(".raw.json") and not p.endswith(".prompt.json")
        ]
        raw_files = glob.glob(str(ROOT / "cache" / "schemas" / cfg.name / "*" / "*" / "schema_*.raw.json"))
        row["n_valid_schemas"] = len(schema_files)
        row["n_raw_responses"] = len(raw_files)
        for g in generators:
            row[f"has_{g}"] = any(f"/{g}/" in p for p in schema_files)

        ds = None
        t0 = time.time()
        load_error = ""
        try:
            signal.alarm(150)
            ds = load_dataset(cfg.name)
            signal.alarm(0)
        except Timeout:
            load_error = "timeout>150s"
        except Exception as exc:  # noqa: BLE001
            signal.alarm(0)
            load_error = f"{type(exc).__name__}: {str(exc)[:120]}"
        row["load_seconds"] = round(time.time() - t0, 1)
        row["load_error"] = load_error

        hashes: dict[str, str] = {}
        raw_cols: set[str] = set()
        safe_cols: set[str] = set()
        if ds is not None:
            row["n_rows"] = int(len(ds.X))
            row["n_features"] = int(ds.X.shape[1])
            row["n_categorical"] = len(ds.categorical_columns)
            row["n_classes"] = int(ds.y.astype(str).nunique())
            raw_cols = set(map(str, ds.X.columns))
            ds_safe = safe_columns(ds)
            safe_cols = set(ds_safe.X.columns)
            row["n_cols_renamed_by_safe_columns"] = sum(1 for a, b in zip(ds.X.columns, ds_safe.X.columns) if str(a) != b)
            # evaluation geometry under the main-benchmark protocol (cap 5000 then 0.3/0.7 split, seed 42)
            ev = None
            ev_safe = None
            try:
                capped = stratified_cap(ds, CAP)
                _, ev = schema_design_eval_split(capped, 0.3, 42)
                _, ev_safe = schema_design_eval_split(stratified_cap(ds_safe, CAP), 0.3, 42)
                row["eval_rows_cap5000_split0.3"] = int(len(ev.X))
                cat_card = sum(int(ev.X[c].nunique()) for c in ds.categorical_columns if c in ev.X.columns)
                row["eval_onehot_width_est"] = int(cat_card + len(ds.numeric_columns))
                row["max_cat_cardinality_eval"] = int(max((ev.X[c].nunique() for c in ds.categorical_columns if c in ev.X.columns), default=0))
            except Exception as exc:  # noqa: BLE001
                row["eval_split_error"] = f"{type(exc).__name__}: {str(exc)[:80]}"
            # prompt-hash provenance: which (fraction, naming) reproduces the cached filename hash
            for frac in FRACTIONS:
                for naming, dsv in (("raw_names", ds), ("safe_names", ds_safe)):
                    try:
                        design, _ = schema_design_eval_split(dsv, frac, 42)
                        summ = dataset_summary(design)
                        for g in generators:
                            prompt = build_schema_prompt(summ, "linear_svm", g, n_features=N_FEATURES)
                            h = stable_hash({"prompt": prompt, "model": g})
                            label = f"frac{frac}+{naming}" if raw_cols != safe_cols else f"frac{frac}+raw_names(rename_noop)"
                            hashes.setdefault(h, label)
                    except Exception as exc:  # noqa: BLE001
                        row[f"hash_error_{frac}_{naming}"] = str(exc)[:60]

        for p in sorted(schema_files):
            parts = Path(p).parts
            family, generator = parts[-3], parts[-2]
            srow = {
                "dataset": cfg.name,
                "openml_id": cfg.openml_id,
                "family": family,
                "generator": generator,
                "schema_path": os.path.relpath(p, ROOT),
                "mtime": dt.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M"),
            }
            try:
                data = json.load(open(p))
                schema = SchemaSpec.model_validate(data)
                srow["n_features"] = len(schema.features)
                srow["n_formula"] = len(schema.formula_features)
                srow["n_judgment"] = len(schema.judgment_features)
                srow["salvaged_partial"] = "salvaged_from_partial_raw" in (schema.metadata or {})
                fh = Path(p).stem.replace("schema_", "")
                srow["provenance_by_prompt_hash"] = hashes.get(fh, "no_match" if hashes else "dataset_not_loaded")
                if ds is not None:
                    ok_raw, err_raw = count_valid(schema, raw_cols)
                    ok_safe, err_safe = count_valid(schema, safe_cols)
                    srow["n_formula_valid_raw_names"] = ok_raw
                    srow["n_formula_valid_safe_names"] = ok_safe
                    srow["first_error_raw_names"] = err_raw[0] if err_raw else ""
                    srow["first_error_safe_names"] = err_safe[0] if err_safe else ""
                    prov = srow["provenance_by_prompt_hash"]
                    naming = "safe" if "safe_names" in prov else "raw"
                    srow["naming_for_runner"] = naming
                    srow["n_formula_valid_own_naming"] = ok_safe if naming == "safe" else ok_raw
                    evx = ev_safe if naming == "safe" else ev
                    if evx is not None:
                        try:
                            mat = materialize_formula_features(evx.X.reset_index(drop=True), schema)
                            good = [c for c in mat.columns if mat[c].notna().any() and mat[c].nunique(dropna=True) > 1]
                            srow["n_formula_materialized_nondegenerate"] = len(good)
                            srow["n_formula_all_nan"] = int(sum(mat[c].isna().all() for c in mat.columns))
                            srow["n_formula_constant"] = int(sum((mat[c].notna().any()) and (mat[c].nunique(dropna=True) <= 1) for c in mat.columns))
                        except Exception as exc:  # noqa: BLE001
                            srow["materialize_error"] = f"{type(exc).__name__}: {str(exc)[:80]}"
                    else:
                        srow["materialize_error"] = row.get("eval_split_error", "no eval split")
            except Exception as exc:  # noqa: BLE001
                srow["schema_error"] = f"{type(exc).__name__}: {str(exc)[:100]}"
            schema_rows.append(srow)
        ds_rows.append(row)
        print(f"{cfg.name:45s} rows={row.get('n_rows')} schemas={len(schema_files)} load={row['load_seconds']}s {load_error}", flush=True)

    ds_df = pd.DataFrame(ds_rows)
    sc_df = pd.DataFrame(schema_rows)
    ds_df.to_csv(OUT / "dataset_inventory.csv", index=False)
    sc_df.to_csv(OUT / "schema_inventory.csv", index=False)

    lines = []
    p2 = ds_df[ds_df.tier == "paper2_expansion"]
    lines.append(f"non-main datasets in configs/datasets.yaml: {len(ds_df)} "
                 f"(paper2_expansion={len(p2)}, other tiers={ds_df.tier[ds_df.tier != 'paper2_expansion'].value_counts().to_dict()})")
    lines.append(f"paper2_expansion unique openml ids: {p2.openml_id.nunique()} (duplicate-name rows: {len(p2) - p2.openml_id.nunique()})")
    lines.append(f"paper2_expansion loadable offline: {int((p2.load_error == '').sum())}/{len(p2)}")
    lines.append(f"in data/local_cache: {int(ds_df.in_local_cache.sum())}; in data/raw: {int(ds_df.in_data_raw.sum())}; "
                 f"openml cache has data file: {int(ds_df.openml_cache_has_data.sum())}")
    if not sc_df.empty:
        lines.append("\nvalid cached schemas per (family, generator):")
        lines.append(sc_df.groupby(["family", "generator"]).size().to_string())
        lines.append("\nprovenance (prompt-hash match) per generator:")
        lines.append(sc_df.groupby(["generator", "provenance_by_prompt_hash"]).size().to_string())
        ok = sc_df.dropna(subset=["n_formula_valid_raw_names"])
        lines.append("\nformula validity (mean n valid / n formula) under raw vs safe column names, per generator:")
        lines.append(ok.groupby("generator")[["n_formula", "n_formula_valid_raw_names", "n_formula_valid_safe_names"]].mean().round(2).to_string())
        lines.append(f"\nschemas with >=1 formula valid under OWN provenance naming: {int((ok.n_formula_valid_own_naming >= 1).sum())}/{len(ok)}")
        lines.append(f"schemas with >=1 NON-DEGENERATE materialized formula column on the eval split: {int((ok.n_formula_materialized_nondegenerate.fillna(0) >= 1).sum())}/{len(ok)}")
        lines.append(f"schemas with >=5 non-degenerate formula columns: {int((ok.n_formula_materialized_nondegenerate.fillna(0) >= 5).sum())}/{len(ok)}")
        lines.append("\nnon-degenerate materialized formula columns per generator (mean, min):")
        lines.append(ok.groupby("generator")["n_formula_materialized_nondegenerate"].agg(["mean", "min", "count"]).round(2).to_string())
        lines.append(f"\nschemas with >=1 formula valid under RAW names: {int((ok.n_formula_valid_raw_names >= 1).sum())}/{len(ok)}")
        lines.append(f"schemas with >=1 formula valid under SAFE names: {int((ok.n_formula_valid_safe_names >= 1).sum())}/{len(ok)}")
        lines.append(f"schemas where safe > raw validity: {int((ok.n_formula_valid_safe_names > ok.n_formula_valid_raw_names).sum())}")
        # dataset-level usability (dedupe duplicate-name rows by openml id)
        p2s = sc_df[sc_df.dataset.isin(p2.dataset)]
        for g in ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-4.7", "claude-sonnet-4.6"]:
            sub = p2s[(p2s.generator == g) & (p2s.n_formula_materialized_nondegenerate.fillna(0) >= 1)]
            lines.append(f"paper2 datasets (unique openml id) with a usable {g} schema (>=1 non-degenerate materialized formula): {sub.openml_id.nunique()}")
        both = p2s[p2s.generator.isin(["gpt-5.5-pro", "gemini-3.1-pro-preview"]) & (p2s.n_formula_materialized_nondegenerate.fillna(0) >= 1)]
        lines.append(f"paper2 datasets with >=1 usable GPT or Gemini schema: {both.openml_id.nunique()}")
        anyg = p2s[p2s.n_formula_materialized_nondegenerate.fillna(0) >= 1]
        lines.append(f"paper2 datasets with >=1 usable schema from any generator: {anyg.openml_id.nunique()}")
        lines.append("\nprovenance x generator:")
        lines.append(pd.crosstab(sc_df.generator, sc_df.provenance_by_prompt_hash).to_string())
    (OUT / "inventory_summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
