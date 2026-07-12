"""Deterministic repository content-integrity checks.

Rules intentionally use narrow signatures and explicit scope to avoid noisy
heuristics. Templates and known placeholder guides are not shipped artifacts.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from .diagnostics import (
    Diagnostic,
    REPOSITORY_ADR_REFERENCE_INVALID,
    REPOSITORY_ADR_STATUS_INVALID,
    REPOSITORY_ANCHOR_MISSING,
    REPOSITORY_DUPLICATE_ANCHOR,
    REPOSITORY_LIFECYCLE_ORPHAN,
    REPOSITORY_LINK_TARGET_MISSING,
    REPOSITORY_PLACEHOLDER_FORBIDDEN,
    REPOSITORY_SECRET_DETECTED,
    REPOSITORY_STALE_REFERENCE,
    Severity,
)
from .knowledge_ir import KnowledgeIR
from .pipeline import AdapterResult
from .project_discovery import ProjectIndex
from .runtime_ir import RuntimeIR
from .skill_ir import SkillIR
from .workflow_ir import WorkflowIR

_MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*\s*$")
_EXPLICIT_ANCHOR_RE = re.compile(r"<a\s+(?:name|id)=[\"'](?P<id>[^\"']+)[\"']", re.I)
_ADR_RE = re.compile(r"ADR-(?P<number>\d{4})(?![\w-])")
_ADR_STATUS_LINE_RE = re.compile(r"^-\s+\*\*Status:\*\*\s*(?P<value>.+?)\s*$", re.MULTILINE)
_ADR_SUPERSEDED_RE = re.compile(r"^Superseded by (?P<adr>ADR-\d{4})$")
_ADR_ALLOWED_STATUSES = frozenset({"Proposed", "Accepted"})
_PLACEHOLDER_RE = re.compile(r"\b(?:TODO|FIXME|TBD)\b|<[a-z][a-z0-9-]*>")
_STALE_REFERENCES = (
    "knowledge/research/" + "methodology/",
    "kb:research:" + "methodology:",
)
_TEXT_SUFFIXES = frozenset({".md", ".yaml", ".yml", ".json", ".py", ".ps1", ".txt"})
_SECRET_PATTERNS = (
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    ("github-token", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
)


def validate_content_integrity(
    index: ProjectIndex, results: list[AdapterResult]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    markdown = _repository_markdown(index.workspace_root)
    anchor_cache = {path: _anchors(path) for path in markdown}

    for path, (anchors, duplicates) in anchor_cache.items():
        relative = path.relative_to(index.workspace_root).as_posix()
        for anchor in sorted(duplicates):
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_DUPLICATE_ANCHOR,
                    severity=Severity.ERROR,
                    artifact=relative,
                    location=f"#{anchor}",
                    message=f"Markdown anchor '{anchor}' is declared more than once.",
                    suggestion="Rename duplicate headings or explicit anchors.",
                )
            )
        diagnostics.extend(_validate_links(index.workspace_root, path, anchors, anchor_cache))

    diagnostics.extend(_validate_adr_references(index.workspace_root, markdown))
    diagnostics.extend(_validate_adr_status(index.workspace_root))
    diagnostics.extend(_validate_shipped_placeholders(index, results))
    diagnostics.extend(_validate_stale_references(index.workspace_root))
    diagnostics.extend(_validate_obvious_secrets(index.workspace_root))
    diagnostics.extend(_validate_lifecycle_orphans(index, results))
    return diagnostics


def _repository_markdown(root: Path) -> tuple[Path, ...]:
    excluded = {".git", ".agents", ".codex"}
    return tuple(
        sorted(
            (
                path
                for path in root.rglob("*.md")
                if not any(part in excluded for part in path.relative_to(root).parts)
            ),
            key=lambda path: path.relative_to(root).as_posix().casefold(),
        )
    )


def _anchors(path: Path) -> tuple[set[str], set[str]]:
    raw: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            slug = _github_slug(heading.group("title"))
            if slug:
                raw.append(slug)
        raw.extend(match.group("id") for match in _EXPLICIT_ANCHOR_RE.finditer(line))
    counts = Counter(raw)
    return set(raw), {anchor for anchor, count in counts.items() if count > 1}


def _github_slug(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title).strip().lower()
    title = re.sub(r"[^\w\s-]", "", title)
    return re.sub(r"\s+", "-", title)


def _validate_links(
    root: Path,
    source: Path,
    source_anchors: set[str],
    anchor_cache: dict[Path, tuple[set[str], set[str]]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    relative = source.relative_to(root).as_posix()
    for match in _MARKDOWN_LINK_RE.finditer(source.read_text(encoding="utf-8")):
        raw = match.group("target").strip().split()[0].strip("<>")
        if raw.startswith(("http://", "https://", "mailto:")):
            continue
        path_text, separator, fragment = raw.partition("#")
        target = source if not path_text else (source.parent / unquote(path_text)).resolve()
        if not target.exists():
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_LINK_TARGET_MISSING,
                    severity=Severity.ERROR,
                    artifact=relative,
                    location=raw,
                    message=f"Relative Markdown link target '{raw}' does not exist.",
                    suggestion="Fix the relative path or add the referenced file.",
                )
            )
            continue
        if not separator or not fragment:
            continue
        fragment = unquote(fragment).lower()
        anchors = source_anchors if target == source else anchor_cache.get(target, (set(), set()))[0]
        if target.suffix.lower() == ".md" and fragment not in anchors:
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_ANCHOR_MISSING,
                    severity=Severity.ERROR,
                    artifact=relative,
                    location=raw,
                    message=f"Markdown anchor '#{fragment}' does not exist in '{target.name}'.",
                    suggestion="Fix the fragment or add the target heading.",
                )
            )
    return diagnostics


def _validate_adr_references(root: Path, markdown: tuple[Path, ...]) -> list[Diagnostic]:
    known = {
        path.name[:8]
        for path in (root / "docs" / "adr").glob("ADR-[0-9][0-9][0-9][0-9]-*.md")
    }
    diagnostics: list[Diagnostic] = []
    for path in markdown:
        if path.name == "ADR_TEMPLATE.md":
            continue
        for match in _ADR_RE.finditer(path.read_text(encoding="utf-8")):
            adr = f"ADR-{match.group('number')}"
            if adr not in known:
                diagnostics.append(
                    Diagnostic(
                        code=REPOSITORY_ADR_REFERENCE_INVALID,
                        severity=Severity.ERROR,
                        artifact=path.relative_to(root).as_posix(),
                        location=adr,
                        message=f"ADR reference '{adr}' has no canonical ADR document.",
                        suggestion="Fix the ADR number or add the referenced decision record.",
                    )
                )
    return diagnostics


def _validate_adr_status(root: Path) -> list[Diagnostic]:
    """ASF-REPOSITORY-014: each canonical ADR's own `- **Status:**` field
    must be one of the values ADR_TEMPLATE.md declares as allowed
    (`Proposed`, `Accepted`, or `Superseded by ADR-<NNNN>` naming a real
    ADR) -- a lightweight mechanical check for
    `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance convention, which
    otherwise has no automated way to catch a typo'd or stale Status value.
    This only checks the field's *value* is well-formed; it never infers or
    changes what a Status should be -- accepting an ADR remains a human
    decision (DECISION_RIGHTS.md), this only keeps the field mechanically
    honest once a human has set it.
    """
    adr_dir = root / "docs" / "adr"
    paths = sorted(adr_dir.glob("ADR-[0-9][0-9][0-9][0-9]-*.md"))
    known = {path.name[:8] for path in paths}
    diagnostics: list[Diagnostic] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        match = _ADR_STATUS_LINE_RE.search(text)
        if match is None:
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_ADR_STATUS_INVALID,
                    severity=Severity.ERROR,
                    artifact=relative,
                    location="Status",
                    message="ADR has no '- **Status:**' field.",
                    suggestion="Add a Status field matching ADR_TEMPLATE.md.",
                )
            )
            continue
        value = match.group("value")
        superseded = _ADR_SUPERSEDED_RE.match(value)
        if value in _ADR_ALLOWED_STATUSES:
            continue
        if superseded and superseded.group("adr") in known:
            continue
        if superseded:
            diagnostics.append(
                Diagnostic(
                    code=REPOSITORY_ADR_STATUS_INVALID,
                    severity=Severity.ERROR,
                    artifact=relative,
                    location="Status",
                    message=(
                        f"ADR Status references '{superseded.group('adr')}', "
                        "which has no canonical ADR document."
                    ),
                    suggestion="Fix the ADR number or add the referenced decision record.",
                )
            )
            continue
        diagnostics.append(
            Diagnostic(
                code=REPOSITORY_ADR_STATUS_INVALID,
                severity=Severity.ERROR,
                artifact=relative,
                location="Status",
                message=(
                    f"ADR Status '{value}' is not one of "
                    f"{sorted(_ADR_ALLOWED_STATUSES)} or 'Superseded by ADR-<NNNN>'."
                ),
                suggestion="Use a Status value matching ADR_TEMPLATE.md.",
            )
        )
    return diagnostics


def _validate_shipped_placeholders(
    index: ProjectIndex, results: list[AdapterResult]
) -> list[Diagnostic]:
    active_packages = {
        Path(result.artifact).resolve().parent
        for result in results
        if result.ok
        and isinstance(result.ir, (SkillIR, WorkflowIR))
        and result.ir.metadata.status == "active"
    }
    active_files = {
        Path(result.artifact).resolve()
        for result in results
        if result.ok
        and (
            (
                isinstance(result.ir, (SkillIR, WorkflowIR))
                and result.ir.metadata.status == "active"
            )
            or (isinstance(result.ir, KnowledgeIR) and result.ir.status == "active")
        )
    }
    for package in active_packages:
        active_files.update(
            path
            for path in package.rglob("*")
            if path.is_file() and path.suffix.lower() in _TEXT_SUFFIXES
        )
    diagnostics: list[Diagnostic] = []
    for path in sorted(active_files, key=lambda item: str(item).casefold()):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = _PLACEHOLDER_RE.search(line)
            if match:
                diagnostics.append(
                    Diagnostic(
                        code=REPOSITORY_PLACEHOLDER_FORBIDDEN,
                        severity=Severity.ERROR,
                        artifact=path.relative_to(index.workspace_root).as_posix(),
                        location=f"line {line_number}",
                        message=f"Shipped active artifact contains forbidden marker '{match.group()}'.",
                        suggestion="Replace the marker with final production content.",
                    )
                )
    return diagnostics


def _validate_stale_references(root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for path in _text_files(root):
        text = path.read_text(encoding="utf-8")
        for stale in _STALE_REFERENCES:
            if stale in text:
                diagnostics.append(
                    Diagnostic(
                        code=REPOSITORY_STALE_REFERENCE,
                        severity=Severity.ERROR,
                        artifact=path.relative_to(root).as_posix(),
                        location=stale,
                        message=f"Forbidden stale canonical reference '{stale}' remains.",
                        suggestion="Update the reference to the current canonical identity.",
                    )
                )
    return diagnostics


def _validate_obvious_secrets(root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for path in _text_files(root):
        text = path.read_text(encoding="utf-8")
        for name, pattern in _SECRET_PATTERNS:
            if pattern.search(text):
                diagnostics.append(
                    Diagnostic(
                        code=REPOSITORY_SECRET_DETECTED,
                        severity=Severity.ERROR,
                        artifact=path.relative_to(root).as_posix(),
                        location=name,
                        message=f"Obvious committed secret signature '{name}' detected.",
                        suggestion="Remove and rotate the credential; use a documented secret provider.",
                    )
                )
    return diagnostics


def _text_files(root: Path) -> tuple[Path, ...]:
    excluded = {".git", ".agents", ".codex"}
    return tuple(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in _TEXT_SUFFIXES
        and not any(part in excluded for part in path.relative_to(root).parts)
        and "__pycache__" not in path.parts
    )


def _validate_lifecycle_orphans(
    index: ProjectIndex, results: list[AdapterResult]
) -> list[Diagnostic]:
    skills: dict[str, SkillIR] = {}
    workflows: list[WorkflowIR] = []
    knowledge: dict[str, KnowledgeIR] = {}
    runtimes: dict[str, RuntimeIR] = {}
    for result in results:
        if not result.ok:
            continue
        if isinstance(result.ir, SkillIR):
            skills[result.ir.metadata.id] = result.ir
        elif isinstance(result.ir, WorkflowIR):
            workflows.append(result.ir)
        elif isinstance(result.ir, KnowledgeIR):
            knowledge[result.ir.id] = result.ir
        elif isinstance(result.ir, RuntimeIR):
            runtimes[result.ir.metadata.id] = result.ir
    used_skills = {step.skill.id for workflow in workflows for step in workflow.steps}
    used_knowledge = {
        reference.id
        for skill in skills.values()
        for reference in skill.dependencies.knowledge
    }
    used_runtimes = {
        reference.id for skill in skills.values() for reference in skill.dependencies.runtime
    } | {
        runtime.fallback_profile.fallback_runtime.id
        for runtime in runtimes.values()
        if runtime.fallback_profile.fallback_runtime is not None
    }
    diagnostics: list[Diagnostic] = []
    for skill_id, skill in skills.items():
        if skill.metadata.status == "active" and skill_id not in used_skills:
            diagnostics.append(_orphan(skill_id, "Active Skill has no Workflow consumer."))
    for knowledge_id, artifact in knowledge.items():
        if artifact.status == "active" and knowledge_id not in used_knowledge:
            diagnostics.append(_orphan(knowledge_id, "Active Knowledge has no Skill consumer."))
    for runtime_id, runtime in runtimes.items():
        if runtime.metadata.status == "active" and runtime_id not in used_runtimes:
            diagnostics.append(
                _orphan(
                    runtime_id,
                    "Active Runtime Contract has no Skill consumer and is not another "
                    "active Runtime's fallback.",
                )
            )
    for artifact in index.by_kind("example"):
        relative = artifact.path.relative_to(index.workspace_root)
        if len(relative.parts) < 4 or relative.parts[0] not in ("skills", "workflows"):
            continue
        owner_kind = relative.parts[0]
        owner_name = relative.parts[1]
        owner_id = (
            f"skill:{owner_name}" if owner_kind == "skills" else f"workflow:{owner_name}"
        )
        if owner_id not in skills and not any(
            workflow.metadata.id == owner_id for workflow in workflows
        ):
            diagnostics.append(_orphan(relative.as_posix(), "Example has no discovered owner."))
    return diagnostics


def _orphan(artifact: str, message: str) -> Diagnostic:
    return Diagnostic(
        code=REPOSITORY_LIFECYCLE_ORPHAN,
        severity=Severity.ERROR,
        artifact=artifact,
        location="lifecycle",
        message=message,
        suggestion="Add a canonical consumer/owner or change lifecycle status after review.",
    )
