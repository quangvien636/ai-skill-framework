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


class LoadResult:
    __slots__ = ("document", "text", "diagnostics")

    def __init__(
        self,
        document: Optional[Any],
        text: Optional[str],
        diagnostics: list[Diagnostic],
    ) -> None:
        self.document = document
        self.text = text
        self.diagnostics = diagnostics

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
    return LoadResult(document, text, [])


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
    return LoadResult(document, text, [])


def load_markdown(path: Path) -> LoadResult:
    """Load raw Markdown text (Knowledge). Normalization happens in knowledge_ir."""
    artifact = str(path)
    text, diagnostics = _read_text(path, artifact)
    if text is None:
        return LoadResult(None, None, diagnostics)
    return LoadResult(None, text, [])
