"""LaTeX tables for the restructured benchmark, generated from the aggregation CSVs.

Writes to --out-dir:
  semantic_direct.tex      main table: semantic / direct / vs-random per model and metric (pooled)
  by_generator.tex         semantic and direct ROC-AUC per generator
  random_controls.tex      random-formula, random-all and permuted minus raw (dimensionality controls)
  per_dataset.tex          appendix longtable: per-dataset semantic and direct ROC-AUC per model
  raw_scores.tex           appendix longtable: raw ROC-AUC per dataset per model
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

MM = {"logistic_regression": "Logistic regression", "random_forest": "Random forest", "knn": "KNN", "xgboost": "XGBoost"}
MORDER = ["logistic_regression", "knn", "random_forest", "xgboost"]
METS = {"roc_auc_ovr": "ROC-AUC", "balanced_accuracy": "Bal. accuracy"}
GEN = {"gpt-5.5-pro": "GPT-5.5 Pro", "gemini-3.1-pro-preview": "Gemini 3.1 Pro Preview", "claude-opus-4.7": "Claude Opus 4.7", "claude-sonnet-4.6": "Claude Sonnet 4.6"}


def fp(p: float) -> str:
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def tex(s: str) -> str:
    return s.replace("_", "\\_")


def row(summ: pd.DataFrame, subset_prefix: str, metric: str, model: str, contrast: str) -> pd.Series:
    return summ[(summ.subset.str.startswith(subset_prefix)) & (summ.metric == metric) & (summ.model == model) & (summ.contrast == contrast)].iloc[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agg-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    agg = Path(args.agg_dir); out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    pooled = pd.read_csv(agg / "summary_pooled.csv"); bygen = pd.read_csv(agg / "summary_by_generator.csv")
    dl = pd.read_csv(agg / "dataset_level.csv")

    # 1. main table
    L = ["\\begin{tabular}{llrrrrrrrrr}", "\\toprule",
         "Metric & Downstream model & $N$ & Semantic $\\Delta$ & W/L & $p$ & $p_{\\mathrm{Holm}}$ & Direct $\\Delta$ & W/L & $p$ & $p_{\\mathrm{Holm}}$ \\\\", "\\midrule"]
    for met in METS:
        for m in MORDER:
            s = row(pooled, "all datasets", met, m, "semantic"); d = row(pooled, "all datasets", met, m, "direct")
            L.append(f"{METS[met]} & {MM[m]} & {int(s.n_datasets)} & {s.mean_delta:+.4f} & {int(s.wins)}/{int(s.losses)} & {fp(s.p_wilcoxon_exact)} & {fp(s.p_holm_models)} & {d.mean_delta:+.4f} & {int(d.wins)}/{int(d.losses)} & {fp(d.p_wilcoxon_exact)} & {fp(d.p_holm_models)} \\\\")
        if met == "roc_auc_ovr":
            L.append("\\midrule")
    L += ["\\bottomrule", "\\end{tabular}"]
    (out / "semantic_direct.tex").write_text("\n".join(L) + "\n")

    # 2. by generator (ROC-AUC)
    L = ["\\begin{tabular}{llrrrrrrr}", "\\toprule", "Generator & Downstream model & $N$ & Semantic $\\Delta$ & W/L & $p$ & Direct $\\Delta$ & W/L & $p$ \\\\", "\\midrule"]
    for g in GEN:
        subs = [s for s in bygen.subset.unique() if s.startswith(g)]
        if not subs:
            continue
        for m in MORDER:
            s = row(bygen, g, "roc_auc_ovr", m, "semantic"); d = row(bygen, g, "roc_auc_ovr", m, "direct")
            L.append(f"{GEN[g] if m == MORDER[0] else ''} & {MM[m]} & {int(s.n_datasets)} & {s.mean_delta:+.4f} & {int(s.wins)}/{int(s.losses)} & {fp(s.p_wilcoxon_exact)} & {d.mean_delta:+.4f} & {int(d.wins)}/{int(d.losses)} & {fp(d.p_wilcoxon_exact)} \\\\")
        L.append("\\midrule")
    L[-1] = "\\bottomrule"; L.append("\\end{tabular}")
    (out / "by_generator.tex").write_text("\n".join(L) + "\n")

    # 3. random controls (ROC-AUC, pooled)
    L = ["\\begin{tabular}{lrrrrrrr}", "\\toprule", "Downstream model & $N$ & Random-formula $-$ raw & W/L & Random-all $-$ raw & W/L & Permuted $-$ raw & W/L \\\\", "\\midrule"]
    for m in MORDER:
        a = row(pooled, "all datasets", "roc_auc_ovr", m, "random_formula_vs_raw"); b = row(pooled, "all datasets", "roc_auc_ovr", m, "random_all_vs_raw"); c = row(pooled, "all datasets", "roc_auc_ovr", m, "permuted_vs_raw")
        L.append(f"{MM[m]} & {int(a.n_datasets)} & {a.mean_delta:+.4f} & {int(a.wins)}/{int(a.losses)} & {b.mean_delta:+.4f} & {int(b.wins)}/{int(b.losses)} & {c.mean_delta:+.4f} & {int(c.wins)}/{int(c.losses)} \\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    (out / "random_controls.tex").write_text("\n".join(L) + "\n")

    # 4. per-dataset appendix (ROC-AUC semantic and direct per model)
    piv_s = dl[dl.metric == "roc_auc_ovr"].pivot(index=["tier", "dataset"], columns="model", values="semantic")
    piv_d = dl[dl.metric == "roc_auc_ovr"].pivot(index=["tier", "dataset"], columns="model", values="direct")
    ngen = dl.drop_duplicates("dataset").set_index("dataset").n_generators
    L = ["\\begin{longtable}{llr rrrr rrrr}",
         "\\caption{Per-dataset ROC-AUC deltas, averaged over the generators covering each dataset (gen.). Semantic: raw+formula minus raw+permuted-formula; direct: raw+formula minus raw.}\\label{tab:per-dataset}\\\\",
         "\\toprule", "Tier & Dataset & Gen. & \\multicolumn{4}{c}{Semantic $\\Delta$} & \\multicolumn{4}{c}{Direct $\\Delta$} \\\\",
         " & & & LR & KNN & RF & XGB & LR & KNN & RF & XGB \\\\", "\\midrule", "\\endfirsthead",
         "\\toprule", "Tier & Dataset & Gen. & LR & KNN & RF & XGB & LR & KNN & RF & XGB \\\\", "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    for (tier, ds) in sorted(piv_s.index, key=lambda t: (t[0] != "core", t[1])):
        s = piv_s.loc[(tier, ds)]; d = piv_d.loc[(tier, ds)]
        L.append(f"{tier} & {tex(ds)} & {int(ngen[ds])} & " + " & ".join(f"{s[m]:+.3f}" for m in MORDER) + " & " + " & ".join(f"{d[m]:+.3f}" for m in MORDER) + " \\\\")
    L.append("\\end{longtable}")
    (out / "per_dataset.tex").write_text("\n".join(L) + "\n")

    # 5. raw scores appendix
    piv_r = dl[dl.metric == "roc_auc_ovr"].pivot(index=["tier", "dataset"], columns="model", values="raw")
    L = ["\\begin{longtable}{llrrrr}", "\\caption{Raw-feature ROC-AUC per dataset and downstream model (generator-averaged evaluation split; the raw matrix is shared across generators).}\\label{tab:raw-scores}\\\\",
         "\\toprule", "Tier & Dataset & LR & KNN & RF & XGB \\\\", "\\midrule", "\\endfirsthead", "\\toprule", "Tier & Dataset & LR & KNN & RF & XGB \\\\", "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    for (tier, ds) in sorted(piv_r.index, key=lambda t: (t[0] != "core", t[1])):
        r = piv_r.loc[(tier, ds)]
        L.append(f"{tier} & {tex(ds)} & " + " & ".join(f"{r[m]:.3f}" for m in MORDER) + " \\\\")
    L.append("\\end{longtable}")
    (out / "raw_scores.tex").write_text("\n".join(L) + "\n")
    print("wrote tables to", out)


if __name__ == "__main__":
    main()
