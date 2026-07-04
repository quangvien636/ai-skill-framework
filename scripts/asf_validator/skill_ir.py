"""Skill IR: schemas/skill.schema.json's object model.

build_skill_ir() assumes structural (JSON Schema) validation already
passed; it re-derives nothing schema validation already guarantees except
the two extra checks extract_metadata_ir() adds (ADR-0009).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .diagnostics import Diagnostic, has_errors
from .evaluation_ir import EvaluationIR, build_evaluation_ir
from .metadata_ir import MetadataIR, extract_metadata_ir
from .reference_ir import KnowledgeReferenceIR, ReferenceIR, build_knowledge_reference_ir, build_reference_ir
from .reflection_ir import ReflectionIR, build_reflection_ir


@dataclass(frozen=True)
class FieldIR:
    type: str
    required: bool
    description: str
    constraints: dict[str, Any]
    default: Any = None
    sensitive: bool = False
    additional_properties: bool = False


@dataclass(frozen=True)
class ProcedureStepIR:
    id: str
    action: str
    condition: Optional[str] = None


@dataclass(frozen=True)
class SkillConstraintsIR:
    side_effects: str
    prohibited: tuple[str, ...]
    timeout_seconds: Optional[int] = None
    max_input_size: Optional[int] = None
    max_output_size: Optional[int] = None
    deterministic: Optional[bool] = None


@dataclass(frozen=True)
class SkillDependenciesIR:
    runtime: tuple[ReferenceIR, ...]
    tools: tuple[ReferenceIR, ...]
    knowledge: tuple[KnowledgeReferenceIR, ...]


@dataclass(frozen=True)
class SkillIR:
    metadata: MetadataIR
    responsibility: str
    inputs: dict[str, FieldIR]
    outputs: dict[str, FieldIR]
    dependencies: SkillDependenciesIR
    procedure: tuple[ProcedureStepIR, ...]
    constraints: SkillConstraintsIR
    evaluation: EvaluationIR
    reflection: ReflectionIR


def build_field_ir(doc: dict[str, Any]) -> FieldIR:
    return FieldIR(
        type=doc["type"],
        required=doc["required"],
        description=doc["description"],
        constraints=dict(doc.get("constraints", {})),
        default=doc.get("default"),
        sensitive=doc.get("sensitive", False),
        additional_properties=doc.get("additional_properties", False),
    )


def build_fields(doc: dict[str, Any]) -> dict[str, FieldIR]:
    return {name: build_field_ir(field) for name, field in doc.items()}


def build_skill_ir(doc: dict[str, Any], artifact: str) -> tuple[Optional[SkillIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []

    metadata, metadata_diagnostics = extract_metadata_ir(doc, artifact, id_prefix="skill")
    diagnostics.extend(metadata_diagnostics)
    if metadata is None or has_errors(metadata_diagnostics):
        return None, diagnostics

    deps = doc["dependencies"]
    dependencies = SkillDependenciesIR(
        runtime=tuple(build_reference_ir(r) for r in deps.get("runtime", [])),
        tools=tuple(build_reference_ir(r) for r in deps.get("tools", [])),
        knowledge=tuple(build_knowledge_reference_ir(r) for r in deps.get("knowledge", [])),
    )

    procedure = tuple(
        ProcedureStepIR(id=step["id"], action=step["action"], condition=step.get("condition"))
        for step in doc.get("procedure", [])
    )

    constraints_doc = doc["constraints"]
    constraints = SkillConstraintsIR(
        side_effects=constraints_doc["side_effects"],
        prohibited=tuple(constraints_doc.get("prohibited", [])),
        timeout_seconds=constraints_doc.get("timeout_seconds"),
        max_input_size=constraints_doc.get("max_input_size"),
        max_output_size=constraints_doc.get("max_output_size"),
        deterministic=constraints_doc.get("deterministic"),
    )

    skill = SkillIR(
        metadata=metadata,
        responsibility=doc["responsibility"],
        inputs=build_fields(doc.get("inputs", {})),
        outputs=build_fields(doc.get("outputs", {})),
        dependencies=dependencies,
        procedure=procedure,
        constraints=constraints,
        evaluation=build_evaluation_ir(doc["evaluation"]),
        reflection=build_reflection_ir(doc["reflection"]),
    )
    return skill, diagnostics
