from __future__ import annotations

import json
from typing import Any

from .schema import SchemaSpec, schema_json_instruction


MODEL_FAMILY_GUIDANCE = {
    "tree": "Prioritize thresholds, boolean indicators, ordinal buckets, categorical groupings, and nonlinear interactions that tree models can split on directly.",
    "linear_svm": "Prioritize smooth normalized scores, continuous severity measures, approximate linear projections, ratios, and weighted composites useful for linear/SVM margins.",
    "distance_knn": "Prioritize scale-normalized distances, similarity scores, prototype-distance features, and cluster indicators that improve neighborhood geometry.",
}


def build_schema_prompt(dataset_summary: dict[str, Any], model_family: str, schema_generator: str, n_features: int = 20) -> str:
    guidance = MODEL_FAMILY_GUIDANCE.get(model_family, "Design robust, interpretable tabular features.")
    return f"""You are designing tabular features for downstream model family: {model_family}.

Goal: generate a fixed schema of {n_features} interpretable features containing both deterministic formula features and semantic judgment features. Use only row values and training-set metadata. Avoid target leakage.

Downstream-model guidance:
{guidance}

Dataset summary (training fold only):
{json.dumps(dataset_summary, indent=2, ensure_ascii=False)}

Schema generator id: {schema_generator}

{schema_json_instruction()}

Important constraints:
- Feature names must be stable snake_case keys.
- Formula features must include formulas using existing column names.
- Formula syntax must be vectorized and compatible with pandas Series evaluation.
- Allowed formula operators/functions only: +, -, *, /, **, %, comparisons, vectorized boolean &/| with parentheses, np.where, where, np.logical_and, logical_and, np.logical_or, logical_or, np.minimum, minimum, np.maximum, maximum, np.clip, clip, np.log1p, log1p, np.sqrt, sqrt, np.abs, abs.
- Do NOT use Python ternary expressions like `1 if condition else 0`; use `np.where(condition, 1, 0)`.
- Do NOT use Python builtins `max` or `min`; use `np.maximum` / `np.minimum`.
- Do NOT use target labels, class labels, target-derived thresholds, supervised class prototypes, positive/negative class names, learned model outputs, global test statistics, or future information.
- Do not include the words `target`, `label`, `class1`, `class2`, `positive class`, `negative class`, `majority class`, or `minority class` anywhere in feature names, descriptions, formulas, or expected benefits.
- For KNN/distance schemas, prototypes must be unsupervised or generic row-value references only; never create `class1`, `class2`, positive-class, negative-class, majority-class, or minority-class prototype features.
- Every value_range must be strictly increasing: lower_bound < upper_bound. Never return equal bounds like [250, 250].
- Avoid constant formula features. If a domain constant matters, express a deviation feature such as `np.abs(V3 / V2 - 250.0)` with a non-degenerate range.
- Judgment features must include explicit numeric value ranges.
- Include leakage_risk for every feature.
- Prefer formulas where possible; reserve judgment features for non-formulaic semantic assessments.
- Return JSON only, no markdown.
"""


def build_judgment_prompt(row: dict[str, Any], schema: SchemaSpec) -> str:
    judgment_features = [f.model_dump(mode="json") for f in schema.judgment_features]
    return f"""You are filling values for a fixed tabular feature schema.

Rules:
- Do not invent new features.
- Use only the row values and the feature definitions.
- Respect each feature's numeric value_range.
- Output valid JSON only with exactly the requested feature names.
- Never use or infer the true target label.

Row:
{json.dumps(row, indent=2, ensure_ascii=False, default=str)}

Judgment feature schema:
{json.dumps(judgment_features, indent=2, ensure_ascii=False)}

Return JSON only.
"""


def build_judgment_prompt_batch(rows: list[dict[str, Any]], schema: SchemaSpec) -> str:
    """Build a batched judgment prompt for multiple rows at once."""
    judgment_features = [f.model_dump(mode="json") for f in schema.judgment_features]
    feature_names = [f.name for f in schema.judgment_features]
    rows_block = json.dumps(rows, indent=None, ensure_ascii=False, default=str)
    return f"""You are filling values for a fixed tabular feature schema for MULTIPLE rows.

Rules:
- Do not invent new features.
- Use only each row's values and the feature definitions.
- Respect each feature's numeric value_range.
- Never use or infer the true target label.
- Output a JSON ARRAY with one object per row, in the same order as input.
- Each object must have exactly these keys: {json.dumps(feature_names)}

Judgment feature schema:
{json.dumps(judgment_features, indent=2, ensure_ascii=False)}

Rows ({len(rows)} total):
{rows_block}

Return a JSON array of {len(rows)} objects. No markdown, no explanation.
"""


def build_direct_risk_prompt(
    row: dict[str, Any],
    dataset_summary: dict[str, Any],
    *,
    target_class: str,
    score_name: str = "direct_risk_score",
) -> str:
    return f"""You are creating a direct risk-score baseline for a tabular classification task.

Rules:
- Use only the row values and the dataset context below.
- Do not invent features.
- Return a calibrated score from 0.0 to 1.0 estimating how likely this row is to belong to target class `{target_class}`.
- Output valid JSON only with exactly one key: `{score_name}`.
- This is a baseline for comparison against interpretable DASEF features, not a final model explanation.

Dataset context:
{json.dumps(dataset_summary, indent=2, ensure_ascii=False)}

Row:
{json.dumps(row, indent=2, ensure_ascii=False, default=str)}

Return JSON only.
"""
