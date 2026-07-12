"""Credential-free local Markdown publishing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Mapping

import yaml

from .descriptors import ExportDescriptor


class PublishError(RuntimeError):
    """Raised when a descriptor cannot be safely published."""


class UnsupportedPublishTargetError(PublishError):
    """Raised before mutation for targets requiring external authority."""


@dataclass(frozen=True)
class PublishResult:
    target: str
    path: str
    bytes_written: int


class PublisherAdapter:
    """Publish Markdown descriptors into one caller-owned local root."""

    def __init__(self, output_root: Path, *, overwrite: bool = False) -> None:
        self._output_root = output_root.resolve()
        self._overwrite = overwrite

    def publish(self, descriptor: ExportDescriptor) -> PublishResult:
        if descriptor.target != "markdown":
            raise UnsupportedPublishTargetError(
                f"target '{descriptor.target}' requires external publishing "
                "authority; this execute half supports local Markdown only"
            )

        filename = _safe_filename(descriptor.title)
        destination = (self._output_root / filename).resolve()
        if self._output_root not in destination.parents:
            raise PublishError("Markdown destination escapes the configured output root")

        content = _render_markdown(descriptor)
        self._output_root.mkdir(parents=True, exist_ok=True)
        mode = "w" if self._overwrite else "x"
        try:
            with destination.open(mode, encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        except FileExistsError as error:
            raise PublishError(
                f"destination already exists: '{destination}'"
            ) from error
        return PublishResult(
            target="markdown",
            path=str(destination),
            bytes_written=len(content.encode("utf-8")),
        )


def _safe_filename(title: str) -> str:
    slug = re.sub(r"[^\w]+", "-", title.lower(), flags=re.UNICODE).strip("-_")
    if not slug:
        raise PublishError("title does not contain a usable filename character")
    if slug.upper() in {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1"}:
        raise PublishError("title resolves to a reserved filename")
    return f"{slug}.md"


def _render_markdown(descriptor: ExportDescriptor) -> str:
    front_matter = descriptor.metadata.get("front_matter", {})
    if not isinstance(front_matter, Mapping):
        raise PublishError("markdown front_matter must be a mapping")
    parts: list[str] = []
    if front_matter:
        serialized = yaml.safe_dump(
            dict(front_matter),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=True,
        ).rstrip()
        parts.append(f"---\n{serialized}\n---")
    parts.append(f"# {descriptor.title}")
    parts.append(descriptor.body)
    return "\n\n".join(parts).rstrip() + "\n"

