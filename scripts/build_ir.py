#!/usr/bin/env python3
"""Offline IR-adapter conformance checker (Validator Roadmap Phase 2).

Loads each fixture declared in tests/fixtures/ir/cases.json, runs it through
scripts/asf_validator's loader -> schema validation -> IR adapter pipeline,
and confirms the result (valid IR, or specific diagnostic code) matches what
the case expects. This mirrors scripts/validate_contracts.py's shape but
checks IR construction, not only schema conformance.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from asf_validator.pipeline import build_ir  # noqa: E402
from asf_validator.schema_registry import build_schema_registry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "ir" / "cases.json"
SCHEMA_ROOT = REPO_ROOT / "schemas"


def run(cases_path: Path) -> int:
    schema_registry = build_schema_registry(SCHEMA_ROOT)
    manifest = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = manifest.get("cases", [])
    if not cases:
        print("ERROR: no IR fixture cases declared.", file=sys.stderr)
        return 2

    unexpected = 0
    for case in cases:
        fixture = REPO_ROOT / case["fixture"]
        kind = case["kind"]
        expected = case["expected"]
        expected_code = case.get("expected_code")

        result = build_ir(kind, fixture, schema_registry)
        actual = "valid" if result.ok else "invalid"

        problem = None
        if actual != expected:
            problem = f"expected {expected}, got {actual}"
        elif expected_code and not any(d.code == expected_code for d in result.diagnostics):
            found = sorted({d.code for d in result.diagnostics}) or ["<none>"]
            problem = f"expected diagnostic {expected_code}, got {found}"

        if problem is None:
            print(f"PASS {case['name']}: {actual}")
            if result.diagnostics:
                print(f"  {result.diagnostics[0].code}: {result.diagnostics[0].message}")
        else:
            print(f"FAIL {case['name']}: {problem}")
            for diagnostic in result.diagnostics[:5]:
                print(f"  {diagnostic.code}: {diagnostic.message}")
            unexpected += 1

    print(f"RESULT: {len(cases) - unexpected}/{len(cases)} cases matched expectations.")
    return 1 if unexpected else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IR-adapter fixtures against expectations.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="Path to the IR fixture case manifest.")
    args = parser.parse_args()
    return run(args.cases.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
