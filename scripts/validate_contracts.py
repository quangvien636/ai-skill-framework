#!/usr/bin/env python3
"""Minimal, offline contract-fixture validator for AI Skill Framework."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError as exc:
    print(
        "ERROR: validator dependencies are missing. "
        "Install requirements-validator.txt.",
        file=sys.stderr,
    )
    print(f"DETAIL: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "contracts" / "cases.json"
SCHEMA_ROOT = REPO_ROOT / "schemas"


def load_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"unsupported fixture format: {suffix}")


def build_registry() -> tuple[dict[str, Any], Registry]:
    schemas: dict[str, Any] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for path in sorted(SCHEMA_ROOT.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        schemas[path.name] = schema
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return schemas, Registry().with_resources(resources)


def format_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"{location}: {error.message}"


def run(cases_path: Path) -> int:
    schemas, registry = build_registry()
    manifest = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = manifest.get("cases", [])
    if not cases:
        print("ERROR: no fixture cases declared.", file=sys.stderr)
        return 2

    unexpected = 0
    for case in cases:
        fixture = REPO_ROOT / case["fixture"]
        schema_name = case["schema"]
        expected = case["expected"]
        if schema_name not in schemas:
            print(f"FAIL {case['name']}: unknown schema {schema_name}")
            unexpected += 1
            continue

        try:
            instance = load_document(fixture)
            validator = Draft202012Validator(
                schemas[schema_name],
                registry=registry,
            )
            errors = sorted(validator.iter_errors(instance), key=str)
        except Exception as exc:  # diagnostics are part of the prototype contract
            print(f"FAIL {case['name']}: could not validate: {exc}")
            unexpected += 1
            continue

        actual = "invalid" if errors else "valid"
        if actual == expected:
            print(f"PASS {case['name']}: expected {expected}, got {actual}")
            if errors:
                print(f"  expected diagnostic: {format_error(errors[0])}")
        else:
            print(f"FAIL {case['name']}: expected {expected}, got {actual}")
            for error in errors[:5]:
                print(f"  {format_error(error)}")
            unexpected += 1

    print(
        f"RESULT: {len(cases) - unexpected}/{len(cases)} cases matched expectations."
    )
    return 1 if unexpected else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate declared contract fixtures against local schemas."
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="Path to the fixture case manifest.",
    )
    args = parser.parse_args()
    return run(args.cases.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
