"""Repository-integrity validation over a discovered ProjectIndex."""

from __future__ import annotations

import re
from pathlib import Path

from .diagnostics import (
    Diagnostic,
    REPOSITORY_CANONICAL_PATH_MISMATCH,
    REPOSITORY_CASE_COLLISION,
    REPOSITORY_KNOWLEDGE_INDEX_MISMATCH,
    REPOSITORY_KNOWLEDGE_INDEX_MISSING,
    REPOSITORY_PACKAGE_FILE_MISSING,
    Severity,
)
from .knowledge_ir import KnowledgeIR
from .pipeline import AdapterResult
from .project_discovery import ArtifactLocation, ProjectIndex
from .skill_ir import SkillIR
from .workflow_ir import WorkflowIR
from .content_integrity import validate_content_integrity

_INDEX_ROW_RE = re.compile(
    r"^\|\s*`(?P<id>kb:[^`]+)`\s*\|.*\|\s*`(?P<path>knowledge/[^`]+)`\s*\|"
)
_PACKAGE_REQUIREMENTS = {
    "skill": (
        "README.md",
        "instructions.md",
        "examples/README.md",
        "tests/README.md",
    ),
    "workflow": ("README.md", "examples/README.md", "tests/README.md"),
}


def validate_repository(
    index: ProjectIndex, results: list[AdapterResult]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    result_by_path = {
        Path(result.artifact).resolve(): result
        for result in results
        if result.ok and result.kind in ("skill", "workflow", "knowledge")
    }

    diagnostics.extend(_validate_case_collisions(index))
    diagnostics.extend(_validate_packages(index))

    knowledge_entries = _read_knowledge_index(index.workspace_root)
    discovered_knowledge: dict[str, str] = {}
    for artifact in index.artifacts:
        result = result_by_path.get(artifact.path.resolve())
        if result is None:
            continue
        expected = _expected_relative_path(result)
        actual = artifact.path.relative_to(index.workspace_root).as_posix()
        if expected is not None and actual != expected:
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_CANONICAL_PATH_MISMATCH,
                    severity=Severity.ERROR,
                    artifact=actual,
                    location="path",
                    message=(
                        f"Artifact path '{actual}' does not match canonical path "
                        f"'{expected}' derived from its IR identity."
                    ),
                    suggestion=f"Move the artifact to '{expected}' or correct its identity.",
                )
            )

        if isinstance(result.ir, KnowledgeIR):
            discovered_knowledge[result.ir.id] = actual
            indexed_path = knowledge_entries.get(result.ir.id)
            if indexed_path is None:
                diagnostics.append(
                    Diagnostic(
                        code=REPOSITORY_KNOWLEDGE_INDEX_MISSING,
                        severity=Severity.ERROR,
                        artifact=actual,
                        location="knowledge/KNOWLEDGE_INDEX.md",
                        message=f"Knowledge ID '{result.ir.id}' is not registered.",
                        suggestion="Add exactly one canonical row to the Knowledge Index.",
                    )
                )
            elif indexed_path != actual:
                diagnostics.append(
                    Diagnostic(
                        code=REPOSITORY_KNOWLEDGE_INDEX_MISMATCH,
                        severity=Severity.ERROR,
                        artifact=actual,
                        location="knowledge/KNOWLEDGE_INDEX.md",
                        message=(
                            f"Knowledge ID '{result.ir.id}' is indexed at "
                            f"'{indexed_path}', not '{actual}'."
                        ),
                        suggestion="Update the index path or move the canonical document.",
                    )
                )

    for knowledge_id, indexed_path in knowledge_entries.items():
        actual_path = discovered_knowledge.get(knowledge_id)
        if actual_path is None:
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_KNOWLEDGE_INDEX_MISMATCH,
                    severity=Severity.ERROR,
                    artifact="knowledge/KNOWLEDGE_INDEX.md",
                    location=knowledge_id,
                    message=(
                        f"Knowledge Index entry '{knowledge_id}' points to "
                        f"'{indexed_path}', but no discovered Knowledge artifact owns the ID."
                    ),
                    suggestion="Fix or remove the stale Knowledge Index row.",
                )
            )
    diagnostics.extend(validate_content_integrity(index, results))
    return diagnostics


def _expected_relative_path(result: AdapterResult) -> str | None:
    if isinstance(result.ir, SkillIR):
        return f"skills/{result.ir.metadata.name}/skill.yaml"
    if isinstance(result.ir, WorkflowIR):
        return f"workflows/{result.ir.metadata.name}/workflow.yaml"
    if isinstance(result.ir, KnowledgeIR):
        parts = result.ir.id.split(":")
        if len(parts) == 5 and parts[0] == "kb":
            return f"knowledge/{parts[1]}/{parts[2]}/{parts[3]}/{parts[4]}.md"
    return None


def _validate_packages(index: ProjectIndex) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for kind, required_paths in _PACKAGE_REQUIREMENTS.items():
        for artifact in index.by_kind(kind):
            package = artifact.path.parent
            for relative in required_paths:
                required = package / relative
                if not required.is_file():
                    diagnostics.append(
                        Diagnostic(
                            code=REPOSITORY_PACKAGE_FILE_MISSING,
                            severity=Severity.ERROR,
                            artifact=artifact.path.relative_to(
                                index.workspace_root
                            ).as_posix(),
                            location=relative,
                            message=(
                                f"{kind.title()} package is missing required file "
                                f"'{relative}'."
                            ),
                            suggestion=f"Add '{required.relative_to(index.workspace_root).as_posix()}'.",
                        )
                    )
    return diagnostics


def _validate_case_collisions(index: ProjectIndex) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen: dict[str, ArtifactLocation] = {}
    for artifact in index.artifacts:
        relative = artifact.path.relative_to(index.workspace_root).as_posix()
        key = f"{artifact.kind}:{relative.casefold()}:{artifact.embedded_section or ''}"
        previous = seen.get(key)
        previous_relative = (
            previous.path.relative_to(index.workspace_root).as_posix()
            if previous is not None
            else None
        )
        if previous is not None and previous_relative != relative:
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_CASE_COLLISION,
                    severity=Severity.ERROR,
                    artifact=relative,
                    location="path",
                    message=(
                        f"Case-insensitive path collision between '{relative}' and "
                        f"'{previous_relative}'."
                    ),
                    suggestion="Rename one path so identities differ without case folding.",
                )
            )
        else:
            seen[key] = artifact
    return diagnostics


def _read_knowledge_index(workspace_root: Path) -> dict[str, str]:
    path = workspace_root / "knowledge" / "KNOWLEDGE_INDEX.md"
    if not path.is_file():
        return {}
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _INDEX_ROW_RE.match(line)
        if match:
            entries[match.group("id")] = match.group("path")
    return entries
