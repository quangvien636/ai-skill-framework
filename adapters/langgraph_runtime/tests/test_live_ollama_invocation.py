"""Proves ADR-0015 Phase 4 composes into one real, invoked LangGraph run
through a real local Ollama call -- PROJECT_TRACKER.md Next Actions items
1 ("wire a *_from_binding function into a real invoked path") and 5 ("wire
compile_plan()/compile_plan_from_binding() into a live, invoked run with a
real step_executor").

Deliberately lives in this test file, not in any adapter's own source: no
adapter package may import another (adapters/README.md's isolation rule),
so the composition of langgraph_runtime + model_invokers + ollama_execution
can only happen in neutral code, the same way scripts/asf_cli.py already
imports both langgraph_runtime and ollama_execution as the CLI's own
composition point (see its `compile`/`run` commands).

Opt-in only, mirroring adapters/ollama_execution's existing
ASF_TEST_OLLAMA=1 live-test pattern (adapters/ollama_execution/tests/
test_runner.py::test_live_local_ollama_opt_in): a normal test run never
touches a real Ollama server, requires no API key, and never leaves the
loopback host. Uses runtime/offline/runtime.yaml (a real canonical
Runtime Contract, provider=ollama) bound directly via
asf_runtime.binding.build_runtime_binding() against the minimal
tests/fixtures/graph/valid-runtime/ Skill/Workflow -- not through a
production Skill's dependencies.runtime, since no production Skill
currently declares runtime:offline and wiring one in is a separate,
human-reviewed lifecycle decision (see PROJECT_TRACKER.md).
"""

from __future__ import annotations

import json
import os
from typing import Any

import pytest

import _bootstrap

from asf_runtime.binding import RuntimeBinding, build_runtime_binding
from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext, PlanStep
from asf_runtime.planner import plan_workflow
from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry

from langgraph_runtime.compiler import compile_plan_from_binding
from model_invokers.descriptors import model_descriptor_from_binding
from ollama_execution.executor import DEFAULT_OLLAMA_ENDPOINT, OllamaClient

RUNTIME_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"
OFFLINE_RUNTIME_PATH = _bootstrap.REPO_ROOT / "runtime" / "offline" / "runtime.yaml"


def _fixture_catalog():
    """The full valid-runtime fixture set (matching test_compiler.py's
    runtime_fixture_catalog()) -- skill:use-runtime declares a required
    dependency on runtime:primary, so planning needs it resolvable even
    though this test's actual RuntimeBinding is built separately from the
    real runtime:offline example (see _real_offline_runtime_binding)."""
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    results = [
        build_ir("workflow", RUNTIME_FIXTURES / "workflow.yaml", registry),
        build_ir("skill", RUNTIME_FIXTURES / "skill.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime-fallback.yaml", registry),
        build_ir("tool", RUNTIME_FIXTURES / "tool.yaml", registry),
        build_ir("knowledge", RUNTIME_FIXTURES / "knowledge.md", registry),
    ]
    assert all(result.ok for result in results), [
        (result.artifact, result.diagnostics) for result in results if not result.ok
    ]
    return build_artifact_catalog(results)


def _real_offline_runtime_binding() -> RuntimeBinding:
    """Bind the real runtime/offline/runtime.yaml canonical example directly
    -- not resolved through a production Skill dependency, since nothing
    currently declares it and wiring one in requires a separate,
    human-reviewed status: draft -> active decision (see
    PROJECT_TRACKER.md's Next Actions)."""
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    result = build_ir("runtime", OFFLINE_RUNTIME_PATH, registry)
    assert result.ok, result.diagnostics
    runtime = result.ir
    assert runtime.model.provider == "ollama"
    catalog = _fixture_catalog()
    binding, binding_diagnostics = build_runtime_binding(
        "skill:use-runtime", "1.0.0", runtime, catalog
    )
    assert not [d for d in binding_diagnostics if d.is_error()], binding_diagnostics
    return binding


def _ollama_step_executor(binding: RuntimeBinding, model_override: str | None):
    """Adapt a real local Ollama call into the StepExecutor shape
    compile_plan_from_binding() expects, driven by model_descriptor_from_binding
    -- the exact function Next Actions item 1 asks to exercise in a real call."""
    descriptor = model_descriptor_from_binding(binding)
    assert descriptor is not None
    assert descriptor.provider == "ollama", (
        "hard local-only guard: this proof must never resolve to a paid/cloud "
        f"provider, got '{descriptor.provider}'"
    )
    client = OllamaClient()
    endpoint = descriptor.endpoint or DEFAULT_OLLAMA_ENDPOINT
    model = model_override or descriptor.model

    async def executor(step: PlanStep, state: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Return exactly one JSON object with a single string key "
            '"result" containing one short sentence confirming you received '
            f"this message for step '{step.id}'."
        )
        schema = {
            "type": "object",
            "properties": {"result": {"type": "string", "minLength": 1}},
            "required": ["result"],
        }
        raw = client.generate_structured(
            endpoint, model, prompt, binding.timeout_seconds, schema
        )
        parsed = json.loads(raw)
        return {**state, "result": parsed["result"]}

    return executor


@pytest.mark.skipif(
    os.getenv("ASF_TEST_OLLAMA") != "1",
    reason="live Ollama requires explicit ASF_TEST_OLLAMA=1 opt-in",
)
def test_compile_plan_from_binding_real_invoked_run_via_local_ollama():
    binding = _real_offline_runtime_binding()
    model = os.environ["ASF_OLLAMA_MODEL"]
    catalog = _fixture_catalog()
    context = ExecutionContext.create(
        execution_id="execution-live-ollama-langgraph",
        workflow_id="workflow:use-runtime",
        workflow_version="1.0.0",
        inputs={},
    )
    plan = plan_workflow(context, catalog)

    compiled = compile_plan_from_binding(
        plan,
        step_executor=_ollama_step_executor(binding, model),
        runtime_bindings={"run": binding},
    )

    import asyncio

    result = asyncio.run(compiled.ainvoke({}))
    assert isinstance(result.get("result"), str)
    assert result["result"].strip()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
