"""Artifact catalog built from the shared Validator IR pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.pipeline import AdapterResult
from asf_validator.skill_ir import SkillIR
from asf_validator.version_ir import (
    VersionIR,
    VersionRangeIR,
    parse_version,
    version_satisfies_range,
)
from asf_validator.workflow_ir import WorkflowIR


@dataclass(frozen=True)
class CatalogArtifact:
    kind: str
    id: str
    version: VersionIR
    status: str
    path: str
    ir: Any


@dataclass(frozen=True)
class ArtifactCatalog:
    artifacts: tuple[CatalogArtifact, ...]
    _by_id: Mapping[str, tuple[CatalogArtifact, ...]]

    def candidates(self, artifact_id: str) -> tuple[CatalogArtifact, ...]:
        return self._by_id.get(artifact_id, ())

    def resolve(
        self, artifact_id: str, version_range: VersionRangeIR
    ) -> CatalogArtifact:
        matches = tuple(
            artifact
            for artifact in self.candidates(artifact_id)
            if artifact.status == "active"
            and version_satisfies_range(artifact.version, version_range)
        )
        if len(matches) != 1:
            raise LookupError(
                f"Expected exactly one active '{artifact_id}' satisfying "
                f"'{version_range.raw}', found {len(matches)}."
            )
        return matches[0]

    def exact(self, artifact_id: str, version: str) -> CatalogArtifact:
        matches = tuple(
            artifact
            for artifact in self.candidates(artifact_id)
            if artifact.status == "active" and artifact.version.raw == version
        )
        if len(matches) != 1:
            raise LookupError(
                f"Expected exactly one active '{artifact_id}' at '{version}', "
                f"found {len(matches)}."
            )
        return matches[0]


def build_artifact_catalog(results: Iterable[AdapterResult]) -> ArtifactCatalog:
    artifacts: list[CatalogArtifact] = []
    seen: set[tuple[str, str, str]] = set()
    for result in results:
        if not result.ok:
            continue
        artifact = _catalog_artifact(result)
        if artifact is None:
            continue
        key = (artifact.kind, artifact.id, artifact.version.raw)
        if key in seen:
            raise ValueError(
                f"Duplicate catalog artifact {artifact.kind} '{artifact.id}' "
                f"version '{artifact.version.raw}'."
            )
        seen.add(key)
        artifacts.append(artifact)

    artifacts.sort(key=lambda item: (item.kind, item.id, _version_key(item.version)))
    grouped: dict[str, list[CatalogArtifact]] = {}
    for artifact in artifacts:
        grouped.setdefault(artifact.id, []).append(artifact)
    return ArtifactCatalog(
        artifacts=tuple(artifacts),
        _by_id=MappingProxyType(
            {artifact_id: tuple(entries) for artifact_id, entries in grouped.items()}
        ),
    )


def _catalog_artifact(result: AdapterResult) -> CatalogArtifact | None:
    ir = result.ir
    if isinstance(ir, SkillIR):
        return CatalogArtifact(
            "skill",
            ir.metadata.id,
            ir.metadata.version,
            ir.metadata.status,
            result.artifact,
            ir,
        )
    if isinstance(ir, WorkflowIR):
        return CatalogArtifact(
            "workflow",
            ir.metadata.id,
            ir.metadata.version,
            ir.metadata.status,
            result.artifact,
            ir,
        )
    if isinstance(ir, KnowledgeIR):
        version, error = parse_version(ir.version)
        if version is None:
            raise ValueError(error)
        return CatalogArtifact(
            "knowledge", ir.id, version, ir.status, result.artifact, ir
        )
    return None


def _version_key(version: VersionIR) -> tuple[int, int, int, str, str]:
    return (
        version.major,
        version.minor,
        version.patch,
        version.prerelease or "",
        version.build or "",
    )
