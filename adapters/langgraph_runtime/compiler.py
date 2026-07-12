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

from typing import Annotated, Any, Awaitable, Callable, Mapping, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy

from asf_runtime.binding import RuntimeBinding
from asf_runtime.models import ExecutionPlan, PlanStep
from asf_validator.runtime_ir import RuntimeIR

PlanState = dict[str, Any]
StepExecutor = Callable[[PlanStep, PlanState], Awaitable[PlanState]]
RuntimeBindings = Mapping[str, RuntimeIR]
StepBindings = Mapping[str, RuntimeBinding]


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


def _step_metadata(
    plan: ExecutionPlan,
    step: PlanStep,
    batch_index: int,
    runtime: Optional[RuntimeIR],
) -> dict[str, Any]:
    """Audit metadata carried on the compiled node, per Priority 1's
    "preserve audit metadata" requirement: enough to trace a running node
    back to the exact plan, batch, and dependency resolutions ASF computed.

    When a Runtime Contract is bound (Phase 6, ADR-0014), its
    execution/safety/audit/concurrency profile is attached too -- binding
    only, since none of it triggers any behavior here.
    """
    metadata: dict[str, Any] = {
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
    if runtime is not None:
        metadata.update(
            {
                "runtime_id": runtime.metadata.id,
                "execution_profile": runtime.execution_profile,
                "safety_content_filter": runtime.safety_profile.content_filter,
                "audit_log_level": runtime.audit_profile.log_level,
                "max_parallel_steps": runtime.concurrency_profile.max_parallel_steps,
                "max_parallel_tool_calls": runtime.concurrency_profile.max_parallel_tool_calls,
            }
        )
    return metadata


_BACKOFF_FACTOR = {"none": 1.0, "fixed": 1.0, "exponential": 2.0}
_BACKOFF_INITIAL_INTERVAL = {"none": 0.0, "fixed": 0.5, "exponential": 0.5}


def _retry_policy_for(step: PlanStep, runtime: Optional[RuntimeIR]) -> Optional[RetryPolicy]:
    """A Runtime Contract's own retry_policy (ADR-0014) takes precedence
    over the Skill-level on_error/max_attempts when bound, since it is the
    operational policy meant to govern the binding. Only "retry" (Skill
    level) or max_attempts > 1 (Runtime level) produce a LangGraph
    RetryPolicy; "fail"/"skip"/"manual-review" are failure boundaries
    preserved as metadata (see _step_metadata), not retry behavior.
    """
    if runtime is not None:
        if runtime.retry_policy.max_attempts <= 1:
            return None
        backoff = runtime.retry_policy.backoff
        return RetryPolicy(
            max_attempts=runtime.retry_policy.max_attempts,
            backoff_factor=_BACKOFF_FACTOR[backoff],
            initial_interval=_BACKOFF_INITIAL_INTERVAL[backoff],
        )
    if step.on_error != "retry":
        return None
    return RetryPolicy(max_attempts=step.max_attempts)


def _timeout_for(step: PlanStep, runtime: Optional[RuntimeIR]) -> Optional[int]:
    """A Runtime Contract's own timeout_policy (ADR-0014) takes precedence
    over the resolved Skill's constraints.timeout_seconds when bound."""
    if runtime is not None:
        return runtime.timeout_policy.timeout_seconds
    return step.timeout_seconds


def compile_plan(
    plan: ExecutionPlan,
    step_executor: Optional[StepExecutor] = None,
    runtime_bindings: Optional[RuntimeBindings] = None,
) -> CompiledStateGraph:
    """Compile ``plan`` into a LangGraph StateGraph. Compile only: this
    function never invokes, streams, or otherwise runs the returned graph.

    ``runtime_bindings`` maps a ``PlanStep.id`` to the Runtime Planning-
    resolved ``RuntimeIR`` for that step (from ``PlanStep.runtime`` /
    ``ExecutionPlan.resolutions`` -- this module does not resolve catalog
    references itself). When present for a step, the Runtime Contract's
    own retry/timeout policy and profile metadata are bound onto that
    node instead of (or alongside, for metadata) the Skill-level values.

    Deterministic by construction: nodes and edges are added in
    ``plan.steps`` order, which is itself the deterministic topological/
    manifest-order sequence ``asf_runtime.planner`` already produced.
    """
    executor = step_executor or _unbound_step_executor
    bindings = runtime_bindings or {}
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

        runtime = bindings.get(step.id)
        graph.add_node(
            step.id,
            _node,
            metadata=_step_metadata(plan, step, batch_index_by_step[step.id], runtime),
            retry_policy=_retry_policy_for(step, runtime),
            timeout=_timeout_for(step, runtime),
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


# ── ADR-0015 Phase 4: additive RuntimeBinding-consuming compilation ────────
#
# ``compile_plan`` above (and its private helpers) are untouched. Everything
# below is new and additive: a resolved ``RuntimeBinding`` (Dependency
# Resolver output -- the effective model/retriever/tools/publisher/timeout/
# retry/safety/audit after walking a fallback chain, ADR-0015) carries
# timeout/retry/safety/audit directly, not nested inside a ``RuntimeIR``, so
# these helpers read from a ``RuntimeBinding`` instead of calling
# ``_step_metadata``/``_retry_policy_for``/``_timeout_for``. Note
# ``RuntimeBinding`` does not carry ``execution_profile`` or
# ``concurrency_profile`` (out of Phase 2's scope), so those two metadata
# keys that the ``*_from_runtime`` path adds are not present here.


def _step_metadata_from_binding(
    plan: ExecutionPlan,
    step: PlanStep,
    batch_index: int,
    binding: Optional[RuntimeBinding],
) -> dict[str, Any]:
    """Same audit-metadata shape ``_step_metadata`` produces, sourced from a
    resolved ``RuntimeBinding`` (ADR-0015 Phase 4) instead of a raw
    ``RuntimeIR``."""
    metadata: dict[str, Any] = {
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
    if binding is not None:
        metadata.update(
            {
                "runtime_id": binding.runtime_id,
                "safety_content_filter": binding.safety_profile.content_filter,
                "audit_log_level": binding.audit_profile.log_level,
            }
        )
    return metadata


def _retry_policy_from_binding(
    step: PlanStep, binding: Optional[RuntimeBinding]
) -> Optional[RetryPolicy]:
    """Same precedence rule as ``_retry_policy_for``: a bound RuntimeBinding's
    own retry policy wins over the Skill-level on_error/max_attempts."""
    if binding is not None:
        if binding.retry_policy.max_attempts <= 1:
            return None
        backoff = binding.retry_policy.backoff
        return RetryPolicy(
            max_attempts=binding.retry_policy.max_attempts,
            backoff_factor=_BACKOFF_FACTOR[backoff],
            initial_interval=_BACKOFF_INITIAL_INTERVAL[backoff],
        )
    if step.on_error != "retry":
        return None
    return RetryPolicy(max_attempts=step.max_attempts)


def _timeout_from_binding(step: PlanStep, binding: Optional[RuntimeBinding]) -> Optional[int]:
    """Same precedence rule as ``_timeout_for``: a bound RuntimeBinding's own
    timeout wins over the resolved Skill's constraints.timeout_seconds."""
    if binding is not None:
        return binding.timeout_seconds
    return step.timeout_seconds


def compile_plan_from_binding(
    plan: ExecutionPlan,
    step_executor: Optional[StepExecutor] = None,
    runtime_bindings: Optional[StepBindings] = None,
) -> CompiledStateGraph:
    """Compile ``plan`` into a LangGraph StateGraph using resolved
    ``RuntimeBinding``s (ADR-0015 Phase 4) instead of raw ``RuntimeIR``.
    Compile only: never invokes, streams, or otherwise runs the returned
    graph -- identical guarantee to ``compile_plan``.

    Purely additive alongside ``compile_plan``: same compiled-graph shape,
    same deterministic ``plan.steps``-order node/edge construction, same
    unbound-executor default. ``runtime_bindings`` maps a ``PlanStep.id`` to
    its resolved ``RuntimeBinding`` (from
    ``asf_runtime.binding.resolve_skill_runtime_binding``/
    ``build_runtime_binding`` -- this module does not resolve bindings
    itself, exactly as ``compile_plan`` does not resolve raw ``RuntimeIR``
    references itself).

    ``langgraph_runtime`` has no single-object ``*_from_runtime`` function
    to mirror one-for-one the way the other four adapters do -- its existing
    binding surface is the ``runtime_bindings`` parameter on ``compile_plan``
    itself, since a compiled graph spans many steps, not one descriptor.
    This function is that same shape's additive ``RuntimeBinding`` sibling.
    """
    executor = step_executor or _unbound_step_executor
    bindings = runtime_bindings or {}
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

        binding = bindings.get(step.id)
        graph.add_node(
            step.id,
            _node,
            metadata=_step_metadata_from_binding(plan, step, batch_index_by_step[step.id], binding),
            retry_policy=_retry_policy_from_binding(step, binding),
            timeout=_timeout_from_binding(step, binding),
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
