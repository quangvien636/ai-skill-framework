"""Narrow runner for the canonical Research -> Content -> Review workflow."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from asf_runtime.binding import (
    RuntimeBinding,
    resolve_skill_runtime_binding,
    to_binding_ir,
)
from asf_runtime.catalog import ArtifactCatalog
from asf_runtime.models import ExecutionContext, ExecutionPlan, PlanStep
from asf_runtime.planner import plan_workflow
from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.skill_ir import SkillIR
from asf_validator.workflow_ir import WorkflowIR

from .executor import OllamaStepExecutor
from .models import ExecutionDiagnostic, ExecutionReport, StepExecutionResult
from .topic_relevance import evaluate_topic_relevance
from .topic_relevance_config import load_topic_relevance_config

CANONICAL_WORKFLOW_ID = "workflow:research-content-review"
_SAFE_EXECUTION_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
_TOPIC_RELEVANCE_CONFIG = load_topic_relevance_config()


def run_content_workflow(
    context: ExecutionContext,
    catalog: ArtifactCatalog,
    mode: str = "dry-run",
    executor: OllamaStepExecutor | None = None,
    compiled: Mapping[str, Any] | None = None,
    report_root: Path | None = None,
) -> ExecutionReport:
    """Compile or sequentially execute only ASF's canonical content workflow."""
    started = time.perf_counter()
    if context.workflow_id != CANONICAL_WORKFLOW_ID:
        raise ValueError(
            f"Ollama execution supports only '{CANONICAL_WORKFLOW_ID}'."
        )
    if mode not in ("dry-run", "live-local"):
        raise ValueError("mode must be 'dry-run' or 'live-local'.")
    if mode == "live-local" and executor is None:
        raise ValueError("live-local mode requires an OllamaStepExecutor.")
    if not _SAFE_EXECUTION_ID.fullmatch(context.execution_id):
        raise ValueError("execution_id contains unsafe path characters.")

    plan = plan_workflow(context, catalog)
    workflow_artifact = catalog.exact(plan.workflow_id, plan.workflow_version)
    if not isinstance(workflow_artifact.ir, WorkflowIR):
        raise RuntimeError("Canonical workflow did not resolve to Workflow IR.")
    workflow = workflow_artifact.ir
    bindings = _bindings(plan, catalog)
    report_directory = (
        str((report_root / context.execution_id).resolve())
        if report_root is not None
        else None
    )

    if mode == "dry-run":
        steps = tuple(
            StepExecutionResult(
                step_id=step.id,
                skill_id=step.skill_id,
                runtime_binding=to_binding_ir(bindings[step.id], ()).as_dict(),
                input_artifact=_dry_run_input(step, context, workflow),
                output_artifact=None,
                diagnostics=(),
                status="compiled",
                error_message=None,
                duration_ms=0,
            )
            for step in plan.steps
        )
        report = ExecutionReport(
            report_version="1.0",
            execution_id=context.execution_id,
            workflow_id=plan.workflow_id,
            workflow_version=plan.workflow_version,
            mode=mode,
            status="compiled",
            model=None,
            endpoint=None,
            compiled=dict(compiled or {}),
            steps=steps,
            diagnostics=(),
            final_artifact=None,
            duration_ms=_elapsed_ms(started),
            report_directory=report_directory,
        )
        _persist(report, report_root)
        return report

    assert executor is not None
    outputs_by_step: dict[str, Mapping[str, Any]] = {}
    results: list[StepExecutionResult] = []
    report_diagnostics: list[ExecutionDiagnostic] = []
    topic = context.inputs.get("topic")
    topic = topic if isinstance(topic, str) else None

    for step in plan.steps:
        skill_artifact = catalog.exact(step.skill_id, step.skill_version)
        if not isinstance(skill_artifact.ir, SkillIR):
            raise RuntimeError(f"'{step.skill_id}' did not resolve to Skill IR.")
        skill = skill_artifact.ir
        try:
            step_input = _resolve_step_input(
                step, context, workflow, outputs_by_step
            )
        except ArtifactBoundaryError as error:
            diagnostic = ExecutionDiagnostic(
                error.code,
                "error",
                str(error),
                step.id,
                error.artifact,
            )
            result = StepExecutionResult(
                step_id=step.id,
                skill_id=step.skill_id,
                runtime_binding=to_binding_ir(bindings[step.id], ()).as_dict(),
                input_artifact={},
                output_artifact=None,
                diagnostics=(diagnostic,),
                status="failed",
                error_message=str(error),
                duration_ms=0,
            )
            results.append(result)
            report_diagnostics.append(diagnostic)
            break

        result = executor.execute(
            step,
            skill,
            bindings[step.id],
            step_input,
            _knowledge(step, catalog),
        )
        results.append(result)
        report_diagnostics.extend(result.diagnostics)
        if result.status != "succeeded" or result.output_artifact is None:
            break

        validation = _validate_skill_output(
            step, skill, result.output_artifact, topic
        )
        if validation:
            report_diagnostics.extend(validation)
            results[-1] = StepExecutionResult(
                step_id=result.step_id,
                skill_id=result.skill_id,
                runtime_binding=result.runtime_binding,
                input_artifact=result.input_artifact,
                output_artifact=result.output_artifact,
                diagnostics=result.diagnostics + tuple(validation),
                status="failed",
                error_message=validation[0].message,
                duration_ms=result.duration_ms,
            )
            break
        outputs_by_step[step.id] = result.output_artifact

    final_artifact: Mapping[str, Any] | None = None
    status = "failed"
    if len(outputs_by_step) == len(plan.steps):
        try:
            final_artifact = _resolve_final_artifact(workflow, outputs_by_step)
            _require_final_reviewed_package(final_artifact)
            status = "succeeded"
        except ArtifactBoundaryError as error:
            report_diagnostics.append(
                ExecutionDiagnostic(
                    error.code,
                    "error",
                    str(error),
                    artifact=error.artifact,
                )
            )

    report = ExecutionReport(
        report_version="1.0",
        execution_id=context.execution_id,
        workflow_id=plan.workflow_id,
        workflow_version=plan.workflow_version,
        mode=mode,
        status=status,
        model=executor.model_override,
        endpoint=executor.endpoint,
        compiled=dict(compiled or {}),
        steps=tuple(results),
        diagnostics=tuple(report_diagnostics),
        final_artifact=final_artifact,
        duration_ms=_elapsed_ms(started),
        report_directory=report_directory,
    )
    _persist(report, report_root)
    return report


class ArtifactBoundaryError(ValueError):
    def __init__(self, code: str, artifact: str, message: str):
        super().__init__(message)
        self.code = code
        self.artifact = artifact


def _bindings(
    plan: ExecutionPlan, catalog: ArtifactCatalog
) -> dict[str, RuntimeBinding]:
    bindings: dict[str, RuntimeBinding] = {}
    for step in plan.steps:
        skill_artifact = catalog.exact(step.skill_id, step.skill_version)
        if not isinstance(skill_artifact.ir, SkillIR):
            raise RuntimeError(f"'{step.skill_id}' did not resolve to Skill IR.")
        binding, diagnostics = resolve_skill_runtime_binding(
            skill_artifact.ir, catalog
        )
        if binding is None or any(item.is_error() for item in diagnostics):
            detail = diagnostics[0].message if diagnostics else "binding missing"
            raise RuntimeError(f"Step '{step.id}' RuntimeBinding failed: {detail}")
        bindings[step.id] = binding
    return bindings


def _knowledge(
    step: PlanStep, catalog: ArtifactCatalog
) -> tuple[KnowledgeIR, ...]:
    resolved: list[KnowledgeIR] = []
    for item in step.knowledge:
        artifact = catalog.exact(item.target_id, item.target_version)
        if not isinstance(artifact.ir, KnowledgeIR):
            raise RuntimeError(
                f"'{item.target_id}' did not resolve to Knowledge IR."
            )
        resolved.append(artifact.ir)
    return tuple(resolved)


def _resolve_step_input(
    step: PlanStep,
    context: ExecutionContext,
    workflow: WorkflowIR,
    outputs_by_step: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    prefix = "workflow.inputs."
    for target, source in step.input_mapping.items():
        if source.startswith(prefix):
            name = source.removeprefix(prefix)
            if name in context.inputs:
                resolved[target] = context.inputs[name]
            else:
                resolved[target] = workflow.inputs[name].default
            continue

        parts = source.split(".")
        source_step, output_name = parts[1], parts[3]
        step_output = outputs_by_step.get(source_step)
        if step_output is None or output_name not in step_output:
            raise ArtifactBoundaryError(
                "ASF-EXEC-BOUNDARY-001",
                output_name,
                (
                    f"Required artifact '{output_name}' from step "
                    f"'{source_step}' does not exist before step '{step.id}'."
                ),
            )
        resolved[target] = step_output[output_name]
    return resolved


def _dry_run_input(
    step: PlanStep,
    context: ExecutionContext,
    workflow: WorkflowIR,
) -> dict[str, Any]:
    """Resolve caller-owned inputs while retaining unavailable step sources."""
    resolved: dict[str, Any] = {}
    prefix = "workflow.inputs."
    for target, source in step.input_mapping.items():
        if source.startswith(prefix):
            name = source.removeprefix(prefix)
            resolved[target] = (
                context.inputs[name]
                if name in context.inputs
                else workflow.inputs[name].default
            )
        else:
            resolved[target] = source
    return resolved


def _validate_skill_output(
    step: PlanStep,
    skill: SkillIR,
    output: Mapping[str, Any],
    topic: str | None = None,
) -> list[ExecutionDiagnostic]:
    diagnostics: list[ExecutionDiagnostic] = []
    for name, field in skill.outputs.items():
        if field.required and name not in output:
            diagnostics.append(
                ExecutionDiagnostic(
                    "ASF-EXEC-BOUNDARY-002",
                    "error",
                    f"Step '{step.id}' output is missing required artifact '{name}'.",
                    step.id,
                    name,
                )
            )
            continue
        if name not in output:
            continue
        value = output[name]
        if not _matches_type(value, field.type):
            diagnostics.append(
                ExecutionDiagnostic(
                    "ASF-EXEC-BOUNDARY-003",
                    "error",
                    (
                        f"Artifact '{name}' from step '{step.id}' must be "
                        f"type '{field.type}'."
                    ),
                    step.id,
                    name,
                )
            )
            continue
        if isinstance(value, Mapping):
            missing = sorted(
                set(field.constraints.get("required", ())) - set(value)
            )
            if missing:
                diagnostics.append(
                    ExecutionDiagnostic(
                        "ASF-EXEC-BOUNDARY-004",
                        "error",
                        f"Artifact '{name}' is missing required fields: {missing}.",
                        step.id,
                        name,
                    )
                )
    diagnostics.extend(
        _validate_canonical_content_boundaries(step, skill, output, topic)
    )
    return diagnostics


_MIN_RELEVANT_FINDINGS = 5


def _validate_canonical_content_boundaries(
    step: PlanStep,
    skill: SkillIR,
    output: Mapping[str, Any],
    topic: str | None = None,
) -> list[ExecutionDiagnostic]:
    diagnostics: list[ExecutionDiagnostic] = []
    if skill.metadata.id == "skill:research":
        brief = output.get("research-brief")
        if not isinstance(brief, Mapping):
            return diagnostics
        findings = brief.get("findings") if isinstance(brief, Mapping) else None
        finding_texts = (
            [_finding_text(item) for item in findings]
            if isinstance(findings, (list, tuple))
            else []
        )
        relevant_findings = [text for text in finding_texts if text.strip()]
        if len(relevant_findings) < _MIN_RELEVANT_FINDINGS:
            diagnostics.append(
                _boundary_diagnostic(
                    "ASF-EXEC-BOUNDARY-010",
                    step,
                    "research-brief.findings",
                    (
                        "Research brief must contain at least "
                        f"{_MIN_RELEVANT_FINDINGS} concrete, non-empty findings "
                        f"(found {len(relevant_findings)})."
                    ),
                )
            )
    elif skill.metadata.id == "skill:content-creation":
        package = output.get("content-package")
        if not isinstance(package, Mapping):
            return diagnostics
        primary = (
            package.get("primary-content")
            if isinstance(package, Mapping)
            else None
        )
        if not isinstance(primary, Mapping) or not primary:
            diagnostics.append(
                _boundary_diagnostic(
                    "ASF-EXEC-BOUNDARY-007",
                    step,
                    "content-package.primary-content",
                    "Content package primary-content must be a non-empty object.",
                )
            )
        elif package.get("content-type") == "short-video-script":
            required = (
                "title",
                "script",
                "scenes",
                "voice-over-text",
                "on-screen-text",
                "call-to-action",
                "hashtags",
            )
            empty = [key for key in required if not primary.get(key)]
            if empty:
                diagnostics.append(
                    _boundary_diagnostic(
                        "ASF-EXEC-BOUNDARY-007",
                        step,
                        "content-package.primary-content",
                        f"Short-video primary-content has empty fields: {empty}.",
                    )
                )
            script = primary.get("script")
            voice_over = primary.get("voice-over-text")
            scenes = primary.get("scenes")
            on_screen = primary.get("on-screen-text")
            hashtags = primary.get("hashtags")
            incomplete = []
            if not isinstance(script, str) or len(script.strip()) < 400:
                incomplete.append("script<400-chars")
            if not isinstance(voice_over, str) or len(voice_over.strip()) < 300:
                incomplete.append("voice-over-text<300-chars")
            if not isinstance(scenes, (list, tuple)) or len(scenes) < 5:
                incomplete.append("scenes<5")
            if not _non_empty_strings(on_screen, 5):
                incomplete.append("on-screen-text<5")
            if not _non_empty_strings(hashtags, 3):
                incomplete.append("hashtags<3")
            if incomplete:
                diagnostics.append(
                    _boundary_diagnostic(
                        "ASF-EXEC-BOUNDARY-011",
                        step,
                        "content-package.primary-content",
                        f"Short-video package is incomplete: {incomplete}.",
                    )
                )
        call_to_action = (
            package.get("call-to-action")
            if isinstance(package, Mapping)
            else None
        )
        if not isinstance(call_to_action, str) or not call_to_action.strip():
            diagnostics.append(
                _boundary_diagnostic(
                    "ASF-EXEC-BOUNDARY-008",
                    step,
                    "content-package.call-to-action",
                    "Content package call-to-action must be non-empty.",
                )
            )
    elif skill.metadata.id == "skill:review-quality":
        reviewed = output.get("reviewed-package")
        if not isinstance(reviewed, Mapping):
            return diagnostics
        draft = reviewed.get("draft") if isinstance(reviewed, Mapping) else None
        if not isinstance(draft, Mapping) or not draft:
            diagnostics.append(
                _boundary_diagnostic(
                    "ASF-EXEC-BOUNDARY-009",
                    step,
                    "reviewed-package.draft",
                    "Reviewed Content Package draft must be a non-empty object.",
                )
            )
        recommendation = output.get("review-report", {}).get(
            "recommendation"
        ) if isinstance(output.get("review-report"), Mapping) else None
        status = reviewed.get("status")
        allowed = {"approve", "revise", "reject"}
        if (
            not isinstance(recommendation, str)
            or recommendation.lower() not in allowed
            or not isinstance(status, str)
            or status.lower() not in allowed
        ):
            diagnostics.append(
                _boundary_diagnostic(
                    "ASF-EXEC-BOUNDARY-012",
                    step,
                    "reviewed-package.status",
                    "Review recommendation and status must be approve, revise, or reject.",
                )
            )
    if topic:
        diagnostics.extend(
            _validate_topic_relevance(step, skill, output, topic)
        )
    return diagnostics


def _finding_text(finding: Any) -> str:
    if isinstance(finding, str):
        return finding
    if isinstance(finding, Mapping):
        parts = [
            str(finding.get(key, ""))
            for key in ("technology", "why-it-matters", "practical-risk", "claim")
        ]
        return " ".join(part for part in parts if part)
    return str(finding) if finding else ""


def _content_package_text(package: Any) -> str:
    if not isinstance(package, Mapping):
        return ""
    parts = [str(package.get("hook", "")), str(package.get("call-to-action", ""))]
    primary = package.get("primary-content")
    if isinstance(primary, Mapping):
        parts.extend(
            str(primary.get(key, ""))
            for key in ("title", "script", "voice-over-text", "call-to-action")
        )
    return " ".join(parts)


def _semantic_text(skill_id: str, output: Mapping[str, Any]) -> str:
    if skill_id == "skill:research":
        brief = output.get("research-brief")
        if not isinstance(brief, Mapping):
            return ""
        findings = brief.get("findings")
        texts = (
            [_finding_text(item) for item in findings]
            if isinstance(findings, (list, tuple))
            else []
        )
        texts.append(str(brief.get("objective", "")))
        texts.append(str(brief.get("scope", "")))
        return " ".join(texts)
    if skill_id == "skill:content-creation":
        return _content_package_text(output.get("content-package"))
    if skill_id == "skill:review-quality":
        reviewed = output.get("reviewed-package")
        draft = reviewed.get("draft") if isinstance(reviewed, Mapping) else None
        return _content_package_text(draft)
    return ""


def _validate_topic_relevance(
    step: PlanStep,
    skill: SkillIR,
    output: Mapping[str, Any],
    topic: str,
) -> list[ExecutionDiagnostic]:
    text = _semantic_text(skill.metadata.id, output)
    if not text.strip():
        return []
    result = evaluate_topic_relevance(topic, text, config=_TOPIC_RELEVANCE_CONFIG)
    if result.passed:
        return []
    return [
        _boundary_diagnostic(
            "ASF-EXEC-BOUNDARY-013",
            step,
            "semantic-relevance",
            f"Output for step '{step.id}' {result.reason}.",
        )
    ]


def _boundary_diagnostic(
    code: str,
    step: PlanStep,
    artifact: str,
    message: str,
) -> ExecutionDiagnostic:
    return ExecutionDiagnostic(
        code,
        "error",
        message,
        step.id,
        artifact,
    )


def _non_empty_strings(value: Any, minimum: int) -> bool:
    return (
        isinstance(value, (list, tuple))
        and len(value) >= minimum
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _resolve_final_artifact(
    workflow: WorkflowIR,
    outputs_by_step: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, output in workflow.outputs.items():
        parts = output.source.split(".")
        source_step, output_name = parts[1], parts[3]
        step_output = outputs_by_step.get(source_step)
        if step_output is None or output_name not in step_output:
            raise ArtifactBoundaryError(
                "ASF-EXEC-BOUNDARY-005",
                name,
                f"Final workflow output '{name}' cannot be resolved.",
            )
        result[name] = step_output[output_name]
    return result


def _require_final_reviewed_package(final_artifact: Mapping[str, Any]) -> None:
    value = final_artifact.get("reviewed-content-package")
    if not isinstance(value, Mapping):
        raise ArtifactBoundaryError(
            "ASF-EXEC-BOUNDARY-006",
            "reviewed-content-package",
            "Final Reviewed Content Package is missing or malformed.",
        )


def _matches_type(value: Any, field_type: str) -> bool:
    expected = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": (list, tuple),
        "object": Mapping,
    }[field_type]
    if field_type in ("number", "integer") and isinstance(value, bool):
        return False
    return isinstance(value, expected)


def _persist(report: ExecutionReport, report_root: Path | None) -> None:
    if report_root is None:
        return
    directory = (report_root / report.execution_id).resolve()
    root = report_root.resolve()
    if root != directory and root not in directory.parents:
        raise ValueError("report directory escapes the configured report root.")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "execution-report.json").write_text(
        json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    for step in report.steps:
        (directory / f"{step.step_id}.json").write_text(
            json.dumps(step.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    (directory / "report.txt").write_text(
        _human_report(report), encoding="utf-8"
    )


def _human_report(report: ExecutionReport) -> str:
    lines = [
        f"ASF execution: {report.status.upper()}",
        f"Execution: {report.execution_id}",
        f"Workflow: {report.workflow_id}@{report.workflow_version}",
        f"Mode: {report.mode}",
        f"Duration: {report.duration_ms} ms",
    ]
    if report.steps:
        topic = report.steps[0].input_artifact.get("topic")
        if isinstance(topic, str):
            lines.append(f"Topic: {topic}")
    for step in report.steps:
        lines.append(
            f"- {step.step_id}: {step.status} ({step.duration_ms} ms)"
        )
        if step.error_message:
            lines.append(f"  Error: {step.error_message}")
    lines.append(
        "Final artifact: "
        + (
            "reviewed-content-package"
            if report.final_artifact is not None
            else "not produced"
        )
    )
    return "\n".join(lines) + "\n"


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.perf_counter() - started) * 1000))
