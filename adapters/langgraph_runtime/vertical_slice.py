"""Compile-only vertical orchestration from ASF artifacts to LangGraph.

This module composes existing Validator, Runtime, Binding, Planner, and
PlanCompiler APIs. It deliberately contains no execution path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langgraph.graph.state import CompiledStateGraph

from asf_runtime.binding import (
    BindingIR,
    RuntimeBinding,
    resolve_skill_runtime_binding,
    to_binding_ir,
    validate_binding_batch,
)
from asf_runtime.catalog import ArtifactCatalog
from asf_runtime.models import ExecutionContext, ExecutionPlan
from asf_runtime.planner import plan_workflow
from asf_validator.runtime_ir import RuntimeIR
from asf_validator.skill_ir import SkillIR

from .compiler import compile_plan


class VerticalSliceError(RuntimeError):
    """A compile-only slice could not be assembled from validated IR."""


@dataclass(frozen=True)
class CompiledVerticalSlice:
    plan: ExecutionPlan
    runtime_bindings: tuple[RuntimeBinding, ...]
    binding_ir: tuple[BindingIR, ...]
    graph: CompiledStateGraph

    def as_dict(self) -> dict[str, Any]:
        """Return a deterministic report suitable for golden snapshots."""
        graph = self.graph.get_graph().to_json()
        return {
            "workflow": {
                "id": self.plan.workflow_id,
                "version": self.plan.workflow_version,
                "execution_id": self.plan.execution_id,
            },
            "bindings": [binding.as_dict() for binding in self.binding_ir],
            "plan": {
                "steps": [
                    {
                        "id": step.id,
                        "manifest_index": step.manifest_index,
                        "skill_id": step.skill_id,
                        "skill_version": step.skill_version,
                        "depends_on": list(step.depends_on),
                        "on_error": step.on_error,
                        "max_attempts": step.max_attempts,
                        "timeout_seconds": step.timeout_seconds,
                        "knowledge": [
                            {
                                "id": item.target_id,
                                "version": item.target_version,
                            }
                            for item in step.knowledge
                        ],
                        "runtime": [
                            {
                                "id": item.target_id,
                                "version": item.target_version,
                                "kind": item.kind,
                            }
                            for item in step.runtime
                        ],
                    }
                    for step in self.plan.steps
                ],
                "batches": [list(batch) for batch in self.plan.batches],
                "outputs": dict(self.plan.outputs),
            },
            "graph": {
                "nodes": graph["nodes"],
                "edges": graph["edges"],
            },
        }


def compile_vertical_slice(
    context: ExecutionContext, catalog: ArtifactCatalog
) -> CompiledVerticalSlice:
    """Resolve, bind, plan, and compile one Workflow without executing it."""
    plan = plan_workflow(context, catalog)
    bindings: list[RuntimeBinding] = []
    binding_ir: list[BindingIR] = []
    runtime_by_step: dict[str, RuntimeIR] = {}

    for step in plan.steps:
        skill_artifact = catalog.exact(step.skill_id, step.skill_version)
        if not isinstance(skill_artifact.ir, SkillIR):
            raise VerticalSliceError(
                f"Plan step '{step.id}' did not resolve to Skill IR."
            )
        binding, diagnostics = resolve_skill_runtime_binding(
            skill_artifact.ir, catalog
        )
        if binding is None:
            detail = diagnostics[0].message if diagnostics else "no runtime declared"
            raise VerticalSliceError(
                f"Plan step '{step.id}' has no RuntimeBinding: {detail}."
            )
        errors = [item for item in diagnostics if item.is_error()]
        if errors:
            raise VerticalSliceError(
                f"Plan step '{step.id}' RuntimeBinding failed: "
                + "; ".join(f"{item.code}: {item.message}" for item in errors)
            )
        runtime_artifact = catalog.exact(
            binding.runtime_id, binding.runtime_version
        )
        if not isinstance(runtime_artifact.ir, RuntimeIR):
            raise VerticalSliceError(
                f"Binding '{binding.runtime_id}' did not resolve to Runtime IR."
            )
        bindings.append(binding)
        binding_ir.append(to_binding_ir(binding, diagnostics))
        runtime_by_step[step.id] = runtime_artifact.ir

    batch_diagnostics = validate_binding_batch(binding_ir)
    batch_errors = [item for item in batch_diagnostics if item.is_error()]
    if batch_errors:
        raise VerticalSliceError(
            "Binding batch failed: "
            + "; ".join(f"{item.code}: {item.message}" for item in batch_errors)
        )

    return CompiledVerticalSlice(
        plan=plan,
        runtime_bindings=tuple(bindings),
        binding_ir=tuple(binding_ir),
        graph=compile_plan(plan, runtime_bindings=runtime_by_step),
    )
