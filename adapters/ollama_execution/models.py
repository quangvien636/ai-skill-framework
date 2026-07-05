"""Serializable execution results owned by the Ollama adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class ExecutionDiagnostic:
    code: str
    severity: str
    message: str
    step_id: Optional[str] = None
    artifact: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "step_id": self.step_id,
            "artifact": self.artifact,
        }


@dataclass(frozen=True)
class StepExecutionResult:
    step_id: str
    skill_id: str
    runtime_binding: Mapping[str, Any]
    input_artifact: Mapping[str, Any]
    output_artifact: Optional[Mapping[str, Any]]
    diagnostics: tuple[ExecutionDiagnostic, ...]
    status: str
    error_message: Optional[str]
    duration_ms: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "skill_id": self.skill_id,
            "runtime_binding": dict(self.runtime_binding),
            "input_artifact": dict(self.input_artifact),
            "output_artifact": (
                dict(self.output_artifact)
                if self.output_artifact is not None
                else None
            ),
            "diagnostics": [item.as_dict() for item in self.diagnostics],
            "status": self.status,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
        }


@dataclass(frozen=True)
class ExecutionReport:
    report_version: str
    execution_id: str
    workflow_id: str
    workflow_version: str
    mode: str
    status: str
    model: Optional[str]
    endpoint: Optional[str]
    compiled: Mapping[str, Any]
    steps: tuple[StepExecutionResult, ...]
    diagnostics: tuple[ExecutionDiagnostic, ...]
    final_artifact: Optional[Mapping[str, Any]]
    duration_ms: int
    report_directory: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_version": self.report_version,
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "workflow_version": self.workflow_version,
            "mode": self.mode,
            "status": self.status,
            "model": self.model,
            "endpoint": self.endpoint,
            "compiled": dict(self.compiled),
            "steps": [step.as_dict() for step in self.steps],
            "diagnostics": [item.as_dict() for item in self.diagnostics],
            "final_artifact": (
                dict(self.final_artifact)
                if self.final_artifact is not None
                else None
            ),
            "duration_ms": self.duration_ms,
            "report_directory": self.report_directory,
        }
