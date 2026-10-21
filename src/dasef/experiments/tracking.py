from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dasef.hash_utils import stable_hash


@dataclass
class RunManifest:
    experiment_name: str
    dataset: str | None = None
    model_family: str | None = None
    schema_model: str | None = None
    judgment_model: str | None = None
    seed: int = 42
    config: dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    git_commit: str | None = None
    python_version: str = field(default_factory=platform.python_version)
    platform: str = field(default_factory=platform.platform)

    def __post_init__(self) -> None:
        if self.git_commit is None:
            self.git_commit = current_git_commit()

    @property
    def run_id(self) -> str:
        return stable_hash(self.__dict__, n=12)


def current_git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def write_manifest(out_dir: str | Path, manifest: RunManifest) -> Path:
    path = Path(out_dir) / manifest.run_id / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump({**manifest.__dict__, "run_id": manifest.run_id}, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def append_event(run_dir: str | Path, event_type: str, payload: dict[str, Any]) -> None:
    path = Path(run_dir) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
