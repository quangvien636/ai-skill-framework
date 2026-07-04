#!/usr/bin/env python3
"""Offline Dependency Graph / Version Graph conformance checker
(Validator Roadmap Phase 3).

Loads each multi-artifact scenario declared in tests/fixtures/graph/cases.json,
runs every listed fixture through scripts/asf_validator's IR pipeline
(Sprint 16, unchanged), builds the Dependency Graph and Version Graph from
the resulting IR objects (Sprint 17), and confirms the set of diagnostic
codes produced matches what the case expects.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from asf_validator.dependency_graph import build_dependency_graph  # noqa: E402
from asf_validator.pipeline import build_ir  # noqa: E402
from asf_validator.schema_registry import build_schema_registry  # noqa: E402
from asf_validator.version_graph import build_version_graph  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "graph" / "cases.json"
SCHEMA_ROOT = REPO_ROOT / "schemas"


def run(cases_path: Path) -> int:
    schema_registry = build_schema_registry(SCHEMA_ROOT)
    manifest = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = manifest.get("cases", [])
    if not cases:
        print("ERROR: no graph fixture cases declared.", file=sys.stderr)
        return 2

    unexpected = 0
    for case in cases:
        results = [
            build_ir(entry["kind"], REPO_ROOT / entry["fixture"], schema_registry)
            for entry in case["artifacts"]
        ]

        dependency_graph, dependency_diagnostics = build_dependency_graph(results)
        _version_graph, version_diagnostics = build_version_graph(dependency_graph)
        all_diagnostics = dependency_diagnostics + version_diagnostics

        actual_codes = sorted({d.code for d in all_diagnostics})
        expected_codes = sorted(case.get("expected_codes", []))

        if actual_codes == expected_codes:
            print(f"PASS {case['name']}: codes {actual_codes or '[]'}")
        else:
            print(f"FAIL {case['name']}: expected codes {expected_codes}, got {actual_codes}")
            for diagnostic in all_diagnostics[:10]:
                print(f"  {diagnostic.code}: {diagnostic.message}")
            unexpected += 1

    print(f"RESULT: {len(cases) - unexpected}/{len(cases)} cases matched expectations.")
    return 1 if unexpected else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Dependency/Version Graph fixtures against expectations.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="Path to the graph fixture case manifest.")
    args = parser.parse_args()
    return run(args.cases.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
