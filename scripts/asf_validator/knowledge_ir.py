"""Knowledge IR: the Markdown normalizer producing schemas/knowledge.schema.json's
normalized object from a canonical Knowledge Markdown document
(knowledge/_templates/KNOWLEDGE_TEMPLATE.md's structure).

This is the one "real transform" IR_ARCHITECTURE.md's Normalization
Strategy describes -- the other adapters are close to identity mappings.
It requires every canonical section/metadata bullet to be *present* to
normalize at all (ASF-PARSE-003); it does not check the extracted values
against the Knowledge Index or the file's own path -- that remains Phase 3
(ADR-0009's scope boundary).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .diagnostics import Diagnostic, PARSE_MISSING_KNOWLEDGE_SECTION, Severity

_METADATA_BULLET_RE = re.compile(r"^-\s+\*\*([^:*]+):\*\*\s*(.*)$")
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
_BULLET_RE = re.compile(r"^-\s+(?!\[)(.*)$")
_NUMBERED_RE = re.compile(r"^\d+\.\s+(.*)$")
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")

_REQUIRED_METADATA_KEYS = {
    "knowledge id": "id",
    "status": "status",
    "category": "category",
    "domain": "domain",
    "topic": "topic",
    "version": "version",
    "last updated": "last_updated",
}

_REQUIRED_SECTIONS = (
    "summary",
    "applies to",
    "scope",
    "guidance",
    "decision rules",
    "examples",
    "limitations and risks",
    "related knowledge",
    "sources",
    "revision history",
)


@dataclass(frozen=True)
class RevisionEntryIR:
    version: str
    date: str
    description: str


@dataclass(frozen=True)
class KnowledgeIR:
    id: str
    title: str
    status: str
    category: str
    domain: str
    topic: str
    version: str
    last_updated: str
    summary: str
    applies_to: tuple[str, ...]
    scope_includes: tuple[str, ...]
    scope_excludes: tuple[str, ...]
    guidance: str
    decision_rules: tuple[str, ...]
    examples_good: str
    examples_counterexample: str
    limitations_and_risks: tuple[str, ...]
    related_knowledge: tuple[str, ...]
    sources: tuple[str, ...]
    revision_history: tuple[RevisionEntryIR, ...]

    def as_normalized_dict(self) -> dict:
        """The object schemas/knowledge.schema.json validates."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "category": self.category,
            "domain": self.domain,
            "topic": self.topic,
            "version": self.version,
            "last_updated": self.last_updated,
            "summary": self.summary,
            "applies_to": list(self.applies_to),
            "scope": {"includes": list(self.scope_includes), "excludes": list(self.scope_excludes)},
            "guidance": self.guidance,
            "decision_rules": list(self.decision_rules),
            "examples": {"good": self.examples_good, "counterexample": self.examples_counterexample},
            "limitations_and_risks": list(self.limitations_and_risks),
            "related_knowledge": list(self.related_knowledge),
            "sources": list(self.sources),
            "revision_history": [
                {"version": r.version, "date": r.date, "description": r.description}
                for r in self.revision_history
            ],
        }


def _strip_backticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1]
    return value


def _section_key(heading_text: str) -> str:
    return heading_text.strip().lower()


class _Section:
    __slots__ = ("content_lines", "subsections")

    def __init__(self) -> None:
        self.content_lines: list[str] = []
        self.subsections: dict[str, list[str]] = {}


def _parse_structure(text: str) -> tuple[Optional[str], dict[str, str], dict[str, _Section]]:
    lines = text.splitlines()
    title: Optional[str] = None
    metadata: dict[str, str] = {}
    sections: dict[str, _Section] = {}

    current_h2: Optional[str] = None
    current_h3: Optional[str] = None
    in_metadata_block = False

    for line in lines:
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            level, text_ = heading_match.groups()
            if level == "#":
                title = text_.strip()
                in_metadata_block = True
                current_h2 = None
                current_h3 = None
                continue
            if level == "##":
                current_h2 = _section_key(text_)
                current_h3 = None
                sections.setdefault(current_h2, _Section())
                in_metadata_block = False
                continue
            if level == "###":
                current_h3 = _section_key(text_)
                if current_h2 is not None:
                    sections[current_h2].subsections.setdefault(current_h3, [])
                in_metadata_block = False
                continue

        if in_metadata_block:
            bullet_match = _METADATA_BULLET_RE.match(line)
            if bullet_match:
                key, value = bullet_match.groups()
                metadata[key.strip().lower()] = _strip_backticks(value)
                continue
            if line.strip() == "":
                continue
            in_metadata_block = False

        if current_h2 is None:
            continue
        if current_h3 is not None:
            sections[current_h2].subsections[current_h3].append(line)
        else:
            sections[current_h2].content_lines.append(line)

    return title, metadata, sections


def _bullets(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        match = _BULLET_RE.match(line.strip())
        if match:
            items.append(match.group(1).strip())
    return items


def _numbered(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        match = _NUMBERED_RE.match(line.strip())
        if match:
            items.append(match.group(1).strip())
    return items


def _paragraph(lines: list[str]) -> str:
    return "\n".join(line for line in lines if line.strip() != "").strip()


def _parse_revision_table(lines: list[str]) -> list[RevisionEntryIR]:
    rows = [line.strip() for line in lines if _TABLE_ROW_RE.match(line.strip())]
    entries: list[RevisionEntryIR] = []
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if set(cells[0]) <= {"-", " "}:
            continue  # separator row
        if cells[0].lower() == "version":
            continue  # header row
        entries.append(RevisionEntryIR(version=cells[0], date=cells[1], description=cells[2]))
    return entries


def build_knowledge_ir(text: str, artifact: str) -> tuple[Optional[KnowledgeIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    title, metadata, sections = _parse_structure(text)

    if not title:
        diagnostics.append(
            Diagnostic(
                code=PARSE_MISSING_KNOWLEDGE_SECTION,
                severity=Severity.ERROR,
                artifact=artifact,
                location="<title>",
                message="Document has no top-level '# Title' heading.",
            )
        )

    for bullet_label, field_name in _REQUIRED_METADATA_KEYS.items():
        if bullet_label not in metadata:
            diagnostics.append(
                Diagnostic(
                    code=PARSE_MISSING_KNOWLEDGE_SECTION,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location="<metadata>",
                    message=f"Missing required metadata bullet '{bullet_label}' (-> {field_name}).",
                )
            )

    for section_name in _REQUIRED_SECTIONS:
        if section_name not in sections:
            diagnostics.append(
                Diagnostic(
                    code=PARSE_MISSING_KNOWLEDGE_SECTION,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"## {section_name}",
                    message=f"Missing required section '## {section_name.title()}'.",
                )
            )

    if diagnostics:
        return None, diagnostics

    scope = sections["scope"]
    examples = sections["examples"]

    knowledge = KnowledgeIR(
        id=metadata["knowledge id"],
        title=title,  # type: ignore[arg-type]
        status=metadata["status"].strip().lower(),
        category=metadata["category"],
        domain=metadata["domain"],
        topic=metadata["topic"],
        version=metadata["version"],
        last_updated=metadata["last updated"],
        summary=_paragraph(sections["summary"].content_lines),
        applies_to=tuple(_bullets(sections["applies to"].content_lines)),
        scope_includes=tuple(_bullets(scope.subsections.get("includes", []))),
        scope_excludes=tuple(_bullets(scope.subsections.get("excludes", []))),
        guidance=_paragraph(sections["guidance"].content_lines),
        decision_rules=tuple(_numbered(sections["decision rules"].content_lines)),
        examples_good=_paragraph(examples.subsections.get("good example", [])),
        examples_counterexample=_paragraph(examples.subsections.get("counterexample", [])),
        limitations_and_risks=tuple(_bullets(sections["limitations and risks"].content_lines)),
        related_knowledge=tuple(_bullets(sections["related knowledge"].content_lines)),
        sources=tuple(_bullets(sections["sources"].content_lines)),
        revision_history=tuple(_parse_revision_table(sections["revision history"].content_lines)),
    )
    return knowledge, diagnostics
