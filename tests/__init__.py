"""Allow bare ``python -m unittest discover`` to load the unit-test suite."""

from pathlib import Path
import sys


def load_tests(loader, standard_tests, pattern):
    unit_root = Path(__file__).resolve().parent / "unit"
    sys.path.insert(0, str(unit_root))
    discovered = loader.discover(str(unit_root), pattern=pattern or "test*.py")
    standard_tests.addTests(discovered)
    return standard_tests
