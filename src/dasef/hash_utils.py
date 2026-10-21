from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def stable_hash(obj: Any, n: int = 16) -> str:
    return hashlib.sha256(stable_json(obj).encode("utf-8")).hexdigest()[:n]
