from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .config import LLMModelConfig
from .features.formula import UnsafeFormula, validate_formula
from .hash_utils import stable_hash
from .io_utils import write_json, write_model
from .llm.base import LLMRequest
from .llm.providers import client_for_provider
from .paths import CACHE_DIR
from .prompts import build_schema_prompt
from .schema import SchemaSpec

logger = logging.getLogger(__name__)

# Only flag truly dangerous leakage — direct target references in feature NAMES.
# Description/benefit text can mention "outcome" without leaking the actual label.
DISALLOWED_NAME_TERMS = (
    "target",
    "label",
    "class1",
    "class2",
    "positive_class",
    "negative_class",
    "true_class",
    "is_positive",
    "is_negative",
)
# Stronger terms that indicate leakage even in descriptions/formulas
DISALLOWED_FORMULA_TERMS = (
    "y_true",
    "y_pred",
    "ground_truth",
    "actual_label",
)


def validate_schema_no_obvious_leakage(schema: SchemaSpec) -> None:
    errors: list[str] = []
    for feature in schema.features:
        # Check feature name for direct target references
        name_lower = feature.name.lower()
        name_hits = [term for term in DISALLOWED_NAME_TERMS if term in name_lower]
        if name_hits:
            errors.append(f"{feature.name}: possible leakage terms in name {name_hits}")
            continue
        # Check formula/computation for dangerous references
        formula_blob = " ".join(
            str(part or "")
            for part in (feature.formula, feature.computation_method)
        ).lower()
        formula_hits = [term for term in DISALLOWED_FORMULA_TERMS if term in formula_blob]
        if formula_hits:
            errors.append(f"{feature.name}: possible leakage terms in formula {formula_hits}")
    if errors:
        raise ValueError("Schema contains obvious target-leakage language:\n" + "\n".join(errors))


def validate_schema_formulas(schema: SchemaSpec, dataset_summary: dict[str, Any]) -> None:
    allowed_names = {col["name"] for col in dataset_summary.get("columns", []) if "name" in col}
    errors: list[str] = []
    for feature in schema.formula_features:
        if not feature.formula:
            errors.append(f"{feature.name}: missing formula")
            continue
        try:
            validate_formula(feature.formula, allowed_names)
        except UnsafeFormula as exc:
            errors.append(f"{feature.name}: {exc}")
    if errors:
        raise ValueError("Schema contains invalid formulas:\n" + "\n".join(errors))


def parse_schema_response(text: str, dataset_name: str, model_family: str, schema_generator: str, prompt_hash: str) -> SchemaSpec:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(text[start : end + 1])
        else:
            raise exc
    data.setdefault("dataset_name", dataset_name)
    data.setdefault("model_family", model_family)
    data.setdefault("schema_generator", schema_generator)
    data.setdefault("schema_version", "v1")
    data["prompt_hash"] = prompt_hash
    # Auto-clean: strip formula from judgment features (LLMs often mistakenly include them)
    for feat in data.get("features", []):
        if feat.get("type") == "judgment" and feat.get("formula"):
            logger.warning(f"Stripping formula from judgment feature: {feat.get('name')}")
            del feat["formula"]
    return SchemaSpec.model_validate(data)


def generate_schema(
    dataset_summary: dict[str, Any],
    model_family: str,
    model_config: LLMModelConfig,
    n_features: int = 20,
    dry_run: bool = False,
    out_dir: Path = CACHE_DIR / "schemas",
) -> SchemaSpec | Path:
    dataset_name = dataset_summary["name"]
    prompt = build_schema_prompt(dataset_summary, model_family, model_config.id, n_features=n_features)
    prompt_hash = stable_hash({"prompt": prompt, "model": model_config.id})
    out_path = out_dir / dataset_name / model_family / model_config.id / f"schema_{prompt_hash}.json"
    if dry_run:
        write_json(out_path.with_suffix(".prompt.json"), {"prompt_hash": prompt_hash, "prompt": prompt, "model": model_config.model_dump()})
        logger.info("Dry-run schema prompt written to %s", out_path.with_suffix(".prompt.json"))
        return out_path.with_suffix(".prompt.json")
    client = client_for_provider(model_config.provider)
    provider_model = model_config.provider_model or model_config.id
    # GPT-5.5 needs higher token budget since reasoning tokens count toward output
    token_budget = 16384 if provider_model.startswith("gpt-5") else 8192
    response = client.complete(LLMRequest(model=provider_model, prompt=prompt, max_output_tokens=token_budget, reasoning=model_config.reasoning))
    raw_path = out_path.with_suffix(".raw.json")
    write_json(raw_path, {"text": response.text, "provider": response.provider, "model": response.model, "input_tokens": response.input_tokens, "output_tokens": response.output_tokens, "prompt_hash": prompt_hash})
    try:
        schema = parse_schema_response(response.text, dataset_name, model_family, model_config.id, prompt_hash)
        validate_schema_formulas(schema, dataset_summary)
        validate_schema_no_obvious_leakage(schema)
    except (json.JSONDecodeError, ValidationError, ValueError):
        logger.exception("Schema validation failed dataset=%s family=%s model=%s", dataset_name, model_family, model_config.id)
        raise
    write_model(out_path, schema)
    logger.info("Schema written to %s", out_path)
    return schema
