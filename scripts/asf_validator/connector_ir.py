"""Connector IR: schemas/connector.schema.json's object model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .diagnostics import Diagnostic, has_errors
from .metadata_ir import MetadataIR, extract_metadata_ir
from .skill_ir import FieldIR, build_fields


@dataclass(frozen=True)
class ConnectorIR:
    metadata: MetadataIR
    responsibility: str
    authentication: str
    configuration: dict[str, FieldIR]


def build_connector_ir(doc: dict[str, Any], artifact: str) -> tuple[Optional[ConnectorIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []

    metadata, metadata_diagnostics = extract_metadata_ir(doc, artifact, id_prefix="connector")
    diagnostics.extend(metadata_diagnostics)
    if metadata is None or has_errors(metadata_diagnostics):
        return None, diagnostics

    connector = ConnectorIR(
        metadata=metadata,
        responsibility=doc["responsibility"],
        authentication=doc["authentication"],
        configuration=build_fields(doc.get("configuration", {})),
    )
    return connector, diagnostics
