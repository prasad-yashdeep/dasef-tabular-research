from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

# Load only this repository's .env file. Do not depend on global shell secrets.
load_dotenv(ENV_PATH, override=False)


def get_project_secret(name: str) -> str | None:
    """Read a project-local secret from this repo's .env only.

    Keep API keys scoped to this project. Callers must never print returned values.
    """
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value


def require_project_secret(name: str) -> str:
    value = get_project_secret(name)
    if not value:
        raise RuntimeError(f"Missing required project-local secret: {name}. Add it to {ENV_PATH}")
    return value
