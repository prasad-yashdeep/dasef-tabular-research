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
from dasef.prompts import build_direct_risk_prompt

logger = logging.getLogger(__name__)


def parse_direct_risk_response(text: str, *, score_name: str = "direct_risk_score") -> float:
    payload = text[text.find("{") :] if "{" in text else text
    data, _ = json.JSONDecoder().raw_decode(payload)
    value = float(data.get(score_name, np.nan))
    return float(np.clip(value, 0.0, 1.0)) if not np.isnan(value) else np.nan


def fill_direct_risk_scores(
    df: pd.DataFrame,
    dataset_summary: dict,
    *,
    target_class: str,
    filler_model_id: str,
    filler_provider: str,
    score_name: str = "direct_risk_score",
    dry_run: bool = False,
    out_dir: Path | None = None,
) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index, columns=[score_name], dtype=float)
    out_dir = out_dir or Path("cache/direct_risk") / filler_provider / filler_model_id
    out_dir.mkdir(parents=True, exist_ok=True)
    client = None if dry_run else client_for_provider(filler_provider)
    for idx, row in df.iterrows():
        prompt = build_direct_risk_prompt(
            row.to_dict(),
            dataset_summary,
            target_class=target_class,
            score_name=score_name,
        )
        h = stable_hash({"prompt": prompt, "model": filler_model_id, "score_name": score_name})
        cache_path = out_dir / f"row_{idx}_{h}.json"
        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            out.loc[idx, score_name] = data["value"]
            continue
        if dry_run:
            write_json(
                cache_path.with_suffix(".prompt.json"),
                {"prompt": prompt, "model": filler_model_id, "score_name": score_name},
            )
            continue
        last_error: Exception | None = None
        for attempt in range(1, 4):
            response = client.complete(LLMRequest(model=filler_model_id, prompt=prompt, max_output_tokens=512))
            try:
                value = parse_direct_risk_response(response.text, score_name=score_name)
                write_json(
                    cache_path,
                    {
                        "row_index": idx,
                        "value": value,
                        "score_name": score_name,
                        "model": filler_model_id,
                        "provider": filler_provider,
                        "target_class": target_class,
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                    },
                )
                out.loc[idx, score_name] = value
                break
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                last_error = exc
                logger.warning(
                    "Invalid direct-risk JSON row=%s model=%s attempt=%s text_prefix=%r",
                    idx,
                    filler_model_id,
                    attempt,
                    response.text[:200],
                )
                if attempt < 3:
                    time.sleep(2 * attempt)
        else:
            raise RuntimeError(f"Failed to parse direct-risk JSON for row {idx} after 3 attempts") from last_error
    return out
