"""Tool IR: schemas/tool.schema.json's object model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .diagnostics import Diagnostic, has_errors
from .metadata_ir import MetadataIR, extract_metadata_ir
from .reference_ir import ReferenceIR, build_reference_ir
from .skill_ir import FieldIR, build_fields


@dataclass(frozen=True)
class ToolConstraintsIR:
    side_effects: str
    timeout_seconds: Optional[int] = None
    max_input_size: Optional[int] = None
    max_output_size: Optional[int] = None
    deterministic: Optional[bool] = None
    requires_network: Optional[bool] = None
    requires_local_filesystem: Optional[bool] = None


@dataclass(frozen=True)
class ToolDependenciesIR:
    connectors: tuple[ReferenceIR, ...]


@dataclass(frozen=True)
class ToolIR:
    metadata: MetadataIR
    responsibility: str
    inputs: dict[str, FieldIR]
    outputs: dict[str, FieldIR]
    dependencies: ToolDependenciesIR
    constraints: ToolConstraintsIR


def build_tool_ir(doc: dict[str, Any], artifact: str) -> tuple[Optional[ToolIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []

    metadata, metadata_diagnostics = extract_metadata_ir(doc, artifact, id_prefix="tool")
    diagnostics.extend(metadata_diagnostics)
    if metadata is None or has_errors(metadata_diagnostics):
        return None, diagnostics

    deps = doc["dependencies"]
    dependencies = ToolDependenciesIR(
        connectors=tuple(build_reference_ir(r) for r in deps.get("connectors", [])),
    )

    constraints_doc = doc["constraints"]
    constraints = ToolConstraintsIR(
        side_effects=constraints_doc["side_effects"],
        timeout_seconds=constraints_doc.get("timeout_seconds"),
        max_input_size=constraints_doc.get("max_input_size"),
        max_output_size=constraints_doc.get("max_output_size"),
        deterministic=constraints_doc.get("deterministic"),
        requires_network=constraints_doc.get("requires_network"),
        requires_local_filesystem=constraints_doc.get("requires_local_filesystem"),
    )

    tool = ToolIR(
        metadata=metadata,
        responsibility=doc["responsibility"],
        inputs=build_fields(doc.get("inputs", {})),
        outputs=build_fields(doc.get("outputs", {})),
        dependencies=dependencies,
        constraints=constraints,
    )
    return tool, diagnostics
