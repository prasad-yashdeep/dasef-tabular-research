#!/usr/bin/env bash
set -euo pipefail

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERROR: .env is tracked by git. Remove with: git rm --cached .env" >&2
  exit 1
fi

echo "Secret hygiene check passed: .env is not tracked."
