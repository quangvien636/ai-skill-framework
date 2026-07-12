import unittest
from pathlib import Path

import _bootstrap

from asf_runtime.binding import resolve_skill_runtime_binding, to_binding_ir
from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_runtime.planner import plan_workflow
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from asf_validator.semantic_validator import validate_semantics
from asf_validator.skill_ir import SkillIR


WORKFLOW = "workflows/research-content-review/workflow.yaml"


def production_results():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    index = discover_project(
        _bootstrap.REPO_ROOT,
        kinds=("skill", "workflow", "knowledge", "runtime"),
    )
    return [
        build_ir(artifact.kind, artifact.path, registry)
        for artifact in index.artifacts
    ]


def composite_inputs():
    return {
        "topic": "Five AI technologies to watch.",
        "objective": "Prepare a practical short-video brief.",
        "content-type": "short-video-script",
        "brief": "Explain five AI risks without exaggeration.",
        "audience": "Working adults and small businesses.",
        "platform": "youtube",
    }


class CompositeWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = production_results()
        assert all(result.ok for result in cls.results)
        cls.catalog = build_artifact_catalog(cls.results)

    def test_composite_artifact_flow_is_semantically_valid(self):
        composite = next(
            result
            for result in self.results
            if Path(result.artifact).resolve()
            == (_bootstrap.REPO_ROOT / WORKFLOW).resolve()
        )
        related = [
            result
            for result in self.results
            if isinstance(result.ir, SkillIR) or result is composite
        ]
        self.assertEqual(validate_semantics(related), [])

        steps = {step.id: step for step in composite.ir.steps}
        self.assertEqual(
            steps["create-content"].input_mapping["research-brief"],
            "steps.research-topic.outputs.research-brief",
        )
        self.assertEqual(
            steps["review-content"].input_mapping["draft"],
            "steps.create-content.outputs.content-package",
        )

    def test_composite_plan_is_one_deterministic_dependency_chain(self):
        context = ExecutionContext.create(
            "composite-plan",
            "workflow:research-content-review",
            "1.0.0",
            composite_inputs(),
        )
        plan = plan_workflow(context, self.catalog)

        self.assertEqual(
            [step.id for step in plan.steps],
            ["research-topic", "create-content", "review-content"],
        )
        self.assertEqual(
            plan.batches,
            (("research-topic",), ("create-content",), ("review-content",)),
        )
        self.assertEqual(
            [step.depends_on for step in plan.steps],
            [(), ("research-topic",), ("create-content",)],
        )

    def test_every_composite_step_has_a_clean_runtime_binding(self):
        plan = plan_workflow(
            ExecutionContext.create(
                "composite-bindings",
                "workflow:research-content-review",
                "1.0.0",
                composite_inputs(),
            ),
            self.catalog,
        )
        runtime_ids = []
        for step in plan.steps:
            skill = self.catalog.exact(step.skill_id, step.skill_version).ir
            binding, diagnostics = resolve_skill_runtime_binding(skill, self.catalog)
            self.assertIsNotNone(binding)
            self.assertFalse(any(item.is_error() for item in diagnostics))
            runtime_ids.append(to_binding_ir(binding, diagnostics).runtime_id)

        self.assertEqual(
            runtime_ids,
            ["runtime:research", "runtime:offline", "runtime:simple"],
        )


if __name__ == "__main__":
    unittest.main()
