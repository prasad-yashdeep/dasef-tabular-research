from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
    re.compile(r"(api[_-]?key\s*[=:]\s*)[^\s,;]+", re.I),
    re.compile(r"(authorization\s*[:=]\s*bearer\s+)[^\s,;]+", re.I),
]


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("<redacted>" if "key" in k.lower() or "secret" in k.lower() else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if not isinstance(value, str):
        return value
    out = value
    for pattern in SECRET_PATTERNS:
        out = pattern.sub(lambda m: (m.group(1) if m.groups() else "") + "<redacted>", out)
    return out


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.msg)
        if record.args:
            record.args = tuple(redact(a) for a in record.args)
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            payload["event"] = redact(getattr(record, "event"))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(log_dir: str | Path = "logs", level: str = "INFO") -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    filt = RedactingFilter()

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    console.addFilter(filt)
    root.addHandler(console)

    Path(log_dir).mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(Path(log_dir) / "dasef.jsonl", encoding="utf-8")
    file_handler.setFormatter(JsonFormatter())
    file_handler.addFilter(filt)
    root.addHandler(file_handler)
