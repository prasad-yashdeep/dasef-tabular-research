"""Count usable, all-NaN and constant formula columns in every benchmark run (the 120 core runs of
all three families under results/judgments and the 131 expansion runs), for the paper's data-quality
statements ("no all-NaN columns", "k runs materialize fewer than five usable columns").

Usage: python scripts/expansion/scan_formula_columns.py --out results/statistics/benchmark44/formula_column_scan.csv
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GENERATORS = ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-4.7", "claude-sonnet-4.6"]


def scan(run_dir: Path) -> tuple[int, int, int, int]:
    schema = json.load(open(run_dir / "schema.normalized.json"))
    fm = pd.read_parquet(run_dir / "matrices" / "formula.parquet")
    names = [f["name"] for f in schema["features"] if f.get("formula") and f["name"] in fm.columns]
    allnan = sum(int(fm[n].isna().all()) for n in names)
    const = sum(int(fm[n].nunique(dropna=True) <= 1 and not fm[n].isna().all()) for n in names)
    usable = sum(int(fm[n].nunique(dropna=True) > 1) for n in names)
    return len(names), usable, allnan, const


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = []
    for gen in GENERATORS:
        for rd in glob.glob(str(ROOT / f"results/expansion_offline/{gen}/*/runs/*")):
            r = json.load(open(Path(rd) / "results.json"))
            rows.append(("expansion", gen, r["dataset"], Path(rd).name, *scan(Path(rd))))
    # core tier: the 120 DeepSeek-Reasoner judgment runs (10 datasets x 4 generators x 3 families); the
    # DeepSeek-V4-Pro duplicates of the same cells are skipped so that no cell is counted twice
    for rd in glob.glob(str(ROOT / "results/judgments/*/results.json")):
        run_dir = Path(rd).parent
        jfiles = glob.glob(str(run_dir / "judgments" / "*.json"))
        if not jfiles or json.load(open(jfiles[0])).get("model") != "deepseek-reasoner":
            continue
        r = json.load(open(rd))
        sp = r["artifacts"]["schema"]
        parts = sp.split("/")
        gen = parts[parts.index("schemas") + 3] if "schemas" in parts else None
        if gen not in GENERATORS:
            continue
        rows.append(("core", gen, r["dataset"], run_dir.name, *scan(run_dir)))
    df = pd.DataFrame(rows, columns=["tier", "gen", "dataset", "run_id", "n_formula", "n_usable", "n_allnan", "n_const"])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print("runs:", len(df), "| all-NaN cols:", int(df.n_allnan.sum()), "| constant cols:", int(df.n_const.sum()), "in", int((df.n_const > 0).sum()), "runs")
    print(df[df.n_usable < 5].to_string(index=False))


if __name__ == "__main__":
    main()
