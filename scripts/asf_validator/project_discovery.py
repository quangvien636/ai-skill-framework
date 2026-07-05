"""Deterministic, lazy Project Discovery.

Discovery enumerates source locations only. It never parses or normalizes an
artifact. Evaluation and Reflection are represented as embedded locations in
each discovered Skill manifest, preserving their embedded-only architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

SUPPORTED_DISCOVERY_KINDS = (
    "skill",
    "workflow",
    "knowledge",
    "evaluation",
    "reflection",
    "example",
)
_EXAMPLE_SUFFIXES = frozenset({".yaml", ".yml", ".json", ".md"})


@dataclass(frozen=True)
class ArtifactLocation:
    kind: str
    path: Path
    embedded_section: str | None = None

    @property
    def is_embedded(self) -> bool:
        return self.embedded_section is not None


@dataclass(frozen=True)
class ProjectIndex:
    workspace_root: Path
    artifacts: tuple[ArtifactLocation, ...]
    _by_kind: dict[str, tuple[ArtifactLocation, ...]] = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        grouped: dict[str, list[ArtifactLocation]] = {
            kind: [] for kind in SUPPORTED_DISCOVERY_KINDS
        }
        for artifact in self.artifacts:
            grouped[artifact.kind].append(artifact)
        object.__setattr__(
            self,
            "_by_kind",
            {kind: tuple(entries) for kind, entries in grouped.items()},
        )

    def by_kind(self, kind: str) -> tuple[ArtifactLocation, ...]:
        _validate_kinds((kind,))
        return self._by_kind[kind]

    def relative_path(self, artifact: ArtifactLocation) -> Path:
        return artifact.path.relative_to(self.workspace_root)


def discover_project(
    workspace_root: Path, kinds: Iterable[str] = SUPPORTED_DISCOVERY_KINDS
) -> ProjectIndex:
    """Enumerate only requested artifact kinds beneath an established root."""
    root = workspace_root.resolve()
    requested = tuple(dict.fromkeys(kinds))
    _validate_kinds(requested)

    artifacts: list[ArtifactLocation] = []
    skill_paths: tuple[Path, ...] | None = None

    def skills() -> tuple[Path, ...]:
        nonlocal skill_paths
        if skill_paths is None:
            skill_paths = tuple((root / "skills").glob("*/skill.yaml"))
        return skill_paths

    if "skill" in requested:
        artifacts.extend(ArtifactLocation("skill", path) for path in skills())
    if "workflow" in requested:
        artifacts.extend(
            ArtifactLocation("workflow", path)
            for path in (root / "workflows").glob("*/workflow.yaml")
        )
    if "knowledge" in requested:
        artifacts.extend(
            ArtifactLocation("knowledge", path)
            for path in (root / "knowledge").rglob("*.md")
            if _is_knowledge_artifact(root, path)
        )
    if "evaluation" in requested:
        artifacts.extend(
            ArtifactLocation("evaluation", path, "evaluation") for path in skills()
        )
    if "reflection" in requested:
        artifacts.extend(
            ArtifactLocation("reflection", path, "reflection") for path in skills()
        )
    if "example" in requested:
        artifacts.extend(
            ArtifactLocation("example", path)
            for package_root in (root / "skills", root / "workflows")
            for path in package_root.glob("*/examples/**/*")
            if _is_example_artifact(path)
        )

    artifacts.sort(
        key=lambda artifact: (
            artifact.kind,
            artifact.path.relative_to(root).as_posix().casefold(),
            artifact.path.relative_to(root).as_posix(),
            artifact.embedded_section or "",
        )
    )
    return ProjectIndex(workspace_root=root, artifacts=tuple(artifacts))


def _is_knowledge_artifact(root: Path, path: Path) -> bool:
    relative = path.relative_to(root / "knowledge")
    return (
        not any(part.startswith("_") for part in relative.parts)
        and path.name != "README.md"
        and path.name == path.name.lower()
    )


def _is_example_artifact(path: Path) -> bool:
    return (
        path.is_file()
        and path.name != "README.md"
        and path.suffix.lower() in _EXAMPLE_SUFFIXES
    )


def _validate_kinds(kinds: Iterable[str]) -> None:
    unsupported = sorted(set(kinds) - set(SUPPORTED_DISCOVERY_KINDS))
    if unsupported:
        raise ValueError(
            f"unsupported discovery kinds: {unsupported}; "
            f"supported: {list(SUPPORTED_DISCOVERY_KINDS)}"
        )
