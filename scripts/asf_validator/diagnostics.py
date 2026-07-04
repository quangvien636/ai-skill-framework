"""Diagnostic shape shared by every IR adapter.

Matches docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md's diagnostic
fields (code, severity, artifact, location, message, rule_reference,
suggestion), the ASF-PARSE-* prefix allocated by ADR-0009, and the
ASF-GRAPH-* prefix allocated by ADR-0010.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: Severity
    artifact: str
    location: str
    message: str
    rule_reference: Optional[str] = None
    suggestion: Optional[str] = None

    def is_error(self) -> bool:
        return self.severity is Severity.ERROR


def has_errors(diagnostics: list[Diagnostic]) -> bool:
    return any(d.is_error() for d in diagnostics)


# ASF-PARSE-* code allocations (ADR-0009). Each is a distinct, stable
# reason an IR adapter could not (fully) build an IR object.
PARSE_MALFORMED_SOURCE = "ASF-PARSE-001"
PARSE_UNSUPPORTED_SCHEMA_VERSION = "ASF-PARSE-002"
PARSE_MISSING_KNOWLEDGE_SECTION = "ASF-PARSE-003"
PARSE_UNRESOLVED_WORKFLOW_REFERENCE = "ASF-PARSE-004"
PARSE_METADATA_ID_NAME_MISMATCH = "ASF-PARSE-005"
PARSE_WORKFLOW_GRAPH_CYCLE = "ASF-PARSE-006"

# ASF-GRAPH-* code allocations (ADR-0010). Cross-artifact Dependency Graph
# and Version Graph diagnostics -- these fire after IR construction already
# succeeded for each artifact individually.
GRAPH_MISSING_DEPENDENCY = "ASF-GRAPH-001"
GRAPH_REFERENCE_CYCLE = "ASF-GRAPH-002"
GRAPH_DUPLICATE_ARTIFACT_ID = "ASF-GRAPH-003"
GRAPH_VERSION_UNSATISFIABLE = "ASF-GRAPH-004"
GRAPH_DEPRECATED_DEPENDENCY = "ASF-GRAPH-005"
GRAPH_AMBIGUOUS_VERSION_REFERENCE = "ASF-GRAPH-006"
GRAPH_SELF_CONTRADICTORY_RANGE = "ASF-GRAPH-007"
