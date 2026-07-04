"""Structural (JSON Schema) validation, factored out of scripts/validate_contracts.py
so it is reusable by the IR pipeline without duplicating schema-loading logic.

Building a SchemaRegistry takes an explicit schema_root; nothing is read
from a hardcoded path or module-level global.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .diagnostics import Diagnostic, Severity


@dataclass(frozen=True)
class SchemaRegistry:
    schemas: dict[str, Any]
    registry: Registry

    def validator_for(self, schema_name: str) -> Draft202012Validator:
        return Draft202012Validator(self.schemas[schema_name], registry=self.registry)

    def validate(self, schema_name: str, instance: Any, artifact: str) -> list[Diagnostic]:
        validator = self.validator_for(schema_name)
        diagnostics: list[Diagnostic] = []
        for error in sorted(validator.iter_errors(instance), key=str):
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            diagnostics.append(
                Diagnostic(
                    code="ASF-SCHEMA-001",
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=location,
                    message=error.message,
                    rule_reference=schema_name,
                )
            )
        return diagnostics


def build_schema_registry(schema_root: Path) -> SchemaRegistry:
    schemas: dict[str, Any] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for path in sorted(schema_root.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        schemas[path.name] = schema
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return SchemaRegistry(schemas=schemas, registry=Registry().with_resources(resources))
