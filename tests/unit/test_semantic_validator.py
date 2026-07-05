import unittest

import _bootstrap

from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from asf_validator.semantic_validator import validate_semantics


SEMANTIC_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "semantic"


class SemanticValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)

    def load(self, entries):
        return [
            build_ir(kind, SEMANTIC_FIXTURES / name, self.registry)
            for kind, name in entries
        ]

    def test_duplicate_metrics_weight_and_reflection_rules(self):
        results = self.load([("skill", "invalid-skill.yaml")])
        self.assertTrue(all(result.ok for result in results))
        diagnostics = validate_semantics(results)
        self.assertEqual(
            {diagnostic.code for diagnostic in diagnostics},
            {
                "ASF-SEMANTIC-001",
                "ASF-SEMANTIC-002",
                "ASF-SEMANTIC-003",
                "ASF-SEMANTIC-004",
            },
        )

    def test_mapping_routing_type_and_topology_rules(self):
        results = self.load(
            [
                ("skill", "mapping-skill.yaml"),
                ("workflow", "invalid-workflow.yaml"),
            ]
        )
        self.assertTrue(all(result.ok for result in results))
        diagnostics = validate_semantics(results)
        self.assertEqual(
            {diagnostic.code for diagnostic in diagnostics},
            {
                "ASF-SEMANTIC-005",
                "ASF-SEMANTIC-006",
                "ASF-SEMANTIC-007",
                "ASF-SEMANTIC-008",
                "ASF-SEMANTIC-009",
            },
        )

    def test_all_production_skills_and_workflows_are_semantically_valid(self):
        entries = [
            (
                "skill",
                _bootstrap.REPO_ROOT / "skills/content-creation/skill.yaml",
            ),
            (
                "workflow",
                _bootstrap.REPO_ROOT
                / "workflows/content-brief-to-package/workflow.yaml",
            ),
            ("skill", _bootstrap.REPO_ROOT / "skills/research/skill.yaml"),
            (
                "workflow",
                _bootstrap.REPO_ROOT
                / "workflows/research-topic-to-brief/workflow.yaml",
            ),
            ("skill", _bootstrap.REPO_ROOT / "skills/review-quality/skill.yaml"),
            (
                "workflow",
                _bootstrap.REPO_ROOT
                / "workflows/draft-to-reviewed-package/workflow.yaml",
            ),
        ]
        results = [build_ir(kind, path, self.registry) for kind, path in entries]
        self.assertTrue(all(result.ok for result in results))
        self.assertEqual(validate_semantics(results), [])

    def test_diagnostics_are_structured_and_actionable(self):
        diagnostics = validate_semantics(
            self.load([("skill", "invalid-skill.yaml")])
        )
        self.assertTrue(diagnostics)
        self.assertTrue(all(diagnostic.artifact for diagnostic in diagnostics))
        self.assertTrue(all(diagnostic.location for diagnostic in diagnostics))
        self.assertTrue(all(diagnostic.message for diagnostic in diagnostics))
        self.assertTrue(all(diagnostic.suggestion for diagnostic in diagnostics))


if __name__ == "__main__":
    unittest.main()
