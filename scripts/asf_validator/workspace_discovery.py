"""Workspace-root discovery defined by ADR-0007."""

from __future__ import annotations

from pathlib import Path

WORKSPACE_MARKERS = ("PROJECT_CONTEXT.md", "PROJECT_TRACKER.md")
DEFAULT_MAX_PARENTS = 64


class WorkspaceNotFoundError(RuntimeError):
    """Raised when the framework root cannot be found from a start path."""


def discover_workspace_root(
    start: Path, max_parents: int = DEFAULT_MAX_PARENTS
) -> Path:
    """Return the nearest ancestor containing both framework marker files."""
    if max_parents < 0:
        raise ValueError("max_parents must be non-negative")

    original = start.resolve()
    current = original if original.is_dir() else original.parent
    for _ in range(max_parents + 1):
        if all((current / marker).is_file() for marker in WORKSPACE_MARKERS):
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    raise WorkspaceNotFoundError(
        f"Could not find an AI Skill Framework workspace from '{original}' "
        f"within {max_parents} parent directories; expected both "
        f"{WORKSPACE_MARKERS[0]} and {WORKSPACE_MARKERS[1]}."
    )
