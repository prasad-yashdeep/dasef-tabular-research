"""Classical AutoFE baselines versus DASEF formulas on the restructured benchmark.

Computes classical deltas directly from dataset_model_summary.csv (mean_score per
dataset/variant/model/metric), not from the derived deltas_vs_dasef_formula.csv --
that convenience file is written by run_classical_baselines_expansion.py per dataset-batch
call and only reflects the --variants list of whichever call wrote it last, so when
different subprocess calls used different --variants (some expansion datasets were run
without OpenFE after a native crash), it silently dropped OpenFE rows for datasets that
did have them in dataset_model_summary.csv. Recomputing from the summary avoids that.

Joins with the generator-averaged DASEF direct delta from aggregate_benchmark44.py's
dataset_level.csv, on matched datasets.

Outputs (--out-dir): classical_vs_dasef_dataset_level.csv, classical_vs_dasef_summary.csv/.md,
and paper table classical.tex (ROC-AUC, mean classical delta, mean DASEF delta on the same
datasets, W/L of classical minus DASEF, exact Wilcoxon p).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

MM = {"logistic_regression": "Logistic regression", "knn": "KNN", "random_forest": "Random forest", "xgboost": "XGBoost"}
MORDER = ["logistic_regression", "knn", "random_forest", "xgboost"]
VAR = {"raw+poly": "Polynomial", "raw+openfe": "OpenFE", "raw+autofeat": "autofeat"}


def exact_p(x: np.ndarray) -> float:
    x = x[x != 0]
    if len(x) == 0:
        return 1.0
    try:
        return float(wilcoxon(x, method="exact").pvalue)
    except Exception:
        return float(wilcoxon(x).pvalue)


def classical_deltas(summary_dirs: list[str]) -> pd.DataFrame:
    frames = []
    for d in summary_dirs:
        df = pd.read_csv(Path(d) / "dataset_model_summary.csv")
        df = df[df.metric.isin(["roc_auc_ovr", "balanced_accuracy"])]
        raw = df[df.variant == "raw"].set_index(["dataset", "downstream_model", "metric"]).mean_score
        for variant in ["raw+poly", "raw+openfe", "raw+autofeat"]:
            sub = df[df.variant == variant].copy()
            if sub.empty:
                continue
            sub["classical_delta"] = sub.apply(
                lambda r: r.mean_score - raw.get((r.dataset, r.downstream_model, r.metric), np.nan), axis=1
            )
            sub = sub.dropna(subset=["classical_delta"])
            frames.append(sub.rename(columns={"downstream_model": "model"})[["dataset", "model", "metric", "variant", "classical_delta"]])
    out = pd.concat(frames, ignore_index=True)
    dup = out.groupby(["dataset", "model", "metric", "variant"]).size()
    if (dup > 1).any():
        out = out.groupby(["dataset", "model", "metric", "variant"], as_index=False).classical_delta.mean()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--classical-dirs", nargs="+", required=True, help="dirs each containing dataset_model_summary.csv")
    ap.add_argument("--dataset-level", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    cl = classical_deltas(args.classical_dirs)
    dl = pd.read_csv(args.dataset_level)[["dataset", "tier", "model", "metric", "direct", "n_generators"]].rename(columns={"direct": "dasef_delta"})
    j = cl.merge(dl, on=["dataset", "model", "metric"], how="inner")
    j["classical_minus_dasef"] = j.classical_delta - j.dasef_delta
    j.to_csv(out / "classical_vs_dasef_dataset_level.csv", index=False)
    rows = []
    for (variant, model, metric), g in j.groupby(["variant", "model", "metric"]):
        x = g.classical_minus_dasef.to_numpy()
        rows.append({"variant": variant, "model": model, "metric": metric, "n": len(g), "classical_delta": g.classical_delta.mean(),
                     "dasef_delta": g.dasef_delta.mean(), "classical_minus_dasef": x.mean(), "wins_classical": int((x > 0).sum()),
                     "wins_dasef": int((x < 0).sum()), "p": exact_p(x)})
    s = pd.DataFrame(rows)
    s.to_csv(out / "classical_vs_dasef_summary.csv", index=False)
    md = ["# Classical AutoFE vs DASEF formulas (restructured benchmark)", "", "| Variant | Model | Metric | N | classical Δ | DASEF Δ | classical − DASEF | W(classical)/W(DASEF) | p |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r in s.iterrows():
        md.append(f"| {r.variant} | {r.model} | {r.metric} | {r.n} | {r.classical_delta:+.4f} | {r.dasef_delta:+.4f} | {r.classical_minus_dasef:+.4f} | {r.wins_classical}/{r.wins_dasef} | {r.p:.3g} |")
    (out / "classical_vs_dasef_summary.md").write_text("\n".join(md))
    L = ["\\begin{tabular}{llrrrrr}", "\\toprule", "Variant & Downstream model & $N$ & Classical $\\Delta$ & DASEF formula $\\Delta$ & W/L (classical vs DASEF) & $p$ \\\\", "\\midrule"]
    for variant in ["raw+poly", "raw+openfe", "raw+autofeat"]:
        for m in MORDER:
            r = s[(s.variant == variant) & (s.model == m) & (s.metric == "roc_auc_ovr")]
            if r.empty:
                continue
            r = r.iloc[0]
            L.append(f"{VAR[variant]} & {MM[m]} & {int(r.n)} & {r.classical_delta:+.4f} & {r.dasef_delta:+.4f} & {int(r.wins_classical)}/{int(r.wins_dasef)} & {'$<$0.001' if r.p < 0.001 else f'{r.p:.3f}'} \\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    (out / "classical.tex").write_text("\n".join(L) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
