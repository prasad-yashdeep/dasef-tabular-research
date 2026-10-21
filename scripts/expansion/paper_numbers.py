"""Print every number the paper's prose quotes, straight from the files on disk, so the
text can be written from (and later checked against) one verified source.

Usage: python scripts/expansion/paper_numbers.py [--agg-dir results/statistics/benchmark44]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
SHORT = {"logistic_regression": "LR", "knn": "KNN", "random_forest": "RF", "xgboost": "XGB"}


def fmt_p(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def block(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agg-dir", default="results/statistics/benchmark44")
    args = ap.parse_args()
    agg = ROOT / args.agg_dir
    pooled = pd.read_csv(agg / "summary_pooled.csv")
    dl = pd.read_csv(agg / "dataset_level.csv")
    cov = pd.read_csv(agg / "coverage.csv")
    by_gen = pd.read_csv(agg / "summary_by_generator.csv")
    common = pd.read_csv(agg / "summary_common.csv")

    block("coverage")
    print("N datasets:", cov.dataset.nunique(), "| core:", (cov.tier == "core").sum(), "| expansion:", (cov.tier == "expansion").sum())
    print("generators per dataset:", cov.n_generators.value_counts().sort_index().to_dict())
    print("dataset x generator cells:", int(cov.n_generators.sum()))
    exp = cov[cov.tier == "expansion"]
    print("expansion datasets with 4/3/2/1 generators:", exp.n_generators.value_counts().sort_index().to_dict())

    for label in pooled.subset.unique():
        block(f"pooled: {label}")
        sub = pooled[pooled.subset == label]
        for metric in ["roc_auc_ovr", "balanced_accuracy"]:
            for contrast in ["semantic", "direct", "vs_random", "random_formula_vs_raw", "random_all_vs_raw", "permuted_vs_raw"]:
                for m in MODELS:
                    r = sub[(sub.metric == metric) & (sub.contrast == contrast) & (sub.model == m)]
                    if r.empty:
                        continue
                    r = r.iloc[0]
                    print(f"{metric:17s} {contrast:22s} {SHORT[m]:4s} N={int(r.n_datasets):3d} mean={r.mean_delta:+.4f} median={r.median_delta:+.4f} "
                          f"W/L/T={int(r.wins)}/{int(r.losses)}/{int(r.ties)} p={r.p_wilcoxon_exact:.2g} pHolm={r.p_holm_models:.2g} "
                          f"cliff={r.cliffs_delta:+.2f} CI=[{r.ci95_lo:+.4f},{r.ci95_hi:+.4f}]")

    block("common coverage (all four generators)")
    for metric in ["roc_auc_ovr"]:
        for contrast in ["semantic", "direct"]:
            for m in MODELS:
                r = common[(common.metric == metric) & (common.contrast == contrast) & (common.model == m)].iloc[0]
                print(f"{contrast:9s} {SHORT[m]:4s} N={int(r.n_datasets)} mean={r.mean_delta:+.4f} W/L={int(r.wins)}/{int(r.losses)} p={r.p_wilcoxon_exact:.2g} pHolm={r.p_holm_models:.2g}")

    block("by generator (ROC-AUC)")
    for label in by_gen.subset.unique():
        sub = by_gen[(by_gen.subset == label) & (by_gen.metric == "roc_auc_ovr")]
        for contrast in ["semantic", "direct"]:
            row = " | ".join(f"{SHORT[m]} {r.mean_delta:+.4f} {int(r.wins)}/{int(r.losses)} p={r.p_wilcoxon_exact:.2g}"
                             for m in MODELS for r in [sub[(sub.contrast == contrast) & (sub.model == m)].iloc[0]])
            print(f"{label:35s} {contrast:9s} {row}")

    block("per-dataset facts (ROC-AUC, generator-averaged)")
    roc = dl[dl.metric == "roc_auc_ovr"]
    for m in MODELS:
        s = roc[roc.model == m].set_index("dataset")
        top = s.semantic.sort_values(ascending=False)
        print(f"{SHORT[m]} semantic: top {[(d, round(v, 3)) for d, v in top.head(4).items()]} | negative: {[(d, round(v, 3)) for d, v in s.semantic[s.semantic < 0].items()]}")
        topd = s.direct.sort_values(ascending=False)
        print(f"{SHORT[m]} direct: top {[(d, round(v, 3)) for d, v in topd.head(4).items()]} | n>0.02: {int((s.direct > 0.02).sum())} | n>0.01: {int((s.direct > 0.01).sum())} | n<-0.005: {int((s.direct < -0.005).sum())} | min {topd.idxmin()} {topd.min():+.3f}")
    piv = roc.pivot(index="dataset", columns="model", values="raw")
    print("ceiling datasets (raw XGB >= 0.995):", sorted(piv[piv.xgboost >= 0.995].index))
    print("datasets where all four semantic deltas are ~0 (|d|<0.001):", sorted(roc.groupby("dataset").semantic.apply(lambda v: (v.abs() < 0.001).all()).pipe(lambda s: s[s].index)))
    d = roc.pivot(index="dataset", columns="model", values="direct")
    sm = roc.pivot(index="dataset", columns="model", values="semantic")
    gap = piv.xgboost - piv.logistic_regression
    rho, p = spearmanr(d.logistic_regression, gap)
    print(f"spearman direct LR vs (raw XGB - raw LR): rho={rho:+.2f} p={p:.2g}")
    rho, p = spearmanr(sm.logistic_regression, gap)
    print(f"spearman semantic LR vs (raw XGB - raw LR): rho={rho:+.2f} p={p:.2g}")
    rho, p = spearmanr(d.knn, piv.xgboost - piv.knn)
    print(f"spearman direct KNN vs (raw XGB - raw KNN): rho={rho:+.2f} p={p:.2g}")
    terc = pd.qcut(gap, 3, labels=["small", "mid", "large"])
    print("direct LR by raw-gap tercile (mean/median):", {k: (round(v.mean(), 4), round(v.median(), 4), len(v)) for k, v in d.logistic_regression.groupby(terc, observed=True)})
    print("tier means LR direct: core", round(roc[(roc.model == 'logistic_regression') & (roc.tier == 'core')].direct.mean(), 4),
          "expansion", round(roc[(roc.model == 'logistic_regression') & (roc.tier == 'expansion')].direct.mean(), 4))

    block("Friedman / Nemenyi (diagram convention: lower rank is better)")
    txt = (agg / "friedman_nemenyi.md").read_text()
    for sec in txt.split("## ")[1:]:
        head = sec.split("\n")[0]
        ranks = re.findall(r"\| (raw\S*) \| ([0-9.]+) \|", sec)
        cd = re.search(r"CD \(α=0.05\): ([0-9.]+)", sec)
        k = len(ranks)
        conv = ", ".join(f"{name.replace('raw_plus_', 'raw+')}={k + 1 - float(r):.2f}" for name, r in ranks)
        print(f"{head}: {conv} | CD={cd.group(1) if cd else '?'}")

    block("classical (ROC-AUC unless noted)")
    cl = pd.read_csv(ROOT / "results/statistics/benchmark44_classical/classical_vs_dasef_summary.csv")
    for _, r in cl.sort_values(["variant", "metric", "model"]).iterrows():
        print(f"{r.variant:13s} {r.metric:17s} {SHORT[r.model]:4s} N={int(r.n)} classical={r.classical_delta:+.4f} dasef={r.dasef_delta:+.4f} diff={r.classical_minus_dasef:+.4f} W={int(r.wins_classical)}/{int(r.wins_dasef)} p={r.p:.3g}")

    block("core tier: judgments, families (results/statistics/dataset_level/primary_hypotheses.csv)")
    ph = pd.read_csv(ROOT / "results/statistics/dataset_level/primary_hypotheses.csv")
    ph["pair"] = ph.baseline + " -> " + ph.candidate
    for pair in ph.pair.unique():
        for metric in ["roc_auc_ovr", "balanced_accuracy"]:
            sub = ph[(ph.pair == pair) & (ph.metric == metric)]
            if sub.empty:
                continue
            cells = " | ".join(f"{SHORT.get(r.downstream_model, r.downstream_model)} {r.mean_delta:+.4f} {int(r.wins)}/{int(r.losses)} p={r.p_value:.4f} pHolm={r.p_corrected_holm:.3f} cliff={r.cliffs_delta:+.2f}" for _, r in sub.iterrows())
            print(f"{pair:60s} {metric:17s} {cells}")
    jw = ph[(ph.baseline == "raw_plus_formula") & (ph.candidate == "raw_plus_formula_plus_judgment")]
    print("judgment wins of 40 cells:", {m: int(jw[jw.metric == m].wins.sum()) for m in ["roc_auc_ovr", "balanced_accuracy"]})
    perm = (ROOT / "results/statistics/permuted_control/formula_vs_permuted_summary.md").read_text()
    print(perm)

    block("anonymized control")
    print((ROOT / "results/statistics/anonymized_control/anonymized_summary.md").read_text())

    block("anonymized versus random expressions (GPT-5.5 Pro core cells; Section 5.8)")
    try:
        from scipy.stats import wilcoxon
        an = pd.read_csv(ROOT / "results/anonymized_control/anonymized_per_run.csv")
        dgr = pd.read_csv(ROOT / "results/statistics/random_formula_control/dataset_generator_level.csv")
        g = dgr[(dgr.generator == "gpt-5.5-pro") & (dgr.tier == "core") & (dgr.metric == "roc_auc_ovr")]
        for m in ["logistic_regression", "knn"]:
            a = an[(an.metric == "roc_auc_ovr") & (an.downstream_model == m)].set_index("dataset")
            r = g[g.model == m].set_index("dataset")
            common = sorted(set(a.index) & set(r.index))
            for label, d in [("anonymized formula - random expr.", a.loc[common, "formula"] - r.loc[common, "raw_plus_random_formula_fx"]),
                             ("named formula - random expr.    ", r.loc[common, "raw_plus_formula"] - r.loc[common, "raw_plus_random_formula_fx"])]:
                nz = d[d != 0]
                print(f"{SHORT[m]:4s} {label} N={len(d)} mean={d.mean():+.4f} W/L={int((d > 0).sum())}/{int((d < 0).sum())} p={wilcoxon(nz, method='exact').pvalue:.3f}")
    except FileNotFoundError as exc:
        print("skipped:", exc)

    block("downstream awareness (results/statistics/awareness_full)")
    for f in sorted((ROOT / "results/statistics/awareness_full").glob("downstream_awareness_*.md")):
        t = f.read_text()
        m = re.search(r"Matched comparisons: (\d+).*?beats best mismatch: (\d+).*?loses to best mismatch: (\d+)", t, re.S)
        print(f.name, m.groups() if m else "?")

    block("leakage equivalence")
    t = (ROOT / "results/statistics/dataset_level/leakage_equivalence.md").read_text()
    print("\n".join(t.split("\n")[:20]))

    block("thin schemas / constant columns (scan)")
    scan = ROOT / "results/statistics/benchmark44/formula_column_scan.csv"
    if scan.exists():
        sc = pd.read_csv(scan)
        print("runs:", len(sc), "| mean formula count core/expansion:", round(sc[sc.tier == 'core'].n_formula.mean(), 2), round(sc[sc.tier == 'expansion'].n_formula.mean(), 2))
        print("runs with <5 usable columns:", sc[sc.n_usable < 5][["tier", "gen", "dataset", "n_formula", "n_usable"]].to_string(index=False))
        print("all-NaN columns:", int(sc.n_allnan.sum()), "| constant columns:", int(sc.n_const.sum()), "in", int((sc.n_const > 0).sum()), "runs")


if __name__ == "__main__":
    main()
