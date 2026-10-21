"""Stage A: Generate schemas for GPT-5.5-pro and Gemini-3-pro."""
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dasef.datasets import load_dataset, dataset_summary
from dasef.config import LLMModelConfig
from dasef.schema_generation import generate_schema

DATASETS = ["blood_transfusion", "pima_diabetes", "credit_g", "qsar_biodegradation"]
FAMILIES = ["tree", "linear_svm", "distance_knn"]
MODELS = [
    LLMModelConfig(id="gpt-5.5-pro", provider="openai", provider_model="gpt-5.5-pro", env_key="OPENAI_API_KEY", reasoning="max_available"),
    LLMModelConfig(id="gemini-3-pro", provider="gemini", provider_model="gemini-3-pro-preview", env_key="GEMINI_API_KEY", reasoning="max_available"),
]

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "schemas"

results = {"generated": [], "skipped": [], "failed": []}

for dataset_name in DATASETS:
    print(f"\n{'='*60}")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*60}")
    ds = load_dataset(dataset_name)
    ds_summary = dataset_summary(ds)
    
    for family in FAMILIES:
        for model_cfg in MODELS:
            combo = f"{dataset_name}/{family}/{model_cfg.id}"
            schema_dir = CACHE_DIR / dataset_name / family / model_cfg.id
            # Check existing
            existing = list(schema_dir.glob("schema_*.json")) if schema_dir.exists() else []
            existing = [p for p in existing if ".raw." not in p.name]
            if existing:
                print(f"  SKIP {combo} — exists: {existing[0].name}")
                results["skipped"].append(combo)
                continue
            
            success = False
            for attempt in range(1, 4):
                try:
                    print(f"  GEN {combo} (attempt {attempt}/3)...")
                    schema = generate_schema(ds_summary, family, model_cfg, n_features=12)
                    print(f"  ✓ SUCCESS {combo}")
                    results["generated"].append(combo)
                    success = True
                    break
                except Exception as e:
                    print(f"  ✗ FAILED {combo} attempt {attempt}: {type(e).__name__}: {str(e)[:200]}")
                    if attempt == 3:
                        traceback.print_exc()
            
            if not success:
                results["failed"].append(combo)

print(f"\n\n{'='*60}")
print(f"STAGE A COMPLETE")
print(f"Generated: {len(results['generated'])} | Skipped: {len(results['skipped'])} | Failed: {len(results['failed'])}")
print(f"{'='*60}")
if results["failed"]:
    print("FAILURES:")
    for f in results["failed"]:
        print(f"  - {f}")

# Save results log
log_path = Path(__file__).resolve().parent.parent / "results" / "model_sweeps" / "stage_a_log.json"
log_path.parent.mkdir(parents=True, exist_ok=True)
log_path.write_text(json.dumps(results, indent=2))
print(f"\nLog saved to {log_path}")
