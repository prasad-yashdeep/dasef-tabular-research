"""Per-dataset semantic-control figure for the restructured benchmark.

One panel per downstream model: datasets sorted by the generator-averaged semantic delta
(raw+formula minus raw+permuted-formula, ROC-AUC), one dot per dataset, core datasets
marked, zero line, and the mean with its bootstrap CI as a band.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import os

import matplotlib

if os.environ.get("DASEF_FIG_PGF"):  # paper figures: text set by pdflatex in Latin Modern (Type 1), no Type 3 fonts
    matplotlib.use("pgf")
    matplotlib.rcParams.update({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False, "font.family": "serif",
                                "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage{lmodern}"})
else:
    matplotlib.use("Agg")
    matplotlib.rcParams["pdf.fonttype"] = 42  # embed TrueType outlines rather than Type 3 bitmap fonts
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODELS = [("logistic_regression", "Logistic regression"), ("knn", "KNN"), ("random_forest", "Random forest"), ("xgboost", "XGBoost")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-level", required=True)
    ap.add_argument("--summary", required=True, help="summary_pooled.csv")
    ap.add_argument("--metric", default="roc_auc_ovr")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    dl = pd.read_csv(args.dataset_level)
    summ = pd.read_csv(args.summary)
    summ = summ[summ.subset.str.startswith("all datasets")]
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.6), sharey=False)
    axes = axes.ravel()
    for ax, (model, label) in zip(axes, MODELS):
        sub = dl[(dl.metric == args.metric) & (dl.model == model)].sort_values("semantic")
        x = np.arange(len(sub))
        core = (sub.tier == "core").to_numpy()
        ax.axhline(0, color="black", lw=0.8)
        s = summ[(summ.metric == args.metric) & (summ.model == model) & (summ.contrast == "semantic")].iloc[0]
        ax.axhspan(s.ci95_lo, s.ci95_hi, color="tab:blue", alpha=0.12, lw=0)
        ax.axhline(s.mean_delta, color="tab:blue", lw=1.0, ls="--")
        ax.scatter(x[~core], sub.semantic.to_numpy()[~core], s=18, color="tab:blue", label="expansion dataset")
        ax.scatter(x[core], sub.semantic.to_numpy()[core], s=34, color="tab:red", marker="D", label="core dataset")
        ax.set_title(f"{label}: {int(s.wins)}/{int(s.n_datasets)} datasets $>0$, mean {s.mean_delta:+.3f}", fontsize=11)
        ax.set_xticks([])
        ax.tick_params(axis="y", labelsize=10)
        if ax in (axes[2], axes[3]):
            ax.set_xlabel("datasets (sorted by semantic $\\Delta$)", fontsize=10)
        if ax in (axes[0], axes[2]):
            ax.set_ylabel("semantic $\\Delta$ ROC-AUC", fontsize=10)
        if ax is axes[0]:
            ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, bbox_inches="tight")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
