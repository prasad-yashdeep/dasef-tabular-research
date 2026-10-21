"""Core-tier LaTeX tables generated from the statistics files (no hand transcription):

  paper/tables/judgment.tex       incremental effect of per-row judgments (10 core datasets,
                                  all 12 schema runs per dataset), from
                                  results/statistics/dataset_level/primary_hypotheses.csv
  paper/tables/core_families.tex  semantic and direct contrasts on the core tier averaged over
                                  all three schema families and four generators, from
                                  results/statistics/permuted_control/formula_vs_permuted_dataset_level.csv
                                  and primary_hypotheses.csv
  paper/tables/anonymized.tex     anonymized-column control, from
                                  results/statistics/anonymized_control/anonymized_summary.csv

Usage: python scripts/expansion/make_core_tables.py --out-dir paper/tables
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[2]
MM = {"logistic_regression": "Logistic regression", "knn": "KNN", "random_forest": "Random forest", "xgboost": "XGBoost"}
MORDER = ["logistic_regression", "knn", "random_forest", "xgboost"]
METRICS = [("roc_auc_ovr", "ROC-AUC"), ("balanced_accuracy", "Bal. accuracy")]


def fp(p: float) -> str:
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def exact_p(x: np.ndarray) -> float:
    x = x[x != 0]
    if len(x) == 0:
        return 1.0
    try:
        return float(wilcoxon(x, method="exact").pvalue)
    except Exception:
        return float(wilcoxon(x).pvalue)


def judgment_table(ph: pd.DataFrame) -> str:
    L = ["\\begin{tabular}{llrrrrr}", "\\toprule", "Metric & Downstream model & $N$ & Mean $\\Delta$ & W/L/T & Cliff's $\\delta$ & $p$ \\\\", "\\midrule"]
    for i, (metric, label) in enumerate(METRICS):
        if i:
            L.append("\\midrule")
        for m in MORDER:
            r = ph[(ph.metric == metric) & (ph.baseline == "raw_plus_formula") & (ph.candidate == "raw_plus_formula_plus_judgment") & (ph.downstream_model == m)].iloc[0]
            L.append(f"{label} & {MM[m]} & {int(r.n_datasets)} & {r.mean_delta:+.4f} & {int(r.wins)}/{int(r.losses)}/{int(r.ties)} & {r.cliffs_delta:+.2f} & {r.p_value:.4f} \\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(L) + "\n"


def core_families_table(ph: pd.DataFrame, perm: pd.DataFrame) -> str:
    L = ["\\begin{tabular}{llrrrrrrr}", "\\toprule",
         "Metric & Downstream model & $N$ & Semantic $\\Delta$ & W/L & $p$ & Direct $\\Delta$ & W/L & $p$ \\\\", "\\midrule"]
    for i, (metric, label) in enumerate(METRICS):
        if i:
            L.append("\\midrule")
        for m in MORDER:
            s = perm[(perm.metric == metric) & (perm.downstream_model == m)].mean_delta_formula_minus_permuted.to_numpy()
            d = ph[(ph.metric == metric) & (ph.baseline == "raw") & (ph.candidate == "raw_plus_formula") & (ph.downstream_model == m)].iloc[0]
            L.append(f"{label} & {MM[m]} & {len(s)} & {s.mean():+.4f} & {int((s > 0).sum())}/{int((s < 0).sum())} & {fp(exact_p(s))} & "
                     f"{d.mean_delta:+.4f} & {int(d.wins)}/{int(d.losses)} & {fp(d.p_value)} \\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(L) + "\n"


def anonymized_table(an: pd.DataFrame) -> str:
    L = ["\\begin{tabular}{llrrrr}", "\\toprule", "Metric & Downstream model & Direct $\\Delta$ & Semantic $\\Delta$ & Sem. W/L & Sem. $p$ \\\\", "\\midrule"]
    for i, (metric, label) in enumerate(METRICS):
        if i:
            L.append("\\midrule")
        for m in MORDER:
            r = an[(an.metric == metric) & (an.downstream_model == m)].iloc[0]
            L.append(f"{label} & {MM[m]} & {r.direct_delta:+.4f} & {r.semantic_delta:+.4f} & {int(r.semantic_wins)}/{int(r.semantic_losses)} & {r.semantic_p:.4f} \\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="paper/tables")
    args = ap.parse_args()
    out = ROOT / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    ph = pd.read_csv(ROOT / "results/statistics/dataset_level/primary_hypotheses.csv")
    perm = pd.read_csv(ROOT / "results/statistics/permuted_control/formula_vs_permuted_dataset_level.csv")
    an = pd.read_csv(ROOT / "results/statistics/anonymized_control/anonymized_summary.csv")
    (out / "judgment.tex").write_text(judgment_table(ph))
    (out / "core_families.tex").write_text(core_families_table(ph, perm))
    (out / "anonymized.tex").write_text(anonymized_table(an))
    for f in ["judgment.tex", "core_families.tex", "anonymized.tex"]:
        print(f"--- {f}"); print((out / f).read_text())


if __name__ == "__main__":
    main()
