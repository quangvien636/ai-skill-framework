"""Adds adapters/ to sys.path for this package's own tests."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ADAPTERS_DIR = REPO_ROOT / "adapters"
if str(ADAPTERS_DIR) not in sys.path:
    sys.path.insert(0, str(ADAPTERS_DIR))
