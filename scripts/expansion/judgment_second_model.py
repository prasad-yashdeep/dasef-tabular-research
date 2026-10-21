#!/usr/bin/env python
"""Second judgment model (DeepSeek-V4-Pro) robustness check for the per-row judgment null.

Aggregates raw+formula+judgment minus raw+formula over the completed DeepSeek-V4-Pro runs under
results/judgments (dataset-level means over the cells each dataset has, exact Wilcoxon over datasets)
and writes results/statistics/judgment_v4pro/{run_level.csv,summary.csv,summary.md} and the LaTeX
table paper/dmlr/tables/judgment_v4pro.tex. Offline; no LLM call.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "expansion"))
from aggregate_benchmark44 import exact_p, holm  # noqa: E402

MODELS = ["logistic_regression", "knn", "random_forest", "xgboost"]
LAB = {"logistic_regression": "Logistic regression", "knn": "KNN", "random_forest": "Random forest", "xgboost": "XGBoost"}
METRICS = {"roc_auc_ovr": "ROC-AUC", "balanced_accuracy": "Bal. accuracy"}


def main() -> None:
    rows = []
    for rd in sorted(glob.glob(str(ROOT / "results/judgments/*"))):
        rd = Path(rd)
        js = glob.glob(str(rd / "judgments" / "*.json"))
        if not js or not (rd / "results.json").exists():
            continue
        model = json.load(open(js[0])).get("model")
        res = json.load(open(rd / "results.json"))
        ev = {e["matrix_name"]: e for e in res["evaluations"]}
        if "raw_plus_formula_plus_judgment" not in ev:
            continue
        for m in MODELS:
            for met in METRICS:
                rows.append({"judgment_model": model, "run_id": rd.name, "dataset": res["dataset"], "schema": res["artifacts"]["schema"], "model": m, "metric": met,
                             "raw_plus_formula": ev["raw_plus_formula"]["models"][m][met],
                             "raw_plus_formula_plus_judgment": ev["raw_plus_formula_plus_judgment"]["models"][m][met]})
    rl = pd.DataFrame(rows)
    rl["judgment_delta"] = rl.raw_plus_formula_plus_judgment - rl.raw_plus_formula
    out = ROOT / "results/statistics/judgment_v4pro"; out.mkdir(parents=True, exist_ok=True)
    rl.to_csv(out / "run_level.csv", index=False)
    summ = []
    for jm in sorted(rl.judgment_model.unique()):
        sub = rl[rl.judgment_model == jm]
        cov = sub.drop_duplicates("run_id").groupby("dataset").size()
        dl = sub.groupby(["dataset", "model", "metric"], as_index=False).judgment_delta.mean()
        for met in METRICS:
            ps = []
            for m in MODELS:
                x = dl[(dl.model == m) & (dl.metric == met)].judgment_delta.to_numpy(dtype=float)
                ps.append({"judgment_model": jm, "metric": met, "model": m, "n_datasets": len(x), "n_runs": int(sub.run_id.nunique()),
                           "mean_delta": x.mean(), "median_delta": float(np.median(x)), "wins": int((x > 0).sum()), "losses": int((x < 0).sum()),
                           "ties": int((x == 0).sum()), "p_wilcoxon_exact": exact_p(x), "cliffs_delta": ((x > 0).sum() - (x < 0).sum()) / len(x)})
            hp = holm([p["p_wilcoxon_exact"] for p in ps])
            for p, h in zip(ps, hp):
                p["p_holm_models"] = h
            summ += ps
        print(jm, "runs", sub.run_id.nunique(), "datasets", cov.to_dict())
    sdf = pd.DataFrame(summ); sdf.to_csv(out / "summary.csv", index=False)
    md = ["# Per-row judgment increment (raw+formula+judgment minus raw+formula), dataset level", ""]
    for _, r in sdf.iterrows():
        md.append(f"{r.judgment_model} {r.metric} {r.model}: N={int(r.n_datasets)} runs={int(r.n_runs)} mean={r.mean_delta:+.4f} W/L/T={int(r.wins)}/{int(r.losses)}/{int(r.ties)} p={r.p_wilcoxon_exact:.3g} pHolm={r.p_holm_models:.3g}")
    (out / "summary.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
    v4 = sdf[sdf.judgment_model == "deepseek-v4-pro"]
    cov = rl[rl.judgment_model == "deepseek-v4-pro"].drop_duplicates("run_id").groupby("dataset").size()
    lines = ["\\begin{table}[htbp]",
             f"\\caption{{Second judgment model: incremental effect of DeepSeek-V4-Pro per-row judgment features beyond deterministic formulas on the ten core datasets ({int(v4.n_runs.iloc[0])} completed schema runs; coverage per dataset {int(cov.min())} to {int(cov.max())} of 12 cells, averaged per dataset before testing). Columns as in Table~\\ref{{tab:judgment}}; $p$ is the exact two-sided Wilcoxon test over datasets.}}\\label{{tab:judgment-v4pro}}",
             "\\centering", "\\small", "\\begin{tabular}{llrrrrr}", "\\toprule", "Metric & Downstream model & \\(N\\) & Mean \\(\\Delta\\) & W/L/T & Cliff's \\(\\delta\\) & \\(p\\) \\\\", "\\midrule"]
    for mi, met in enumerate(METRICS):
        if mi:
            lines.append("\\midrule")
        for m in MODELS:
            r = v4[(v4.metric == met) & (v4.model == m)].iloc[0]
            lines.append(f"{METRICS[met]} & {LAB[m]} & {int(r.n_datasets)} & {r.mean_delta:+.4f} & {int(r.wins)}/{int(r.losses)}/{int(r.ties)} & {r.cliffs_delta:+.2f} & {r.p_wilcoxon_exact:.4f} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    tex = ROOT / "paper/dmlr/tables/judgment_v4pro.tex"; tex.write_text("\n".join(lines) + "\n"); print("wrote", tex)


if __name__ == "__main__":
    main()
