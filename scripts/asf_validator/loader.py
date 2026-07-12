"""Repository loading: read one source file into a raw parsed document.

This module performs no schema validation and no IR normalization; it only
turns bytes on disk into a Python object (dict/list/str) or reports that it
could not. See docs/architecture/IR_ARCHITECTURE.md's Parser Strategy.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml

from .diagnostics import Diagnostic, PARSE_MALFORMED_SOURCE, Severity


SourcePath = tuple[str | int, ...]
SourcePositionMap = dict[SourcePath, tuple[int, int]]


class LoadResult:
    __slots__ = ("document", "text", "diagnostics", "positions")

    def __init__(
        self,
        document: Optional[Any],
        text: Optional[str],
        diagnostics: list[Diagnostic],
        positions: Optional[SourcePositionMap] = None,
    ) -> None:
        self.document = document
        self.text = text
        self.diagnostics = diagnostics
        self.positions = positions or {}

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _read_text(path: Path, artifact: str) -> tuple[Optional[str], list[Diagnostic]]:
    try:
        return path.read_text(encoding="utf-8"), []
    except OSError as exc:
        return None, [
            Diagnostic(
                code=PARSE_MALFORMED_SOURCE,
                severity=Severity.ERROR,
                artifact=artifact,
                location="<file>",
                message=f"Could not read file: {exc}",
            )
        ]


def load_yaml(path: Path) -> LoadResult:
    """Load a YAML manifest (Skill, Workflow) with unsafe features disabled."""
    artifact = str(path)
    text, diagnostics = _read_text(path, artifact)
    if text is None:
        return LoadResult(None, None, diagnostics)
    try:
        document = yaml.safe_load(text)
        positions = _source_positions(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        location = (
            f"line {mark.line + 1}, column {mark.column + 1}"
            if mark is not None
            else "<yaml>"
        )
        return LoadResult(
            None,
            text,
            [
                Diagnostic(
                    code=PARSE_MALFORMED_SOURCE,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=location,
                    message=f"Malformed YAML: {exc}",
                )
            ],
        )
    if not isinstance(document, dict):
        return LoadResult(
            None,
            text,
            [
                Diagnostic(
                    code=PARSE_MALFORMED_SOURCE,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location="<root>",
                    message="Top-level YAML document must be a mapping.",
                )
            ],
        )
    return LoadResult(document, text, [], positions)


def load_json(path: Path) -> LoadResult:
    """Load a JSON fixture (Evaluation, Reflection, or a Knowledge fixture)."""
    import json

    artifact = str(path)
    text, diagnostics = _read_text(path, artifact)
    if text is None:
        return LoadResult(None, None, diagnostics)
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        return LoadResult(
            None,
            text,
            [
                Diagnostic(
                    code=PARSE_MALFORMED_SOURCE,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"line {exc.lineno}, column {exc.colno}",
                    message=f"Malformed JSON: {exc.msg}",
                )
            ],
        )
    return LoadResult(document, text, [], _source_positions(text))


def load_markdown(path: Path) -> LoadResult:
    """Load raw Markdown text (Knowledge). Normalization happens in knowledge_ir."""
    artifact = str(path)
    text, diagnostics = _read_text(path, artifact)
    if text is None:
        return LoadResult(None, None, diagnostics)
    return LoadResult(None, text, [])


def _source_positions(text: str) -> SourcePositionMap:
    """Return key/item marks without changing the safe parsed document."""
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if root is None:
        return {}
    positions: SourcePositionMap = {}

    def record(node: yaml.Node, path: SourcePath, position_node: yaml.Node | None = None) -> None:
        mark = (position_node or node).start_mark
        positions[path] = (mark.line + 1, mark.column + 1)
        if isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                key = key_node.value
                record(value_node, path + (key,), key_node)
        elif isinstance(node, yaml.SequenceNode):
            for index, item_node in enumerate(node.value):
                record(item_node, path + (index,))

    record(root, ())
    return positions


def attach_source_positions(
    diagnostics: list[Diagnostic], positions: SourcePositionMap
) -> list[Diagnostic]:
    """Append the closest source mark while preserving the field path."""
    from dataclasses import replace

    enriched: list[Diagnostic] = []
    for diagnostic in diagnostics:
        if "line " in diagnostic.location and "column " in diagnostic.location:
            enriched.append(diagnostic)
            continue
        path = _diagnostic_path(diagnostic.location)
        candidate = path
        while candidate not in positions and candidate:
            candidate = candidate[:-1]
        position = positions.get(candidate) or positions.get(())
        if position is None:
            enriched.append(diagnostic)
            continue
        line, column = position
        enriched.append(
            replace(
                diagnostic,
                location=f"{diagnostic.location} (line {line}, column {column})",
            )
        )
    return enriched


def _diagnostic_path(location: str) -> SourcePath:
    if location in {"<root>", "<yaml>", "<file>"}:
        return ()
    parts: list[str | int] = []
    for part in location.split("."):
        parts.append(int(part) if part.isdigit() else part)
    return tuple(parts)
