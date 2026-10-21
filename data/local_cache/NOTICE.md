# Tables redistributed in this directory

Each subdirectory holds one prepared table (`data.parquet` plus `meta.json`). The six core tables are the locally cached
copies the paper's core tier was evaluated on; the post-cutoff tables are the prepared feature matrices of the paper's
post-cutoff replication. Licences are reported as recorded by the respective sources on 11 October 2026 ("Public" is the
uploader assertion recorded on OpenML that no restrictive licence applies). Derived artifacts (schemas, scores, statistics,
generated columns) are released under CC BY 4.0; the raw columns stay under the terms below, and artifacts derived from the
two non-commercial tables carry the same non-commercial terms (this also applies to the matrices in `matrices_postcutoff.tar.gz`).

| Directory | Source | Licence |
|---|---|---|
| `adult_income` | 45,222-row complete-case variant of OpenML 1590 (adult) | Public (OpenML) |
| `bank_marketing` | 20-feature, 41,188-row UCI bank-additional variant of OpenML 1461 | Public (OpenML) |
| `car_evaluation` | OpenML 40975, version 3 | Public (OpenML) |
| `electricity` | 7-feature variant of OpenML 151 (without the `day` column) | Public (OpenML) |
| `phoneme` | OpenML 1489, version 1 | Public (OpenML) |
| `spambase` | OpenML 44, version 1 | Public (OpenML) |
| `postcutoff_clinical_trials_ai_20260517` | Hugging Face `moncefem/clinical-trials-ai-2000-2025` (ClinicalTrials.gov records) | Apache 2.0 |
| `postcutoff_prediction_markets_20260517` | Hugging Face `ImpliedData/prediction-markets` (no longer publicly accessible since October 2026) | CC BY-NC 4.0 (non-commercial) |
| `postcutoff_ro_real_estate_20260503` | Hugging Face `palerflavius/ro-real-estate-listings` (repository updated continuously; this is the table as fetched in June 2026) | MIT |
| `postcutoff_tracker_radar_20260316` | Hugging Face `olafuraron/tracker-radar-ml` (DuckDuckGo Tracker Radar with EasyPrivacy labels) | CC BY-NC-SA 4.0 (non-commercial, share-alike) |
| `postcutoff_water_quality_nys_20260406` | Hugging Face `food-ai-nexus/fecal-indicator-water-nys` (Zenodo 10.5281/zenodo.18500867) | MIT |
| `postcutoff_salmonella_serovar_20260401` | Hugging Face `food-ai-nexus/salmonella-serovar-hyperspectral-spectra` (Zenodo 10.5281/zenodo.16740800); 74 MB, shipped as a release asset, only `meta.json` is committed | CC BY 4.0 |

Full provenance (repository creation dates, preparation steps, target derivations) is in Appendix B of the paper and in
`results/statistics/benchmark44/dataset_provenance.csv` for the OpenML tables.
