"""Metadata IR: the commonArtifact fields shared by Skill IR and Workflow IR.

Not a standalone file adapter -- there is no metadata.yaml (ADR-0009).
extract_metadata_ir() is called by the Skill and Workflow adapters after
schema validation has already confirmed the fields are present and
well-typed; it adds the two checks schema validation cannot express:
supported schema_version major, and id/name self-consistency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .diagnostics import (
    Diagnostic,
    PARSE_METADATA_ID_NAME_MISMATCH,
    PARSE_UNSUPPORTED_SCHEMA_VERSION,
    Severity,
    has_errors,
)
from .version_ir import VersionIR, parse_version

# The only schema_version major this adapter generation understands.
# A future major bump requires a new adapter version, per the Version
# Specification's "unknown major versions fail" rule.
SUPPORTED_SCHEMA_MAJORS = frozenset({1})


@dataclass(frozen=True)
class MetadataIR:
    schema_version: VersionIR
    id: str
    name: str
    display_name: str
    description: str
    version: VersionIR
    status: str
    owners: tuple[str, ...]
    tags: tuple[str, ...]


def extract_metadata_ir(
    doc: dict[str, Any], artifact: str, id_prefix: str
) -> tuple[Optional[MetadataIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []

    schema_version, schema_version_error = parse_version(doc["schema_version"])
    if schema_version is None:  # pragma: no cover - schema already validates format
        diagnostics.append(
            Diagnostic(
                code=PARSE_UNSUPPORTED_SCHEMA_VERSION,
                severity=Severity.ERROR,
                artifact=artifact,
                location="schema_version",
                message=schema_version_error or "invalid schema_version",
            )
        )
    elif schema_version.major not in SUPPORTED_SCHEMA_MAJORS:
        diagnostics.append(
            Diagnostic(
                code=PARSE_UNSUPPORTED_SCHEMA_VERSION,
                severity=Severity.ERROR,
                artifact=artifact,
                location="schema_version",
                message=(
                    f"schema_version major {schema_version.major} is not supported "
                    f"by this adapter (supported: {sorted(SUPPORTED_SCHEMA_MAJORS)})."
                ),
                suggestion="Pin schema_version to a supported major, or update the adapter.",
            )
        )

    artifact_id = doc["id"]
    name = doc["name"]
    expected_id = f"{id_prefix}:{name}"
    if artifact_id != expected_id:
        diagnostics.append(
            Diagnostic(
                code=PARSE_METADATA_ID_NAME_MISMATCH,
                severity=Severity.ERROR,
                artifact=artifact,
                location="id",
                message=f"id '{artifact_id}' does not match expected '{expected_id}' derived from name '{name}'.",
                suggestion=f"Set id to '{expected_id}' or rename to match id.",
            )
        )

    version, version_error = parse_version(doc["version"])
    if version is None:  # pragma: no cover - schema already validates format
        diagnostics.append(
            Diagnostic(
                code=PARSE_UNSUPPORTED_SCHEMA_VERSION,
                severity=Severity.ERROR,
                artifact=artifact,
                location="version",
                message=version_error or "invalid version",
            )
        )

    if schema_version is None or version is None or has_errors(diagnostics):
        return None, diagnostics

    metadata = MetadataIR(
        schema_version=schema_version,
        id=artifact_id,
        name=name,
        display_name=doc["display_name"],
        description=doc["description"],
        version=version,
        status=doc["status"],
        owners=tuple(doc["owners"]),
        tags=tuple(doc.get("tags", [])),
    )
    return metadata, diagnostics
