#!/usr/bin/env python
"""Mechanism case study (Appendix A): one uniform hand-built interaction expansion.

Usage, from the repo root:

    python run_mechanism_case_study.py --out results/statistics/mechanism_panel_poc.json

Protocol (identical for every dataset, no per-dataset hand-picked features):
  * OpenML datasets (openml cache honoured); all rows used, no subsampling.
  * Categorical columns -> LabelEncoder integer codes (alphabetical order of the
    string values); numeric columns kept as they are.
  * Formula block on the ordinal-coded matrix X: all pairwise products x_i*x_j
    (i<j), all squares x_i^2, and all three-way products x_i*x_j*x_k (i<j<k).
    The three-way block is included only when the expanded matrix would still
    have fewer columns than rows (p_expanded < n); otherwise the dataset gets
    pairwise products + squares only. The rule applied is recorded per dataset
    ("pairwise+squares+threeway" or "pairwise+squares"). No ratios, no cap.
  * StandardScaler fit on all rows (as in the original proof of concept), then
    RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42).
  * LogisticRegression(max_iter=2000 raw / 3000 formula, random_state=42),
    RandomForestClassifier(n_estimators=100, random_state=42),
    KNeighborsClassifier(n_neighbors=5); scikit-learn defaults otherwise.
  * Metric: roc_auc (binary) or roc_auc_ovr_weighted (multiclass), mean over
    the 10 folds.

The output JSON keeps the structure and keys of
results/statistics/mechanism_panel_poc.json (feats, rows, lr_raw, rf_raw,
lr_formula, rf_formula, lr_delta, rf_delta, da_gap, verdict), which is what
scripts/make_paper_figures.py reads, and adds knn_raw, knn_formula, knn_delta,
rule, n_features_added, n_classes, metric and seconds.
"""
from __future__ import annotations

import argparse
import json
import time
import warnings
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

DATASETS: list[tuple[str, int]] = [
    ("tic-tac-toe", 50),
    ("monks-problems-1", 333),
    ("ionosphere", 59),
    ("glass", 41),
    ("haberman", 43),
    ("balance-scale", 11),
    ("vehicle", 54),
]


def block_network() -> None:
    """Hard-fail on any network access so the run is provably cache-only."""
    import socket
    import urllib.request

    import requests

    def _blocked(*args, **kwargs):
        raise RuntimeError("network access blocked (--offline)")

    requests.Session.request = _blocked  # type: ignore[assignment]
    urllib.request.urlopen = _blocked  # type: ignore[assignment]
    socket.socket.connect = _blocked  # type: ignore[assignment]


def load_openml(openml_id: int) -> tuple[pd.DataFrame, pd.Series]:
    import openml

    ds = openml.datasets.get_dataset(openml_id)
    X, y, _, _ = ds.get_data(target=ds.default_target_attribute)
    return X, pd.Series(y)


def ordinal_encode(X: pd.DataFrame) -> np.ndarray:
    from sklearn.preprocessing import LabelEncoder

    X = X.copy()
    for col in X.columns:
        if X[col].dtype == "object" or X[col].dtype.name == "category":
            X[col] = LabelEncoder().fit_transform(X[col].astype(str))
    return X.to_numpy(dtype=float)


def expand(X: np.ndarray, force_threeway: bool = False) -> tuple[np.ndarray, str]:
    n_rows, p = X.shape
    n_pw, n_sq, n_tw = p * (p - 1) // 2, p, p * (p - 1) * (p - 2) // 6
    use_threeway = force_threeway or (p + n_pw + n_sq + n_tw < n_rows)
    feats = [X[:, i] * X[:, j] for i, j in combinations(range(p), 2)]
    feats += [X[:, i] ** 2 for i in range(p)]
    rule = "pairwise+squares"
    if use_threeway:
        feats += [X[:, i] * X[:, j] * X[:, k] for i, j, k in combinations(range(p), 3)]
        rule = "pairwise+squares+threeway"
    return np.column_stack([X] + feats), rule


def score_models(X: np.ndarray, y: np.ndarray, n_classes: int, formula: bool) -> dict[str, float]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.preprocessing import StandardScaler

    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)
    scoring = "roc_auc_ovr_weighted" if n_classes > 2 else "roc_auc"
    X_scaled = np.nan_to_num(StandardScaler().fit_transform(X), nan=0.0, posinf=0.0, neginf=0.0)
    models = {
        "lr": LogisticRegression(max_iter=3000 if formula else 2000, random_state=42),
        "rf": RandomForestClassifier(n_estimators=100, random_state=42),
        "knn": KNeighborsClassifier(n_neighbors=5),
    }
    return {
        name: float(cross_val_score(model, X_scaled, y, cv=cv, scoring=scoring, error_score="raise").mean())
        for name, model in models.items()
    }


def verdict(lr_delta: float, rf_delta: float) -> str:
    """Label rule; reproduces all seven verdict strings of the original JSON."""
    gap = lr_delta - rf_delta
    if lr_delta >= 0.05 and gap >= 0.05:
        return "DA_confirmed"
    if lr_delta >= 0.02:
        return "marginal_but_RF_hurts" if rf_delta <= -0.01 else "marginal_DA"
    if lr_delta > 0.01 and rf_delta > 0.01:
        return "both_benefit"
    return "marginal"


def evaluate(name: str, openml_id: int, force_threeway: bool) -> dict:
    from sklearn.preprocessing import LabelEncoder

    t0 = time.time()
    X_df, y = load_openml(openml_id)
    X = ordinal_encode(X_df)
    y_enc = LabelEncoder().fit_transform(y.astype(str))
    n_classes = int(len(np.unique(y_enc)))
    raw = score_models(X, y_enc, n_classes, formula=False)
    X_formula, rule = expand(X, force_threeway=force_threeway)
    form = score_models(X_formula, y_enc, n_classes, formula=True)
    r4 = lambda v: round(float(v), 4)  # noqa: E731
    lr_delta, rf_delta = form["lr"] - raw["lr"], form["rf"] - raw["rf"]
    return {
        "feats": int(X.shape[1]),
        "rows": int(X.shape[0]),
        "lr_raw": r4(raw["lr"]),
        "rf_raw": r4(raw["rf"]),
        "lr_formula": r4(form["lr"]),
        "rf_formula": r4(form["rf"]),
        "lr_delta": r4(lr_delta),
        "rf_delta": r4(rf_delta),
        "da_gap": r4(lr_delta - rf_delta),
        "verdict": verdict(lr_delta, rf_delta),
        "knn_raw": r4(raw["knn"]),
        "knn_formula": r4(form["knn"]),
        "knn_delta": r4(form["knn"] - raw["knn"]),
        "rule": rule,
        "n_features_added": int(X_formula.shape[1] - X.shape[1]),
        "n_classes": n_classes,
        "metric": "roc_auc_ovr_weighted" if n_classes > 2 else "roc_auc",
        "seconds": round(time.time() - t0, 1),
    }


def print_table(results: dict[str, dict]) -> None:
    hdr = (
        f"{'dataset':17s} {'rule':27s} {'added':>5s} | {'LR raw':>7s} {'LR form':>7s} {'dLR':>7s} | "
        f"{'RF raw':>7s} {'RF form':>7s} {'dRF':>7s} | {'KNN raw':>7s} {'KNN frm':>7s} {'dKNN':>7s} | {'sec':>5s}"
    )
    print(hdr)
    print("-" * len(hdr))
    for name, r in results.items():
        print(
            f"{name:17s} {r['rule']:27s} {r['n_features_added']:5d} | "
            f"{r['lr_raw']:7.4f} {r['lr_formula']:7.4f} {r['lr_delta']:+7.4f} | "
            f"{r['rf_raw']:7.4f} {r['rf_formula']:7.4f} {r['rf_delta']:+7.4f} | "
            f"{r['knn_raw']:7.4f} {r['knn_formula']:7.4f} {r['knn_delta']:+7.4f} | {r['seconds']:5.1f}"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path, help="output JSON path")
    ap.add_argument("--datasets", default=None, help="comma-separated subset of dataset names")
    ap.add_argument("--force-threeway", action="store_true", help="include three-way products even when p_expanded >= n")
    ap.add_argument("--offline", action="store_true", help="block all network access (OpenML cache only)")
    args = ap.parse_args()
    if args.offline:
        block_network()
    wanted = set(args.datasets.split(",")) if args.datasets else None
    results: dict[str, dict] = {}
    t0 = time.time()
    for name, openml_id in DATASETS:
        if wanted and name not in wanted:
            continue
        print(f"[{name}] OpenML {openml_id} ...", flush=True)
        results[name] = evaluate(name, openml_id, args.force_threeway)
        r = results[name]
        print(f"  {r['rule']} (+{r['n_features_added']} features) lr {r['lr_raw']:.4f}->{r['lr_formula']:.4f} "
              f"rf {r['rf_raw']:.4f}->{r['rf_formula']:.4f} knn {r['knn_raw']:.4f}->{r['knn_formula']:.4f} "
              f"[{r['seconds']}s]", flush=True)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print()
    print_table(results)
    print(f"\nTotal wall time {time.time() - t0:.1f}s; wrote {args.out}")


if __name__ == "__main__":
    main()
