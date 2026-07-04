"""Reference IR: resolved-or-resolvable pointers from one artifact to another.

See docs/specifications/IR_SPECIFICATION.md's Reference IR section. This
module only structures a reference (target id + version constraint); it
does not resolve it against the rest of the repository -- resolution is the
Dependency Graph, Phase 3/4 work (ADR-0009's scope boundary).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .version_ir import VersionRangeIR, parse_version_range


@dataclass(frozen=True)
class ReferenceIR:
    id: str
    version: VersionRangeIR
    required: bool = True


@dataclass(frozen=True)
class KnowledgeReferenceIR:
    id: str
    version: VersionRangeIR
    required: bool
    purpose: str
    sections: tuple[str, ...] = ()


def build_reference_ir(doc: dict[str, Any]) -> Optional[ReferenceIR]:
    version_range, error = parse_version_range(doc["version"])
    if version_range is None:  # pragma: no cover - schema already validates format
        return None
    return ReferenceIR(id=doc["id"], version=version_range, required=doc.get("required", True))


def build_knowledge_reference_ir(doc: dict[str, Any]) -> Optional[KnowledgeReferenceIR]:
    version_range, error = parse_version_range(doc["version"])
    if version_range is None:  # pragma: no cover - schema already validates format
        return None
    return KnowledgeReferenceIR(
        id=doc["id"],
        version=version_range,
        required=doc["required"],
        purpose=doc["purpose"],
        sections=tuple(doc.get("sections", [])),
    )
