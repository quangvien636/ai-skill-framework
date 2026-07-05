import unittest
from dataclasses import replace
from types import MappingProxyType

import _bootstrap

from asf_runtime.catalog import ArtifactCatalog, CatalogArtifact, build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_runtime.planner import PlanningError, plan_workflow
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry

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


def production_catalog():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    index = discover_project(
        _bootstrap.REPO_ROOT, kinds=("skill", "workflow", "knowledge")
    )
    return build_artifact_catalog(
        build_ir(artifact.kind, artifact.path, registry)
        for artifact in index.artifacts
    )


class RuntimePlannerTests(unittest.TestCase):
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

    def test_plans_production_workflow_and_resolves_knowledge(self):
        plan = plan_workflow(self.content_context(), self.catalog)
        self.assertEqual(plan.workflow_id, "workflow:content-brief-to-package")
        self.assertEqual([step.id for step in plan.steps], ["create-content"])
        self.assertEqual(plan.batches, (("create-content",),))
        self.assertEqual(len(plan.steps[0].knowledge), 5)
        self.assertEqual(len(plan.resolutions), 6)
        self.assertTrue(
            all(resolution.target_version == "1.0.0" for resolution in plan.resolutions)
        )

    def test_execution_context_deep_freezes_inputs(self):
        context = self.content_context(inputs={"constraints": ["one"]})
        self.assertEqual(context.inputs["constraints"], ("one",))
        with self.assertRaises(TypeError):
            context.inputs["brief"] = "changed"

    def test_missing_required_input_fails_before_planning(self):
        context = self.content_context()
        inputs = dict(context.inputs)
        del inputs["brief"]
        with self.assertRaises(PlanningError) as caught:
            plan_workflow(
                ExecutionContext.create(
                    "execution-2",
                    context.workflow_id,
                    context.workflow_version,
                    inputs,
                ),
                self.catalog,
            )
        self.assertEqual(caught.exception.code, "ASF-RUNTIME-PLAN-002")

    def test_undeclared_input_fails_before_planning(self):
        with self.assertRaises(PlanningError) as caught:
            plan_workflow(
                self.content_context(inputs={"not-declared": "value"}), self.catalog
            )
        self.assertEqual(caught.exception.code, "ASF-RUNTIME-PLAN-002")

    def test_missing_skill_resolution_is_structured_failure(self):
        artifacts = tuple(
            artifact
            for artifact in self.catalog.artifacts
            if artifact.id != "skill:content-creation"
        )
        by_id = {}
        for artifact in artifacts:
            by_id.setdefault(artifact.id, []).append(artifact)
        catalog = ArtifactCatalog(
            artifacts,
            MappingProxyType(
                {key: tuple(entries) for key, entries in by_id.items()}
            ),
        )
        with self.assertRaises(PlanningError) as caught:
            plan_workflow(self.content_context(), catalog)
        self.assertEqual(caught.exception.code, "ASF-RUNTIME-PLAN-003")

    def test_branching_plan_uses_manifest_order_for_ready_batches(self):
        workflow_artifact = self.catalog.exact(
            "workflow:content-brief-to-package", "1.0.0"
        )
        workflow = workflow_artifact.ir
        base = workflow.steps[0]
        steps = (
            replace(base, id="start", depends_on=()),
            replace(base, id="branch-b", depends_on=("start",)),
            replace(base, id="branch-a", depends_on=("start",)),
            replace(base, id="finish", depends_on=("branch-b", "branch-a")),
        )
        branched = replace(
            workflow,
            entrypoint="start",
            steps=steps,
            graph={step.id: step.depends_on for step in steps},
        )
        replacement = CatalogArtifact(
            kind=workflow_artifact.kind,
            id=workflow_artifact.id,
            version=workflow_artifact.version,
            status=workflow_artifact.status,
            path=workflow_artifact.path,
            ir=branched,
        )
        artifacts = tuple(
            replacement if item is workflow_artifact else item
            for item in self.catalog.artifacts
        )
        grouped = {}
        for artifact in artifacts:
            grouped.setdefault(artifact.id, []).append(artifact)
        catalog = ArtifactCatalog(
            artifacts,
            MappingProxyType(
                {key: tuple(entries) for key, entries in grouped.items()}
            ),
        )
        plan = plan_workflow(self.content_context(), catalog)
        self.assertEqual(
            plan.batches,
            (("start",), ("branch-b", "branch-a"), ("finish",)),
        )
        self.assertEqual(
            [step.id for step in plan.steps],
            ["start", "branch-b", "branch-a", "finish"],
        )

    def test_plans_runtime_contract_resolution_chain(self):
        catalog = runtime_fixture_catalog()
        context = ExecutionContext.create(
            execution_id="execution-runtime-1",
            workflow_id="workflow:use-runtime",
            workflow_version="1.0.0",
            inputs={},
        )
        plan = plan_workflow(context, catalog)

        self.assertEqual([step.id for step in plan.steps], ["run"])
        step = plan.steps[0]
        self.assertEqual(
            {(r.target_id, r.kind) for r in step.runtime},
            {
                ("runtime:primary", "skill-runtime"),
                ("kb:technical:writing:summarization:brevity", "runtime-knowledge"),
                ("tool:read-file", "runtime-tool"),
                ("runtime:fallback-target", "runtime-runtime"),
            },
        )
        # Every runtime resolution is also recorded on the overall plan.
        plan_runtime_kinds = {
            (r.target_id, r.kind)
            for r in plan.resolutions
            if r.kind in ("skill-runtime", "runtime-knowledge", "runtime-tool", "runtime-runtime")
        }
        self.assertEqual(plan_runtime_kinds, {(r.target_id, r.kind) for r in step.runtime})

    def test_missing_runtime_resolution_is_structured_failure(self):
        catalog = runtime_fixture_catalog()
        artifacts = tuple(
            artifact for artifact in catalog.artifacts if artifact.id != "runtime:primary"
        )
        by_id: dict[str, list] = {}
        for artifact in artifacts:
            by_id.setdefault(artifact.id, []).append(artifact)
        pruned = ArtifactCatalog(
            artifacts, MappingProxyType({key: tuple(entries) for key, entries in by_id.items()})
        )
        context = ExecutionContext.create(
            execution_id="execution-runtime-2",
            workflow_id="workflow:use-runtime",
            workflow_version="1.0.0",
            inputs={},
        )
        with self.assertRaises(PlanningError) as caught:
            plan_workflow(context, pruned)
        self.assertEqual(caught.exception.code, "ASF-RUNTIME-PLAN-006")


if __name__ == "__main__":
    unittest.main()
