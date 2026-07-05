#!/usr/bin/env python3
"""Offline semantic-validator conformance checker (Roadmap Phase 3)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from asf_validator.pipeline import build_ir  # noqa: E402
from asf_validator.schema_registry import build_schema_registry  # noqa: E402
from asf_validator.semantic_validator import validate_semantics  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "semantic" / "cases.json"
SCHEMA_ROOT = REPO_ROOT / "schemas"


def run(cases_path: Path) -> int:
    schema_registry = build_schema_registry(SCHEMA_ROOT)
    cases = json.loads(cases_path.read_text(encoding="utf-8")).get("cases", [])
    if not cases:
        print("ERROR: no semantic fixture cases declared.", file=sys.stderr)
        return 2

    unexpected = 0
    for case in cases:
        results = [
            build_ir(entry["kind"], REPO_ROOT / entry["fixture"], schema_registry)
            for entry in case["artifacts"]
        ]
        ir_diagnostics = [d for result in results for d in result.diagnostics]
        diagnostics = ir_diagnostics + validate_semantics(results)
        actual_codes = sorted({diagnostic.code for diagnostic in diagnostics})
        expected_codes = sorted(case.get("expected_codes", []))

        if actual_codes == expected_codes:
            print(f"PASS {case['name']}: codes {actual_codes or '[]'}")
        else:
            print(
                f"FAIL {case['name']}: expected codes {expected_codes}, "
                f"got {actual_codes}"
            )
            for diagnostic in diagnostics[:10]:
                print(f"  {diagnostic.code}: {diagnostic.message}")
            unexpected += 1

    print(f"RESULT: {len(cases) - unexpected}/{len(cases)} cases matched expectations.")
    return 1 if unexpected else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate semantic fixtures against expected diagnostics."
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="Path to the semantic case manifest.",
    )
    return run(parser.parse_args().cases.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
