#!/usr/bin/env python3
"""Generate publication figures used by the DASEF TMLR paper."""
from __future__ import annotations

import os

import json
from pathlib import Path

import matplotlib as mpl

if os.environ.get("DASEF_FIG_PGF"):  # paper figures: text set by pdflatex in Latin Modern (Type 1), no Type 3 fonts
    mpl.use("pgf")
    mpl.rcParams.update({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False,
                         "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage{lmodern}"})
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "results" / "figures"
DATASET_DELTAS = ROOT / "results" / "statistics" / "dataset_level" / "per_dataset_deltas.csv"
PERMUTED_DELTAS = (
    ROOT / "results" / "statistics" / "permuted_control" / "formula_vs_permuted_dataset_level.csv"
)
MECHANISM_JSON = ROOT / "results" / "statistics" / "mechanism_panel_poc.json"

DATASET_ORDER = [
    "adult_income",
    "bank_marketing",
    "blood_transfusion",
    "car_evaluation",
    "credit_g",
    "electricity",
    "phoneme",
    "pima_diabetes",
    "qsar_biodegradation",
    "spambase",
]

DATASET_LABELS = {
    "adult_income": "adult",
    "bank_marketing": "bank",
    "blood_transfusion": "blood",
    "car_evaluation": "car",
    "credit_g": "credit",
    "electricity": "electricity",
    "phoneme": "phoneme",
    "pima_diabetes": "pima",
    "qsar_biodegradation": "qsar",
    "spambase": "spambase",
    "tic-tac-toe": "tic-tac-toe",
    "monks-problems-1": "monks-1",
    "ionosphere": "ionosphere",
}

MODEL_ORDER = ["logistic_regression", "random_forest", "knn", "xgboost"]
MODEL_LABELS = {
    "logistic_regression": "LR",
    "random_forest": "RF",
    "knn": "KNN",
    "xgboost": "XGB",
}


def configure_style() -> None:
    sns.set_theme(style="whitegrid", context="paper")
    mpl.rcParams.update(
        {
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 11,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save(fig: mpl.figure.Figure, filename: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / filename, bbox_inches="tight")
    plt.close(fig)


def make_delta_heatmap() -> None:
    df = pd.read_csv(DATASET_DELTAS)
    df = df[
        (df["metric"] == "roc_auc_ovr")
        & (df["baseline"] == "raw")
        & (df["candidate"] == "raw_plus_formula")
    ].copy()
    matrix = (
        df.pivot_table(
            index="downstream_model",
            columns="dataset",
            values="delta",
            aggfunc="mean",
        )
        .reindex(index=MODEL_ORDER, columns=DATASET_ORDER)
        .rename(index=MODEL_LABELS, columns=DATASET_LABELS)
    )

    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    sns.heatmap(
        matrix,
        ax=ax,
        cmap="RdBu",
        center=0,
        vmin=-0.11,
        vmax=0.11,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": r"$\Delta$ ROC-AUC", "shrink": 0.8},
        annot=matrix.map(lambda v: "0.000" if abs(v) < 0.0005 else f"{v:+.3f}"),
        fmt="",
        annot_kws={"fontsize": 7},
    )
    ax.set_title("Direct effect of formula features ($\\Delta$ ROC-AUC vs. raw)")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Downstream model")
    ax.tick_params(axis="x", rotation=35)
    save(fig, "delta_heatmap.pdf")


def make_loo_stability() -> None:
    dropped = DATASET_ORDER
    p_values = np.full(len(dropped), 0.004)
    full_p = 0.002

    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    x = np.arange(len(dropped))
    ax.scatter(x, p_values, s=46, color="#2A6FBB", edgecolor="white", linewidth=0.7, zorder=3)
    ax.axhline(full_p, color="#1B1B1B", linewidth=1.2, linestyle="-", label="Full sample p=0.002")
    ax.axhline(0.05, color="#B23A48", linewidth=1.2, linestyle="--", label=r"$\alpha=0.05$")
    ax.set_xticks(x)
    ax.set_xticklabels([DATASET_LABELS[d] for d in dropped], rotation=35, ha="right")
    ax.set_ylim(0, 0.06)
    ax.set_ylabel("Wilcoxon p-value")
    ax.set_xlabel("Dataset removed")
    ax.set_title("Leave-one-dataset-out stability of the LR semantic-control result")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(axis="x", visible=False)
    save(fig, "loo_stability.pdf")


def make_mechanism_panel() -> None:
    data = json.loads(MECHANISM_JSON.read_text(encoding="utf-8"))
    datasets = ["tic-tac-toe", "monks-problems-1", "ionosphere"]
    lr = [data[d]["lr_delta"] for d in datasets]
    rf = [data[d]["rf_delta"] for d in datasets]

    fig, ax = plt.subplots(figsize=(6.4, 3.25))
    x = np.arange(len(datasets))
    width = 0.34
    colors = ["#2A6FBB", "#E6862A"]
    ax.bar(x - width / 2, lr, width, label="LR lift", color=colors[0])
    ax.bar(x + width / 2, rf, width, label="RF lift", color=colors[1])
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([DATASET_LABELS[d] for d in datasets])
    ax.set_ylabel(r"$\Delta$ ROC-AUC vs. raw")
    ax.set_title("Model-appropriate mechanism: hand-built interaction features help LR, not RF")
    ax.legend(frameon=True, loc="upper right")
    for xpos, value in zip(x - width / 2, lr, strict=True):
        ax.text(xpos, value + 0.008, f"+{value:.3f}", ha="center", va="bottom", fontsize=8)
    for xpos, value in zip(x + width / 2, rf, strict=True):
        label = f"{value:+.3f}"
        va = "bottom" if value >= 0 else "top"
        offset = 0.006 if value >= 0 else -0.006
        ax.text(xpos, value + offset, label, ha="center", va=va, fontsize=8)
    ax.set_ylim(-0.035, 0.42)
    save(fig, "mechanism_panel.pdf")


def make_permutation_control() -> None:
    df = pd.read_csv(PERMUTED_DELTAS)
    df = df[
        (df["metric"] == "roc_auc_ovr") & (df["downstream_model"] == "logistic_regression")
    ].copy()
    df["dataset"] = pd.Categorical(df["dataset"], categories=DATASET_ORDER, ordered=True)
    df = df.sort_values("dataset")

    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    x = np.arange(len(df))
    vals = df["mean_delta_formula_minus_permuted"].to_numpy()
    bars = ax.bar(x, vals, color="#2A6FBB", edgecolor="#173F6B", linewidth=0.5)
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([DATASET_LABELS[d] for d in df["dataset"].astype(str)], rotation=35, ha="right")
    ax.set_ylabel(r"$\Delta$ ROC-AUC (formula $-$ permuted)")
    ax.set_xlabel("Dataset")
    ax.set_title("Semantic control: formula vs. permuted-formula (LR, ROC-AUC)")
    ax.set_ylim(0, max(vals) + 0.04)
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, vals, strict=True):
        if True:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.012,
                f"+{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )
    save(fig, "permutation_control.pdf")


def main() -> None:
    configure_style()
    make_delta_heatmap()
    # make_loo_stability() removed: the LOO result is fully conveyed by Table 7;
    # the single-panel p-value scatter (10 identical points) added no information.
    make_mechanism_panel()
    make_permutation_control()
    print(f"Wrote paper figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
