"""Version Graph: docs/specifications/IR_SPECIFICATION.md's Version Graph,
built from a DependencyGraph's nodes and edges (never re-derives references
from IR objects -- that is the Dependency Graph's job, per ADR-0010's "one
IR, many consumers" principle already established in ADR-0005).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .dependency_graph import DependencyGraph
from .diagnostics import (
    Diagnostic,
    GRAPH_AMBIGUOUS_VERSION_REFERENCE,
    GRAPH_DEPRECATED_DEPENDENCY,
    GRAPH_SELF_CONTRADICTORY_RANGE,
    GRAPH_VERSION_UNSATISFIABLE,
    Severity,
)
from .version_ir import range_is_self_contradictory, version_satisfies_range

_DEPRECATED_WARN_STATUSES = frozenset({"deprecated"})


@dataclass
class VersionGraph:
    dependency_graph: DependencyGraph

    def known_version(self, artifact_id: str):
        node = self.dependency_graph.nodes.get(artifact_id)
        return node.version if node else None


def build_version_graph(dependency_graph: DependencyGraph) -> tuple[VersionGraph, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    version_edges = [edge for edge in dependency_graph.edges if edge.version is not None]

    for edge in version_edges:
        if range_is_self_contradictory(edge.version):
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_SELF_CONTRADICTORY_RANGE,
                    severity=Severity.ERROR,
                    artifact=edge.source,
                    location=f"-> {edge.target}",
                    message=f"Version range '{edge.version.raw}' can never be satisfied by any version.",
                )
            )
            continue  # a self-contradictory range can't meaningfully be checked further

        target_node = dependency_graph.nodes.get(edge.target)
        if target_node is None or target_node.version is None:
            continue  # unresolved target already reported by the Dependency Graph

        if not version_satisfies_range(target_node.version, edge.version):
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_VERSION_UNSATISFIABLE,
                    severity=Severity.ERROR,
                    artifact=edge.source,
                    location=f"-> {edge.target}",
                    message=(
                        f"'{edge.source}' requires '{edge.target}' {edge.version.raw}, "
                        f"but the loaded version is {target_node.version.raw}."
                    ),
                )
            )
        elif target_node.status == "archived":
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_DEPRECATED_DEPENDENCY,
                    severity=Severity.ERROR if edge.required else Severity.WARNING,
                    artifact=edge.source,
                    location=f"-> {edge.target}",
                    message=f"'{edge.source}' depends on '{edge.target}', which is archived.",
                )
            )
        elif target_node.status in _DEPRECATED_WARN_STATUSES:
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_DEPRECATED_DEPENDENCY,
                    severity=Severity.WARNING,
                    artifact=edge.source,
                    location=f"-> {edge.target}",
                    message=f"'{edge.source}' depends on '{edge.target}', whose status is '{target_node.status}'.",
                )
            )

    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for edge in version_edges:
        grouped[(edge.source, edge.target)].add(edge.version.raw)
    for (source, target), raw_ranges in grouped.items():
        if len(raw_ranges) > 1:
            diagnostics.append(
                Diagnostic(
                    code=GRAPH_AMBIGUOUS_VERSION_REFERENCE,
                    severity=Severity.ERROR,
                    artifact=source,
                    location=f"-> {target}",
                    message=(
                        f"'{source}' declares conflicting version constraints for '{target}': "
                        f"{sorted(raw_ranges)}."
                    ),
                )
            )

    return VersionGraph(dependency_graph=dependency_graph), diagnostics
