"""Workflow IR: schemas/workflow.schema.json's object model, plus the built
step graph docs/specifications/IR_SPECIFICATION.md's Workflow IR section
describes as part of the IR itself (resolved step references, acyclic
graph) -- not a Phase 3 semantic rule (ADR-0009).

This adapter resolves references only *within* the one Workflow document
(step ids, entrypoint, input/output mappings). It does not resolve the
Skill each step names against the rest of the repository -- that is the
Dependency Graph, out of scope here (ADR-0009).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from .diagnostics import (
    Diagnostic,
    PARSE_UNRESOLVED_WORKFLOW_REFERENCE,
    PARSE_WORKFLOW_GRAPH_CYCLE,
    Severity,
    has_errors,
)
from .graph import detect_cycle
from .metadata_ir import MetadataIR, extract_metadata_ir
from .reference_ir import ReferenceIR, build_reference_ir
from .skill_ir import FieldIR, build_fields

_STEP_INPUT_MAPPING_RE = re.compile(r"^steps\.(?P<step>[a-z][a-z0-9-]*)\.outputs\.")
_OUTPUT_SOURCE_RE = re.compile(r"^steps\.(?P<step>[a-z][a-z0-9-]*)\.outputs\.")


@dataclass(frozen=True)
class RetryIR:
    max_attempts: int


@dataclass(frozen=True)
class WorkflowStepIR:
    id: str
    skill: ReferenceIR
    depends_on: tuple[str, ...]
    input_mapping: dict[str, str]
    optional: bool
    on_error: str
    retry: Optional[RetryIR] = None


@dataclass(frozen=True)
class WorkflowOutputIR:
    type: str
    source: str
    description: Optional[str] = None


@dataclass(frozen=True)
class WorkflowIR:
    metadata: MetadataIR
    entrypoint: str
    inputs: dict[str, FieldIR]
    steps: tuple[WorkflowStepIR, ...]
    outputs: dict[str, WorkflowOutputIR]
    error_handling: dict[str, Any]
    graph: dict[str, tuple[str, ...]]


def build_workflow_ir(doc: dict[str, Any], artifact: str) -> tuple[Optional[WorkflowIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []

    metadata, metadata_diagnostics = extract_metadata_ir(doc, artifact, id_prefix="workflow")
    diagnostics.extend(metadata_diagnostics)
    if metadata is None or has_errors(metadata_diagnostics):
        return None, diagnostics

    step_docs = doc["steps"]
    step_ids = {step["id"] for step in step_docs}

    steps: list[WorkflowStepIR] = []
    graph: dict[str, tuple[str, ...]] = {}
    for step_doc in step_docs:
        step_id = step_doc["id"]
        depends_on = tuple(step_doc.get("depends_on", []))
        graph[step_id] = depends_on

        for dependency in depends_on:
            if dependency not in step_ids:
                diagnostics.append(
                    Diagnostic(
                        code=PARSE_UNRESOLVED_WORKFLOW_REFERENCE,
                        severity=Severity.ERROR,
                        artifact=artifact,
                        location=f"steps.{step_id}.depends_on",
                        message=f"depends_on references unknown step '{dependency}'.",
                    )
                )

        input_mapping = dict(step_doc.get("input_mapping", {}))
        for input_name, source in input_mapping.items():
            match = _STEP_INPUT_MAPPING_RE.match(source)
            if match and match.group("step") not in step_ids:
                diagnostics.append(
                    Diagnostic(
                        code=PARSE_UNRESOLVED_WORKFLOW_REFERENCE,
                        severity=Severity.ERROR,
                        artifact=artifact,
                        location=f"steps.{step_id}.input_mapping.{input_name}",
                        message=f"input_mapping references unknown step '{match.group('step')}'.",
                    )
                )

        retry_doc = step_doc.get("retry")
        steps.append(
            WorkflowStepIR(
                id=step_id,
                skill=build_reference_ir(step_doc["skill"]),
                depends_on=depends_on,
                input_mapping=input_mapping,
                optional=step_doc.get("optional", False),
                on_error=step_doc["on_error"],
                retry=RetryIR(max_attempts=retry_doc["max_attempts"]) if retry_doc else None,
            )
        )

    entrypoint = doc["entrypoint"]
    if entrypoint not in step_ids:
        diagnostics.append(
            Diagnostic(
                code=PARSE_UNRESOLVED_WORKFLOW_REFERENCE,
                severity=Severity.ERROR,
                artifact=artifact,
                location="entrypoint",
                message=f"entrypoint references unknown step '{entrypoint}'.",
            )
        )

    outputs: dict[str, WorkflowOutputIR] = {}
    for output_name, output_doc in doc["outputs"].items():
        source = output_doc["from"]
        match = _OUTPUT_SOURCE_RE.match(source)
        if match and match.group("step") not in step_ids:
            diagnostics.append(
                Diagnostic(
                    code=PARSE_UNRESOLVED_WORKFLOW_REFERENCE,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"outputs.{output_name}.from",
                    message=f"output references unknown step '{match.group('step')}'.",
                )
            )
        outputs[output_name] = WorkflowOutputIR(
            type=output_doc["type"], source=source, description=output_doc.get("description")
        )

    cycle = detect_cycle(graph)
    if cycle is not None:
        diagnostics.append(
            Diagnostic(
                code=PARSE_WORKFLOW_GRAPH_CYCLE,
                severity=Severity.ERROR,
                artifact=artifact,
                location="steps",
                message=f"depends_on graph contains a cycle: {' -> '.join(cycle)}.",
            )
        )

    if has_errors(diagnostics):
        return None, diagnostics

    workflow = WorkflowIR(
        metadata=metadata,
        entrypoint=entrypoint,
        inputs=build_fields(doc.get("inputs", {})),
        steps=tuple(steps),
        outputs=outputs,
        error_handling=dict(doc["error_handling"]),
        graph=graph,
    )
    return workflow, diagnostics
