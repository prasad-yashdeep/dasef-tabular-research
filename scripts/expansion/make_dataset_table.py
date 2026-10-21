"""LaTeX table of the benchmark datasets (core + expansion) from the inventory and coverage.

Usage: python make_dataset_table.py --inventory results/statistics/benchmark44/dataset_inventory.csv \
          --coverage <agg>/coverage.csv --core-ids configs/datasets.yaml --out paper/tables/datasets.tex
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

CORE = ["adult_income", "bank_marketing", "blood_transfusion", "car_evaluation", "credit_g",
        "electricity", "phoneme", "pima_diabetes", "qsar_biodegradation", "spambase"]


# Licence strings exactly as recorded on OpenML, shortened for the table; "Public" is OpenML's label for
# datasets whose uploader declared no restrictive licence. Entries that name an institution or a
# repository rather than a licence are printed as "see source" (the source URL is in dataset_provenance.csv).
LOCAL_VARIANTS = {"adult_income", "bank_marketing", "electricity"}  # local variants of the listed OpenML table (Section 4.1)

LICENCE_LABELS = {
    "Public": "Public", "public": "Public", "CC BY 4.0": "CC BY 4.0",
    "Attribution 4.0 International (CC BY 4.0)": "CC BY 4.0", "CC0": "CC0", "BSD": "BSD",
    "See source": "see source", "Nanyang Technological University": "see source",
    "Online News Popularity Data Set and UCI": "see source",
}


def tex(s: str) -> str:
    return s.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--coverage", required=True)
    ap.add_argument("--datasets-yaml", default="configs/datasets.yaml")
    ap.add_argument("--core-inventory", default=None, help="CSV with dataset,n_rows,n_features,n_classes,n_categorical for the core datasets (the expansion inventory does not cover them)")
    ap.add_argument("--provenance", default=None, help="CSV from fetch_openml_provenance.py; adds OpenML version and licence columns")
    ap.add_argument("--style", choices=["longtable", "table"], default="longtable", help="longtable (TMLR) or a [H] table with adjustbox (DMLR)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    prov = pd.read_csv(args.provenance).set_index("dataset") if args.provenance else None
    inv = pd.read_csv(args.inventory).drop_duplicates("dataset").set_index("dataset")
    if args.core_inventory:
        core_inv = pd.read_csv(args.core_inventory).set_index("dataset")
        inv = pd.concat([inv, core_inv[~core_inv.index.isin(inv.index)]])
    cov = pd.read_csv(args.coverage).set_index("dataset")
    cfg = {d["name"]: d for d in yaml.safe_load(open(args.datasets_yaml))["datasets"]}
    rows = []
    for name in cov.index:
        tier = cov.loc[name, "tier"]
        n_gen = int(cov.loc[name, "n_generators"])
        oid = cfg.get(name, {}).get("openml_id", inv.loc[name, "openml_id"] if name in inv.index else "")
        if name in inv.index:
            r = inv.loc[name]
            n_rows, n_feat, n_cls, n_cat = int(r.n_rows), int(r.n_features), int(r.n_classes), int(r.n_categorical)
        else:
            n_rows = n_feat = n_cls = n_cat = None
        ver = lic = ""
        if prov is not None and name in prov.index:
            ver = int(prov.loc[name, "version"])
            lic = LICENCE_LABELS.get(str(prov.loc[name, "licence"]).strip(), str(prov.loc[name, "licence"]).strip())
        rows.append((tier, name, oid, ver, lic, n_rows, n_feat, n_cls, n_cat, n_gen))
    df = pd.DataFrame(rows, columns=["tier", "dataset", "openml_id", "version", "licence", "rows", "features", "classes", "categorical", "generators"])
    df["tier_order"] = (df.tier != "core").astype(int)
    df = df.sort_values(["tier_order", "dataset"])
    with_prov = prov is not None
    header = ("Tier & Dataset & OpenML id & Ver. & Licence & Rows & Features & Classes & Cat. & Gen. \\\\" if with_prov
              else "Tier & Dataset & OpenML id & Rows & Features & Classes & Cat. & Gen. \\\\")
    colspec = "llrrlrrrrr" if with_prov else "llrrrrrc"
    caption = ("Benchmark datasets. ``OpenML id'' and ``Ver.'' are the OpenML dataset identifier and version that were loaded (each identifier"
               " denotes one fixed version); ``Licence'' is the licence recorded on OpenML (``Public'' is an uploader assertion recorded by OpenML that no"
               " restrictive licence applies, not a formal licence; ``see source'' marks entries that name a source rather than a licence;"
               " the OpenML source description of each is in the released provenance file). Rows and features are the full table as loaded before the"
               " 5{,}000-row cap ($^{\\dagger}$: local variant of the listed OpenML table, whose own listing has a different size; Section~\\ref{sec:datasets});"
               " ``Cat.'' is the number of categorical columns; ``Gen.'' is the number of schema generators with a cached linear/SVM schema"
               " for the dataset (core datasets also have tree and distance schemas from all four generators). Six core datasets (adult"
               " income, bank marketing, car evaluation, electricity, phoneme, spambase) are loaded from a local cache; for three of them"
               " (adult income, bank marketing, car evaluation) it stores the categorical columns as integer codes, which are restored to"
               " categorical columns before downstream modelling (Section~\\ref{sec:protocol}); three are local variants of the listed"
               " OpenML table (Section~\\ref{sec:datasets})." if with_prov else
               "Benchmark datasets. Rows and features are the full OpenML table before the 5{,}000-row cap; ``cat.'' is the number of categorical columns; ``gen.'' is the number of schema generators with a cached linear/SVM schema for the dataset (core datasets also have tree and distance schemas from all four generators). Six core datasets (adult income, bank marketing, car evaluation, electricity, phoneme, spambase) are loaded from a local cache; for three of them (adult income, bank marketing, car evaluation) it stores the categorical columns as integer codes, which are restored to categorical columns before downstream modelling.")
    if args.style == "longtable":
        lines = ["\\begin{longtable}{" + colspec + "}", "\\caption{" + caption + "}\\label{tab:datasets}\\\\",
                 "\\toprule", header, "\\midrule", "\\endfirsthead",
                 "\\toprule", header, "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    else:
        lines = ["\\begin{table}[htbp]", "\\caption{" + caption + "}\\label{tab:datasets}", "\\centering", "\\scriptsize",
                 "\\begin{adjustbox}{max width=\\linewidth}", "\\begin{tabular}{" + colspec + "}", "\\toprule", header, "\\midrule"]
    fmt = lambda v: "" if v is None or v == "" or pd.isna(v) else f"{int(v):,}".replace(",", "{,}")
    last_tier = None
    for _, r in df.iterrows():
        if args.style == "table" and last_tier is not None and r.tier != last_tier:
            lines.append("\\midrule")
        last_tier = r.tier
        oid = "" if r.openml_id == "" or pd.isna(r.openml_id) else str(int(r.openml_id))  # identifiers carry no thousands separator
        name = tex(r.dataset) + ("$^{\\dagger}$" if with_prov and r.dataset in LOCAL_VARIANTS else "")
        cells = ["core" if r.tier == "core" else "expansion", name, oid]
        if with_prov:
            cells += [fmt(r.version), tex(str(r.licence))]
        cells += [fmt(r.rows), fmt(r.features), fmt(r.classes), fmt(r.categorical), str(r.generators)]
        lines.append(" & ".join(cells) + " \\\\")
    if args.style == "longtable":
        lines.append("\\end{longtable}")
    else:
        lines += ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\end{table}"]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n")
    print(df.to_string()); print("wrote", args.out, "rows:", len(df))


if __name__ == "__main__":
    main()
