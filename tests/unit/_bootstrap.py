"""Adds scripts/ to sys.path so tests can `import asf_validator` without a
package install step. Imported first by every test_*.py in this directory.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "ir"
SCHEMA_ROOT = REPO_ROOT / "schemas"
