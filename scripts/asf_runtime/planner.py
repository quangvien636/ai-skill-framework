"""Deterministic Workflow planning without execution."""

from __future__ import annotations

from collections import defaultdict
from types import MappingProxyType
from typing import Any

from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.skill_ir import FieldIR, SkillIR
from asf_validator.workflow_ir import WorkflowIR

from .catalog import ArtifactCatalog
from .models import (
    DependencyResolution,
    ExecutionContext,
    ExecutionPlan,
    PlanStep,
)


class PlanningError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def plan_workflow(
    context: ExecutionContext, catalog: ArtifactCatalog
) -> ExecutionPlan:
    try:
        workflow_artifact = catalog.exact(
            context.workflow_id, context.workflow_version
        )
    except LookupError as error:
        raise PlanningError("ASF-RUNTIME-PLAN-001", str(error)) from error
    if not isinstance(workflow_artifact.ir, WorkflowIR):
        raise PlanningError(
            "ASF-RUNTIME-PLAN-001",
            f"'{context.workflow_id}' does not resolve to a Workflow.",
        )
    workflow = workflow_artifact.ir
    _validate_context_inputs(context, workflow)

    ordered_ids, batches = _topological_order(workflow)
    step_by_id = {step.id: step for step in workflow.steps}
    manifest_index = {step.id: index for index, step in enumerate(workflow.steps)}
    plan_steps: list[PlanStep] = []
    all_resolutions: list[DependencyResolution] = []

    for step_id in ordered_ids:
        step = step_by_id[step_id]
        try:
            skill_artifact = catalog.resolve(step.skill.id, step.skill.version)
        except LookupError as error:
            raise PlanningError("ASF-RUNTIME-PLAN-003", str(error)) from error
        if not isinstance(skill_artifact.ir, SkillIR):
            raise PlanningError(
                "ASF-RUNTIME-PLAN-003",
                f"'{step.skill.id}' does not resolve to a Skill.",
            )

        skill_resolution = DependencyResolution(
            source_id=workflow.metadata.id,
            target_id=skill_artifact.id,
            target_version=skill_artifact.version.raw,
            kind="workflow-skill",
        )
        all_resolutions.append(skill_resolution)
        knowledge = _resolve_knowledge(skill_artifact.ir, catalog)
        all_resolutions.extend(knowledge)
        plan_steps.append(
            PlanStep(
                id=step.id,
                manifest_index=manifest_index[step.id],
                skill_id=skill_artifact.id,
                skill_version=skill_artifact.version.raw,
                depends_on=step.depends_on,
                input_mapping=MappingProxyType(dict(step.input_mapping)),
                on_error=step.on_error,
                max_attempts=step.retry.max_attempts if step.retry else 1,
                knowledge=knowledge,
                timeout_seconds=skill_artifact.ir.constraints.timeout_seconds,
            )
        )

    return ExecutionPlan(
        execution_id=context.execution_id,
        workflow_id=workflow.metadata.id,
        workflow_version=workflow.metadata.version.raw,
        context=context,
        steps=tuple(plan_steps),
        batches=batches,
        outputs=MappingProxyType(
            {name: output.source for name, output in workflow.outputs.items()}
        ),
        resolutions=tuple(all_resolutions),
    )


def _resolve_knowledge(
    skill: SkillIR, catalog: ArtifactCatalog
) -> tuple[DependencyResolution, ...]:
    resolutions: list[DependencyResolution] = []
    for reference in skill.dependencies.knowledge:
        try:
            artifact = catalog.resolve(reference.id, reference.version)
        except LookupError as error:
            if not reference.required:
                continue
            raise PlanningError("ASF-RUNTIME-PLAN-004", str(error)) from error
        if not isinstance(artifact.ir, KnowledgeIR):
            raise PlanningError(
                "ASF-RUNTIME-PLAN-004",
                f"'{reference.id}' does not resolve to Knowledge.",
            )
        resolutions.append(
            DependencyResolution(
                source_id=skill.metadata.id,
                target_id=artifact.id,
                target_version=artifact.version.raw,
                kind="skill-knowledge",
            )
        )
    return tuple(resolutions)


def _validate_context_inputs(
    context: ExecutionContext, workflow: WorkflowIR
) -> None:
    unknown = sorted(set(context.inputs) - set(workflow.inputs))
    if unknown:
        raise PlanningError(
            "ASF-RUNTIME-PLAN-002",
            f"Workflow inputs contain undeclared fields: {unknown}.",
        )
    missing = sorted(
        name
        for name, field in workflow.inputs.items()
        if field.required and name not in context.inputs
    )
    if missing:
        raise PlanningError(
            "ASF-RUNTIME-PLAN-002",
            f"Workflow required inputs are missing: {missing}.",
        )
    for name, value in context.inputs.items():
        field = workflow.inputs[name]
        if not _value_matches_type(value, field):
            raise PlanningError(
                "ASF-RUNTIME-PLAN-002",
                f"Workflow input '{name}' does not match declared type '{field.type}'.",
            )


def _value_matches_type(value: Any, field: FieldIR) -> bool:
    expected = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": tuple,
        "object": dict,
    }[field.type]
    if field.type in ("number", "integer") and isinstance(value, bool):
        return False
    if field.type == "object":
        from collections.abc import Mapping

        return isinstance(value, Mapping)
    return isinstance(value, expected)


def _topological_order(
    workflow: WorkflowIR,
) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    index = {step.id: position for position, step in enumerate(workflow.steps)}
    indegree = {step.id: len(step.depends_on) for step in workflow.steps}
    dependents: dict[str, list[str]] = defaultdict(list)
    for step in workflow.steps:
        for dependency in step.depends_on:
            dependents[dependency].append(step.id)
    for entries in dependents.values():
        entries.sort(key=index.__getitem__)

    ready = sorted(
        (step_id for step_id, degree in indegree.items() if degree == 0),
        key=index.__getitem__,
    )
    ordered: list[str] = []
    batches: list[tuple[str, ...]] = []
    while ready:
        batch = tuple(ready)
        batches.append(batch)
        ordered.extend(batch)
        next_ready: list[str] = []
        for step_id in batch:
            for dependent in dependents[step_id]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_ready.append(dependent)
        ready = sorted(next_ready, key=index.__getitem__)
    if len(ordered) != len(workflow.steps):
        raise PlanningError(
            "ASF-RUNTIME-PLAN-005",
            f"Workflow '{workflow.metadata.id}' cannot be topologically planned.",
        )
    return tuple(ordered), tuple(batches)
