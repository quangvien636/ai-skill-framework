"""Dependency Graph: docs/specifications/IR_SPECIFICATION.md's Dependency
Graph, built from already-produced IR objects (never re-parses source).

Node kinds and which references become edges are fixed by ADR-0010 and
extended by ADR-0014: nodes are Skill/Workflow/Knowledge/Tool/Connector/
Runtime IDs; edges are Skill -> Knowledge, Workflow step -> Skill,
Knowledge -> Knowledge (related_knowledge), Skill -> Tool, Tool -> Connector,
Skill -> Runtime, Runtime -> Knowledge (retriever), Runtime -> Tool, and
Runtime -> Runtime (fallback).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .diagnostics import (
    Diagnostic,
    GRAPH_DUPLICATE_ARTIFACT_ID,
    GRAPH_MISSING_DEPENDENCY,
    GRAPH_REFERENCE_CYCLE,
    Severity,
)
from .graph import detect_cycle
from .knowledge_ir import KnowledgeIR
from .pipeline import AdapterResult
from .runtime_ir import RuntimeIR
from .skill_ir import SkillIR
from .tool_ir import ToolIR
from .connector_ir import ConnectorIR
from .version_ir import VersionIR, VersionRangeIR, parse_version
from .workflow_ir import WorkflowIR


@dataclass(frozen=True)
class DependencyGraphNode:
    id: str
    kind: str  # "skill" | "workflow" | "knowledge" | "tool" | "connector" | "runtime"
    version: Optional[VersionIR]
    status: str
    artifact: str  # source path, for diagnostics


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    kind: str  # "skill-knowledge" | "workflow-skill" | "knowledge-knowledge" | "skill-tool"
    # | "tool-connector" | "skill-runtime" | "runtime-knowledge" | "runtime-tool" | "runtime-runtime"
    required: bool
    version: Optional[VersionRangeIR] = None


@dataclass
class DependencyGraph:
    nodes: dict[str, DependencyGraphNode] = field(default_factory=dict)
    edges: tuple[DependencyEdge, ...] = ()

    def adjacency(self) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = defaultdict(list)
        for edge in self.edges:
            adjacency[edge.source].append(edge.target)
        return adjacency

    def dependents_of(self, target_id: str) -> tuple[str, ...]:
        """IDs that declare an edge to `target_id` -- 'what depends on this ID'."""
        return tuple(edge.source for edge in self.edges if edge.target == target_id)


def _node_info(result: AdapterResult) -> tuple[str, str, Optional[VersionIR], str]:
    ir = result.ir
    if result.kind == "skill":
        assert isinstance(ir, SkillIR)
        return ir.metadata.id, "skill", ir.metadata.version, ir.metadata.status
    if result.kind == "workflow":
        assert isinstance(ir, WorkflowIR)
        return ir.metadata.id, "workflow", ir.metadata.version, ir.metadata.status
    if result.kind == "tool":
        assert isinstance(ir, ToolIR)
        return ir.metadata.id, "tool", ir.metadata.version, ir.metadata.status
    if result.kind == "connector":
        assert isinstance(ir, ConnectorIR)
        return ir.metadata.id, "connector", ir.metadata.version, ir.metadata.status
    if result.kind == "runtime":
        assert isinstance(ir, RuntimeIR)
        return ir.metadata.id, "runtime", ir.metadata.version, ir.metadata.status
    assert result.kind == "knowledge" and isinstance(ir, KnowledgeIR)
    version, _error = parse_version(ir.version)
    return ir.id, "knowledge", version, ir.status


def build_dependency_graph(results: list[AdapterResult]) -> tuple[DependencyGraph, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    nodes: dict[str, DependencyGraphNode] = {}

    for result in results:
        if not result.ok:
            continue  # Sprint 16 already reported this artifact's own diagnostics
        if result.kind not in ("skill", "workflow", "knowledge", "tool", "connector", "runtime"):
            continue  # Evaluation/Reflection are not graph nodes (ADR-0010)

        artifact_id, kind, version, status = _node_info(result)
        if artifact_id in nodes:
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_DUPLICATE_ARTIFACT_ID,
                    severity=Severity.ERROR,
                    artifact=result.artifact,
                    location="id",
                    message=(
                        f"Duplicate artifact id '{artifact_id}': already defined by "
                        f"'{nodes[artifact_id].artifact}'."
                    ),
                )
            )
            continue
        nodes[artifact_id] = DependencyGraphNode(
            id=artifact_id, kind=kind, version=version, status=status, artifact=result.artifact
        )

    edges: list[DependencyEdge] = []
    for result in results:
        if not result.ok:
            continue
        ir = result.ir
        if isinstance(ir, SkillIR):
            for knowledge_ref in ir.dependencies.knowledge:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=knowledge_ref.id,
                        kind="skill-knowledge",
                        required=knowledge_ref.required,
                        version=knowledge_ref.version,
                    )
                )
            for tool_ref in ir.dependencies.tools:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=tool_ref.id,
                        kind="skill-tool",
                        required=tool_ref.required,
                        version=tool_ref.version,
                    )
                )
            for runtime_ref in ir.dependencies.runtime:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=runtime_ref.id,
                        kind="skill-runtime",
                        required=runtime_ref.required,
                        version=runtime_ref.version,
                    )
                )
        elif isinstance(ir, WorkflowIR):
            for step in ir.steps:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=step.skill.id,
                        kind="workflow-skill",
                        required=not step.optional,
                        version=step.skill.version,
                    )
                )
        elif isinstance(ir, KnowledgeIR):
            for related_id in ir.related_knowledge:
                edges.append(
                    DependencyEdge(
                        source=ir.id,
                        target=related_id,
                        kind="knowledge-knowledge",
                        required=False,
                        version=None,
                    )
                )
        elif isinstance(ir, ToolIR):
            for conn_ref in ir.dependencies.connectors:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=conn_ref.id,
                        kind="tool-connector",
                        required=conn_ref.required,
                        version=conn_ref.version,
                    )
                )
        elif isinstance(ir, RuntimeIR):
            for knowledge_ref in ir.retriever.knowledge:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=knowledge_ref.id,
                        kind="runtime-knowledge",
                        required=knowledge_ref.required,
                        version=knowledge_ref.version,
                    )
                )
            for tool_ref in ir.tools.refs:
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=tool_ref.id,
                        kind="runtime-tool",
                        required=tool_ref.required,
                        version=tool_ref.version,
                    )
                )
            if ir.fallback_profile.fallback_runtime is not None:
                fallback_ref = ir.fallback_profile.fallback_runtime
                edges.append(
                    DependencyEdge(
                        source=ir.metadata.id,
                        target=fallback_ref.id,
                        kind="runtime-runtime",
                        required=fallback_ref.required,
                        version=fallback_ref.version,
                    )
                )

    for edge in edges:
        if edge.target not in nodes:
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_MISSING_DEPENDENCY,
                    severity=Severity.ERROR if edge.required else Severity.WARNING,
                    artifact=edge.source,
                    location=f"-> {edge.target}",
                    message=(
                        f"{edge.source} references '{edge.target}' ({edge.kind}), "
                        f"which is not among the loaded artifacts."
                    ),
                    suggestion="Add the missing artifact to the loaded set, or fix the reference.",
                )
            )

    graph = DependencyGraph(nodes=nodes, edges=tuple(edges))
    cycle = detect_cycle(graph.adjacency())
    if cycle is not None:
        diagnostics.append(
            Diagnostic(
                code=GRAPH_REFERENCE_CYCLE,
                severity=Severity.ERROR,
                artifact=cycle[0],
                location="dependency graph",
                message=f"Reference cycle: {' -> '.join(cycle)}.",
            )
        )

    return graph, diagnostics
