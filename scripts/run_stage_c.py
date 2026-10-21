"""Stage C: Generate summary files for GPT/Gemini formula-only sweep."""
import json
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results" / "model_sweeps"
SUMMARY_DIR = ROOT / "results" / "sweep_summaries"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = ["blood_transfusion", "pima_diabetes", "credit_g", "qsar_biodegradation"]
FAMILIES = ["tree", "linear_svm", "distance_knn"]
MODELS = ["gemini-3-pro"]  # GPT-5.5-pro excluded due to API timeout
DOWNSTREAM = ["xgboost", "random_forest", "logistic_regression", "knn"]

rows = []

for dataset in DATASETS:
    for family in FAMILIES:
        for model in MODELS:
            eval_file = RESULTS_DIR / f"{dataset}_{family}_{model}_formula_eval.json"
            if not eval_file.exists():
                rows.append({
                    "dataset": dataset, "family": family, "schema_model": model,
                    "downstream_model": "N/A", "status": "MISSING",
                    "raw_roc_auc": None, "formula_roc_auc": None, "delta_roc_auc": None,
                    "raw_bal_acc": None, "formula_bal_acc": None, "delta_bal_acc": None,
                    "schema_path": None
                })
                continue
            
            with open(eval_file) as f:
                data = json.load(f)
            
            schema_path = data["artifacts"]["schema"]
            # Make path relative
            if str(ROOT) in schema_path:
                schema_path = schema_path.replace(str(ROOT) + "/", "")
            
            raw_eval = None
            formula_eval = None
            for ev in data["evaluations"]:
                if ev["matrix_name"] == "raw":
                    raw_eval = ev
                elif ev["matrix_name"] in ("formula", "raw_plus_formula"):
                    formula_eval = ev
            
            if not raw_eval or not formula_eval:
                rows.append({
                    "dataset": dataset, "family": family, "schema_model": model,
                    "downstream_model": "N/A", "status": "INCOMPLETE_EVAL",
                    "raw_roc_auc": None, "formula_roc_auc": None, "delta_roc_auc": None,
                    "raw_bal_acc": None, "formula_bal_acc": None, "delta_bal_acc": None,
                    "schema_path": schema_path
                })
                continue
            
            for dm in DOWNSTREAM:
                raw_m = raw_eval["models"].get(dm, {})
                form_m = formula_eval["models"].get(dm, {})
                
                raw_roc = raw_m.get("roc_auc_ovr")
                form_roc = form_m.get("roc_auc_ovr")
                raw_bal = raw_m.get("balanced_accuracy")
                form_bal = form_m.get("balanced_accuracy")
                
                delta_roc = (form_roc - raw_roc) if (raw_roc is not None and form_roc is not None) else None
                delta_bal = (form_bal - raw_bal) if (raw_bal is not None and form_bal is not None) else None
                
                rows.append({
                    "dataset": dataset, "family": family, "schema_model": model,
                    "downstream_model": dm, "status": "OK",
                    "raw_roc_auc": raw_roc, "formula_roc_auc": form_roc, "delta_roc_auc": delta_roc,
                    "raw_bal_acc": raw_bal, "formula_bal_acc": form_bal, "delta_bal_acc": delta_bal,
                    "schema_path": schema_path
                })

# Sort by delta_roc_auc descending
rows_sorted = sorted(rows, key=lambda r: r.get("delta_roc_auc") or -999, reverse=True)

# Write CSV
csv_path = SUMMARY_DIR / "gpt_gemini_formula_summary.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "dataset", "family", "schema_model", "downstream_model", "status",
        "raw_roc_auc", "formula_roc_auc", "delta_roc_auc",
        "raw_bal_acc", "formula_bal_acc", "delta_bal_acc", "schema_path"
    ])
    writer.writeheader()
    writer.writerows(rows_sorted)

# Write Markdown
md_path = SUMMARY_DIR / "gpt_gemini_formula_summary.md"
with open(md_path, "w") as f:
    f.write("# GPT / Gemini Formula-Only Sweep Summary\n\n")
    f.write(f"**Date**: 2026-05-10\n")
    f.write(f"**Models tested**: gemini-3-pro (gemini-3-pro-preview)\n")
    f.write(f"**GPT-5.5-pro**: EXCLUDED — API consistently times out (>180s per request, 502 Bad Gateway)\n")
    f.write(f"**Datasets**: {', '.join(DATASETS)}\n")
    f.write(f"**Families**: {', '.join(FAMILIES)}\n")
    f.write(f"**Downstream models**: {', '.join(DOWNSTREAM)}\n")
    f.write(f"**CV**: 5-fold × 2 repeats\n\n")
    
    f.write("## Top Gains by Δ ROC-AUC\n\n")
    f.write("| Dataset | Family | Schema Model | Downstream | Raw ROC-AUC | Formula ROC-AUC | Δ ROC-AUC | Δ Bal.Acc |\n")
    f.write("|---------|--------|-------------|------------|-------------|-----------------|-----------|----------|\n")
    top_roc = [r for r in rows_sorted if r["delta_roc_auc"] is not None][:20]
    for r in top_roc:
        f.write(f"| {r['dataset']} | {r['family']} | {r['schema_model']} | {r['downstream_model']} | "
                f"{r['raw_roc_auc']:.4f} | {r['formula_roc_auc']:.4f} | "
                f"{r['delta_roc_auc']:+.4f} | {r['delta_bal_acc']:+.4f} |\n")
    
    f.write("\n## Top Gains by Δ Balanced Accuracy\n\n")
    rows_by_bal = sorted([r for r in rows if r.get("delta_bal_acc") is not None], key=lambda r: r["delta_bal_acc"], reverse=True)
    f.write("| Dataset | Family | Schema Model | Downstream | Raw Bal.Acc | Formula Bal.Acc | Δ Bal.Acc | Δ ROC-AUC |\n")
    f.write("|---------|--------|-------------|------------|-------------|-----------------|-----------|----------|\n")
    for r in rows_by_bal[:20]:
        f.write(f"| {r['dataset']} | {r['family']} | {r['schema_model']} | {r['downstream_model']} | "
                f"{r['raw_bal_acc']:.4f} | {r['formula_bal_acc']:.4f} | "
                f"{r['delta_bal_acc']:+.4f} | {r['delta_roc_auc']:+.4f} |\n")
    
    f.write("\n## Summary Statistics\n\n")
    valid = [r for r in rows if r["delta_roc_auc"] is not None]
    positive_roc = [r for r in valid if r["delta_roc_auc"] > 0]
    positive_bal = [r for r in valid if r["delta_bal_acc"] > 0]
    f.write(f"- Total evaluations: {len(valid)}\n")
    f.write(f"- Positive Δ ROC-AUC: {len(positive_roc)}/{len(valid)} ({100*len(positive_roc)/len(valid):.0f}%)\n")
    f.write(f"- Positive Δ Bal.Acc: {len(positive_bal)}/{len(valid)} ({100*len(positive_bal)/len(valid):.0f}%)\n")
    if valid:
        avg_roc = sum(r["delta_roc_auc"] for r in valid) / len(valid)
        avg_bal = sum(r["delta_bal_acc"] for r in valid) / len(valid)
        max_roc = max(r["delta_roc_auc"] for r in valid)
        max_bal = max(r["delta_bal_acc"] for r in valid)
        f.write(f"- Mean Δ ROC-AUC: {avg_roc:+.4f}\n")
        f.write(f"- Max Δ ROC-AUC: {max_roc:+.4f}\n")
        f.write(f"- Mean Δ Bal.Acc: {avg_bal:+.4f}\n")
        f.write(f"- Max Δ Bal.Acc: {max_bal:+.4f}\n")
    
    f.write("\n## Per-Dataset Breakdown\n\n")
    for dataset in DATASETS:
        ds_rows = [r for r in valid if r["dataset"] == dataset]
        if ds_rows:
            avg_d = sum(r["delta_roc_auc"] for r in ds_rows) / len(ds_rows)
            best = max(ds_rows, key=lambda r: r["delta_roc_auc"])
            f.write(f"### {dataset}\n")
            f.write(f"- Mean Δ ROC-AUC: {avg_d:+.4f}\n")
            f.write(f"- Best: {best['family']}/{best['downstream_model']} Δ={best['delta_roc_auc']:+.4f}\n\n")

print(f"Written: {csv_path}")
print(f"Written: {md_path}")
print(f"Total rows: {len(rows)}, valid: {len([r for r in rows if r['delta_roc_auc'] is not None])}")
