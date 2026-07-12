"""Semantic validation over successfully built IR artifacts.

This layer does not parse source, discover files, or rebuild dependency graph
facts. It checks Evaluation/Reflection contracts embedded in Skills and
Workflow topology, routing, and mappings using resolved Skill IR when present.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict, deque

from .diagnostics import (
    Diagnostic,
    SEMANTIC_DUPLICATE_METRIC_NAME,
    SEMANTIC_INVALID_METRIC_WEIGHT_TOTAL,
    SEMANTIC_REFLECTABLE_GATE_UNKNOWN,
    SEMANTIC_REFLECTION_ROUTING_INCONSISTENT,
    SEMANTIC_RUNTIME_FALLBACK_CHAIN_INVALID,
    SEMANTIC_RUNTIME_MODEL_MISSING,
    SEMANTIC_RUNTIME_PUBLISHER_INVALID,
    SEMANTIC_RUNTIME_RETRIEVER_MISSING,
    SEMANTIC_RUNTIME_RETRY_POLICY_INCOMPATIBLE,
    SEMANTIC_RUNTIME_TIMEOUT_PROFILE_INVALID,
    SEMANTIC_RUNTIME_TOOLS_MISSING,
    SEMANTIC_WORKFLOW_MAPPING_SOURCE_INVALID,
    SEMANTIC_WORKFLOW_MAPPING_TARGET_INVALID,
    SEMANTIC_WORKFLOW_MAPPING_TYPE_MISMATCH,
    SEMANTIC_WORKFLOW_ROUTING_INCONSISTENT,
    SEMANTIC_WORKFLOW_STEP_UNREACHABLE,
    Severity,
)
from .pipeline import AdapterResult
from .loader import attach_source_positions
from .runtime_ir import RuntimeIR
from .skill_ir import FieldIR, SkillIR
from .workflow_ir import WorkflowIR, WorkflowStepIR

_WORKFLOW_INPUT_RE = re.compile(r"^workflow\.inputs\.(?P<input>[a-z][a-z0-9-]*)$")
_STEP_OUTPUT_RE = re.compile(
    r"^steps\.(?P<step>[a-z][a-z0-9-]*)\.outputs\.(?P<output>[a-z][a-z0-9-]*)$"
)


def validate_semantics(results: list[AdapterResult]) -> list[Diagnostic]:
    """Return deterministic semantic diagnostics for valid IR results."""
    diagnostics: list[Diagnostic] = []
    skills: dict[str, SkillIR] = {}
    workflows: list[tuple[str, WorkflowIR]] = []

    for result in results:
        if not result.ok:
            continue
        if isinstance(result.ir, SkillIR):
            skills.setdefault(result.ir.metadata.id, result.ir)
            diagnostics.extend(_validate_skill(result.artifact, result.ir))
        elif isinstance(result.ir, WorkflowIR):
            workflows.append((result.artifact, result.ir))
        elif isinstance(result.ir, RuntimeIR):
            diagnostics.extend(_validate_runtime(result.artifact, result.ir))

    for artifact, workflow in workflows:
        diagnostics.extend(_validate_workflow(artifact, workflow, skills))

    positions_by_artifact = {
        result.artifact: result.source_positions
        for result in results
        if result.source_positions
    }
    enriched: list[Diagnostic] = []
    for diagnostic in diagnostics:
        enriched.extend(
            attach_source_positions(
                [diagnostic], positions_by_artifact.get(diagnostic.artifact, {})
            )
        )
    return enriched


def _validate_skill(artifact: str, skill: SkillIR) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    names: set[str] = set()
    for index, metric in enumerate(skill.evaluation.metrics):
        if metric.name in names:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_DUPLICATE_METRIC_NAME,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"evaluation.metrics.{index}.name",
                    message=f"Evaluation metric name '{metric.name}' is duplicated.",
                    suggestion="Give every evaluation metric a unique name.",
                )
            )
        names.add(metric.name)

    weight_total = math.fsum(metric.weight for metric in skill.evaluation.metrics)
    if not math.isclose(weight_total, 1.0, rel_tol=0.0, abs_tol=1e-9):
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_INVALID_METRIC_WEIGHT_TOTAL,
                severity=Severity.ERROR,
                artifact=artifact,
                location="evaluation.metrics",
                message=f"Evaluation metric weights sum to {weight_total:g}; expected 1.0.",
                suggestion="Adjust metric weights so their total is exactly 1.0.",
            )
        )

    routes_to_reflection = skill.evaluation.on_failure == "reflect"
    if routes_to_reflection != skill.reflection.enabled:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_REFLECTION_ROUTING_INCONSISTENT,
                severity=Severity.ERROR,
                artifact=artifact,
                location="evaluation.on_failure",
                message=(
                    "Evaluation on_failure and reflection.enabled disagree: "
                    f"on_failure='{skill.evaluation.on_failure}', "
                    f"reflection.enabled={str(skill.reflection.enabled).lower()}."
                ),
                suggestion=(
                    "Use on_failure 'reflect' with enabled reflection, or disable "
                    "reflection when failure routes elsewhere."
                ),
            )
        )

    hard_gates = set(skill.evaluation.acceptance.hard_gates)
    for gate in skill.reflection.reflectable_hard_gates:
        if gate not in hard_gates:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_REFLECTABLE_GATE_UNKNOWN,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location="reflection.reflectable_hard_gates",
                    message=f"Reflectable hard gate '{gate}' is not an acceptance hard gate.",
                    suggestion="Declare the gate in evaluation.acceptance.hard_gates or remove it.",
                )
            )
    return diagnostics


def _validate_runtime(artifact: str, runtime: RuntimeIR) -> list[Diagnostic]:
    """Single-artifact internal consistency for Runtime Contracts (ADR-0014).

    Cross-artifact reference resolution (does a referenced Knowledge/Tool/
    Runtime id actually exist) is the Dependency Graph's job
    (runtime-knowledge/runtime-tool/runtime-runtime edges); this function
    only checks that a section's own `enabled` flag agrees with its
    configured content, and that policy fields agree with each other.
    """
    diagnostics: list[Diagnostic] = []

    if runtime.model.enabled and not runtime.model.model:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_MODEL_MISSING,
                severity=Severity.ERROR,
                artifact=artifact,
                location="model",
                message="model.enabled is true but no model.model is configured.",
                suggestion="Set model.model, or set model.enabled to false.",
            )
        )

    if runtime.retriever.enabled and not runtime.retriever.knowledge:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_RETRIEVER_MISSING,
                severity=Severity.ERROR,
                artifact=artifact,
                location="retriever",
                message="retriever.enabled is true but retriever.knowledge is empty.",
                suggestion="Reference at least one Knowledge document, or set retriever.enabled to false.",
            )
        )

    if runtime.tools.enabled and not runtime.tools.refs:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_TOOLS_MISSING,
                severity=Severity.ERROR,
                artifact=artifact,
                location="tools",
                message="tools.enabled is true but tools.refs is empty.",
                suggestion="Reference at least one Tool, or set tools.enabled to false.",
            )
        )

    if runtime.publisher.enabled and not runtime.publisher.target:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_PUBLISHER_INVALID,
                severity=Severity.ERROR,
                artifact=artifact,
                location="publisher",
                message="publisher.enabled is true but no publisher.target is configured.",
                suggestion="Set publisher.target, or set publisher.enabled to false.",
            )
        )

    if runtime.retry_policy.backoff == "exponential" and runtime.retry_policy.max_attempts < 2:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_RETRY_POLICY_INCOMPATIBLE,
                severity=Severity.ERROR,
                artifact=artifact,
                location="retry_policy",
                message="retry_policy.backoff is 'exponential' but max_attempts < 2.",
                suggestion="Raise max_attempts to at least 2, or use backoff 'none'/'fixed'.",
            )
        )

    if (
        runtime.timeout_policy.on_timeout == "retry"
        and runtime.retry_policy.max_attempts < 2
    ):
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_TIMEOUT_PROFILE_INVALID,
                severity=Severity.ERROR,
                artifact=artifact,
                location="timeout_policy.on_timeout",
                message="timeout_policy.on_timeout is 'retry' but retry_policy.max_attempts < 2.",
                suggestion="Raise retry_policy.max_attempts, or choose a different on_timeout.",
            )
        )
    if (
        runtime.timeout_policy.on_timeout == "fallback"
        and not runtime.fallback_profile.enabled
    ):
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_TIMEOUT_PROFILE_INVALID,
                severity=Severity.ERROR,
                artifact=artifact,
                location="timeout_policy.on_timeout",
                message="timeout_policy.on_timeout is 'fallback' but fallback_profile.enabled is false.",
                suggestion="Enable fallback_profile, or choose a different on_timeout.",
            )
        )

    fallback = runtime.fallback_profile
    if fallback.enabled and fallback.fallback_runtime is None:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_FALLBACK_CHAIN_INVALID,
                severity=Severity.ERROR,
                artifact=artifact,
                location="fallback_profile",
                message="fallback_profile.enabled is true but no fallback_runtime is configured.",
                suggestion="Set fallback_profile.fallback_runtime, or set enabled to false.",
            )
        )
    elif not fallback.enabled and fallback.fallback_runtime is not None:
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_FALLBACK_CHAIN_INVALID,
                severity=Severity.ERROR,
                artifact=artifact,
                location="fallback_profile",
                message="fallback_profile.fallback_runtime is set but enabled is false.",
                suggestion="Set fallback_profile.enabled to true, or remove fallback_runtime.",
            )
        )
    elif (
        fallback.fallback_runtime is not None
        and fallback.fallback_runtime.id == runtime.metadata.id
    ):
        diagnostics.append(
            Diagnostic(
                code=SEMANTIC_RUNTIME_FALLBACK_CHAIN_INVALID,
                severity=Severity.ERROR,
                artifact=artifact,
                location="fallback_profile.fallback_runtime",
                message=f"Runtime '{runtime.metadata.id}' declares itself as its own fallback.",
                suggestion="Reference a different Runtime Contract as the fallback.",
            )
        )

    return diagnostics


def _validate_workflow(
    artifact: str, workflow: WorkflowIR, skills: dict[str, SkillIR]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    step_by_id = {step.id: step for step in workflow.steps}
    ancestors = _ancestor_sets(workflow)

    reachable = _reachable_from_entrypoint(workflow)
    for step in workflow.steps:
        if step.id not in reachable:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_WORKFLOW_STEP_UNREACHABLE,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"steps.{step.id}",
                    message=(
                        f"Step '{step.id}' is not reachable from entrypoint "
                        f"'{workflow.entrypoint}'."
                    ),
                    suggestion="Connect the step to the entrypoint dependency chain or remove it.",
                )
            )

        has_retry = step.retry is not None
        if (step.on_error == "retry") != has_retry:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_WORKFLOW_ROUTING_INCONSISTENT,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"steps.{step.id}.on_error",
                    message=(
                        f"Step '{step.id}' on_error='{step.on_error}' and retry "
                        f"configuration presence ({str(has_retry).lower()}) disagree."
                    ),
                    suggestion="Provide retry only when on_error is 'retry', and require it then.",
                )
            )

        skill = skills.get(step.skill.id)
        if skill is None:
            continue  # Dependency Graph owns missing Skill diagnostics.
        diagnostics.extend(
            _validate_step_mapping(
                artifact, workflow, step, skill, step_by_id, skills, ancestors[step.id]
            )
        )

    for output_name, output in workflow.outputs.items():
        match = _STEP_OUTPUT_RE.fullmatch(output.source)
        if match is None:
            continue  # Schema/IR owns syntax.
        source_step = step_by_id.get(match.group("step"))
        source_skill = skills.get(source_step.skill.id) if source_step else None
        source_field = source_skill.outputs.get(match.group("output")) if source_skill else None
        location = f"outputs.{output_name}.from"
        if source_field is None:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_WORKFLOW_MAPPING_SOURCE_INVALID,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=location,
                    message=f"Workflow output source '{output.source}' does not resolve.",
                    suggestion="Reference an output declared by the source step's Skill.",
                )
            )
        elif source_field.type != output.type:
            diagnostics.append(_type_mismatch(artifact, location, source_field.type, output.type))
    return diagnostics


def _validate_step_mapping(
    artifact: str,
    workflow: WorkflowIR,
    step: WorkflowStepIR,
    skill: SkillIR,
    step_by_id: dict[str, WorkflowStepIR],
    skills: dict[str, SkillIR],
    ancestors: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    mapped = set(step.input_mapping)
    for input_name, field in skill.inputs.items():
        if field.required and input_name not in mapped:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_WORKFLOW_MAPPING_TARGET_INVALID,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=f"steps.{step.id}.input_mapping",
                    message=(
                        f"Required Skill input '{input_name}' is not mapped for step "
                        f"'{step.id}'."
                    ),
                    suggestion="Map every required input declared by the referenced Skill.",
                )
            )

    for input_name, source in step.input_mapping.items():
        location = f"steps.{step.id}.input_mapping.{input_name}"
        target = skill.inputs.get(input_name)
        if target is None:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_WORKFLOW_MAPPING_TARGET_INVALID,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=location,
                    message=f"Referenced Skill '{skill.metadata.id}' has no input '{input_name}'.",
                    suggestion="Remove the mapping or use an input declared by the Skill.",
                )
            )
            continue

        source_field = _resolve_mapping_source(
            source, workflow, step_by_id, skills, ancestors
        )
        if source_field is None:
            diagnostics.append(
                Diagnostic(
                    code=SEMANTIC_WORKFLOW_MAPPING_SOURCE_INVALID,
                    severity=Severity.ERROR,
                    artifact=artifact,
                    location=location,
                    message=(
                        f"Mapping source '{source}' is unavailable, undeclared, or "
                        f"not an ancestor of step '{step.id}'."
                    ),
                    suggestion="Reference a Workflow input or an output of an ancestor step.",
                )
            )
        elif source_field.type != target.type:
            diagnostics.append(_type_mismatch(artifact, location, source_field.type, target.type))
    return diagnostics


def _resolve_mapping_source(
    source: str,
    workflow: WorkflowIR,
    step_by_id: dict[str, WorkflowStepIR],
    skills: dict[str, SkillIR],
    ancestors: set[str],
) -> FieldIR | None:
    workflow_match = _WORKFLOW_INPUT_RE.fullmatch(source)
    if workflow_match:
        return workflow.inputs.get(workflow_match.group("input"))

    step_match = _STEP_OUTPUT_RE.fullmatch(source)
    if step_match is None or step_match.group("step") not in ancestors:
        return None
    source_step = step_by_id.get(step_match.group("step"))
    source_skill = skills.get(source_step.skill.id) if source_step else None
    return source_skill.outputs.get(step_match.group("output")) if source_skill else None


def _ancestor_sets(workflow: WorkflowIR) -> dict[str, set[str]]:
    memo: dict[str, set[str]] = {}

    def visit(step_id: str) -> set[str]:
        if step_id not in memo:
            result: set[str] = set()
            for dependency in workflow.graph[step_id]:
                result.add(dependency)
                result.update(visit(dependency))
            memo[step_id] = result
        return memo[step_id]

    for step in workflow.steps:
        visit(step.id)
    return memo


def _reachable_from_entrypoint(workflow: WorkflowIR) -> set[str]:
    dependents: dict[str, list[str]] = defaultdict(list)
    for step, dependencies in workflow.graph.items():
        for dependency in dependencies:
            dependents[dependency].append(step)
    reachable = {workflow.entrypoint}
    queue = deque([workflow.entrypoint])
    while queue:
        for dependent in dependents[queue.popleft()]:
            if dependent not in reachable:
                reachable.add(dependent)
                queue.append(dependent)
    return reachable


def _type_mismatch(
    artifact: str, location: str, source_type: str, target_type: str
) -> Diagnostic:
    return Diagnostic(
        code=SEMANTIC_WORKFLOW_MAPPING_TYPE_MISMATCH,
        severity=Severity.ERROR,
        artifact=artifact,
        location=location,
        message=f"Mapping type '{source_type}' is incompatible with target type '{target_type}'.",
        suggestion="Map fields with identical declared types.",
    )
