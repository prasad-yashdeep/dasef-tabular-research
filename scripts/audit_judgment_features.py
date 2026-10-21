#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from dasef.datasets import load_dataset, stratified_cap
from dasef.io_utils import read_json, read_model, write_json
from dasef.judgment_audit import (
    audit_judgment_features,
    audits_to_frame,
    write_judgment_audit_markdown,
)
from dasef.schema import SchemaSpec


DEFAULT_RESULT_DIRS = (
    "results/judgment_shortlist",
    "results/deepseek_judgment_shortlist",
    "results/schema_runs",
)


def find_result_files(paths: list[str]) -> list[Path]:
    result_files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file():
            result_files.append(path)
        elif path.exists():
            result_files.extend(path.rglob("results.json"))
    return sorted(set(result_files))


def _target_for_result(result: dict[str, Any]) -> pd.Series | None:
    try:
        ds = load_dataset(result["dataset"])
        if result.get("cap_rows"):
            ds = stratified_cap(ds, result["cap_rows"])
    except Exception:
        return None
    return ds.y.reset_index(drop=True)


def audit_result_file(result_path: Path, *, include_target_correlation: bool) -> dict[str, Any] | None:
    result = read_json(result_path)
    artifacts = result.get("artifacts", {})
    schema_path = artifacts.get("schema")
    judgment_path = artifacts.get("judgment_matrix")
    if not schema_path or not judgment_path or not Path(judgment_path).exists():
        return None
    schema = read_model(schema_path, SchemaSpec)
    judgment_df = pd.read_parquet(judgment_path).reset_index(drop=True)
    y = _target_for_result(result) if include_target_correlation else None
    if y is not None and len(y) != len(judgment_df):
        y = None
    audit = audit_judgment_features(judgment_df, schema, y=y)
    audit["result_path"] = str(result_path)
    audit["judgment_matrix"] = judgment_path
    audit["target_correlation_included"] = y is not None
    return audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit stored DASEF judgment matrices.")
    parser.add_argument("paths", nargs="*", default=list(DEFAULT_RESULT_DIRS))
    parser.add_argument("--out-dir", default="results/statistics")
    parser.add_argument("--include-target-correlation", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result_files = find_result_files(args.paths)
    audits = [
        audit
        for path in result_files
        if (audit := audit_result_file(path, include_target_correlation=args.include_target_correlation))
        is not None
    ]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "judgment_feature_audit.json"
    csv_path = out_dir / "judgment_feature_audit.csv"
    md_path = out_dir / "judgment_feature_audit.md"
    write_json(json_path, {"audits": audits, "result_files_scanned": len(result_files)})
    df = audits_to_frame(audits)
    df.to_csv(csv_path, index=False)
    write_judgment_audit_markdown(df, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
