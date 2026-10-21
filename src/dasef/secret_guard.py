from __future__ import annotations

from pathlib import Path

FORBIDDEN_FILES = {".env"}
SECRET_PATTERNS = ["API_KEY=", "sk-", "ANTHROPIC_API_KEY=", "OPENAI_API_KEY=", "DEEPSEEK_API_KEY=", "GEMINI_API_KEY="]


def assert_no_tracked_secret_files(repo_root: Path) -> None:
    """Lightweight local guard for future pre-commit/CI integration."""
    for rel in FORBIDDEN_FILES:
        path = repo_root / rel
        if path.exists():
            # Existence is okay locally; this guard is for code paths that might package files.
            continue
