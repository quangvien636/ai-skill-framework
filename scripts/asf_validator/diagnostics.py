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

# ASF-SEMANTIC-* code allocations. These rules run over successfully built IR
# and validate relationships inside or between those typed artifacts without
# consulting repository layout.
SEMANTIC_DUPLICATE_METRIC_NAME = "ASF-SEMANTIC-001"
SEMANTIC_INVALID_METRIC_WEIGHT_TOTAL = "ASF-SEMANTIC-002"
SEMANTIC_REFLECTION_ROUTING_INCONSISTENT = "ASF-SEMANTIC-003"
SEMANTIC_REFLECTABLE_GATE_UNKNOWN = "ASF-SEMANTIC-004"
SEMANTIC_WORKFLOW_MAPPING_TARGET_INVALID = "ASF-SEMANTIC-005"
SEMANTIC_WORKFLOW_MAPPING_SOURCE_INVALID = "ASF-SEMANTIC-006"
SEMANTIC_WORKFLOW_MAPPING_TYPE_MISMATCH = "ASF-SEMANTIC-007"
SEMANTIC_WORKFLOW_ROUTING_INCONSISTENT = "ASF-SEMANTIC-008"
SEMANTIC_WORKFLOW_STEP_UNREACHABLE = "ASF-SEMANTIC-009"
