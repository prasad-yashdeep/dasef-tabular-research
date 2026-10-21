"""Dataset-level aggregation for the restructured benchmark: 10 core + expansion datasets,
four generators, linear/SVM schema family, five treatments.

Inputs
  --core-run-level   CSV built by pooled_matched.py for each generator (columns: dataset,
                     run_id, model, metric, raw, raw_plus_formula, raw_plus_random_formula,
                     raw_plus_random_all, raw_plus_permuted_formula, generator)
  --expansion-run-level  all_generators_run_level.csv from the expansion (same columns)
Outputs (--out-dir)
  dataset_generator_level.csv   one row per dataset x generator x model x metric
  dataset_level.csv             per dataset x model x metric, mean over the generators that
                                cover that dataset (with n_generators)
  summary_pooled.csv/.md        contrasts over datasets, generator-averaged
  summary_by_generator.csv/.md  contrasts over datasets, one generator at a time
  summary_common.csv/.md        contrasts over the datasets covered by all four generators
  coverage.csv                  which generators cover which dataset
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

TREATMENTS = ["raw", "raw_plus_formula", "raw_plus_random_formula", "raw_plus_random_all", "raw_plus_permuted_formula"]
CONTRASTS = {
    "semantic": ("raw_plus_formula", "raw_plus_permuted_formula"),
    "direct": ("raw_plus_formula", "raw"),
    "vs_random": ("raw_plus_formula", "raw_plus_random_formula"),
    "random_formula_vs_raw": ("raw_plus_random_formula", "raw"),
    "random_all_vs_raw": ("raw_plus_random_all", "raw"),
    "permuted_vs_raw": ("raw_plus_permuted_formula", "raw"),
}
MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
METRICS = ["roc_auc_ovr", "balanced_accuracy"]


def exact_p(x: np.ndarray) -> float:
    x = x[x != 0]
    if len(x) == 0:
        return 1.0
    try:
        return float(wilcoxon(x, alternative="two-sided", method="exact").pvalue)
    except Exception:
        return float(wilcoxon(x, alternative="two-sided").pvalue)


def boot_ci(x: np.ndarray, n: int = 10000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def holm(pvals: list[float]) -> list[float]:
    order = np.argsort(pvals)
    m = len(pvals)
    adj = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * pvals[idx])
        running = max(running, val)
        adj[idx] = running
    return adj


def summarize(df: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        for model in MODELS:
            sub = df[(df.metric == metric) & (df.model == model)]
            for name, (a, b) in CONTRASTS.items():
                x = (sub[a] - sub[b]).to_numpy(dtype=float)
                if len(x) == 0:
                    continue
                lo, hi = boot_ci(x)
                rows.append({
                    "subset": label, "metric": metric, "model": model, "contrast": name,
                    "n_datasets": len(x), "mean_delta": x.mean(), "median_delta": float(np.median(x)),
                    "sd_delta": float(x.std(ddof=1)) if len(x) > 1 else np.nan,
                    "wins": int((x > 0).sum()), "losses": int((x < 0).sum()), "ties": int((x == 0).sum()),
                    "p_wilcoxon_exact": exact_p(x), "cliffs_delta": ((x > 0).sum() - (x < 0).sum()) / len(x),
                    "ci95_lo": lo, "ci95_hi": hi,
                })
    out = pd.DataFrame(rows)
    # Holm across the four models within each metric x contrast (the paper's family)
    out["p_holm_models"] = np.nan
    for (metric, contrast), idx in out.groupby(["metric", "contrast"]).groups.items():
        out.loc[idx, "p_holm_models"] = holm(out.loc[idx, "p_wilcoxon_exact"].tolist())
    return out


def to_md(summ: pd.DataFrame, title: str) -> str:
    lines = [f"# {title}", ""]
    for label in summ.subset.unique():
        lines += [f"## {label}", ""]
        for metric in METRICS:
            lines += [f"### {metric}", "", "| Model | contrast | N | mean Δ | median Δ | W/L/T | p (exact) | p Holm | Cliff | 95% CI |", "|---|---|---|---|---|---|---|---|---|---|"]
            s = summ[(summ.subset == label) & (summ.metric == metric)]
            for _, r in s.iterrows():
                lines.append(f"| {r.model} | {r.contrast} | {r.n_datasets} | {r.mean_delta:+.4f} | {r.median_delta:+.4f} | {r.wins}/{r.losses}/{r.ties} | {r.p_wilcoxon_exact:.2g} | {r.p_holm_models:.2g} | {r.cliffs_delta:+.2f} | [{r.ci95_lo:+.4f}, {r.ci95_hi:+.4f}] |")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core-run-level", nargs="+", required=True)
    ap.add_argument("--expansion-run-level", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--exclude-datasets", default="", help="comma-separated dataset names to drop")
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    core = pd.concat([pd.read_csv(f) for f in args.core_run_level], ignore_index=True)
    core["tier"] = "core"
    exp = pd.concat([pd.read_csv(f) for f in args.expansion_run_level], ignore_index=True)
    exp["tier"] = "expansion"
    df = pd.concat([core, exp], ignore_index=True)
    assert "generator" in df.columns, "run-level files need a generator column"
    excl = {d for d in args.exclude_datasets.split(",") if d}
    df = df[~df.dataset.isin(excl)]
    dg = df.groupby(["dataset", "tier", "generator", "model", "metric"], as_index=False)[TREATMENTS].mean()
    for name, (a, b) in CONTRASTS.items():
        dg[name] = dg[a] - dg[b]
    dg.to_csv(out / "dataset_generator_level.csv", index=False)

    cov = dg.groupby(["dataset", "tier"]).generator.nunique().reset_index().rename(columns={"generator": "n_generators"})
    cov.to_csv(out / "coverage.csv", index=False)
    dl = dg.groupby(["dataset", "tier", "model", "metric"], as_index=False)[TREATMENTS].mean()
    dl = dl.merge(cov[["dataset", "n_generators"]], on="dataset")
    for name, (a, b) in CONTRASTS.items():
        dl[name] = dl[a] - dl[b]
    dl.to_csv(out / "dataset_level.csv", index=False)

    n_all = dl.dataset.nunique()
    n_core = dl[dl.tier == "core"].dataset.nunique()
    n_exp = dl[dl.tier == "expansion"].dataset.nunique()
    pooled = pd.concat([
        summarize(dl, f"all datasets, generator-averaged (N={n_all}: {n_core} core + {n_exp} expansion)"),
        summarize(dl[dl.tier == "expansion"], f"expansion only, generator-averaged (N={n_exp})"),
        summarize(dl[dl.tier == "core"], f"core only, linear/SVM schemas, generator-averaged (N={n_core})"),
    ], ignore_index=True)
    pooled.to_csv(out / "summary_pooled.csv", index=False)
    (out / "summary_pooled.md").write_text(to_md(pooled, "Restructured benchmark: pooled over generators"))

    by_gen = pd.concat([
        summarize(dg[dg.generator == g], f"{g} (N={dg[dg.generator == g].dataset.nunique()})") for g in sorted(dg.generator.unique())
    ], ignore_index=True)
    by_gen.to_csv(out / "summary_by_generator.csv", index=False)
    (out / "summary_by_generator.md").write_text(to_md(by_gen, "Restructured benchmark: by generator"))

    common = cov[cov.n_generators == dg.generator.nunique()].dataset
    cm = summarize(dl[dl.dataset.isin(common)], f"datasets covered by all {dg.generator.nunique()} generators (N={len(common)})")
    cm.to_csv(out / "summary_common.csv", index=False)
    (out / "summary_common.md").write_text(to_md(cm, "Restructured benchmark: common-coverage datasets"))
    print((out / "summary_pooled.md").read_text())
    print("coverage:\n", cov.n_generators.value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
