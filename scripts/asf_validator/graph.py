"""Generic directed-graph utility shared by the Workflow IR's within-document
step graph (Sprint 16) and the Dependency/Version Graphs (Sprint 17), so
cycle detection exists in exactly one place instead of being reimplemented
per graph kind.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional, TypeVar

Node = TypeVar("Node")


def detect_cycle(adjacency: Mapping[Node, Iterable[Node]]) -> Optional[list[Node]]:
    """Return one cycle (list of nodes, first repeated as the last element)
    if `adjacency` (node -> its outgoing edges) contains one, else None.

    Nodes referenced only as edge targets (not present as a key) are treated
    as leaves with no further outgoing edges -- callers that need to flag an
    edge to an unknown node do so separately (a missing-dependency check is
    not the same failure as a cycle).
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[Node, int] = {node: WHITE for node in adjacency}
    path: list[Node] = []

    def visit(node: Node) -> Optional[list[Node]]:
        color[node] = GRAY
        path.append(node)
        for neighbor in adjacency.get(node, ()):
            if color.get(neighbor) == GRAY:
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]
            if neighbor in adjacency and color.get(neighbor) == WHITE:
                result = visit(neighbor)
                if result is not None:
                    return result
        path.pop()
        color[node] = BLACK
        return None

    for node in adjacency:
        if color[node] == WHITE:
            cycle = visit(node)
            if cycle is not None:
                return cycle
    return None
