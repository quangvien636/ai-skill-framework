"""The reusable loader pipeline: Repository loading -> Schema validation ->
IR conversion -> Diagnostics, with each stage in its own module
(loader.py, schema_registry.py, the per-kind *_ir.py adapters,
diagnostics.py). No stage holds global state; every function takes the
paths/registries it needs as arguments.

Pipeline order per docs/architecture/IR_ARCHITECTURE.md and
docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md: for YAML sources
(Skill, Workflow) and embedded-object fixtures (Evaluation, Reflection),
the parsed document already matches the IR shape, so schema validation acts
as the normalization gate before typed IR construction. For Knowledge
Markdown, normalization must happen before schema validation, because the
schema validates the normalized object, not raw Markdown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .diagnostics import Diagnostic, has_errors
from .evaluation_ir import EvaluationIR, build_evaluation_ir
from .knowledge_ir import build_knowledge_ir
from .loader import load_json, load_markdown, load_yaml
from .reflection_ir import ReflectionIR, build_reflection_ir
from .schema_registry import SchemaRegistry
from .skill_ir import SkillIR, build_skill_ir
from .tool_ir import ToolIR, build_tool_ir
from .workflow_ir import WorkflowIR, build_workflow_ir

SUPPORTED_KINDS = ("skill", "workflow", "knowledge", "evaluation", "reflection", "tool")

_SCHEMA_BY_KIND = {
    "skill": "skill.schema.json",
    "workflow": "workflow.schema.json",
    "knowledge": "knowledge.schema.json",
    "evaluation": "evaluation.schema.json",
    "reflection": "reflection.schema.json",
    "tool": "tool.schema.json",
}


@dataclass
class AdapterResult:
    kind: str
    artifact: str
    ir: Optional[Any] = None
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.ir is not None and not has_errors(self.diagnostics)


def build_ir(kind: str, path: Path, schema_registry: SchemaRegistry) -> AdapterResult:
    if kind not in _SCHEMA_BY_KIND:
        raise ValueError(f"unsupported artifact kind: {kind!r} (supported: {SUPPORTED_KINDS})")

    artifact = str(path)
    schema_name = _SCHEMA_BY_KIND[kind]

    if kind == "knowledge":
        return _build_knowledge(path, artifact, schema_registry, schema_name)
    if kind in ("skill", "workflow", "tool"):
        return _build_yaml_artifact(kind, path, artifact, schema_registry, schema_name)
    return _build_json_artifact(kind, path, artifact, schema_registry, schema_name)


def _build_yaml_artifact(
    kind: str, path: Path, artifact: str, schema_registry: SchemaRegistry, schema_name: str
) -> AdapterResult:
    result = AdapterResult(kind=kind, artifact=artifact)

    loaded = load_yaml(path)
    if not loaded.ok:
        result.diagnostics.extend(loaded.diagnostics)
        return result

    schema_diagnostics = schema_registry.validate(schema_name, loaded.document, artifact)
    result.diagnostics.extend(schema_diagnostics)
    if has_errors(schema_diagnostics):
        return result

    if kind == "skill":
        ir, adapter_diagnostics = build_skill_ir(loaded.document, artifact)
    elif kind == "tool":
        ir, adapter_diagnostics = build_tool_ir(loaded.document, artifact)
    else:
        ir, adapter_diagnostics = build_workflow_ir(loaded.document, artifact)
    result.diagnostics.extend(adapter_diagnostics)
    result.ir = ir
    return result


def _build_json_artifact(
    kind: str, path: Path, artifact: str, schema_registry: SchemaRegistry, schema_name: str
) -> AdapterResult:
    result = AdapterResult(kind=kind, artifact=artifact)

    loaded = load_json(path)
    if not loaded.ok:
        result.diagnostics.extend(loaded.diagnostics)
        return result

    schema_diagnostics = schema_registry.validate(schema_name, loaded.document, artifact)
    result.diagnostics.extend(schema_diagnostics)
    if has_errors(schema_diagnostics):
        return result

    if kind == "evaluation":
        result.ir = build_evaluation_ir(loaded.document)
    else:
        result.ir = build_reflection_ir(loaded.document)
    return result


def _build_knowledge(
    path: Path, artifact: str, schema_registry: SchemaRegistry, schema_name: str
) -> AdapterResult:
    result = AdapterResult(kind="knowledge", artifact=artifact)

    loaded = load_markdown(path)
    if not loaded.ok:
        result.diagnostics.extend(loaded.diagnostics)
        return result

    ir, parse_diagnostics = build_knowledge_ir(loaded.text, artifact)
    result.diagnostics.extend(parse_diagnostics)
    if ir is None:
        return result

    schema_diagnostics = schema_registry.validate(schema_name, ir.as_normalized_dict(), artifact)
    result.diagnostics.extend(schema_diagnostics)
    if has_errors(schema_diagnostics):
        return result

    result.ir = ir
    return result
