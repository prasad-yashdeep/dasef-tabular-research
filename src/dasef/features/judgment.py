from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

from dasef.hash_utils import stable_hash
from dasef.io_utils import write_json
from dasef.llm.base import LLMRequest
from dasef.llm.providers import client_for_provider
from dasef.prompts import build_judgment_prompt, build_judgment_prompt_batch
from dasef.schema import SchemaSpec

logger = logging.getLogger(__name__)


def parse_judgment_response(text: str, schema: SchemaSpec) -> dict[str, float]:
    payload = text[text.find("{") :] if "{" in text else text
    data, _ = json.JSONDecoder().raw_decode(payload)
    out: dict[str, float] = {}
    for feature in schema.judgment_features:
        value = data.get(feature.name, np.nan)
        try:
            value_f = float(value)
        except Exception:
            value_f = np.nan
        lo, hi = feature.value_range
        out[feature.name] = float(np.clip(value_f, lo, hi)) if not np.isnan(value_f) else np.nan
    return out


def parse_judgment_response_batch(text: str, schema: SchemaSpec, expected_count: int) -> list[dict[str, float]]:
    """Parse a batched judgment response containing a JSON array of row results."""
    # Find the array start
    arr_start = text.find("[")
    if arr_start < 0:
        raise ValueError("No JSON array found in response")
    payload = text[arr_start:]
    # Try to parse the full array
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")
    if len(data) != expected_count:
        raise ValueError(f"Expected {expected_count} results, got {len(data)}")
    results: list[dict[str, float]] = []
    for item in data:
        out: dict[str, float] = {}
        for feature in schema.judgment_features:
            value = item.get(feature.name, np.nan)
            try:
                value_f = float(value)
            except Exception:
                value_f = np.nan
            lo, hi = feature.value_range
            out[feature.name] = float(np.clip(value_f, lo, hi)) if not np.isnan(value_f) else np.nan
        results.append(out)
    return results


def fill_judgment_features(
    df: pd.DataFrame,
    schema: SchemaSpec,
    filler_model_id: str,
    filler_provider: str,
    batch_size: int = 25,
    dry_run: bool = False,
    out_dir: Path | None = None,
) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index, columns=[f.name for f in schema.judgment_features], dtype=float)
    out_dir = out_dir or Path("cache/judgments") / schema.dataset_name / schema.model_family / filler_model_id
    out_dir.mkdir(parents=True, exist_ok=True)
    client = None if dry_run else client_for_provider(filler_provider)

    # Identify rows needing filling (not cached)
    pending_indices = []
    for idx, row in df.iterrows():
        prompt = build_judgment_prompt(row.to_dict(), schema)
        h = stable_hash({"prompt": prompt, "model": filler_model_id})
        cache_path = out_dir / f"row_{idx}_{h}.json"
        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            out.loc[idx, list(data["values"].keys())] = list(data["values"].values())
        else:
            pending_indices.append(idx)

    if not pending_indices:
        return out

    logger.info("Judgment fill: %d cached, %d pending (batch_size=%d)", len(df) - len(pending_indices), len(pending_indices), batch_size)

    if batch_size <= 1:
        # Legacy single-row path
        return _fill_single_row(df, schema, filler_model_id, filler_provider, client, out, out_dir, pending_indices, dry_run)

    # Batched path
    batches = [pending_indices[i:i + batch_size] for i in range(0, len(pending_indices), batch_size)]
    for batch_num, batch_idx in enumerate(batches, 1):
        rows_data = [df.loc[idx].to_dict() for idx in batch_idx]

        if dry_run:
            prompt = build_judgment_prompt_batch(rows_data, schema)
            write_json(out_dir / f"batch_{batch_num}.prompt.json", {"prompt": prompt, "model": filler_model_id, "row_count": len(batch_idx)})
            continue

        prompt = build_judgment_prompt_batch(rows_data, schema)
        last_error: Exception | None = None
        for attempt in range(1, 4):
            # Use higher max_output for batched responses
            max_tokens = min(4096 * len(batch_idx), 65536)
            response = client.complete(LLMRequest(model=filler_model_id, prompt=prompt, max_output_tokens=max_tokens))
            try:
                batch_results = parse_judgment_response_batch(response.text, schema, len(batch_idx))
                # Cache each row individually
                for row_idx, values in zip(batch_idx, batch_results):
                    row_prompt = build_judgment_prompt(df.loc[row_idx].to_dict(), schema)
                    h = stable_hash({"prompt": row_prompt, "model": filler_model_id})
                    cache_path = out_dir / f"row_{row_idx}_{h}.json"
                    write_json(cache_path, {"row_index": row_idx, "values": values, "model": filler_model_id, "provider": filler_provider, "input_tokens": response.input_tokens // len(batch_idx), "output_tokens": response.output_tokens // len(batch_idx), "batch_size": len(batch_idx)})
                    out.loc[row_idx, list(values.keys())] = list(values.values())
                break
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                logger.warning(
                    "Invalid batched judgment JSON batch=%d/%d model=%s attempt=%d error=%s",
                    batch_num, len(batches), filler_model_id, attempt, str(exc)[:150],
                )
                if attempt < 3:
                    time.sleep(2 * attempt)
        else:
            # Fallback: try single-row for this batch
            logger.warning("Batch %d failed after 3 attempts, falling back to single-row for %d rows", batch_num, len(batch_idx))
            _fill_single_row(df, schema, filler_model_id, filler_provider, client, out, out_dir, batch_idx, dry_run)

        if batch_num % 10 == 0:
            filled = len(df) - len(pending_indices) + batch_num * batch_size
            logger.info("Progress: %d/%d rows filled (batch %d/%d)", min(filled, len(df)), len(df), batch_num, len(batches))

    return out


def _fill_single_row(
    df: pd.DataFrame,
    schema: SchemaSpec,
    filler_model_id: str,
    filler_provider: str,
    client,
    out: pd.DataFrame,
    out_dir: Path,
    indices: list,
    dry_run: bool,
) -> pd.DataFrame:
    """Fill judgment features one row at a time (fallback path)."""
    for idx in indices:
        row = df.loc[idx]
        prompt = build_judgment_prompt(row.to_dict(), schema)
        h = stable_hash({"prompt": prompt, "model": filler_model_id})
        cache_path = out_dir / f"row_{idx}_{h}.json"
        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            out.loc[idx, list(data["values"].keys())] = list(data["values"].values())
            continue
        if dry_run:
            write_json(cache_path.with_suffix(".prompt.json"), {"prompt": prompt, "model": filler_model_id})
            continue
        last_error: Exception | None = None
        for attempt in range(1, 4):
            response = client.complete(LLMRequest(model=filler_model_id, prompt=prompt, max_output_tokens=2048))
            try:
                values = parse_judgment_response(response.text, schema)
                write_json(cache_path, {"row_index": idx, "values": values, "model": filler_model_id, "provider": filler_provider, "input_tokens": response.input_tokens, "output_tokens": response.output_tokens})
                out.loc[idx, list(values.keys())] = list(values.values())
                break
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                logger.warning(
                    "Invalid judgment JSON row=%s model=%s attempt=%s text_prefix=%r",
                    idx, filler_model_id, attempt, response.text[:200],
                )
                if attempt < 3:
                    time.sleep(2 * attempt)
        else:
            raise RuntimeError(f"Failed to parse judgment JSON for row {idx} after 3 attempts") from last_error
    return out
