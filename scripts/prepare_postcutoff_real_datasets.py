#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd


LOCAL_CACHE = Path("data/local_cache")


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    repo_id: str
    created: str
    updated: str
    source_url: str
    target_name: str
    task_note: str
    parquet_urls: tuple[str, ...]
    builder: str


def _read_parquets(urls: tuple[str, ...]) -> pd.DataFrame:
    frames = [pd.read_parquet(url) for url in urls]
    return pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [
        str(col)
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
        for col in out.columns
    ]
    return out


def build_salmonella(spec: DatasetSpec) -> pd.DataFrame:
    df = _clean_columns(_read_parquets(spec.parquet_urls))
    df = df.drop(columns=["InImage_ID"], errors="ignore")
    df = df.dropna(subset=["Serovar"]).reset_index(drop=True)
    return df.rename(columns={"Serovar": spec.target_name})


def build_tracker_radar(spec: DatasetSpec) -> pd.DataFrame:
    df = _clean_columns(_read_parquets(spec.parquet_urls))
    df = df.drop(columns=["domain", "label_source"], errors="ignore")
    df = df.dropna(subset=["label"]).reset_index(drop=True)
    return df.rename(columns={"label": spec.target_name})


def build_clinical_trials(spec: DatasetSpec) -> pd.DataFrame:
    df = _clean_columns(_read_parquets(spec.parquet_urls))
    df = df.drop(columns=["id"], errors="ignore")
    df = df.dropna(subset=["industry_sponsored"]).reset_index(drop=True)
    df["industry_sponsored"] = df["industry_sponsored"].astype(str).str.lower().isin({"true", "1", "yes"})
    return df.rename(columns={"industry_sponsored": spec.target_name})


def build_real_estate(spec: DatasetSpec) -> pd.DataFrame:
    df = _clean_columns(_read_parquets(spec.parquet_urls))
    df = df.dropna(subset=["price_eur"]).reset_index(drop=True)
    df[spec.target_name] = np.where(df["price_eur"] >= df["price_eur"].median(), "high_price", "low_price")
    return df.drop(columns=["price_eur", "page_url"], errors="ignore")


def build_water_quality(spec: DatasetSpec) -> pd.DataFrame:
    df = _clean_columns(_read_parquets(spec.parquet_urls))
    df = df.dropna(subset=["ecoli"]).reset_index(drop=True)
    df[spec.target_name] = np.where(df["ecoli"] >= df["ecoli"].median(), "high_ecoli", "low_ecoli")
    return df.drop(columns=["ecoli"], errors="ignore")


def build_prediction_markets(spec: DatasetSpec) -> pd.DataFrame:
    df = _clean_columns(_read_parquets(spec.parquet_urls))
    df = df.dropna(subset=["open", "close"]).reset_index(drop=True)
    df[spec.target_name] = np.where(df["close"] > df["open"], "up", "not_up")
    return df.drop(columns=["close", "timestamp"], errors="ignore")


BUILDERS: dict[str, Callable[[DatasetSpec], pd.DataFrame]] = {
    "salmonella": build_salmonella,
    "tracker_radar": build_tracker_radar,
    "clinical_trials": build_clinical_trials,
    "real_estate": build_real_estate,
    "water_quality": build_water_quality,
    "prediction_markets": build_prediction_markets,
}


SPECS: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        name="postcutoff_salmonella_serovar_20260401",
        repo_id="food-ai-nexus/salmonella-serovar-hyperspectral-spectra",
        created="2026-04-01",
        updated="2026-04-01",
        source_url="https://huggingface.co/datasets/food-ai-nexus/salmonella-serovar-hyperspectral-spectra",
        target_name="target_serovar",
        task_note="Real food-safety hyperspectral single-cell spectra; predict Salmonella serovar.",
        parquet_urls=(
            "https://huggingface.co/datasets/food-ai-nexus/salmonella-serovar-hyperspectral-spectra/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
            "https://huggingface.co/datasets/food-ai-nexus/salmonella-serovar-hyperspectral-spectra/resolve/refs%2Fconvert%2Fparquet/default/test/0000.parquet",
        ),
        builder="salmonella",
    ),
    DatasetSpec(
        name="postcutoff_tracker_radar_20260316",
        repo_id="olafuraron/tracker-radar-ml",
        created="2026-03-16",
        updated="2026-03-16",
        source_url="https://huggingface.co/datasets/olafuraron/tracker-radar-ml",
        target_name="target_tracker",
        task_note="Real web-tracking detector table with 295 behavioral/API-count features.",
        parquet_urls=(
            "https://huggingface.co/datasets/olafuraron/tracker-radar-ml/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
        ),
        builder="tracker_radar",
    ),
    DatasetSpec(
        name="postcutoff_clinical_trials_ai_20260517",
        repo_id="moncefem/clinical-trials-ai-2000-2025",
        created="2026-05-17",
        updated="2026-05-17",
        source_url="https://huggingface.co/datasets/moncefem/clinical-trials-ai-2000-2025",
        target_name="target_industry_sponsored",
        task_note="ClinicalTrials.gov AI/ML/digital-health trials table; predict whether a trial is industry-sponsored.",
        parquet_urls=(
            "https://huggingface.co/datasets/moncefem/clinical-trials-ai-2000-2025/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
        ),
        builder="clinical_trials",
    ),
    DatasetSpec(
        name="postcutoff_ro_real_estate_20260503",
        repo_id="palerflavius/ro-real-estate-listings",
        created="2026-05-03",
        updated="2026-06-08",
        source_url="https://huggingface.co/datasets/palerflavius/ro-real-estate-listings",
        target_name="target_price_band",
        task_note="Public Romanian real-estate listings scraped from property websites; predict above/below median price.",
        parquet_urls=tuple(
            f"https://huggingface.co/datasets/palerflavius/ro-real-estate-listings/resolve/refs%2Fconvert%2Fparquet/default/train/{i:04d}.parquet"
            for i in range(37)
        ),
        builder="real_estate",
    ),
    DatasetSpec(
        name="postcutoff_water_quality_nys_20260406",
        repo_id="food-ai-nexus/fecal-indicator-water-nys",
        created="2026-04-06",
        updated="2026-04-06",
        source_url="https://huggingface.co/datasets/food-ai-nexus/fecal-indicator-water-nys",
        target_name="target_ecoli_band",
        task_note="Real agricultural water-quality table; predict high versus low E. coli.",
        parquet_urls=(
            "https://huggingface.co/datasets/food-ai-nexus/fecal-indicator-water-nys/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
        ),
        builder="water_quality",
    ),
    DatasetSpec(
        name="postcutoff_prediction_markets_20260517",
        repo_id="ImpliedData/prediction-markets",
        created="2026-05-17",
        updated="2026-05-19",
        source_url="https://huggingface.co/datasets/ImpliedData/prediction-markets",
        target_name="target_price_up",
        task_note="Real prediction-market OHLCV sample; predict whether close exceeds open.",
        parquet_urls=(
            "https://huggingface.co/datasets/ImpliedData/prediction-markets/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
            "https://huggingface.co/datasets/ImpliedData/prediction-markets/resolve/refs%2Fconvert%2Fparquet/default/train/0001.parquet",
            "https://huggingface.co/datasets/ImpliedData/prediction-markets/resolve/refs%2Fconvert%2Fparquet/default/train/0002.parquet",
        ),
        builder="prediction_markets",
    ),
)


def write_dataset(spec: DatasetSpec, force: bool = False) -> dict:
    out_dir = LOCAL_CACHE / spec.name
    data_path = out_dir / "data.parquet"
    if data_path.exists() and not force:
        return {"name": spec.name, "status": "cached", "path": str(data_path)}

    df = BUILDERS[spec.builder](spec)
    if spec.target_name not in df.columns:
        raise ValueError(f"{spec.name}: missing target column {spec.target_name}")
    df = df.dropna(axis=1, how="all").reset_index(drop=True)
    if df[spec.target_name].nunique(dropna=True) < 2:
        raise ValueError(f"{spec.name}: target has <2 classes")

    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(data_path, index=False)
    meta = {
        **asdict(spec),
        "parquet_urls": list(spec.parquet_urls),
        "target_name": spec.target_name,
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "target_distribution": df[spec.target_name].astype(str).value_counts(dropna=False).to_dict(),
        "post_cutoff_claim": f"Hugging Face dataset repository created on {spec.created}.",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {"name": spec.name, "status": "written", "path": str(data_path), "rows": len(df), "columns": df.shape[1]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare real post-cutoff tabular datasets for DASEF.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--names", help="Comma-separated dataset names to prepare.")
    args = parser.parse_args()

    requested = set(args.names.split(",")) if args.names else None
    rows = []
    for spec in SPECS:
        if requested and spec.name not in requested:
            continue
        rows.append(write_dataset(spec, force=args.force))

    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
