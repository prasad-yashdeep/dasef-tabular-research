#!/usr/bin/env python3
"""Create Demsar-style critical difference diagrams from Friedman/Nemenyi output."""
from __future__ import annotations

import re
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
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results" / "statistics" / "dataset_level" / "friedman_nemenyi.md"
OUT_DIR = ROOT / "results" / "figures" / "cd_diagrams"
TREATMENT_LABELS = {
    "raw": "raw",
    "raw_plus_formula": "raw+formula",
    "raw_plus_formula_plus_judgment": "raw+formula+judgment",
    "raw_plus_random_formula": "raw+random-formula",
    "raw_plus_random_all": "raw+random-all",
}


def parse_report(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^## ", text, flags=re.MULTILINE)
    parsed: list[dict] = []
    for block in blocks[1:]:
        header, *rest = block.splitlines()
        if " / " not in header:
            continue
        metric, model = [part.strip() for part in header.split(" / ", 1)]
        cd_match = re.search(r"Nemenyi CD .*?:\s*([0-9.]+)", block)
        n_match = re.search(r"- N =\s*(\d+)\s+datasets", block)
        rows = []
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("| ") or line.startswith("| Treatment") or line.startswith("|---"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 3:
                rows.append(
                    {
                        "treatment": cells[0],
                        "avg_rank": float(cells[1]),
                        "mean_score": float(cells[2]),
                    }
                )
        if rows and cd_match:
            parsed.append(
                {
                    "metric": metric,
                    "model": model,
                    "n": int(n_match.group(1)) if n_match else None,
                    "cd": float(cd_match.group(1)),
                    "ranks": pd.DataFrame(rows),
                }
            )
    return parsed


def cliques_by_cd(df: pd.DataFrame, cd: float) -> list[tuple[float, float]]:
    """Return maximal adjacent rank ranges whose endpoints differ by <= CD."""
    ranks = sorted(df["avg_rank"].tolist())
    cliques: list[tuple[float, float]] = []
    for i, start in enumerate(ranks):
        end = start
        for candidate in ranks[i + 1 :]:
            if candidate - start <= cd + 1e-12:
                end = candidate
        if end > start and not any(start >= a and end <= b for a, b in cliques):
            cliques.append((start, end))
    return cliques


def draw_diagram(item: dict) -> None:
    df = item["ranks"].copy()
    n_treatments = len(df)
    df["avg_rank"] = (n_treatments + 1) - df["avg_rank"]
    df = df.sort_values("avg_rank")
    cd = item["cd"]
    low = 1.0
    high = float(n_treatments)

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.set_xlim(low, high)
    ax.set_ylim(0, 1)
    ax.axis("off")

    y_axis = 0.58
    ax.hlines(y_axis, low, high, color="black", linewidth=1.2)
    for tick in range(1, n_treatments + 1):
        ax.vlines(tick, y_axis - 0.025, y_axis + 0.025, color="black", linewidth=1.0)
        ax.text(tick, y_axis + 0.06, str(tick), ha="center", va="bottom", fontsize=10)
    ax.text((low + high) / 2, y_axis + 0.15, "Average rank (lower is better)", ha="center", fontsize=11)

    cd_y = 0.82
    cd_start = low
    cd_end = min(high, cd_start + cd)
    ax.hlines(cd_y, cd_start, cd_end, color="black", linewidth=1.5)
    ax.vlines([cd_start, cd_end], cd_y - 0.035, cd_y + 0.035, color="black", linewidth=1.2)
    ax.text((cd_start + cd_end) / 2, cd_y + 0.05, f"CD = {cd:.3f}", ha="center", fontsize=9)

    left_rows = df.iloc[: (len(df) + 1) // 2].sort_values("avg_rank")
    right_rows = df.iloc[(len(df) + 1) // 2 :].sort_values("avg_rank", ascending=False)
    left_y = [0.42 - i * 0.09 for i in range(len(left_rows))]
    right_y = [0.42 - i * 0.09 for i in range(len(right_rows))]

    for (_, row), y in zip(left_rows.iterrows(), left_y, strict=False):
        rank = row["avg_rank"]
        label = TREATMENT_LABELS.get(row["treatment"], row["treatment"])
        ax.plot([rank, rank, low], [y_axis, y, y], color="black", linewidth=0.9)
        ax.text(low - 0.02, y, f"{label} ({rank:.2f})", ha="right", va="center", fontsize=9)

    for (_, row), y in zip(right_rows.iterrows(), right_y, strict=False):
        rank = row["avg_rank"]
        label = TREATMENT_LABELS.get(row["treatment"], row["treatment"])
        ax.plot([rank, rank, high], [y_axis, y, y], color="black", linewidth=0.9)
        ax.text(high + 0.02, y, f"{label} ({rank:.2f})", ha="left", va="center", fontsize=9)

    for offset, (start, end) in enumerate(cliques_by_cd(df, cd)):
        y = 0.18 - offset * 0.045
        ax.hlines(y, start, end, color="black", linewidth=3.0)

    METRIC_LABELS = {
        "roc_auc_ovr": "ROC-AUC (One-vs-Rest)",
        "balanced_accuracy": "Balanced Accuracy",
    }
    MODEL_LABELS = {
        "logistic_regression": "Logistic Regression",
        "random_forest": "Random Forest",
        "knn": "KNN",
        "xgboost": "XGBoost",
    }
    title = f"{METRIC_LABELS.get(item['metric'], item['metric'])}: {MODEL_LABELS.get(item['model'], item['model'])}"
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    safe = f"{item['metric']}__{item['model']}".replace("/", "_").replace(" ", "_")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{safe}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_DIR / f"{safe}.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    items = parse_report(INPUT)
    if len(items) != 8:
        print(f"Warning: expected 8 diagrams, parsed {len(items)}")
    for item in items:
        draw_diagram(item)
    print(f"Wrote {len(items)} CD diagrams to {OUT_DIR}")


if __name__ == "__main__":
    main()
