"""Adds scripts/ and adapters/ to sys.path for Ollama adapter tests."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
ADAPTERS_DIR = REPO_ROOT / "adapters"
for path in (SCRIPTS_DIR, ADAPTERS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

SCHEMA_ROOT = REPO_ROOT / "schemas"
