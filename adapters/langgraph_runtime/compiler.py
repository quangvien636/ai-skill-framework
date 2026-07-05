"""Compiles a validated ASF ExecutionPlan into a LangGraph StateGraph.

Implements the PlanCompiler seam (asf_runtime.interfaces.PlanCompiler) from
docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md. This module performs
compilation only: it never calls .invoke()/.stream()/.ainvoke() on the graph
it builds, and the per-step node it registers has no Skill-invocation logic
of its own -- that behavior is always a caller-supplied ``step_executor``,
mirroring how adapters/mcp_tools binds a caller-supplied handler rather than
inventing tool behavior. Retries, timeouts, and state persistence during an
actual run are LangGraph's responsibility once compiled, per ADR-0013.
"""

from __future__ import annotations

from typing import Annotated, Any, Awaitable, Callable, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy

from asf_runtime.models import ExecutionPlan, PlanStep

PlanState = dict[str, Any]
StepExecutor = Callable[[PlanStep, PlanState], Awaitable[PlanState]]


def _merge_step_outputs(current: PlanState, update: PlanState) -> PlanState:
    """Reducer for concurrent writes within one parallel batch.

    Plain ``dict`` uses LangGraph's default last-value channel, which
    rejects more than one write per superstep -- exactly what happens when
    two independent steps in the same batch (ADR-0010/ADR-0011 "ready
    batches") write state concurrently. A shallow merge preserves each
    step's contribution instead of raising ``InvalidUpdateError``.
    """
    merged = dict(current)
    merged.update(update)
    return merged


_PlanStateSchema = Annotated[PlanState, _merge_step_outputs]


async def _unbound_step_executor(step: PlanStep, state: PlanState) -> PlanState:
    raise NotImplementedError(
        f"step '{step.id}' (skill '{step.skill_id}') has no bound step_executor. "
        "compile_plan() only produces a compiled graph shape (ADR-0013); pass "
        "step_executor=... to bind real Skill invocation before running it."
    )


def _step_metadata(plan: ExecutionPlan, step: PlanStep, batch_index: int) -> dict[str, Any]:
    """Audit metadata carried on the compiled node, per Priority 1's
    "preserve audit metadata" requirement: enough to trace a running node
    back to the exact plan, batch, and dependency resolutions ASF computed.
    """
    return {
        "execution_id": plan.execution_id,
        "workflow_id": plan.workflow_id,
        "workflow_version": plan.workflow_version,
        "step_id": step.id,
        "manifest_index": step.manifest_index,
        "batch_index": batch_index,
        "skill_id": step.skill_id,
        "skill_version": step.skill_version,
        "on_error": step.on_error,
        "max_attempts": step.max_attempts,
        "timeout_seconds": step.timeout_seconds,
        "knowledge": tuple(
            {"target_id": resolution.target_id, "target_version": resolution.target_version}
            for resolution in step.knowledge
        ),
    }


def _retry_policy_for(step: PlanStep) -> Optional[RetryPolicy]:
    # Only "retry" is a LangGraph RetryPolicy; "fail"/"skip"/"manual-review"
    # are failure boundaries preserved as metadata (see _step_metadata),
    # not translated into retry behavior.
    if step.on_error != "retry":
        return None
    return RetryPolicy(max_attempts=step.max_attempts)


def compile_plan(
    plan: ExecutionPlan,
    step_executor: Optional[StepExecutor] = None,
) -> CompiledStateGraph:
    """Compile ``plan`` into a LangGraph StateGraph. Compile only: this
    function never invokes, streams, or otherwise runs the returned graph.

    Deterministic by construction: nodes and edges are added in
    ``plan.steps`` order, which is itself the deterministic topological/
    manifest-order sequence ``asf_runtime.planner`` already produced.
    """
    executor = step_executor or _unbound_step_executor
    graph: StateGraph = StateGraph(_PlanStateSchema)

    batch_index_by_step = {
        step_id: index for index, batch in enumerate(plan.batches) for step_id in batch
    }
    dependents_of: dict[str, list[str]] = {step.id: [] for step in plan.steps}
    for step in plan.steps:
        for dependency in step.depends_on:
            dependents_of[dependency].append(step.id)

    for step in plan.steps:
        async def _node(state: PlanState, _step: PlanStep = step) -> PlanState:
            return await executor(_step, state)

        graph.add_node(
            step.id,
            _node,
            metadata=_step_metadata(plan, step, batch_index_by_step[step.id]),
            retry_policy=_retry_policy_for(step),
            timeout=step.timeout_seconds,
        )

    for step in plan.steps:
        if step.depends_on:
            for dependency in step.depends_on:
                graph.add_edge(dependency, step.id)
        else:
            graph.add_edge(START, step.id)
        if not dependents_of[step.id]:
            graph.add_edge(step.id, END)

    return graph.compile()
