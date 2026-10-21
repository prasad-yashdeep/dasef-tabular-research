#!/usr/bin/env python
"""Refresh the inline tables of the DMLR paper source from the generated table files.

The paper keeps its tables inline in paper/dmlr/sections/{body,appendix}.tex (captions and layout are edited by hand);
their data rows come from the files that the rebuild scripts write to paper/tables/*.tex and
paper/dmlr/tables/datasets.tex. This script swaps the rows between the header rule and \\bottomrule of each inline table
for the rows of the matching generated file (keeping the inline table's \\midrule group separators), and replaces the whole
benchmark-dataset table block with the generated one. Only random_expression.tex and judgment_v4pro.tex are \\input directly.

Usage (from the repo root): python scripts/release/splice_paper_tables.py [--dry-run]
"""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DMLR = ROOT / "paper/dmlr"
GENERATED = ROOT / "paper/tables"
MAP = {  # label of the inline table in the DMLR source -> generated file
    "tab:semantic-direct": "semantic_direct.tex", "tab:random-controls": "random_controls.tex", "tab:judgment": "judgment.tex",
    "tab:classical": "classical.tex", "tab:generators": "by_generator.tex", "tab:anon": "anonymized.tex",
    "tab:core-families": "core_families.tex", "tab:per-dataset": "per_dataset.tex", "tab:raw-scores": "raw_scores.tex",
}


def data_rows(tex: str) -> list[str]:
    """Data rows (and \\midrule separators) of the first tabular or longtable in `tex`."""
    lines = tex.splitlines()
    if "\\begin{longtable}" in tex:
        last_foot = max(i for i, l in enumerate(lines) if l.strip() in ("\\endfoot", "\\endlastfoot"))
        end = next(i for i in range(last_foot + 1, len(lines)) if lines[i].strip().startswith("\\end{longtable}"))
        rows = lines[last_foot + 1:end]
    else:
        top = next(i for i, l in enumerate(lines) if l.strip() == "\\toprule")
        start = next(i for i in range(top + 1, len(lines)) if lines[i].strip() == "\\midrule") + 1
        end = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("\\bottomrule"))
        rows = lines[start:end]
    return [l for l in rows if l.strip()]


def splice_rows(block: str, new_rows: list[str]) -> str:
    old_rows = data_rows(block)
    if not any(r.strip() == "\\midrule" for r in new_rows):  # keep the inline table's group separators
        cuts, n = [], 0
        for r in old_rows:
            if r.strip() == "\\midrule":
                cuts.append(n)
            else:
                n += 1
        data = [r for r in new_rows if r.strip() != "\\midrule"]
        rebuilt = []
        for i, r in enumerate(data):
            if i in cuts:
                rebuilt.append("\\midrule")
            rebuilt.append(r)
        new_rows = rebuilt
    lines = block.splitlines()
    top = next(i for i, l in enumerate(lines) if l.strip() == "\\toprule")
    start = next(i for i in range(top + 1, len(lines)) if lines[i].strip() == "\\midrule") + 1
    end = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("\\bottomrule"))
    return "\n".join(lines[:start] + new_rows + lines[end:])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="report the row differences without writing")
    args = ap.parse_args()
    files = {k: DMLR / f"sections/{k}.tex" for k in ("body", "appendix")}
    texts = {k: p.read_text() for k, p in files.items()}
    changed = set()
    for label, fname in MAP.items():
        new_rows = data_rows((GENERATED / fname).read_text())
        for key, txt in texts.items():
            pos = txt.find("\\label{" + label + "}")
            if pos < 0:
                continue
            a = txt.rfind("\\begin{table}", 0, pos)
            b = txt.find("\\end{table}", pos) + len("\\end{table}")
            block = txt[a:b]
            new_block = splice_rows(block, new_rows)
            ndiff = sum(1 for x, y in zip(data_rows(block), data_rows(new_block)) if x != y) + abs(len(data_rows(block)) - len(data_rows(new_block)))
            print(f"{label}: {len(data_rows(block))} -> {len(data_rows(new_block))} rows, {ndiff} rows differ")
            if new_block != block:
                texts[key] = txt[:a] + new_block + txt[b:]
                changed.add(key)
            break
        else:
            print(f"{label}: no inline table found (probably \\input), skipped")
    # benchmark-dataset table: the generated file replaces the whole block (caption included), forced to [htbp]
    app = texts["appendix"]
    a = app.index("\\begin{table}[htbp]\n\\caption{Benchmark datasets.")
    b = app.index("\\end{table}", a) + len("\\end{table}")
    gen = (DMLR / "tables/datasets.tex").read_text().rstrip("\n").replace("\\begin{table}[H]", "\\begin{table}[htbp]", 1)
    diff = list(difflib.unified_diff(app[a:b].splitlines(), gen.splitlines(), "inline", "generated", lineterm="", n=0))
    print(f"tab:datasets: {max(len(diff) - 2, 0)} diff lines")
    if gen != app[a:b]:
        texts["appendix"] = app[:a] + gen + app[b:]
        changed.add("appendix")
    if args.dry_run:
        print("dry run; nothing written" + (f" (would change {sorted(changed)})" if changed else ""))
        return
    for key in changed:
        files[key].write_text(texts[key])
    print("written:", sorted(changed) or "nothing (already up to date)")


if __name__ == "__main__":
    main()
