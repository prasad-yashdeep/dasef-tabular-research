#!/usr/bin/env python
"""Download datasets from alternative sources when OpenML API is down.

Downloads from UCI, sklearn, or direct URLs and saves as parquet in a local
cache that the DASEF loader can fall back to.
"""
from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_DIR = Path("data/local_cache")


def save_dataset(name: str, X: pd.DataFrame, y: pd.Series, target_name: str):
    out_dir = CACHE_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    df = X.copy()
    df[target_name] = y
    df.to_parquet(out_dir / "data.parquet", index=False)
    meta = {"target_name": target_name, "n_rows": len(df), "n_features": X.shape[1],
            "feature_names": list(X.columns), "classes": sorted(y.unique().tolist())}
    import json
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"  ✓ Saved {name}: {len(df)} rows × {X.shape[1]} features → {out_dir}")


def download_spambase():
    """UCI ID 94, OpenML ID 44"""
    import urllib.request
    print("Downloading spambase from UCI...")
    url = "https://archive.ics.uci.edu/static/public/94/spambase.zip"
    resp = urllib.request.urlopen(url, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(resp.read()))
    data = pd.read_csv(io.StringIO(z.read("spambase.data").decode()), header=None)
    # Last column is the target (1=spam, 0=not spam)
    X = data.iloc[:, :-1]
    X.columns = [f"word_freq_{i}" if i < 48 else f"char_freq_{i-48}" if i < 54 
                 else ["capital_run_length_average", "capital_run_length_longest", 
                       "capital_run_length_total"][i-54] for i in range(57)]
    y = data.iloc[:, -1].map({1: "spam", 0: "not_spam"})
    save_dataset("spambase", X, y, "class")


def download_adult_income():
    """UCI ID 2, OpenML ID 1590"""
    import urllib.request
    print("Downloading adult_income from UCI...")
    url = "https://archive.ics.uci.edu/static/public/2/adult.zip"
    resp = urllib.request.urlopen(url, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(resp.read()))
    cols = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status",
            "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss",
            "hours_per_week", "native_country", "income"]
    data = pd.read_csv(io.StringIO(z.read("adult.data").decode()), 
                       names=cols, skipinitialspace=True, na_values="?")
    test = pd.read_csv(io.StringIO(z.read("adult.test").decode()),
                       names=cols, skipinitialspace=True, na_values="?", skiprows=1)
    data = pd.concat([data, test], ignore_index=True).dropna()
    X = data.drop(columns=["income"])
    y = data["income"].str.strip(".").map(lambda x: "<=50K" if "<=50K" in x else ">50K")
    # Encode categoricals
    for col in X.select_dtypes(include="object").columns:
        X[col] = X[col].astype("category").cat.codes
    save_dataset("adult_income", X, y, "class")


def download_bank_marketing():
    """UCI ID 222, OpenML ID 1461"""
    import urllib.request
    print("Downloading bank_marketing from UCI...")
    url = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"
    resp = urllib.request.urlopen(url, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(resp.read()))
    # Use bank-full.csv (all examples)
    fname = [n for n in z.namelist() if "bank-full.csv" in n][0]
    data = pd.read_csv(io.StringIO(z.read(fname).decode()), sep=";")
    X = data.drop(columns=["y"])
    y = data["y"]
    for col in X.select_dtypes(include="object").columns:
        X[col] = X[col].astype("category").cat.codes
    save_dataset("bank_marketing", X, y, "class")


def download_car_evaluation():
    """UCI ID 19, OpenML ID 40975"""
    import urllib.request
    print("Downloading car_evaluation from UCI...")
    url = "https://archive.ics.uci.edu/static/public/19/car+evaluation.zip"
    resp = urllib.request.urlopen(url, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(resp.read()))
    cols = ["buying", "maint", "doors", "persons", "lug_boot", "safety", "class"]
    data = pd.read_csv(io.StringIO(z.read("car.data").decode()), names=cols)
    X = data.drop(columns=["class"])
    y = data["class"]
    for col in X.select_dtypes(include="object").columns:
        X[col] = X[col].astype("category").cat.codes
    save_dataset("car_evaluation", X, y, "class")


def download_electricity():
    """OpenML ID 151 — originally from NSW electricity market data"""
    import urllib.request
    print("Downloading electricity from OpenML static mirror...")
    # This is the Elec2 dataset, available from multiple mirrors
    url = "https://raw.githubusercontent.com/automl/auto-sklearn/master/test/test_automl/data/electricity-normalized.csv"
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        data = pd.read_csv(io.BytesIO(resp.read()))
        X = data.drop(columns=["class"])
        y = data["class"]
        save_dataset("electricity", X, y, "class")
    except Exception as e:
        print(f"  ✗ Primary mirror failed: {e}")
        # Fallback: generate from description
        print("  Trying sklearn fetch...")
        from sklearn.datasets import fetch_openml
        data = fetch_openml(data_id=151, as_frame=True, parser='auto')
        X = data.data
        y = data.target
        save_dataset("electricity", X, y, "class")


def download_phoneme():
    """OpenML ID 1489"""
    import urllib.request
    print("Downloading phoneme...")
    # Phoneme dataset - 5 features, 5404 instances
    # Available from KEEL repository
    url = "https://sci2s.ugr.es/keel/dataset/data/classification/phoneme.zip"
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        z = zipfile.ZipFile(io.BytesIO(resp.read()))
        fname = [n for n in z.namelist() if n.endswith(".dat")][0]
        lines = z.read(fname).decode().split("\n")
        # KEEL format: skip header lines starting with @
        data_lines = [l for l in lines if l.strip() and not l.startswith("@")]
        data = pd.DataFrame([l.split(",") for l in data_lines])
        X = data.iloc[:, :-1].astype(float)
        X.columns = [f"V{i+1}" for i in range(X.shape[1])]
        y = data.iloc[:, -1].str.strip()
        save_dataset("phoneme", X, y, "Class")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")


def download_kc1():
    """OpenML ID 1067 — KC1 Software defect prediction"""
    import urllib.request
    print("Downloading kc1_software_defect from PROMISE repo...")
    url = "https://raw.githubusercontent.com/klainfo/DefectData/master/CombinedDataset/kc1.csv"
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        data = pd.read_csv(io.BytesIO(resp.read()))
        target_col = data.columns[-1]  # Last column is defect label
        X = data.drop(columns=[target_col])
        y = data[target_col].astype(str)
        for col in X.select_dtypes(include="object").columns:
            X[col] = X[col].astype("category").cat.codes
        save_dataset("kc1_software_defect", X, y, "defects")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")


def download_pc1():
    """OpenML ID 1068 — PC1 Software defect prediction"""
    import urllib.request
    print("Downloading pc1_software_defect from PROMISE repo...")
    url = "https://raw.githubusercontent.com/klainfo/DefectData/master/CombinedDataset/pc1.csv"
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        data = pd.read_csv(io.BytesIO(resp.read()))
        target_col = data.columns[-1]
        X = data.drop(columns=[target_col])
        y = data[target_col].astype(str)
        for col in X.select_dtypes(include="object").columns:
            X[col] = X[col].astype("category").cat.codes
        save_dataset("pc1_software_defect", X, y, "defects")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")


def download_nomao():
    """OpenML ID 1486 — 89 features, 34465 rows"""
    import urllib.request
    print("Downloading nomao...")
    # Large dataset, might need special handling
    url = "https://archive.ics.uci.edu/static/public/302/nomao.zip"
    try:
        resp = urllib.request.urlopen(url, timeout=60)
        z = zipfile.ZipFile(io.BytesIO(resp.read()))
        fname = [n for n in z.namelist() if n.endswith(".csv") or n.endswith(".arff")][0]
        if fname.endswith(".arff"):
            from scipy.io import arff
            data_raw, meta = arff.loadarff(io.BytesIO(z.read(fname)))
            data = pd.DataFrame(data_raw)
            target_col = data.columns[-1]
            X = data.drop(columns=[target_col])
            y = data[target_col].apply(lambda x: x.decode() if isinstance(x, bytes) else str(x))
        else:
            data = pd.read_csv(io.StringIO(z.read(fname).decode()))
            target_col = data.columns[-1]
            X = data.drop(columns=[target_col])
            y = data[target_col].astype(str)
        for col in X.select_dtypes(include="object").columns:
            X[col] = X[col].astype("category").cat.codes
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
        save_dataset("nomao", X, y, "Class")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")


def download_first_order_theorem():
    """OpenML ID 1475 — 51 features"""
    print("Skipping first_order_theorem_proving (no easy mirror, will retry OpenML later)")


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading datasets to {CACHE_DIR}\n")
    
    downloaders = [
        download_spambase,
        download_adult_income,
        download_bank_marketing,
        download_car_evaluation,
        download_phoneme,
        download_kc1,
        download_pc1,
        download_electricity,
        download_nomao,
        download_first_order_theorem,
    ]
    
    for fn in downloaders:
        try:
            fn()
        except Exception as e:
            print(f"  ✗ {fn.__name__} FAILED: {e}")
        print()
    
    # Summary
    print("\n=== Download Summary ===")
    for d in sorted(CACHE_DIR.iterdir()):
        if (d / "meta.json").exists():
            import json
            meta = json.loads((d / "meta.json").read_text())
            print(f"  ✓ {d.name}: {meta['n_rows']} rows × {meta['n_features']} feat")
        else:
            print(f"  ✗ {d.name}: incomplete")


if __name__ == "__main__":
    main()
