"""Immutable Runtime context and execution-plan models."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


def freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze_value(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze_value(item) for item in value)
    return value


@dataclass(frozen=True)
class ExecutionContext:
    execution_id: str
    workflow_id: str
    workflow_version: str
    inputs: Mapping[str, Any]

    @classmethod
    def create(
        cls,
        execution_id: str,
        workflow_id: str,
        workflow_version: str,
        inputs: Mapping[str, Any],
    ) -> "ExecutionContext":
        if not execution_id:
            raise ValueError("execution_id must not be empty")
        return cls(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            inputs=freeze_value(inputs),
        )


@dataclass(frozen=True)
class DependencyResolution:
    source_id: str
    target_id: str
    target_version: str
    kind: str


@dataclass(frozen=True)
class PlanStep:
    id: str
    manifest_index: int
    skill_id: str
    skill_version: str
    depends_on: tuple[str, ...]
    input_mapping: Mapping[str, str]
    on_error: str
    max_attempts: int
    knowledge: tuple[DependencyResolution, ...]


@dataclass(frozen=True)
class ExecutionPlan:
    execution_id: str
    workflow_id: str
    workflow_version: str
    context: ExecutionContext
    steps: tuple[PlanStep, ...]
    batches: tuple[tuple[str, ...], ...]
    outputs: Mapping[str, str]
    resolutions: tuple[DependencyResolution, ...]
