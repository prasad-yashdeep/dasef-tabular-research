"""Fetch licence and provenance metadata for every benchmark dataset from the OpenML API.

Metadata only (no data download). Writes results/statistics/benchmark44/dataset_provenance.csv
with one row per benchmark dataset: OpenML dataset id, OpenML name and version, licence string as
published on OpenML, upload date, original data URL, paper URL, citation text and the OpenML page URL.

Usage: python scripts/expansion/fetch_openml_provenance.py [--coverage results/statistics/benchmark44/coverage.csv]
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", default="results/statistics/benchmark44/coverage.csv")
    ap.add_argument("--datasets-yaml", default="configs/datasets.yaml")
    ap.add_argument("--inventory", default="results/statistics/benchmark44/dataset_inventory.csv")
    ap.add_argument("--out", default="results/statistics/benchmark44/dataset_provenance.csv")
    args = ap.parse_args()

    import openml  # metadata calls only

    cov = pd.read_csv(ROOT / args.coverage)
    cfg = {d["name"]: d for d in yaml.safe_load(open(ROOT / args.datasets_yaml))["datasets"]}
    inv = pd.read_csv(ROOT / args.inventory).drop_duplicates("dataset").set_index("dataset")
    rows = []
    for name, tier in zip(cov.dataset, cov.tier):
        oid = cfg.get(name, {}).get("openml_id")
        if oid is None and name in inv.index and pd.notna(inv.loc[name, "openml_id"]):
            oid = int(inv.loc[name, "openml_id"])
        rec = {"dataset": name, "tier": tier, "openml_id": oid}
        if oid is None:
            rec["error"] = "no openml id"
            rows.append(rec)
            continue
        for attempt in range(3):
            try:
                ds = openml.datasets.get_dataset(int(oid), download_data=False, download_qualities=False,
                                                 download_features_meta_data=False)
                rec.update({
                    "openml_name": ds.name,
                    "version": ds.version,
                    "licence": ds.licence,
                    "upload_date": ds.upload_date,
                    "original_data_url": ds.original_data_url,
                    "paper_url": ds.paper_url,
                    "citation": (ds.citation or "").replace("\n", " ").strip(),
                    "default_target": ds.default_target_attribute,
                    "collection_date": ds.collection_date,
                    "creator": "; ".join(ds.creator) if isinstance(ds.creator, list) else (ds.creator or ""),
                    "contributor": "; ".join(ds.contributor) if isinstance(ds.contributor, list) else (ds.contributor or ""),
                    "openml_url": f"https://www.openml.org/d/{int(oid)}",
                    "description_head": (ds.description or "")[:300].replace("\n", " "),
                })
                rec.pop("error", None)
                break
            except Exception as exc:  # network hiccups
                rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
                time.sleep(2 * (attempt + 1))
        rows.append(rec)
        print(name, oid, rec.get("licence"), rec.get("version"), rec.get("error", ""), flush=True)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False, quoting=csv.QUOTE_ALL)
    print("wrote", out, "rows:", len(rows))


if __name__ == "__main__":
    main()
