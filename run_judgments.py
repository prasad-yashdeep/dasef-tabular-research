#!/usr/bin/env python3
"""DASEF Judgment Filling — runs DeepSeek R1 + V4 Pro on all completed schemas."""
from __future__ import annotations

import glob
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from dasef.settings import ENV_PATH  # noqa: triggers dotenv load
from dasef.config import load_datasets, load_llm_models
from dasef.experiments.paper1_pipeline import EvaluationPlan, run_schema_evaluation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATASETS = [
    "adult_income", "bank_marketing", "blood_transfusion", "car_evaluation",
    "credit_g", "electricity", "phoneme", "pima_diabetes",
    "qsar_biodegradation", "spambase",
]
FAMILIES = ["tree", "linear_svm", "distance_knn"]
SCHEMA_MODELS = ["claude-opus-4.7", "gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-sonnet-4.6"]


def find_schema(dataset: str, family: str, model: str) -> str | None:
    schemas = glob.glob(f"cache/schemas/{dataset}/{family}/{model}/schema_*.json")
    schemas = [s for s in schemas if not s.endswith(".raw.json")]
    return schemas[0] if schemas else None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--judgment-model", default="deepseek-r1")
    parser.add_argument("--schema-models", nargs="+", default=SCHEMA_MODELS)
    parser.add_argument("--datasets", nargs="+", default=DATASETS)
    parser.add_argument("--out-dir", default="results/judgments")
    parser.add_argument("--batch-size", type=int, default=25, help="Rows per LLM call (default 25, use 1 for legacy single-row)")
    args = parser.parse_args()

    os.chdir(Path(__file__).parent)
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    llm_reg = load_llm_models()
    jm = next(m for m in llm_reg.judgment_fillers if m.id == args.judgment_model)

    # Collect all available schemas
    work = []
    for schema_model in args.schema_models:
        for ds in args.datasets:
            for fam in FAMILIES:
                schema_path = find_schema(ds, fam, schema_model)
                if schema_path:
                    work.append((schema_path, ds, fam, schema_model))

    print(f"\n{'='*60}")
    print(f"  Judgment Filling: {args.judgment_model}")
    print(f"  Provider: {jm.provider} / {jm.provider_model}")
    print(f"  Schemas to evaluate: {len(work)}")
    print(f"{'='*60}\n")

    plan = EvaluationPlan()
    successes = 0
    failures = 0

    for i, (schema_path, ds, fam, schema_model) in enumerate(work, 1):
        print(f"[{i}/{len(work)}] {ds}/{fam}/{schema_model} → {args.judgment_model}")
        try:
            # Determine cap for large datasets
            ds_cfg = None
            try:
                from dasef.config import load_datasets as ld
                reg = ld()
                ds_cfg = next((d for d in reg.datasets if d.name == ds), None)
            except Exception:
                pass
            cap = getattr(ds_cfg, 'judgment_cap_rows', None) if ds_cfg else None

            run_schema_evaluation(
                dataset_name=ds,
                schema_path=schema_path,
                out_dir=args.out_dir,
                cap_rows=cap,
                plan=plan,
                judgment_model_id=jm.provider_model,
                judgment_provider=jm.provider,
                dry_run_judgments=False,
                schema_design_fraction=0.3,
                schema_design_seed=42,
                include_random_controls=True,
                random_control_seed=42,
                judgment_batch_size=args.batch_size,
            )
            print(f"  ✓ Done")
            successes += 1
        except Exception as e:
            print(f"  ✗ Failed: {str(e)[:200]}")
            failures += 1

    print(f"\n{'='*60}")
    print(f"  Judgment Filling Complete")
    print(f"  Successes: {successes} | Failures: {failures}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
