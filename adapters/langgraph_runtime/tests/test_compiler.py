import asyncio
import unittest
from dataclasses import replace
from types import MappingProxyType

import _bootstrap

from asf_runtime.catalog import ArtifactCatalog, CatalogArtifact, build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_runtime.planner import plan_workflow
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from langgraph.graph import END, START

from langgraph_runtime.compiler import compile_plan


def production_catalog():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    index = discover_project(
        _bootstrap.REPO_ROOT, kinds=("skill", "workflow", "knowledge")
    )
    return build_artifact_catalog(
        build_ir(artifact.kind, artifact.path, registry)
        for artifact in index.artifacts
    )


RUNTIME_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"


def runtime_fixture_catalog():
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


def _replace_catalog_artifact(catalog, artifact_id, new_ir):
    old = next(a for a in catalog.artifacts if a.id == artifact_id)
    replacement = CatalogArtifact(
        kind=old.kind, id=old.id, version=old.version, status=old.status,
        path=old.path, ir=new_ir,
    )
    artifacts = tuple(replacement if a is old else a for a in catalog.artifacts)
    grouped: dict[str, list] = {}
    for artifact in artifacts:
        grouped.setdefault(artifact.id, []).append(artifact)
    return ArtifactCatalog(
        artifacts, MappingProxyType({k: tuple(v) for k, v in grouped.items()})
    )


class CompilePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = production_catalog()

    def content_context(self, **overrides):
        inputs = {
            "content-type": "social-media-post",
            "brief": "Explain the supplied planning ritual.",
            "audience": "Independent designers.",
            "platform": "linkedin",
        }
        inputs.update(overrides.pop("inputs", {}))
        return ExecutionContext.create(
            execution_id=overrides.pop("execution_id", "execution-1"),
            workflow_id="workflow:content-brief-to-package",
            workflow_version="1.0.0",
            inputs=inputs,
        )

    def _branching_plan(self):
        workflow_artifact = self.catalog.exact(
            "workflow:content-brief-to-package", "1.0.0"
        )
        workflow = workflow_artifact.ir
        base = workflow.steps[0]
        steps = (
            replace(base, id="start", depends_on=(), on_error="fail"),
            replace(base, id="branch-b", depends_on=("start",), on_error="retry"),
            replace(base, id="branch-a", depends_on=("start",), on_error="fail"),
            replace(base, id="finish", depends_on=("branch-b", "branch-a"), on_error="fail"),
        )
        branched = replace(
            workflow,
            entrypoint="start",
            steps=steps,
            graph={step.id: step.depends_on for step in steps},
        )
        catalog = _replace_catalog_artifact(
            self.catalog, "workflow:content-brief-to-package", branched
        )
        return plan_workflow(self.content_context(), catalog)

    def test_compiles_linear_production_plan_with_start_and_end(self):
        plan = plan_workflow(self.content_context(), self.catalog)
        compiled = compile_plan(plan)

        node_ids = {step.id for step in plan.steps}
        self.assertTrue(node_ids.issubset(set(compiled.nodes.keys())))

        edges = {(e.source, e.target) for e in compiled.get_graph().edges}
        self.assertIn((START, "create-content"), edges)
        self.assertIn(("create-content", END), edges)

    def test_preserves_dependency_ordering_and_parallel_batches(self):
        plan = self._branching_plan()
        compiled = compile_plan(plan)

        edges = {(e.source, e.target) for e in compiled.get_graph().edges}
        self.assertIn((START, "start"), edges)
        self.assertIn(("start", "branch-b"), edges)
        self.assertIn(("start", "branch-a"), edges)
        self.assertIn(("branch-b", "finish"), edges)
        self.assertIn(("branch-a", "finish"), edges)
        self.assertIn(("finish", END), edges)
        # branch-b/branch-a share a batch (no edge between them) -- parallel.
        self.assertNotIn(("branch-b", "branch-a"), edges)
        self.assertNotIn(("branch-a", "branch-b"), edges)

    def test_preserves_retry_metadata_only_for_retry_steps(self):
        plan = self._branching_plan()
        compiled = compile_plan(plan)

        self.assertIsNotNone(compiled.nodes["branch-b"].retry_policy)
        self.assertEqual(
            compiled.nodes["branch-b"].retry_policy[0].max_attempts,
            plan.steps[[s.id for s in plan.steps].index("branch-b")].max_attempts,
        )
        self.assertIsNone(compiled.nodes["start"].retry_policy)
        self.assertIsNone(compiled.nodes["branch-a"].retry_policy)

    def test_preserves_timeout_metadata(self):
        skill_artifact = self.catalog.exact("skill:content-creation", "1.0.0")
        timed_skill = replace(
            skill_artifact.ir,
            constraints=replace(skill_artifact.ir.constraints, timeout_seconds=45),
        )
        catalog = _replace_catalog_artifact(
            self.catalog, "skill:content-creation", timed_skill
        )
        plan = plan_workflow(self.content_context(), catalog)
        compiled = compile_plan(plan)

        self.assertEqual(plan.steps[0].timeout_seconds, 45)
        self.assertEqual(compiled.nodes["create-content"].timeout.run_timeout, 45)

    def test_preserves_audit_metadata(self):
        plan = plan_workflow(self.content_context(execution_id="exec-audit"), self.catalog)
        compiled = compile_plan(plan)

        metadata = compiled.nodes["create-content"].metadata
        self.assertEqual(metadata["execution_id"], "exec-audit")
        self.assertEqual(metadata["workflow_id"], "workflow:content-brief-to-package")
        self.assertEqual(metadata["skill_id"], "skill:content-creation")
        self.assertEqual(metadata["batch_index"], 0)
        self.assertEqual(metadata["on_error"], plan.steps[0].on_error)

    def test_compilation_never_executes_and_is_deterministic(self):
        plan = self._branching_plan()
        compiled_once = compile_plan(plan)
        compiled_twice = compile_plan(plan)

        self.assertEqual(
            sorted(compiled_once.nodes.keys()), sorted(compiled_twice.nodes.keys())
        )
        self.assertEqual(
            {(e.source, e.target) for e in compiled_once.get_graph().edges},
            {(e.source, e.target) for e in compiled_twice.get_graph().edges},
        )

        with self.assertRaises(NotImplementedError):
            asyncio.run(compiled_once.ainvoke({}))

    def test_bound_step_executor_is_used_when_provided(self):
        plan = plan_workflow(self.content_context(), self.catalog)
        calls = []

        async def executor(step, state):
            calls.append(step.id)
            return {**state, "ran": step.id}

        compiled = compile_plan(plan, step_executor=executor)
        result = asyncio.run(compiled.ainvoke({}))

        self.assertEqual(calls, ["create-content"])
        self.assertEqual(result["ran"], "create-content")

    def test_runtime_bindings_take_precedence_over_skill_level_policy(self):
        catalog = runtime_fixture_catalog()
        context = ExecutionContext.create(
            execution_id="execution-runtime-compile",
            workflow_id="workflow:use-runtime",
            workflow_version="1.0.0",
            inputs={},
        )
        plan = plan_workflow(context, catalog)
        runtime_artifact = catalog.exact("runtime:primary", "1.0.0")

        compiled = compile_plan(
            plan, runtime_bindings={"run": runtime_artifact.ir}
        )

        node = compiled.nodes["run"]
        self.assertEqual(node.timeout.run_timeout, runtime_artifact.ir.timeout_policy.timeout_seconds)
        self.assertEqual(node.metadata["runtime_id"], "runtime:primary")
        self.assertEqual(node.metadata["execution_profile"], "sync")
        self.assertEqual(node.metadata["safety_content_filter"], "standard")
        self.assertEqual(node.metadata["audit_log_level"], "basic")

    def test_compile_plan_without_runtime_bindings_uses_skill_level_policy(self):
        catalog = runtime_fixture_catalog()
        context = ExecutionContext.create(
            execution_id="execution-runtime-compile-2",
            workflow_id="workflow:use-runtime",
            workflow_version="1.0.0",
            inputs={},
        )
        plan = plan_workflow(context, catalog)
        compiled = compile_plan(plan)

        node = compiled.nodes["run"]
        self.assertNotIn("runtime_id", node.metadata)


if __name__ == "__main__":
    unittest.main()
